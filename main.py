from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty, ColorProperty, NumericProperty, BooleanProperty
import json
import datetime
import os
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, RoundedRectangle
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.animation import Animation

class WindowManager(ScreenManager):
    pass

class MindfulApp(App):
    theme_mode = StringProperty('light')
    def build(self):
        # Ensure app_data.json exists
        try:
            with open("app_data.json", "x") as f:
                json.dump({
                    "emergency_used": "",
                    "app_unlocked": False,
                    "last_check_date": str(datetime.date.today())
                }, f)
        except FileExistsError:
            # Check if we need to update the structure
            try:
                with open("app_data.json", "r") as f:
                    data = json.load(f)

                if "last_check_date" not in data:
                    data["last_check_date"] = str(datetime.date.today())
                    with open("app_data.json", "w") as f:
                        json.dump(data, f)
            except:
                pass

        # Ensure gratefulness_entries.json exists
        try:
            with open("gratefulness_entries.json", "x") as f:
                json.dump({"entries": []}, f)
        except FileExistsError:
            pass

        # Ensure last_gratefulness_date.json exists
        try:
            with open("last_gratefulness_date.json", "x") as f:
                json.dump({"last_date": ""}, f)
        except FileExistsError:
            pass

        return Builder.load_file('mindful.kv')

def get_last_gratefulness_date():
    try:
        with open("last_gratefulness_date.json", "r") as f:
            data = json.load(f)
            return data.get('last_date', "")
    except (FileExistsError, FileNotFoundError, json.JSONDecodeError):
        return ""

def set_last_gratefulness_date():
    today = str(datetime.date.today())
    with open("last_gratefulness_date.json", "w") as f:
        json.dump({"last_date": today}, f)

def should_show_gratefulness():
    today = str(datetime.date.today())
    last_date = get_last_gratefulness_date()
    return last_date != today

def save_gratefulness_entry(entry):
    try:
        with open("gratefulness_entries.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"entries": []}

    today = str(datetime.date.today())
    new_entry = {"date": today, "entry": entry}
    data["entries"].append(new_entry)

    with open("gratefulness_entries.json", "w") as f:
        json.dump(data, f)

    # Update the last gratefulness date
    set_last_gratefulness_date()

def get_gratefulness_entries():
    try:
        with open("gratefulness_entries.json", "r") as f:
            data = json.load(f)
            return data.get("entries", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def unlock_app():
    try:
        with open("app_data.json", "r") as f:
            data = json.load(f)

        data["app_unlocked"] = True

        with open("app_data.json", "w") as f:
            json.dump(data, f)

        return True
    except:
        return False

def is_app_unlocked():
    try:
        with open("app_data.json", "r") as f:
            data = json.load(f)
            # Make sure we're getting a boolean value
            return bool(data.get("app_unlocked", False))
    except Exception as e:
        print(f"Error checking app unlock status: {e}")
        return False

def reset_app_unlock():
    try:
        with open("app_data.json", "r") as f:
            data = json.load(f)

        data["app_unlocked"] = False
        # Reset emergency_used when resetting app unlock status
        data["emergency_used"] = ""

        with open("app_data.json", "w") as f:
            json.dump(data, f)
    except:
        pass

class BreathingWidget(Widget):
    radius = NumericProperty(30)
    phase_text = StringProperty("Breath!")
    countdown_text = StringProperty("")

    def __init__(self, **kwargs):
        super(BreathingWidget, self).__init__(**kwargs)
        self.breathing = False
        self.inhale_duration = 4
        self.hold_duration = 2
        self.exhale_duration = 4
        self.rest_duration = 2
        self.cycle_count = 0
        self.min_radius = 30
        self.phase_countdown = 0
        self.countdown_event = None

        # Schedule a delayed call to ensure proper initialization
        Clock.schedule_once(self.init_graphics, 0)

    def init_graphics(self, dt):
        # Clear any existing canvas instructions
        self.canvas.clear()

        # Initial circle
        with self.canvas:
            Color(0.4, 0.8, 0.9, 0.8)  # Soft blue color
            self.circle = Ellipse(pos=(self.center_x - self.radius, self.center_y - self.radius),
                                 size=(self.radius * 2, self.radius * 2))

        # Bind to property changes
        self.bind(pos=self.update_circle, size=self.update_circle, radius=self.update_circle)

    def update_circle(self, *args):
        if hasattr(self, 'circle'):
            self.circle.pos = (self.center_x - self.radius, self.center_y - self.radius)
            self.circle.size = (self.radius * 2, self.radius * 2)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.breathing:
            self.start_breathing()
            return True
        return super(BreathingWidget, self).on_touch_down(touch)

    def start_breathing(self):
        self.breathing = True
        self.cycle_count = 0
        Clock.schedule_once(self.start_inhale, 0.1)  # Short delay before starting

    def update_countdown(self, dt):
        if self.phase_countdown > 0:
            self.phase_countdown -= 1
            self.countdown_text = str(self.phase_countdown)
        else:
            if self.countdown_event:
                self.countdown_event.cancel()
                self.countdown_event = None

    def start_inhale(self, *args):
        if not self.breathing:
            return  # Stop if breathing exercise has been canceled

        self.phase_text = "Inhale"
        self.phase_countdown = self.inhale_duration
        self.countdown_text = str(self.phase_countdown)

        # Start countdown
        if self.countdown_event:
            self.countdown_event.cancel()
        self.countdown_event = Clock.schedule_interval(self.update_countdown, 1)

        min_dimension = min(self.width, self.height)
        max_radius = min_dimension / 3  # Maximum radius for the circle

        # Cancel any existing animations
        Animation.cancel_all(self)

        # Create the inhale animation
        inhale_anim = Animation(radius=max_radius, duration=self.inhale_duration, transition='out_quad')
        inhale_anim.bind(on_complete=self.start_hold)
        inhale_anim.start(self)

    def start_hold(self, *args):
        if not self.breathing:
            self.phase_text = "c:"
            return  # Stop if breathing exercise has been canceled

        self.phase_text = "Hold"
        self.phase_countdown = self.hold_duration
        self.countdown_text = str(self.phase_countdown)

        # Start countdown
        if self.countdown_event:
            self.countdown_event.cancel()
        self.countdown_event = Clock.schedule_interval(self.update_countdown, 1)

        # Cancel any existing animations
        Animation.cancel_all(self)

        hold_anim = Animation(duration=self.hold_duration)
        hold_anim.bind(on_complete=self.start_exhale)
        hold_anim.start(self)

    def start_exhale(self, *args):
        if not self.breathing:
            return  # Stop if breathing exercise has been canceled

        self.phase_text = "Exhale"
        self.phase_countdown = self.exhale_duration
        self.countdown_text = str(self.phase_countdown)

        # Start countdown
        if self.countdown_event:
            self.countdown_event.cancel()
        self.countdown_event = Clock.schedule_interval(self.update_countdown, 1)

        # Cancel any existing animations
        Animation.cancel_all(self)

        exhale_anim = Animation(radius=self.min_radius, duration=self.exhale_duration, transition='in_quad')
        exhale_anim.bind(on_complete=self.start_rest)
        exhale_anim.start(self)

    def start_rest(self, *args):
        if not self.breathing:
            return  # Stop if breathing exercise has been canceled

        self.cycle_count += 1

        # Start next cycle immediately instead of stopping after max_cycles
        self.phase_text = "Hold"
        self.phase_countdown = self.rest_duration
        self.countdown_text = str(self.phase_countdown)

        # Start countdown
        if self.countdown_event:
            self.countdown_event.cancel()
            self.phase_text = "Done!"
        self.countdown_event = Clock.schedule_interval(self.update_countdown, 1)

        # Cancel any existing animations
        Animation.cancel_all(self)

        rest_anim = Animation(duration=self.rest_duration)
        rest_anim.bind(on_complete=self.start_inhale)
        rest_anim.start(self)

    def reset_exercise(self):
        # Cancel any animations first
        Animation.cancel_all(self)

        # Cancel countdown timer
        if self.countdown_event:
            self.countdown_event.cancel()
            self.countdown_event = None

        # Reset the breathing widget
        self.breathing = False
        self.phase_text = "Breath!"
        self.countdown_text = ""
        self.radius = 50
        self.cycle_count = 0
        self.update_circle()

class MainScreen(Screen):
    message = StringProperty("Start a Challenge first!")

    def on_enter(self):
        # Check and reset app state on new day
        self.check_new_day()

        # Update message based on app unlock status
        if is_app_unlocked():
            self.message = "App is unlocked for today!"
        else:
            self.message = "Start a Challenge first!"

        # Debug logs for troubleshooting
        try:
            with open("app_data.json", "r") as f:
                data = json.load(f)
                print(f"App data: {data}")
                print(f"App unlocked status: {data.get('app_unlocked', False)}")
                print(f"Emergency used: {data.get('emergency_used', '')}")
                print(f"Today's date: {str(datetime.date.today())}")
        except Exception as e:
            print(f"Error reading app data: {e}")

    def check_new_day(self):
        # Reset app unlock status on new day
        today = str(datetime.date.today())
        try:
            # First check if the file exists
            if not os.path.exists("app_data.json"):
                # Create the file with default values
                with open("app_data.json", "w") as f:
                    json.dump({
                        "emergency_used": "",
                        "app_unlocked": False,
                        "last_check_date": today
                    }, f)
                return

            # Read the current data
            with open("app_data.json", "r") as f:
                data = json.load(f)

            # If it's a new day, reset the unlock status
            if "last_check_date" not in data or data.get("last_check_date") != today:
                # Reset app unlock but preserve other data
                data["app_unlocked"] = False
                data["emergency_used"] = ""
                data["last_check_date"] = today

                # Write the updated data back
                with open("app_data.json", "w") as f:
                    json.dump(data, f)

                print(f"Reset app for new day: {today}")

        except Exception as e:
            print(f"Error checking new day: {e}")
            # Create a new file if there was an error
            try:
                with open("app_data.json", "w") as f:
                    json.dump({
                        "emergency_used": "",
                        "app_unlocked": False,
                        "last_check_date": today
                    }, f)
            except Exception as inner_e:
                print(f"Failed to create new app_data.json: {inner_e}")

    def emergency_unlock(self):
        today = str(datetime.date.today())

        try:
            with open("app_data.json", "r") as f:
                data = json.load(f)

            # Check if emergency has been used today
            if data.get("emergency_used") == today:
                self.message = "Emergency already used today."
            else:
                # Update emergency used date and unlock app
                data["emergency_used"] = today
                data["app_unlocked"] = True

                # Make sure to write the file before closing the app
                with open("app_data.json", "w") as f:
                    json.dump(data, f)

                self.message = "Emergency access granted."

                # Close the app after granting emergency access
                Clock.schedule_once(self.close_app, 2)
        except Exception as e:
            print(f"Error in emergency unlock: {e}")
            # Create a new app_data.json file with emergency unlocked if there was an error
            try:
                with open("app_data.json", "w") as f:
                    json.dump({
                        "emergency_used": today,
                        "app_unlocked": True,
                        "last_check_date": today
                    }, f)
                self.message = "Emergency access granted."
                Clock.schedule_once(self.close_app, 2)
            except Exception as inner_e:
                print(f"Failed to create new app_data.json: {inner_e}")
                self.message = "Error processing emergency access."

    def close_app(self, dt):
        # Stop the app
        App.get_running_app().stop()

    def start_challenge(self):
        # Check if gratefulness task should be shown today
        if should_show_gratefulness():
            self.manager.current = "gratitude"
        else:
            self.manager.current = "breath"

class GratefulnessScreen(Screen):
    entry_text = StringProperty("")
    message = StringProperty("What are you grateful for today?")

    def submit_entry(self):
        if self.entry_text.strip():
            save_gratefulness_entry(self.entry_text)
            self.message = "Thank you for sharing your gratitude!"
            # Close the app after short delay
            Clock.schedule_once(self.close_app, 2)
        else:
            self.message = "Please enter something you're grateful for."

    def close_app(self, dt):
        # Stop the app
        App.get_running_app().stop()

class GratefulnessHistoryScreen(Screen):
    entries_text = StringProperty("")

    def on_enter(self):
        entries = get_gratefulness_entries()
        if entries:
            entries_text = ""
            for entry in entries:
                entries_text += f"{entry['date']}: {entry['entry']}\n\n"
            self.entries_text = entries_text
        else:
            self.entries_text = "No gratefulness entries yet."

class BreathingTaskScreen(Screen):
    timer_text = StringProperty("5:00")
    complete_button_opacity = NumericProperty(0.9)
    timer_complete = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(BreathingTaskScreen, self).__init__(**kwargs)
        self.timer_event = None
        self.time_remaining = 10  # 5 minutes in seconds

    def on_enter(self):
        # Start the timer and breathing exercise when entering this screen
        self.start_timer()
        Clock.schedule_once(self.start_breathing_exercise, 0.5)

    def on_leave(self):
        # Cancel timer when leaving this screen
        self.cancel_timer()

    def start_breathing_exercise(self, dt):
        breathing_widget = self.ids.breathing_widget
        if breathing_widget and not breathing_widget.breathing:
            breathing_widget.start_breathing()

    def start_timer(self):
        self.time_remaining = 10  # Reset to 5 minutes
        self.timer_text = "5:00"
        self.timer_complete = False
        self.complete_button_opacity = 0.5  # Increased from 0.3 for better visibility

        # Cancel any existing timer events
        if self.timer_event:
            self.timer_event.cancel()

        # Schedule the timer update
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        if self.time_remaining <= 0:
            # Timer complete
            self.timer_text = "0:00"
            self.timer_complete = True
            self.complete_button_opacity = 1.0

            # Stop the breathing exercise when timer completes
            breathing_widget = self.ids.breathing_widget
            if breathing_widget:
                breathing_widget.breathing = False

            self.timer_event.cancel()
            self.timer_event = None
            return False

        self.time_remaining -= 1
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        self.timer_text = f"{minutes}:{seconds:02d}"

    def cancel_timer(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

        # Reset the breathing widget
        breathing_widget = self.ids.breathing_widget
        if breathing_widget:
            breathing_widget.reset_exercise()

    def go_back(self):
        # Stop exercise and return to main screen
        self.cancel_timer()
        self.manager.current = "main"

    def complete_exercise(self):
        if self.timer_complete:
            # Unlock the app
            unlock_app()
            # Close the app
            App.get_running_app().stop()

if __name__ == "__main__":
    MindfulApp().run()