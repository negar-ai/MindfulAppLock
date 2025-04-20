from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
import json
import datetime

class MainScreen(BoxLayout):
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

class MindfulApp(App):
    def build(self):
        try:
            with open("app_data.json", "x") as f:
                json.dump({"emergency_used": ""}, f)
        except FileExistsError:
            pass
        return MainScreen()

if __name__ == "__main__":
    MindfulApp().run()
