from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.slider import Slider
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
import json, os

Window.size = (360, 640)

USER_DB = "users.json"
if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f)

# ---------- Styled Inputs and Buttons ----------
class OutlinedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.after:
            Color(0.2,0.2,0.6,1)
            self._outline = Line(rectangle=(self.x,self.y,self.width,self.height), width=1.2)
        self.bind(pos=self.update_outline, size=self.update_outline)
    def update_outline(self, *args):
        self._outline.rectangle = (self.x,self.y,self.width,self.height)

def rounded_text_input(hint):
    return OutlinedTextInput(
        hint_text=hint, multiline=False, size_hint=(None,None),
        width=dp(280), height=dp(44),
        padding=[dp(10),dp(12)],
        background_normal='', background_active='',
        background_color=(1,1,1,1),
        foreground_color=(0,0,0,1),
        cursor_color=(0,0,0,1)
    )

def styled_button(text, on_press_fn):
    btn = Button(
        text=text, size_hint=(None,None),
        width=dp(280), height=dp(44),
        background_normal='', background_color=(0.1,0.3,0.6,1),
        color=(1,1,1,1), font_size='16sp'
    )
    btn.bind(on_press=on_press_fn)
    return btn

def screen_layout(title_text, elements):
    layout = BoxLayout(orientation='vertical', spacing=dp(12), size_hint=(1,None), height=dp(600))
    layout.padding = [dp(0), dp(40)]
    layout.add_widget(Label(text="STATHLETE", font_size='32sp', bold=True, color=(0,0,0,1), size_hint=(1,None), height=dp(50)))
    if title_text:
        layout.add_widget(Label(text=title_text, font_size='22sp', color=(0,0,0,1), size_hint=(1,None), height=dp(36)))
    for el in elements:
        box = AnchorLayout(anchor_x='center')
        box.add_widget(el)
        layout.add_widget(box)
    return layout

# ---------- Login Screen ----------
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_background()
        self.username = rounded_text_input("Username or Email")
        self.password = rounded_text_input("Password")
        self.password.password = True

        layout = screen_layout("Login", [
            self.username,
            self.password,
            styled_button("Log In", self.login),
            Label(text="or", font_size='14sp', color=(0.4,0.4,0.4,1), size_hint=(None,None), height=dp(20)),
            styled_button("Sign Up", self.go_to_signup)
        ])

        wrapper = AnchorLayout(anchor_x='center', anchor_y='top')
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def login(self, instance):
        users = load_users()
        uname = self.username.text.strip()
        pword = self.password.text.strip()
        if uname in users and users[uname] == pword:
            self.manager.current = "home"
        else:
            print("Invalid login")

    def go_to_signup(self, instance):
        self.manager.current = "signup"

    def set_background(self):
        with self.canvas.before:
            Color(1,1,1,1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self.update_bg)
    def update_bg(self, *args):
        self.bg_rect.size = self.size

# ---------- Signup Screen ----------
class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_background()
        self.username = rounded_text_input("Username")
        self.email = rounded_text_input("Email")
        self.password = rounded_text_input("Password")
        self.password.password = True

        layout = screen_layout("Sign Up", [
            self.username,
            self.email,
            self.password,
            styled_button("Sign Up", self.register),
            Label(text="Already have an account?", font_size='14sp', color=(0.4,0.4,0.4,1), size_hint=(None,None), height=dp(20)),
            styled_button("Log In", self.go_to_login)
        ])

        wrapper = AnchorLayout(anchor_x='center', anchor_y='top')
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def register(self, instance):
        users = load_users()
        uname = self.username.text.strip()
        pword = self.password.text.strip()
        if uname in users:
            print("Username exists")
        else:
            users[uname] = pword
            save_users(users)
            self.manager.current = "profile"

    def go_to_login(self, instance):
        self.manager.current = "login"

    def set_background(self):
        with self.canvas.before:
            Color(1,1,1,1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self.update_bg)
    def update_bg(self, *args):
        self.bg_rect.size = self.size

# ---------- Custom Blue SpinnerOption ----------
class BlueOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0.1,0.3,0.6,1)
        self.color = (1,1,1,1)

# ---------- Profile Screen ----------
class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_background()
        def styled_spinner(text, values):
            return Spinner(
                text=text, values=values, size_hint=(None,None), width=dp(280), height=dp(44),
                background_normal='', background_color=(0.1,0.3,0.6,1), color=(1,1,1,1),
                option_cls=BlueOption
            )

        self.gender = styled_spinner("Select Gender", ["Male","Female"])
        self.sport = styled_spinner("Select Sport", ["Soccer","Basketball","Football","Baseball","Tennis","Other"])
        self.education = styled_spinner("Select Education/Level", ["High School JV","HS Varsity","D3","D2","D1","NAIA","Other"])
        self.feet = rounded_text_input("Feet")
        self.inches = rounded_text_input("Inches")
        self.weight = rounded_text_input("Weight (lbs)")
        self.age = rounded_text_input("Age")

        elements = [
            Label(text="Complete Your Profile", font_size='22sp', color=(0,0,0,1), size_hint=(1,None), height=dp(36)),
            self.gender, self.feet, self.inches, self.weight, self.age, self.sport, self.education,
            styled_button("Submit Profile", self.submit_profile)
        ]

        layout = screen_layout("", elements)
        wrapper = AnchorLayout(anchor_x='center', anchor_y='top')
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def submit_profile(self, instance):
        self.manager.current = "home"

    def set_background(self):
        with self.canvas.before:
            Color(1,1,1,1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self.update_bg)
    def update_bg(self, *args):
        self.bg_rect.size = self.size

# ---------- Home Screen ----------
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_background()
        root = BoxLayout(orientation='vertical', padding=[dp(16),dp(12),dp(16),dp(16)], spacing=dp(12))

        # Header
        header = BoxLayout(orientation='vertical', size_hint=(1,None), height=dp(68), spacing=dp(2))
        header.add_widget(Label(text="STATHLETE", font_size='26sp', bold=True, color=(0,0,0,1)))
        header.add_widget(Label(text="Your daily performance hub", font_size='13sp', color=(0.3,0.3,0.3,1)))
        root.add_widget(header)

        # Quick Actions
        def centered_row_button(text, fn):
            row = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1,None), height=dp(48))
            row.add_widget(styled_button(text, fn))
            return row

        root.add_widget(centered_row_button("Start Workout", lambda *_: setattr(self.manager, 'current', 'workout_selection')))
        for action in ["Log Stats", "View Trends", "Goals"]:
            root.add_widget(centered_row_button(action, lambda *_: print(action)))

        # Recent Activity
        recent = BoxLayout(orientation='vertical', spacing=dp(4), size_hint=(1,None), padding=[0,0,0,dp(4)])
        recent.bind(minimum_height=recent.setter('height'))
        recent.add_widget(Label(text="Recent Activity", font_size='16sp', color=(0,0,0,1), size_hint=(1,None), height=dp(22)))
        for line in ["• Upper body workout – 45 min","• Sprint drills – 20 min","• Logged recovery & hydration"]:
            recent.add_widget(Label(text=line, font_size='12sp', color=(0.2,0.2,0.2,1), size_hint=(1,None), height=dp(20)))
        root.add_widget(recent)

        root.add_widget(Label(size_hint=(1,1)))  # flexible spacer

        # Logout
        logout_box = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1,None), height=dp(56))
        logout_box.add_widget(styled_button("Logout", self.logout))
        root.add_widget(logout_box)

        wrapper = AnchorLayout()
        wrapper.add_widget(root)
        self.add_widget(wrapper)

    def logout(self, instance):
        self.manager.current = "login"
    def set_background(self):
        with self.canvas.before:
            Color(1,1,1,1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self.update_bg)
    def update_bg(self,*args):
        self.bg_rect.size = self.size

# ---------- Workout Selection / Timer Screen ----------
class WorkoutSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_background()
        self.timer_seconds = 0
        self.clock_event = None

        self.layout = BoxLayout(orientation='vertical', padding=[dp(16),dp(16),dp(16),dp(16)], spacing=dp(12))
        # Timer at the top
        self.time_label = Label(text="00:00:00", font_size='32sp', color=(0,0,0,1), size_hint=(1,None), height=dp(50))
        self.layout.add_widget(self.time_label)

        # Workout spinner in middle
        self.spinner_box = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1,None), height=dp(60))
        self.spinner = Spinner(
            text="Select Workout",
            values=["Weight Lifting", "Cardio", "Practice"],
            size_hint=(None,None),
            width=dp(280),
            height=dp(44),
            option_cls=BlueOption,
            background_color=(0.1,0.3,0.6,1),
            color=(1,1,1,1)
        )
        self.spinner_box.add_widget(self.spinner)
        self.layout.add_widget(self.spinner_box)

        # Centered button
        self.button_box = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1,None), height=dp(60))
        self.start_btn = styled_button("Start Workout", self.start_workout)
        self.button_box.add_widget(self.start_btn)
        self.layout.add_widget(self.button_box)

        wrapper = AnchorLayout()
        wrapper.add_widget(self.layout)
        self.add_widget(wrapper)

    def start_workout(self, instance):
        if self.spinner.text == "Select Workout":
            print("Please select a workout type")
            return
        print(f"Workout Started: {self.spinner.text}")
        self.layout.remove_widget(self.spinner_box)
        self.start_btn.text = "Stop Workout"
        self.start_btn.unbind(on_press=self.start_workout)
        self.start_btn.bind(on_press=self.stop_workout)
        self.timer_seconds = 0
        self.clock_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.timer_seconds += 1
        hours = self.timer_seconds // 3600
        minutes = (self.timer_seconds % 3600) // 60
        seconds = self.timer_seconds % 60
        self.time_label.text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def stop_workout(self, instance):
        if self.clock_event:
            self.clock_event.cancel()
        self.manager.current = "workout_questionnaire"

    def set_background(self):
        with self.canvas.before:
            Color(1,1,1,1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self.update_bg)
    def update_bg(self,*args):
        self.bg_rect.size = self.size

# ---------- Workout Questionnaire Screen ----------
class WorkoutQuestionnaireScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_background()

        layout = BoxLayout(orientation='vertical', padding=[dp(16), dp(16), dp(16), dp(16)], spacing=dp(16))

        layout.add_widget(Label(text="Workout Summary", font_size='24sp', color=(0,0,0,1), size_hint=(1,None), height=dp(40)))
        layout.add_widget(Label(text="What exercises did you do?", font_size='16sp', color=(0,0,0,1)))
        self.exercises_input = rounded_text_input("List your exercises")
        layout.add_widget(self.exercises_input)

        # Intensity slider
        layout.add_widget(Label(text="How intense was the workout?", font_size='16sp', color=(0,0,0,1)))
        self.intensity_slider, self.intensity_label = self.create_slider()
        layout.add_widget(self.intensity_slider)
        layout.add_widget(self.intensity_label)

        # Physical feeling
        layout.add_widget(Label(text="How are you feeling physically?", font_size='16sp', color=(0,0,0,1)))
        self.physical_slider, self.physical_label = self.create_slider()
        layout.add_widget(self.physical_slider)
        layout.add_widget(self.physical_label)

        # Mental feeling
        layout.add_widget(Label(text="How are you feeling mentally?", font_size='16sp', color=(0,0,0,1)))
        self.mental_slider, self.mental_label = self.create_slider()
        layout.add_widget(self.mental_slider)
        layout.add_widget(self.mental_label)

        layout.add_widget(styled_button("Submit", self.submit_feedback))

        wrapper = AnchorLayout()
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def create_slider(self):
        slider = Slider(min=1, max=10, value=5, step=1, size_hint=(1,None), height=dp(44))
        label = Label(text="5/10", color=(0,0,0,1), size_hint=(1,None), height=dp(24))
        slider.bind(value=lambda instance, val: setattr(label, 'text', f"{int(val)}/10"))
        return slider, label

    def submit_feedback(self, instance):
        print(f"Exercises: {self.exercises_input.text}")
        print(f"Intensity: {int(self.intensity_slider.value)}")
        print(f"Physical: {int(self.physical_slider.value)}")
        print(f"Mental: {int(self.mental_slider.value)}")
        self.manager.current = "home"

    def set_background(self):
        with self.canvas.before:
            Color(1,1,1,1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self.update_bg)
    def update_bg(self,*args):
        self.bg_rect.size = self.size

# ---------- Main App ----------
class StathleteApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(WorkoutSelectionScreen(name="workout_selection"))
        sm.add_widget(WorkoutQuestionnaireScreen(name="workout_questionnaire"))
        return sm

if __name__ == "__main__":
    StathleteApp().run()
