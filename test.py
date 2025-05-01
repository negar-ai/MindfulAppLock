from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty

class BreathingWidget(Widget):
    radius = NumericProperty(50)
    phase_text = StringProperty("Tap to Begin")
    
    def __init__(self, **kwargs):
        super(BreathingWidget, self).__init__(**kwargs)
        self.breathing = False
        self.inhale_duration = 4
        self.hold_duration = 2
        self.exhale_duration = 4
        self.rest_duration = 2
        self.cycle_count = 0
        self.max_cycles = 3
        self.min_radius = 50
        
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
    
    def start_inhale(self, *args):
        self.phase_text = "Inhale"
        min_dimension = min(self.width, self.height)
        max_radius = min_dimension / 3  # Maximum radius for the circle
        
        # Cancel any existing animations
        Animation.cancel_all(self)
        
        # Create the inhale animation
        inhale_anim = Animation(radius=max_radius, duration=self.inhale_duration, transition='out_quad')
        inhale_anim.bind(on_complete=self.start_hold)
        inhale_anim.start(self)
    
    def start_hold(self, *args):
        self.phase_text = "Hold"
        # Cancel any existing animations
        Animation.cancel_all(self)
        
        hold_anim = Animation(duration=self.hold_duration)
        hold_anim.bind(on_complete=self.start_exhale)
        hold_anim.start(self)
    
    def start_exhale(self, *args):
        self.phase_text = "Exhale"
        # Cancel any existing animations
        Animation.cancel_all(self)
        
        exhale_anim = Animation(radius=self.min_radius, duration=self.exhale_duration, transition='in_quad')
        exhale_anim.bind(on_complete=self.start_rest)
        exhale_anim.start(self)
    
    def start_rest(self, *args):
        self.cycle_count += 1
        print(f"Completed cycle {self.cycle_count} of {self.max_cycles}")
        
        if self.cycle_count >= self.max_cycles:
            self.phase_text = "Tap to Begin"
            self.breathing = False
            return
        
        self.phase_text = "Rest"
        # Cancel any existing animations
        Animation.cancel_all(self)
        
        rest_anim = Animation(duration=self.rest_duration)
        rest_anim.bind(on_complete=self.start_inhale)
        rest_anim.start(self)

class BreathingApp(App):
    def build(self):
        # Set background color
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        
        # Set up the main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Add instructions label
        instructions = Label(
            text="Breathing Exercise\nFollow the circle and instructions",
            font_size='20sp',
            size_hint=(1, 0.15),
            color=(0.2, 0.2, 0.2, 1)
        )
        main_layout.add_widget(instructions)
        
        # Add the breathing widget (give it more space)
        self.breathing_widget = BreathingWidget()
        main_layout.add_widget(self.breathing_widget)
        
        # Add controls
        controls_layout = BoxLayout(size_hint=(1, 0.15), spacing=15)
        
        reset_button = Button(
            text="Reset", 
            size_hint=(0.5, 1),
            background_color=(0.3, 0.6, 0.9, 1)
        )
        reset_button.bind(on_press=self.reset_exercise)
        
        exit_button = Button(
            text="Exit", 
            size_hint=(0.5, 1),
            background_color=(0.9, 0.3, 0.3, 1)
        )
        exit_button.bind(on_press=self.stop)
        
        controls_layout.add_widget(reset_button)
        controls_layout.add_widget(exit_button)
        main_layout.add_widget(controls_layout)
        
        # Add phase label (make it more prominent)
        self.phase_label = Label(
            font_size='28sp', 
            size_hint=(1, 0.1),
            color=(0.1, 0.4, 0.8, 1),
            bold=True
        )
        main_layout.add_widget(self.phase_label)
        
        # Bind the phase text
        self.breathing_widget.bind(phase_text=self.update_phase_label)
        
        # Add a debug label for tracking cycles
        self.debug_label = Label(
            text="", 
            font_size='14sp', 
            size_hint=(1, 0.05),
            color=(0.5, 0.5, 0.5, 1)
        )
        main_layout.add_widget(self.debug_label)
        
        # Schedule regular updates
        Clock.schedule_interval(self.update_debug, 0.5)
        
        return main_layout
    
    def update_phase_label(self, instance, value):
        self.phase_label.text = value
    
    def update_debug(self, dt):
        if hasattr(self.breathing_widget, 'cycle_count') and self.breathing_widget.breathing:
            self.debug_label.text = f"Cycle: {self.breathing_widget.cycle_count + 1} of {self.breathing_widget.max_cycles}"
        elif not self.breathing_widget.breathing:
            self.debug_label.text = "Ready"
    
    def reset_exercise(self, instance):
        # Cancel any animations first
        Animation.cancel_all(self.breathing_widget)
        
        # Reset the breathing widget
        self.breathing_widget.breathing = False
        self.breathing_widget.phase_text = "Tap to Begin"
        self.breathing_widget.radius = 50 
        self.breathing_widget.cycle_count = 0
        self.breathing_widget.update_circle()

if __name__ == '__main__':
    BreathingApp().run()