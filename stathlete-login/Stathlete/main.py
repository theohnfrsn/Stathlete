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





class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_background()

        # Tighter padding + spacing so all content fits
        root = BoxLayout(orientation='vertical',
                         padding=[dp(16), dp(12), dp(16), dp(16)],
                         spacing=dp(12))

        # --- Header (smaller height/fonts) ---
        header = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(68), spacing=dp(2))
        header.add_widget(Label(text="STATHLETE", font_size='26sp', bold=True, color=(0, 0, 0, 1)))
        header.add_widget(Label(text="Your daily performance hub", font_size='13sp',
                                color=(0.3, 0.3, 0.3, 1)))
        root.add_widget(header)

        # --- Quick Actions (compact) ---
        qa = BoxLayout(orientation='vertical',
                       spacing=dp(8),
                       padding=[0, dp(6), 0, dp(6)],
                       size_hint=(1, None))
        qa.bind(minimum_height=qa.setter('height'))

        qa.add_widget(Label(text="Quick Actions",
                            font_size='16sp',
                            color=(0, 0, 0, 1),
                            size_hint=(1, None),
                            height=dp(24)))

        def centered_row_button(text, fn):
            # Shorter row so stack is more compact
            row = AnchorLayout(anchor_x='center', anchor_y='center',
                               size_hint=(1, None), height=dp(48))
            row.add_widget(styled_button(text, fn))   # button is dp(44) tall from styled_button
            return row

        qa.add_widget(centered_row_button("Start Workout", lambda *_: print("Start Workout")))
        qa.add_widget(centered_row_button("Log Stats",      lambda *_: print("Log Stats")))
        qa.add_widget(centered_row_button("View Trends",    lambda *_: print("View Trends")))
        qa.add_widget(centered_row_button("Goals",          lambda *_: print("Goals")))
        root.add_widget(qa)

        # Small spacer between sections
        root.add_widget(Label(size_hint=(1, None), height=dp(8)))

        # --- Recent Activity (compact) ---
        recent = BoxLayout(orientation='vertical', spacing=dp(4),
                           size_hint=(1, None), padding=[0, 0, 0, dp(4)])
        recent.bind(minimum_height=recent.setter('height'))

        recent.add_widget(Label(text="Recent Activity",
                                font_size='16sp',
                                color=(0, 0, 0, 1),
                                size_hint=(1, None),
                                height=dp(22)))

        for line in [
            "• Upper body workout – 45 min",
            "• Sprint drills – 20 min",
            "• Logged recovery & hydration",
        ]:
            recent.add_widget(Label(text=line,
                                    font_size='12sp',
                                    color=(0.2, 0.2, 0.2, 1),
                                    size_hint=(1, None),
                                    height=dp(20)))
        root.add_widget(recent)

        # Flexible spacer keeps logout at bottom
        root.add_widget(Label(size_hint=(1, 1)))

        # --- Logout ---
        logout_box = AnchorLayout(anchor_x='center', anchor_y='bottom',
                                  size_hint=(1, None), height=dp(56))
        logout_box.add_widget(styled_button("Logout", self.logout))
        root.add_widget(logout_box)

        wrapper = AnchorLayout()
        wrapper.add_widget(root)
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

if __name__ == "__main__":
    StathleteApp().run()
