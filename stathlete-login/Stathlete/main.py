from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Line, Rectangle
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

class OutlinedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.after:
            Color(0.2, 0.2, 0.6, 1)  # Outline color
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

    # STATHLETE logo as text
    layout.add_widget(Label(
        text="STATHLETE",
        font_size='32sp',
        bold=True,
        color=(0, 0, 0, 1),
        size_hint=(1, None),
        height=dp(50)
    ))

    # Screen title
    layout.add_widget(Label(text=title_text, font_size='22sp', color=(0, 0, 0, 1), size_hint=(1, None), height=dp(36)))

    for el in elements:
        box = AnchorLayout(anchor_x='center')
        box.add_widget(el)
        layout.add_widget(box)

    return layout

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
            Label(text="or", font_size='14sp', color=(0.4, 0.4, 0.4, 1), size_hint=(None, None), height=dp(20)),
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
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self.update_bg)

    def update_bg(self, *args):
        self.bg_rect.size = self.size

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
            Label(text="Already have an account?", font_size='14sp', color=(0.4, 0.4, 0.4, 1), size_hint=(None, None), height=dp(20)),
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
            self.manager.current = "login"

    def go_to_login(self, instance):
        self.manager.current = "login"

    def set_background(self):
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self.update_bg)

    def update_bg(self, *args):
        self.bg_rect.size = self.size

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_background()
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        layout.add_widget(Label(text="Welcome to Stathlete!", font_size='22sp', color=(0, 0, 0, 1)))
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
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self.update_bg)

    def update_bg(self, *args):
        self.bg_rect.size = self.size

class StathleteApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(HomeScreen(name="home"))
        return sm

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle

# Simulate mobile phone screen
Window.size = (390, 844)
Window.clearcolor = (1, 1, 1, 1)  # White background

class BoxLabel(BoxLayout):
    """A label inside a colored box."""
    def __init__(self, text, box_color=(13/255, 48/255, 185/255, 1), **kwargs):
        super().__init__(size_hint=(1, None), height=40, **kwargs)
        self.orientation = "vertical"
        self.padding = 5

        # Draw the colored background
        with self.canvas.before:
            Color(*box_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Label text (white)
        self.label = Label(text=text, color=(1, 1, 1, 1))
        self.add_widget(self.label)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class AthleteForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=15, padding=20, **kwargs)

        # Header
        header = Label(text="Stathlete", font_size='32sp', bold=True, size_hint=(1, 0.1), color=(0,0,0,1))
        self.add_widget(header)

        input_bg = (0.95, 0.95, 0.95, 1)  # Light grey for input boxes
        label_box_color = (13/255, 48/255, 185/255, 1)  # Blue #0d30b9

        # Gender
        self.add_widget(BoxLabel(text="Gender", box_color=label_box_color))
        self.gender = Spinner(
            text="Select Gender",
            values=["Male", "Female"],
            size_hint=(1, None), height=50,
            background_color=label_box_color,
            color=(1,1,1,1)  # White text
        )
        self.add_widget(self.gender)

        # Height
        self.add_widget(BoxLabel(text="Height", box_color=label_box_color))
        self.feet = TextInput(hint_text="Feet", input_filter="int", multiline=False,
                              background_color=input_bg, foreground_color=(0,0,0,1))
        self.inches = TextInput(hint_text="Inches", input_filter="int", multiline=False,
                                background_color=input_bg, foreground_color=(0,0,0,1))
        self.add_widget(self.feet)
        self.add_widget(self.inches)

        # Weight
        self.add_widget(BoxLabel(text="Weight", box_color=label_box_color))
        self.weight = TextInput(hint_text="Weight (lbs)", input_filter="int", multiline=False,
                                background_color=input_bg, foreground_color=(0,0,0,1))
        self.add_widget(self.weight)

        # Age
        self.add_widget(BoxLabel(text="Age", box_color=label_box_color))
        self.age = TextInput(hint_text="Age", input_filter="int", multiline=False,
                             background_color=input_bg, foreground_color=(0,0,0,1))
        self.add_widget(self.age)

        # Sport
        self.add_widget(BoxLabel(text="Sport", box_color=label_box_color))
        self.sport = Spinner(
            text="Select Sport",
            values=["Soccer", "Basketball", "Football", "Baseball", "Tennis", "Other"],
            size_hint=(1, None), height=50,
            background_color=label_box_color,
            color=(1,1,1,1)  # White text
        )
        self.add_widget(self.sport)

        # Education
        self.add_widget(BoxLabel(text="Education", box_color=label_box_color))
        self.education = Spinner(
            text="Select Education/Level",
            values=["High School JV", "HS Varsity", "D3", "D2", "D1", "NAIA", "Other"],
            size_hint=(1, None), height=50,
            background_color=label_box_color,
            color=(1,1,1,1)  # White text
        )
        self.add_widget(self.education)

        # Submit button
        self.submit = Button(text="Submit", size_hint=(1, None), height=50,
                             background_color=label_box_color, color=(1,1,1,1))
        self.submit.bind(on_press=self.show_summary)
        self.add_widget(self.submit)

    def show_summary(self, instance):
        summary = f"""
--- Athlete Profile ---
Gender: {self.gender.text}
Height: {self.feet.text} ft {self.inches.text} in
Weight: {self.weight.text} lbs
Age: {self.age.text}
Sport: {self.sport.text}
Education: {self.education.text}
"""
        print(summary)

class AthleteApp(App):
    def build(self):
        return AthleteForm()

if __name__ == "__main__":
    AthleteApp().run()
