from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty, ColorProperty, NumericProperty, BooleanProperty
import json
import datetime
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.animation import Animation

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
        # print(f"Completed cycle {self.cycle_count}")
        
        # Start next cycle immediately instead of stopping after max_cycles
        self.phase_text = "Hold"
        self.phase_countdown = self.rest_duration
        self.countdown_text = str(self.phase_countdown)
        
        # Start countdown
        if self.countdown_event:
            self.countdown_event.cancel()
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
        self.phase_text = "Tap to Begin"
        self.countdown_text = ""
        self.radius = 50 
        self.cycle_count = 0
        self.update_circle()

# Change MainScreen from BoxLayout to Screen
class MainScreen(Screen):
    message = StringProperty("Welcome! Choose an app to open.")

    def open_app(self):
        # Placeholder for logic
        self.message = "You must complete a challenge first!"

    def emergency_unlock(self):
        today = str(datetime.date.today())
        with open("app_data.json", "r+") as f:
            data = json.load(f)
            if data.get("emergency_used") == today:
                self.message = "Emergency already used today."
            else:
                data["emergency_used"] = today
                f.seek(0)
                json.dump(data, f)
                f.truncate()
                self.message = "Emergency access granted."
                
class BreathingTaskScreen(Screen):
    timer_text = StringProperty("5:00")
    complete_button_opacity = NumericProperty(0.9) 
    timer_complete = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(BreathingTaskScreen, self).__init__(**kwargs)
        self.timer_event = None
        self.time_remaining = 300  # 5 minutes in seconds
        
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
        self.time_remaining = 300  # Reset to 5 minutes
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
            # Only allow completion if timer is finished
            self.manager.current = "main"
            # Here you could add additional logic for exercise completion

class WindowManager(ScreenManager):
    pass

class MindfulApp(App):
    def build(self):
        try:
            with open("app_data.json", "x") as f:
                json.dump({"emergency_used": ""}, f)
        except FileExistsError:
            pass
        return Builder.load_file('mindful.kv')
    
if __name__ == "__main__":
    MindfulApp().run()