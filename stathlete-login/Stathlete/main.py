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
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
import json, os, io, datetime
import matplotlib.pyplot as plt

Window.size = (360, 640)

USER_DB = "users.json"
WORKOUT_DB = "workouts.json"
GAME_STATS_DB = "game_stats.json"

# Ensure DB files exist
for db in (USER_DB, WORKOUT_DB, GAME_STATS_DB):
    if not os.path.exists(db):
        with open(db, "w") as f:
            json.dump({}, f)

def load_users():
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f)

def load_workouts():
    with open(WORKOUT_DB, "r") as f:
        return json.load(f)

def save_workout(user, workout):
    workouts = load_workouts()
    if user not in workouts:
        workouts[user] = []
    workouts[user].append(workout)
    with open(WORKOUT_DB, "w") as f:
        json.dump(workouts, f)

def load_game_stats():
    with open(GAME_STATS_DB, "r") as f:
        return json.load(f)

def save_game_stats_for_user(user, game_entry):
    stats = load_game_stats()
    if user not in stats:
        stats[user] = []
    stats[user].append(game_entry)
    with open(GAME_STATS_DB, "w") as f:
        json.dump(stats, f)

# ---------- Styled Inputs and Buttons ----------
class OutlinedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.after:
            Color(0.2,0.2,0.6,1)
            self._outline = Line(rectangle=(self.x,self.y,self.width,self.height), width=1.2)
        self.bind(pos=self.update_outline, size=self.update_outline)
    def update_outline(self, *args):
        try:
            self._outline.rectangle = (self.x,self.y,self.width,self.height)
        except Exception:
            pass

def rounded_text_input(hint, multiline=False, input_filter=None, height=dp(44)):
    params = dict(
        hint_text=hint, multiline=multiline, size_hint=(None,None),
        width=dp(280), height=height,
        padding=[dp(10),dp(12)],
        background_normal='', background_active='',
        background_color=(1,1,1,1),
        foreground_color=(0,0,0,1),
        cursor_color=(0,0,0,1)
    )
    if input_filter:
        params['input_filter'] = input_filter
    return OutlinedTextInput(**params)

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
            self.manager.current_user = uname  # Track current user
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
            self.manager.current_user = uname  # Track current user
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

        header = BoxLayout(orientation='vertical', size_hint=(1,None), height=dp(68), spacing=dp(2))
        header.add_widget(Label(text="STATHLETE", font_size='26sp', bold=True, color=(0,0,0,1)))
        header.add_widget(Label(text="Your daily performance hub", font_size='13sp', color=(0.3,0.3,0.3,1)))
        root.add_widget(header)

        def centered_row_button(text, fn):
            row = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1,None), height=dp(48))
            row.add_widget(styled_button(text, fn))
            return row

        root.add_widget(centered_row_button("Start Workout", lambda *_: setattr(self.manager, 'current', 'workout_selection')))
        # Changed: Log Stats now opens the sport selector
        root.add_widget(centered_row_button("Log Stats", lambda *_: setattr(self.manager, 'current', 'select_sport')))
        root.add_widget(centered_row_button("View Trends", lambda *_: setattr(self.manager, 'current', 'trends')))
        root.add_widget(centered_row_button("Goals", lambda *_: print("Goals")))

        recent = BoxLayout(orientation='vertical', spacing=dp(4), size_hint=(1,None), padding=[0,0,0,dp(4)])
        recent.bind(minimum_height=recent.setter('height'))
        recent.add_widget(Label(text="Recent Activity", font_size='16sp', color=(0,0,0,1), size_hint=(1,None), height=dp(22)))
        for line in ["• Upper body workout – 45 min","• Sprint drills – 20 min","• Logged recovery & hydration"]:
            recent.add_widget(Label(text=line, font_size='12sp', color=(0.2,0.2,0.2,1), size_hint=(1,None), height=dp(20)))
        root.add_widget(recent)

        root.add_widget(Label(size_hint=(1,1)))

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

        self.time_label = Label(text="00:00:00", font_size='32sp', color=(0,0,0,1), size_hint=(1,None), height=dp(50))
        self.layout.add_widget(self.time_label)

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

        exercises_box = AnchorLayout(anchor_x='center')
        self.exercises_input = rounded_text_input("List your exercises")
        exercises_box.add_widget(self.exercises_input)
        layout.add_widget(exercises_box)

        layout.add_widget(Label(text="How intense was the workout?", font_size='16sp', color=(0,0,0,1)))
        self.intensity_slider, self.intensity_label = self.create_slider()
        layout.add_widget(self.intensity_slider)
        layout.add_widget(self.intensity_label)

        layout.add_widget(Label(text="How are you feeling physically?", font_size='16sp', color=(0,0,0,1)))
        self.physical_slider, self.physical_label = self.create_slider()
        layout.add_widget(self.physical_slider)
        layout.add_widget(self.physical_label)

        layout.add_widget(Label(text="How are you feeling mentally?", font_size='16sp', color=(0,0,0,1)))
        self.mental_slider, self.mental_label = self.create_slider()
        layout.add_widget(self.mental_slider)
        layout.add_widget(self.mental_label)

        submit_box = AnchorLayout(anchor_x='center')
        submit_box.add_widget(styled_button("Submit", self.submit_feedback))
        layout.add_widget(submit_box)

        wrapper = AnchorLayout()
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def create_slider(self):
        slider = Slider(min=1, max=10, value=5, step=1, size_hint=(1,None), height=dp(44))
        label = Label(text="5/10", color=(0,0,0,1), size_hint=(1,None), height=dp(24))
        slider.bind(value=lambda instance, val: setattr(label, 'text', f"{int(val)}/10"))
        return slider, label

    def submit_feedback(self, instance):
        user = getattr(self.manager, "current_user", None)
        if not user:
            print("No user logged in")
            return
        workout_data = {
            "exercises": self.exercises_input.text,
            "intensity": int(self.intensity_slider.value),
            "physical": int(self.physical_slider.value),
            "mental": int(self.mental_slider.value)
        }
        save_workout(user, workout_data)
        self.manager.current = "home"

    def set_background(self):
        with self.canvas.before:
            Color(1,1,1,1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self.update_bg)
    def update_bg(self,*args):
        self.bg_rect.size = self.size

# ---------- Trends Screen ----------
class TrendsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_background()

        # Main vertical layout
        self.layout = BoxLayout(orientation='vertical', padding=[dp(16), dp(16), dp(16), dp(16)], spacing=dp(12))

        # Image for graph
        self.img = Image(size_hint=(1, 0.85))
        self.layout.add_widget(self.img)

        # Go Home button
        btn_box = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.15))
        go_home_btn = styled_button("Go Home", self.go_home)
        btn_box.add_widget(go_home_btn)
        self.layout.add_widget(btn_box)

        self.add_widget(self.layout)

    def on_enter(self, *args):
        self.load_trends()  # Refresh every time screen is shown

    def load_trends(self):
        user = getattr(self.manager, "current_user", None)
        if not user:
            print("No user logged in")
            return

        workouts = load_workouts().get(user, [])
        intensities = [w["intensity"] for w in workouts]

        if not intensities:
            print("No workouts yet")
            return

        plt.figure(figsize=(4,3))
        plt.plot(range(1, len(intensities)+1), intensities, marker='o')
        plt.title("Workout Intensity Trend")
        plt.xlabel("Workout #")
        plt.ylabel("Intensity")
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        self.img.texture = CoreImage(buf, ext='png').texture
        plt.close()

    def go_home(self, instance):
        self.manager.current = "home"

    def set_background(self):
        with self.canvas.before:
            Color(1,1,1,1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self.update_bg)
    def update_bg(self,*args):
        self.bg_rect.size = self.size

# ---------- Select Sport Screen ----------
class SelectSportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_background()
        layout = BoxLayout(orientation='vertical', padding=[dp(16),dp(16),dp(16),dp(16)], spacing=dp(12))
        layout.add_widget(Label(text="Select Sport", font_size='24sp', color=(0,0,0,1), size_hint=(1,None), height=dp(40)))

        sports = ["Basketball", "Soccer", "Football", "Baseball", "Tennis", "Other"]
        for s in sports:
            btn = styled_button(s, self.make_select_fn(s))
            wrapper = AnchorLayout(anchor_x='center')
            wrapper.add_widget(btn)
            layout.add_widget(wrapper)

        layout.add_widget(Label(size_hint=(1,1)))
        go_home = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1,None), height=dp(56))
        go_home.add_widget(styled_button("Go Home", self.go_home))
        layout.add_widget(go_home)

        wrapper = AnchorLayout()
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def make_select_fn(self, sport):
        def fn(instance):
            self.manager.selected_sport = sport
            self.manager.current = "game_stats"
        return fn

    def go_home(self, instance):
        self.manager.current = "home"

    def set_background(self):
        with self.canvas.before:
            Color(1,1,1,1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self.update_bg)
    def update_bg(self,*args):
        self.bg_rect.size = self.size

# ---------- Game Stats Screen ----------
class GameStatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_background()
        self.inputs = {}
        self.averages_label = Label(text="", size_hint=(1,None), height=dp(28), color=(0,0,0,1))
        self.main_layout = BoxLayout(orientation='vertical', padding=[dp(12),dp(12),dp(12),dp(12)], spacing=dp(8))
        self.add_widget(self.main_layout)
        # mapping sport -> fields
        self.field_map = {
            "Basketball": [
                ("points", "Points", "int"),
                ("assists", "Assists", "int"),
                ("rebounds", "Rebounds", "int"),
                ("steals", "Steals", "int"),
                ("blocks", "Blocks", "int"),
            ],
            "Soccer": [
                ("goals", "Goals", "int"),
                ("assists", "Assists", "int"),
                ("shots", "Shots", "int"),
                ("tackles", "Tackles", "int"),
                ("pass_accuracy", "Pass Accuracy (%)", None),
            ],
            "Football": [
                ("touchdowns", "Touchdowns", "int"),
                ("passing_yards", "Passing Yards", "int"),
                ("rushing_yards", "Rushing Yards", "int"),
                ("tackles", "Tackles", "int"),
            ],
            "Baseball": [
                ("hits", "Hits", "int"),
                ("home_runs", "Home Runs", "int"),
                ("rbis", "RBIs", "int"),
                ("strikeouts", "Strikeouts", "int"),
            ],
            "Tennis": [
                ("aces", "Aces", "int"),
                ("double_faults", "Double Faults", "int"),
                ("winners", "Winners", "int"),
                ("unforced_errors", "Unforced Errors", "int"),
            ],
            "Other": [
                ("stat1", "Stat 1", "int"),
                ("stat2", "Stat 2", "int"),
            ]
        }
        # saved confirmation label
        self.saved_label = Label(text="", size_hint=(1,None), height=dp(24), color=(0,0.6,0,1))

    def on_enter(self, *args):
        self.build_ui()

    def build_ui(self):
        self.main_layout.clear_widgets()
        self.inputs = {}
        sport = getattr(self.manager, "selected_sport", None)
        user = getattr(self.manager, "current_user", None)
        if not sport:
            self.main_layout.add_widget(Label(text="No sport selected", size_hint=(1,None), height=dp(30)))
            self.main_layout.add_widget(styled_button("Go Back", lambda *_: setattr(self.manager, 'current', 'select_sport')))
            return

        # Averages header
        self.main_layout.add_widget(Label(text=f"{sport} Averages", font_size='20sp', color=(0,0,0,1), size_hint=(1,None), height=dp(30)))
        self.main_layout.add_widget(self.averages_label)

        # Date & opponent
        date_str = datetime.date.today().isoformat()
        self.inputs['date'] = date_str
        self.main_layout.add_widget(Label(text=f"Date: {date_str}", size_hint=(1,None), height=dp(24), color=(0,0,0,1)))

        opp = rounded_text_input("Opponent")
        self.inputs['opponent'] = opp
        opp_box = AnchorLayout(anchor_x='center')
        opp_box.add_widget(opp)
        self.main_layout.add_widget(opp_box)

        # sport-specific fields
        fields = self.field_map.get(sport, self.field_map["Other"])
        for key, placeholder, filt in fields:
            inp = rounded_text_input(placeholder, input_filter=filt)
            self.inputs[key] = inp
            box = AnchorLayout(anchor_x='center')
            box.add_widget(inp)
            self.main_layout.add_widget(box)

        # notes
        notes = OutlinedTextInput(hint_text="Notes (optional)", multiline=True, size_hint=(None,None),
                                  width=dp(280), height=dp(80), padding=[dp(10),dp(10)],
                                  background_normal='', background_active='', background_color=(1,1,1,1))
        self.inputs['notes'] = notes
        notes_box = AnchorLayout(anchor_x='center')
        notes_box.add_widget(notes)
        self.main_layout.add_widget(notes_box)

        # save / go home buttons
        save_box = AnchorLayout(anchor_x='center')
        save_btn = styled_button("Save Game Stats", self.save_stats)
        save_box.add_widget(save_btn)
        self.main_layout.add_widget(save_box)

        go_home_box = AnchorLayout(anchor_x='center')
        go_home_box.add_widget(styled_button("Go Home", lambda *_: setattr(self.manager, 'current', 'home')))
        self.main_layout.add_widget(go_home_box)

        # saved confirmation
        self.saved_label.text = ""
        self.main_layout.add_widget(self.saved_label)

        # compute averages and show
        self.refresh_averages()

    def refresh_averages(self):
        sport = getattr(self.manager, "selected_sport", None)
        user = getattr(self.manager, "current_user", None)
        if not sport or not user:
            self.averages_label.text = "No user or sport selected"
            return
        stats = load_game_stats().get(user, [])
        sport_games = [g for g in stats if g.get("sport") == sport]
        if not sport_games:
            self.averages_label.text = "No games logged yet."
            return

        def avg_for(key):
            vals = [float(g.get(key, 0)) for g in sport_games if g.get(key) is not None and str(g.get(key)) != ""]
            if not vals:
                return None
            return sum(vals) / len(vals)

        if sport == "Basketball":
            ppg = avg_for("points")
            apg = avg_for("assists")
            rpg = avg_for("rebounds")
            stats_text = f"PPG: {ppg:.1f} | APG: {apg:.1f} | RPG: {rpg:.1f}" if ppg is not None else "No numeric stats yet."
        elif sport == "Soccer":
            gpg = avg_for("goals")
            apg = avg_for("assists")
            tpg = avg_for("tackles")
            stats_text = f"GPG: {gpg:.1f} | APG: {apg:.1f} | TPG: {tpg:.1f}" if gpg is not None else "No numeric stats yet."
        elif sport == "Football":
            tdpg = avg_for("touchdowns")
            pass_y = avg_for("passing_yards")
            rush_y = avg_for("rushing_yards")
            stats_text = f"TD/Game: {tdpg:.1f} | Pass Yds: {pass_y:.1f} | Rush Yds: {rush_y:.1f}" if tdpg is not None else "No numeric stats yet."
        else:
            sample_keys = []
            for k in ("points","goals","hits","aces","stat1","stat2","assists"):
                if any(k in g for g in sport_games):
                    sample_keys.append(k)
            if not sample_keys:
                stats_text = "No numeric stats available for this sport."
            else:
                parts = []
                for k in sample_keys[:3]:
                    val = avg_for(k)
                    if val is not None:
                        parts.append(f"{k}: {val:.1f}")
                stats_text = " | ".join(parts) if parts else "No numeric stats yet."

        self.averages_label.text = stats_text

    def save_stats(self, instance):
        user = getattr(self.manager, "current_user", None)
        sport = getattr(self.manager, "selected_sport", None)
        if not user or not sport:
            print("User or sport missing")
            return

        entry = {"sport": sport, "date": self.inputs.get('date')}
        opp_widget = self.inputs.get('opponent')
        entry['opponent'] = opp_widget.text.strip() if isinstance(opp_widget, TextInput) else ""

        for k, widget in list(self.inputs.items()):
            if k in ('date','opponent'):
                continue
            if isinstance(widget, TextInput):
                text = widget.text.strip()
                if text == "":
                    continue
                if k == 'notes':
                    entry[k] = text
                else:
                    try:
                        if getattr(widget, 'input_filter', None) == 'int':
                            entry[k] = int(text)
                        else:
                            entry[k] = float(text) if '.' in text else int(text)
                    except Exception:
                        entry[k] = text

        save_game_stats_for_user(user, entry)
        print("Saved game:", entry)
        # show confirmation and refresh averages, but keep form (clear inputs so user knows it's saved)
        self.saved_label.text = "✅ Game stats saved"
        # clear non-persistent inputs
        for k, widget in self.inputs.items():
            if isinstance(widget, TextInput):
                widget.text = ""
        # refresh displayed averages
        self.refresh_averages()
        # schedule hide confirmation after 2.5s
        Clock.schedule_once(lambda dt: setattr(self.saved_label, 'text', ""), 2.5)

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
        sm.add_widget(TrendsScreen(name="trends"))
        # new screens
        sm.add_widget(SelectSportScreen(name="select_sport"))
        sm.add_widget(GameStatsScreen(name="game_stats"))
        # holder for selected sport and current user will be set dynamically (manager.selected_sport, manager.current_user)
        return sm

if __name__ == "__main__":
    StathleteApp().run()
