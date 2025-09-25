from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.spinner import Spinner, SpinnerOption
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
            from kivy.graphics import Color, Line
            Color(0.2, 0.2, 0.6, 1)
            self._outline = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.2)
        self.bind(pos=self.update_outline, size=self.update_outline)

    def update_outline(self, *args):
        self._outline.rectangle = (self.x, self.y, self.width, self.height)

def rounded_text_input(hint):
    return OutlinedTextInput(
        hint_text=hint,
        multiline=False,
        size_hint=(None, None),
        width=dp(280),
        height=dp(44),
        padding=[dp(10), dp(12)],
        background_normal='',
        background_active='',
        background_color=(1, 1, 1, 1),
        foreground_color=(0, 0, 0, 1),
        cursor_color=(0, 0, 0, 1)
    )

def styled_button(text, on_press_fn):
    btn = Button(
        text=text,
        size_hint=(None, None),
        width=dp(280),
        height=dp(44),
        background_normal='',
        background_color=(0.1, 0.3, 0.6, 1),
        color=(1, 1, 1, 1),
        font_size='16sp'
    )
    btn.bind(on_press=on_press_fn)
    return btn

def screen_layout(title_text, elements):
    layout = BoxLayout(orientation='vertical', spacing=dp(12), size_hint=(1, None), height=dp(600))
    layout.padding = [dp(0), dp(40)]

    layout.add_widget(Label(
        text="STATHLETE",
        font_size='32sp',
        bold=True,
        color=(0, 0, 0, 1),
        size_hint=(1, None),
        height=dp(50)
    ))

    if title_text:
        layout.add_widget(Label(text=title_text, font_size='22sp', color=(0, 0, 0, 1), size_hint=(1, None), height=dp(36)))

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
        from kivy.graphics import Color, Rectangle
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
            print("Username already exists")
        else:
            users[uname] = pword
            save_users(users)
            print("User registered")
            self.manager.current = "profile"

    def go_to_login(self, instance):
        self.manager.current = "login"

    def set_background(self):
        from kivy.graphics import Color, Rectangle
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
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        layout.add_widget(Label(text="Welcome to Stathlete!", font_size='22sp', color=(0,0,0,1)))
        logout_btn = styled_button("Logout", self.logout)
        box = AnchorLayout(anchor_x='center')
        box.add_widget(logout_btn)
        layout.add_widget(box)
        wrapper = AnchorLayout()
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def logout(self, instance):
        self.manager.current = "login"

    def set_background(self):
        from kivy.graphics import Color, Rectangle
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
        # Remove default images
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0.1,0.3,0.6,1)  # button blue
        self.color = (1,1,1,1)  # text white

# ---------- Profile Screen ----------
class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_background()

        def styled_spinner(text, values):
            return Spinner(
                text=text,
                values=values,
                size_hint=(None,None),
                width=dp(280),
                height=dp(44),
                background_normal='',
                background_color=(0.1,0.3,0.6,1),
                color=(1,1,1,1),
                option_cls=BlueOption
            )

        self.gender = styled_spinner("Select Gender", ["Male","Female"])
        self.sport = styled_spinner("Select Sport", ["Soccer","Basketball","Football","Baseball","Tennis","Other"])
        self.education = styled_spinner("Select Education/Level", ["High School JV","HS Varsity","D3","D2","D1","NAIA","Other"])

        # Text inputs
        self.feet = rounded_text_input("Feet")
        self.inches = rounded_text_input("Inches")
        self.weight = rounded_text_input("Weight (lbs)")
        self.age = rounded_text_input("Age")

        elements = [
            Label(text="Complete Your Profile", font_size='22sp', color=(0,0,0,1), size_hint=(1,None), height=dp(36)),
            self.gender,
            self.feet,
            self.inches,
            self.weight,
            self.age,
            self.sport,
            self.education,
            styled_button("Submit Profile", self.submit_profile)
        ]

        layout = screen_layout("", elements)
        wrapper = AnchorLayout(anchor_x='center', anchor_y='top')
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def submit_profile(self, instance):
        print(f"Profile submitted:\nGender: {self.gender.text}\nHeight: {self.feet.text}ft {self.inches.text}in\nWeight: {self.weight.text}lbs\nAge: {self.age.text}\nSport: {self.sport.text}\nEducation: {self.education.text}")
        self.manager.current = "home"

    def set_background(self):
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(1,1,1,1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self.update_bg)

    def update_bg(self, *args):
        self.bg_rect.size = self.size

# ---------- Main App ----------
class StathleteApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(HomeScreen(name="home"))
        return sm

if __name__ == "__main__":
    StathleteApp().run()
