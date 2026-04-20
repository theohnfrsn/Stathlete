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
from kivy.uix.scrollview import ScrollView

import json, os, io, datetime, re
import matplotlib.pyplot as plt

Window.size = (360, 640)

# ─────────────────────────────────────────────
# Database paths & helpers
# ─────────────────────────────────────────────
USER_DB       = "users.json"
WORKOUT_DB    = "workouts.json"
GAME_STATS_DB = "game_stats.json"
GOALS_DB      = "goals.json"
SCHEDULE_DB   = "schedule.json"

for db in (USER_DB, WORKOUT_DB, GAME_STATS_DB, GOALS_DB, SCHEDULE_DB):
    if not os.path.exists(db):
        default = [] if db in (GOALS_DB, SCHEDULE_DB) else {}
        with open(db, "w") as f:
            json.dump(default, f)

def load_users():
    with open(USER_DB) as f: return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f: json.dump(users, f)

def load_workouts():
    with open(WORKOUT_DB) as f: return json.load(f)

def save_workout(user, workout):
    workouts = load_workouts()
    workouts.setdefault(user, []).append(workout)
    with open(WORKOUT_DB, "w") as f: json.dump(workouts, f)

def load_game_stats():
    with open(GAME_STATS_DB) as f: return json.load(f)

def save_game_stats_for_user(user, entry):
    stats = load_game_stats()
    stats.setdefault(user, []).append(entry)
    with open(GAME_STATS_DB, "w") as f: json.dump(stats, f)

def load_goals():
    with open(GOALS_DB) as f: return json.load(f)

def save_goals(goals):
    with open(GOALS_DB, "w") as f: json.dump(goals, f, indent=2)

def load_schedule():
    with open(SCHEDULE_DB) as f: return json.load(f)

def save_schedule(items):
    with open(SCHEDULE_DB, "w") as f: json.dump(items, f, indent=2)

# ─────────────────────────────────────────────
# Shared UI helpers
# ─────────────────────────────────────────────
class OutlinedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.after:
            Color(0.2, 0.2, 0.6, 1)
            self._outline = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.2)
        self.bind(pos=self._update_outline, size=self._update_outline)

    def _update_outline(self, *args):
        try:
            self._outline.rectangle = (self.x, self.y, self.width, self.height)
        except Exception:
            pass


def rounded_text_input(hint, multiline=False, input_filter=None, height=dp(44)):
    params = dict(
        hint_text=hint, multiline=multiline,
        size_hint=(None, None), width=dp(280), height=height,
        padding=[dp(10), dp(12)],
        background_normal='', background_active='',
        background_color=(1, 1, 1, 1),
        foreground_color=(0, 0, 0, 1),
        cursor_color=(0, 0, 0, 1)
    )
    if input_filter:
        params['input_filter'] = input_filter
    return OutlinedTextInput(**params)


def styled_button(text, on_press_fn):
    btn = Button(
        text=text, size_hint=(None, None),
        width=dp(280), height=dp(44),
        background_normal='', background_color=(0.1, 0.3, 0.6, 1),
        color=(1, 1, 1, 1), font_size='16sp'
    )
    btn.bind(on_press=on_press_fn)
    return btn


def small_button(text, on_press_fn, width=100):
    btn = Button(
        text=text, size_hint=(None, None),
        width=dp(width), height=dp(36),
        background_normal='', background_color=(0.1, 0.3, 0.6, 1),
        color=(1, 1, 1, 1), font_size='14sp'
    )
    btn.bind(on_press=on_press_fn)
    return btn


def screen_layout(title_text, elements):
    layout = BoxLayout(orientation='vertical', spacing=dp(12),
                       size_hint=(1, None), height=dp(600))
    layout.padding = [dp(0), dp(40)]
    layout.add_widget(Label(text="STATHLETE", font_size='32sp', bold=True,
                            color=(0, 0, 0, 1), size_hint=(1, None), height=dp(50)))
    if title_text:
        layout.add_widget(Label(text=title_text, font_size='22sp',
                                color=(0, 0, 0, 1), size_hint=(1, None), height=dp(36)))
    for el in elements:
        box = AnchorLayout(anchor_x='center')
        box.add_widget(el)
        layout.add_widget(box)
    return layout


def white_bg(screen):
    """Apply a white background to any Screen."""
    with screen.canvas.before:
        Color(1, 1, 1, 1)
        screen.bg_rect = Rectangle(size=Window.size, pos=screen.pos)
    screen.bind(size=lambda *_: setattr(screen.bg_rect, 'size', screen.size),
                pos=lambda *_: setattr(screen.bg_rect, 'pos', screen.pos))


# ─────────────────────────────────────────────
# Custom SpinnerOption
# ─────────────────────────────────────────────
class BlueOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down   = ''
        self.background_color  = (0.1, 0.3, 0.6, 1)
        self.color             = (1, 1, 1, 1)


# ─────────────────────────────────────────────
# Login Screen
# ─────────────────────────────────────────────
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        white_bg(self)

        self.username = rounded_text_input("Username or Email")
        self.password = rounded_text_input("Password")
        self.password.password = True

        self.error_label = Label(text="", color=(1, 0, 0, 1), font_size='14sp',
                                 size_hint=(1, None), height=dp(20))

        layout = screen_layout("Login", [
            self.username,
            self.password,
            self.error_label,
            styled_button("Log In", self.login),
            Label(text="or", font_size='14sp', color=(0.4, 0.4, 0.4, 1),
                  size_hint=(None, None), height=dp(20)),
            styled_button("Sign Up", lambda *_: setattr(self.manager, 'current', 'signup'))
        ])

        wrapper = AnchorLayout(anchor_x='center', anchor_y='top')
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def login(self, *args):
        users = load_users()
        uname = self.username.text.strip()
        pword = self.password.text.strip()
        if uname in users and users[uname] == pword:
            self.error_label.text = ""
            self.manager.current_user = uname
            self.manager.current = "home"
        else:
            self.error_label.text = "Invalid username or password"
            Clock.schedule_once(lambda dt: setattr(self.error_label, 'text', ""), 2)


# ─────────────────────────────────────────────
# Signup Screen
# ─────────────────────────────────────────────
class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        white_bg(self)

        self.username = rounded_text_input("Username")
        self.email    = rounded_text_input("Email")
        self.password = rounded_text_input("Password")
        self.password.password = True

        layout = screen_layout("Sign Up", [
            self.username,
            self.email,
            self.password,
            styled_button("Sign Up", self.register),
            Label(text="Already have an account?", font_size='14sp',
                  color=(0.4, 0.4, 0.4, 1), size_hint=(None, None), height=dp(20)),
            styled_button("Log In", lambda *_: setattr(self.manager, 'current', 'login'))
        ])

        wrapper = AnchorLayout(anchor_x='center', anchor_y='top')
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def register(self, *args):
        users = load_users()
        uname = self.username.text.strip()
        pword = self.password.text.strip()
        if not uname or not pword:
            return
        if uname in users:
            print("Username already exists")
        else:
            users[uname] = pword
            save_users(users)
            self.manager.current_user = uname
            self.manager.current = "profile"


# ─────────────────────────────────────────────
# Profile Screen
# ─────────────────────────────────────────────
class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        white_bg(self)

        def styled_spinner(text, values):
            return Spinner(
                text=text, values=values,
                size_hint=(None, None), width=dp(280), height=dp(44),
                background_normal='', background_color=(0.1, 0.3, 0.6, 1),
                color=(1, 1, 1, 1), option_cls=BlueOption
            )

        self.gender    = styled_spinner("Select Gender", ["Male", "Female"])
        self.sport     = styled_spinner("Select Sport", ["Soccer", "Basketball", "Football", "Baseball", "Tennis", "Other"])
        self.education = styled_spinner("Select Education/Level",
                                       ["High School JV", "HS Varsity", "D3", "D2", "D1", "NAIA", "Other"])
        self.feet   = rounded_text_input("Feet")
        self.inches = rounded_text_input("Inches")
        self.weight = rounded_text_input("Weight (lbs)")
        self.age    = rounded_text_input("Age")

        elements = [
            Label(text="Complete Your Profile", font_size='22sp', color=(0, 0, 0, 1),
                  size_hint=(1, None), height=dp(36)),
            self.gender, self.feet, self.inches, self.weight, self.age, self.sport, self.education,
            styled_button("Submit Profile", lambda *_: setattr(self.manager, 'current', 'home'))
        ]

        layout = screen_layout("", elements)
        wrapper = AnchorLayout(anchor_x='center', anchor_y='top')
        wrapper.add_widget(layout)
        self.add_widget(wrapper)


# ─────────────────────────────────────────────
# Home Screen
# ─────────────────────────────────────────────
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        white_bg(self)

        root = BoxLayout(orientation='vertical',
                         padding=[dp(16), dp(12), dp(16), dp(16)], spacing=dp(12))

        header = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(68), spacing=dp(2))
        header.add_widget(Label(text="STATHLETE", font_size='26sp', bold=True, color=(0, 0, 0, 1)))
        header.add_widget(Label(text="Your daily performance hub", font_size='13sp', color=(0.3, 0.3, 0.3, 1)))
        root.add_widget(header)

        def centered_row_button(text, fn):
            row = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, None), height=dp(48))
            row.add_widget(styled_button(text, fn))
            return row

        root.add_widget(centered_row_button("Start Workout",
                                            lambda *_: setattr(self.manager, 'current', 'workout_selection')))
        root.add_widget(centered_row_button("Log Stats",
                                            lambda *_: setattr(self.manager, 'current', 'select_sport')))
        root.add_widget(centered_row_button("View Trends",
                                            lambda *_: setattr(self.manager, 'current', 'trends')))
        root.add_widget(centered_row_button("Goals",
                                            lambda *_: setattr(self.manager, 'current', 'goals')))
        root.add_widget(centered_row_button("Schedule",
                                            lambda *_: setattr(self.manager, 'current', 'schedule')))
        root.add_widget(centered_row_button("AI Coach",
                                            lambda *_: setattr(self.manager, 'current', 'coach')))

        recent = BoxLayout(orientation='vertical', spacing=dp(4),
                           size_hint=(1, None), padding=[0, 0, 0, dp(4)])
        recent.bind(minimum_height=recent.setter('height'))
        recent.add_widget(Label(text="Recent Activity", font_size='16sp', color=(0, 0, 0, 1),
                                size_hint=(1, None), height=dp(22)))
        for line in ["• Upper body workout – 45 min",
                     "• Sprint drills – 20 min",
                     "• Logged recovery & hydration"]:
            recent.add_widget(Label(text=line, font_size='12sp', color=(0.2, 0.2, 0.2, 1),
                                    size_hint=(1, None), height=dp(20)))
        root.add_widget(recent)

        root.add_widget(Label(size_hint=(1, 1)))

        logout_box = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, None), height=dp(56))
        logout_box.add_widget(styled_button("Logout", lambda *_: setattr(self.manager, 'current', 'login')))
        root.add_widget(logout_box)

        wrapper = AnchorLayout()
        wrapper.add_widget(root)
        self.add_widget(wrapper)


# ─────────────────────────────────────────────
# Workout Selection / Timer Screen
# ─────────────────────────────────────────────
class WorkoutSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        white_bg(self)
        self.timer_seconds = 0
        self.clock_event   = None

        self.layout = BoxLayout(orientation='vertical',
                                padding=[dp(16), dp(16), dp(16), dp(16)], spacing=dp(12))

        self.time_label = Label(text="00:00:00", font_size='32sp', color=(0, 0, 0, 1),
                                size_hint=(1, None), height=dp(50))
        self.layout.add_widget(self.time_label)

        self.spinner_box = AnchorLayout(anchor_x='center', anchor_y='center',
                                        size_hint=(1, None), height=dp(60))
        self.spinner = Spinner(
            text="Select Workout",
            values=["Weight Lifting", "Cardio", "Practice"],
            size_hint=(None, None), width=dp(280), height=dp(44),
            option_cls=BlueOption,
            background_color=(0.1, 0.3, 0.6, 1), color=(1, 1, 1, 1)
        )
        self.spinner_box.add_widget(self.spinner)
        self.layout.add_widget(self.spinner_box)

        self.button_box = AnchorLayout(anchor_x='center', anchor_y='center',
                                       size_hint=(1, None), height=dp(60))
        self.start_btn = styled_button("Start Workout", self.start_workout)
        self.button_box.add_widget(self.start_btn)
        self.layout.add_widget(self.button_box)

        wrapper = AnchorLayout()
        wrapper.add_widget(self.layout)
        self.add_widget(wrapper)

    def start_workout(self, instance):
        if self.spinner.text == "Select Workout":
            return
        self.layout.remove_widget(self.spinner_box)
        self.start_btn.text = "Stop Workout"
        self.start_btn.unbind(on_press=self.start_workout)
        self.start_btn.bind(on_press=self.stop_workout)
        self.timer_seconds = 0
        self.clock_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.timer_seconds += 1
        h = self.timer_seconds // 3600
        m = (self.timer_seconds % 3600) // 60
        s = self.timer_seconds % 60
        self.time_label.text = f"{h:02d}:{m:02d}:{s:02d}"

    def stop_workout(self, instance):
        if self.clock_event:
            self.clock_event.cancel()
        self.manager.current = "workout_questionnaire"


# ─────────────────────────────────────────────
# Workout Questionnaire Screen
# ─────────────────────────────────────────────
class WorkoutQuestionnaireScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        white_bg(self)

        layout = BoxLayout(orientation='vertical',
                           padding=[dp(16), dp(16), dp(16), dp(16)], spacing=dp(16))

        layout.add_widget(Label(text="Workout Summary", font_size='24sp',
                                color=(0, 0, 0, 1), size_hint=(1, None), height=dp(40)))
        layout.add_widget(Label(text="What exercises did you do?", font_size='16sp', color=(0, 0, 0, 1)))

        box = AnchorLayout(anchor_x='center')
        self.exercises_input = rounded_text_input("List your exercises")
        box.add_widget(self.exercises_input)
        layout.add_widget(box)

        for label_text, attr in [
            ("How intense was the workout?",  "intensity"),
            ("How are you feeling physically?", "physical"),
            ("How are you feeling mentally?",   "mental"),
        ]:
            layout.add_widget(Label(text=label_text, font_size='16sp', color=(0, 0, 0, 1)))
            slider, lbl = self._create_slider()
            setattr(self, f"{attr}_slider", slider)
            setattr(self, f"{attr}_label",  lbl)
            layout.add_widget(slider)
            layout.add_widget(lbl)

        submit_box = AnchorLayout(anchor_x='center')
        submit_box.add_widget(styled_button("Submit", self.submit_feedback))
        layout.add_widget(submit_box)

        wrapper = AnchorLayout()
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def _create_slider(self):
        slider = Slider(min=1, max=10, value=5, step=1, size_hint=(1, None), height=dp(44))
        label  = Label(text="5/10", color=(0, 0, 0, 1), size_hint=(1, None), height=dp(24))
        slider.bind(value=lambda inst, val: setattr(label, 'text', f"{int(val)}/10"))
        return slider, label

    def submit_feedback(self, instance):
        user = getattr(self.manager, "current_user", None)
        if not user:
            return
        save_workout(user, {
            "exercises": self.exercises_input.text,
            "intensity": int(self.intensity_slider.value),
            "physical":  int(self.physical_slider.value),
            "mental":    int(self.mental_slider.value),
        })
        self.manager.current = "home"


# ─────────────────────────────────────────────
# Trends Screen
# ─────────────────────────────────────────────
class TrendsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        white_bg(self)

        self.layout = BoxLayout(orientation='vertical',
                                padding=[dp(16), dp(16), dp(16), dp(16)], spacing=dp(12))
        self.img = Image(size_hint=(1, 0.85))
        self.layout.add_widget(self.img)

        btn_box = AnchorLayout(anchor_x='center', anchor_y='center', size_hint=(1, 0.15))
        btn_box.add_widget(styled_button("Go Home", lambda *_: setattr(self.manager, 'current', 'home')))
        self.layout.add_widget(btn_box)
        self.add_widget(self.layout)

    def on_enter(self, *args):
        user = getattr(self.manager, "current_user", None)
        if not user:
            return
        workouts    = load_workouts().get(user, [])
        intensities = [w["intensity"] for w in workouts]
        if not intensities:
            return
        plt.figure(figsize=(4, 3))
        plt.plot(range(1, len(intensities) + 1), intensities, marker='o')
        plt.title("Workout Intensity Trend")
        plt.xlabel("Workout #")
        plt.ylabel("Intensity")
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        self.img.texture = CoreImage(buf, ext='png').texture
        plt.close()


# ─────────────────────────────────────────────
# Select Sport Screen
# ─────────────────────────────────────────────
class SelectSportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        white_bg(self)

        layout = BoxLayout(orientation='vertical',
                           padding=[dp(16), dp(16), dp(16), dp(16)], spacing=dp(12))
        layout.add_widget(Label(text="Select Sport", font_size='24sp',
                                color=(0, 0, 0, 1), size_hint=(1, None), height=dp(40)))

        for s in ["Basketball", "Soccer", "Football", "Baseball", "Tennis", "Other"]:
            wrapper = AnchorLayout(anchor_x='center')
            wrapper.add_widget(styled_button(s, self._make_select_fn(s)))
            layout.add_widget(wrapper)

        layout.add_widget(Label(size_hint=(1, 1)))
        go_home = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, None), height=dp(56))
        go_home.add_widget(styled_button("Go Home", lambda *_: setattr(self.manager, 'current', 'home')))
        layout.add_widget(go_home)

        wrapper = AnchorLayout()
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def _make_select_fn(self, sport):
        def fn(instance):
            self.manager.selected_sport = sport
            self.manager.current = "game_stats"
        return fn


# ─────────────────────────────────────────────
# Game Stats Screen
# ─────────────────────────────────────────────
class GameStatsScreen(Screen):
    FIELD_MAP = {
        "Basketball": [("points","Points","int"),("assists","Assists","int"),
                       ("rebounds","Rebounds","int"),("steals","Steals","int"),("blocks","Blocks","int")],
        "Soccer":     [("goals","Goals","int"),("assists","Assists","int"),
                       ("shots","Shots","int"),("tackles","Tackles","int"),("pass_accuracy","Pass Accuracy (%)",None)],
        "Football":   [("touchdowns","Touchdowns","int"),("passing_yards","Passing Yards","int"),
                       ("rushing_yards","Rushing Yards","int"),("tackles","Tackles","int")],
        "Baseball":   [("hits","Hits","int"),("home_runs","Home Runs","int"),
                       ("rbis","RBIs","int"),("strikeouts","Strikeouts","int")],
        "Tennis":     [("aces","Aces","int"),("double_faults","Double Faults","int"),
                       ("winners","Winners","int"),("unforced_errors","Unforced Errors","int")],
        "Other":      [("stat1","Stat 1","int"),("stat2","Stat 2","int")],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        white_bg(self)
        self.inputs = {}
        self.averages_label = Label(text="", size_hint=(1, None), height=dp(28), color=(0, 0, 0, 1))
        self.saved_label    = Label(text="", size_hint=(1, None), height=dp(24), color=(0, 0.6, 0, 1))
        self.main_layout    = BoxLayout(orientation='vertical',
                                        padding=[dp(12), dp(12), dp(12), dp(12)], spacing=dp(8))
        self.add_widget(self.main_layout)

    def on_enter(self, *args):
        self.build_ui()

    def build_ui(self):
        self.main_layout.clear_widgets()
        self.inputs = {}
        sport = getattr(self.manager, "selected_sport", None)
        if not sport:
            self.main_layout.add_widget(Label(text="No sport selected", size_hint=(1, None), height=dp(30)))
            self.main_layout.add_widget(
                styled_button("Go Back", lambda *_: setattr(self.manager, 'current', 'select_sport')))
            return

        self.main_layout.add_widget(Label(text=f"{sport} Stats", font_size='20sp',
                                          color=(0, 0, 0, 1), size_hint=(1, None), height=dp(30)))
        self.main_layout.add_widget(self.averages_label)

        date_str = datetime.date.today().isoformat()
        self.inputs['date'] = date_str
        self.main_layout.add_widget(Label(text=f"Date: {date_str}", size_hint=(1, None),
                                          height=dp(24), color=(0, 0, 0, 1)))

        opp = rounded_text_input("Opponent")
        self.inputs['opponent'] = opp
        opp_box = AnchorLayout(anchor_x='center')
        opp_box.add_widget(opp)
        self.main_layout.add_widget(opp_box)

        for key, placeholder, filt in self.FIELD_MAP.get(sport, self.FIELD_MAP["Other"]):
            inp = rounded_text_input(placeholder, input_filter=filt)
            self.inputs[key] = inp
            box = AnchorLayout(anchor_x='center')
            box.add_widget(inp)
            self.main_layout.add_widget(box)

        notes = OutlinedTextInput(hint_text="Notes (optional)", multiline=True,
                                  size_hint=(None, None), width=dp(280), height=dp(80),
                                  padding=[dp(10), dp(10)],
                                  background_normal='', background_active='', background_color=(1, 1, 1, 1))
        self.inputs['notes'] = notes
        notes_box = AnchorLayout(anchor_x='center')
        notes_box.add_widget(notes)
        self.main_layout.add_widget(notes_box)

        save_box = AnchorLayout(anchor_x='center')
        save_box.add_widget(styled_button("Save Game Stats", self.save_stats))
        self.main_layout.add_widget(save_box)

        home_box = AnchorLayout(anchor_x='center')
        home_box.add_widget(styled_button("Go Home", lambda *_: setattr(self.manager, 'current', 'home')))
        self.main_layout.add_widget(home_box)

        self.saved_label.text = ""
        self.main_layout.add_widget(self.saved_label)
        self.refresh_averages()

    def refresh_averages(self):
        sport = getattr(self.manager, "selected_sport", None)
        user  = getattr(self.manager, "current_user",   None)
        if not sport or not user:
            self.averages_label.text = "No user or sport selected"
            return
        sport_games = [g for g in load_game_stats().get(user, []) if g.get("sport") == sport]
        if not sport_games:
            self.averages_label.text = "No games logged yet."
            return

        def avg(key):
            vals = [float(g[key]) for g in sport_games if str(g.get(key, "")) != ""]
            return sum(vals) / len(vals) if vals else None

        if sport == "Basketball":
            p, a, r = avg("points"), avg("assists"), avg("rebounds")
            self.averages_label.text = (f"PPG: {p:.1f} | APG: {a:.1f} | RPG: {r:.1f}"
                                        if p is not None else "No stats yet.")
        elif sport == "Soccer":
            g, a, t = avg("goals"), avg("assists"), avg("tackles")
            self.averages_label.text = (f"GPG: {g:.1f} | APG: {a:.1f} | TPG: {t:.1f}"
                                        if g is not None else "No stats yet.")
        elif sport == "Football":
            td, py, ry = avg("touchdowns"), avg("passing_yards"), avg("rushing_yards")
            self.averages_label.text = (f"TD/G: {td:.1f} | Pass: {py:.1f} | Rush: {ry:.1f}"
                                        if td is not None else "No stats yet.")
        else:
            keys  = [k for k in ("points","goals","hits","aces","stat1","stat2","assists")
                     if any(k in g for g in sport_games)]
            parts = [f"{k}: {avg(k):.1f}" for k in keys[:3] if avg(k) is not None]
            self.averages_label.text = " | ".join(parts) if parts else "No stats yet."

    def save_stats(self, instance):
        user  = getattr(self.manager, "current_user",   None)
        sport = getattr(self.manager, "selected_sport", None)
        if not user or not sport:
            return

        entry = {"sport": sport, "date": self.inputs.get('date')}
        opp_widget = self.inputs.get('opponent')
        entry['opponent'] = opp_widget.text.strip() if isinstance(opp_widget, TextInput) else ""

        for k, widget in list(self.inputs.items()):
            if k in ('date', 'opponent') or not isinstance(widget, TextInput):
                continue
            text = widget.text.strip()
            if not text:
                continue
            if k == 'notes':
                entry[k] = text
            else:
                try:
                    entry[k] = int(text) if getattr(widget, 'input_filter', None) == 'int' else (
                        float(text) if '.' in text else int(text))
                except Exception:
                    entry[k] = text

        save_game_stats_for_user(user, entry)
        self.saved_label.text = "✅ Game stats saved"
        for k, w in self.inputs.items():
            if isinstance(w, TextInput):
                w.text = ""
        self.refresh_averages()
        Clock.schedule_once(lambda dt: setattr(self.saved_label, 'text', ""), 2.5)


# ─────────────────────────────────────────────
# Goals Screen
# ─────────────────────────────────────────────
class GoalsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        white_bg(self)

        root = BoxLayout(orientation='vertical',
                         padding=[dp(16), dp(12), dp(16), dp(16)], spacing=dp(10))

        header = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(68), spacing=dp(2))
        header.add_widget(Label(text="STATHLETE", font_size='26sp', bold=True, color=(0, 0, 0, 1)))
        header.add_widget(Label(text="Goals", font_size='18sp', color=(0.1, 0.1, 0.1, 1)))
        root.add_widget(header)

        add_row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(48), spacing=dp(8))
        self.goal_input = TextInput(
            hint_text="Add a new goal…", multiline=False,
            size_hint=(1, None), height=dp(44), padding=[dp(10), dp(12)],
            background_normal='', background_active='',
            background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1), cursor_color=(0, 0, 0, 1)
        )
        add_btn = Button(text="Add", size_hint=(None, None), width=dp(80), height=dp(44),
                         background_normal='', background_color=(0.1, 0.3, 0.6, 1),
                         color=(1, 1, 1, 1), font_size='16sp')
        add_btn.bind(on_press=self.add_goal)
        self.goal_input.bind(on_text_validate=lambda *_: self.add_goal(None))
        add_row.add_widget(self.goal_input)
        add_row.add_widget(add_btn)
        root.add_widget(add_row)

        scroller = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(orientation='vertical', size_hint_y=None,
                                  spacing=dp(6), padding=[0, dp(4), 0, dp(4)])
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        scroller.add_widget(self.list_box)
        root.add_widget(scroller)

        back_box = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, None), height=dp(56))
        back_box.add_widget(styled_button("Back to Home", lambda *_: setattr(self.manager, 'current', 'home')))
        root.add_widget(back_box)

        wrapper = AnchorLayout()
        wrapper.add_widget(root)
        self.add_widget(wrapper)

    def on_pre_enter(self, *args):
        self.refresh_list()

    def add_goal(self, *_):
        text = self.goal_input.text.strip()
        if not text:
            return
        goals = load_goals()
        goals.append(text)
        save_goals(goals)
        self.goal_input.text = ""
        self.refresh_list()

    def refresh_list(self):
        self.list_box.clear_widgets()
        goals = load_goals()
        if not goals:
            self.list_box.add_widget(Label(text="No goals yet. Add your first one above.",
                                           font_size='13sp', color=(0.3, 0.3, 0.3, 1),
                                           size_hint=(1, None), height=dp(22)))
            return
        for g in goals:
            self.list_box.add_widget(Label(text=f"• {g}", font_size='14sp',
                                           color=(0.1, 0.1, 0.1, 1),
                                           size_hint=(1, None), height=dp(22)))


# ─────────────────────────────────────────────
# Schedule helpers
# ─────────────────────────────────────────────
def parse_date_time(date_s: str, time_s: str) -> datetime.datetime:
    date_s = date_s.strip()
    time_s = time_s.strip().lower()
    date_obj = None
    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y"]:
        try:
            date_obj = datetime.datetime.strptime(date_s, fmt).date()
            break
        except Exception:
            pass
    if date_obj is None:
        raise ValueError("Bad date")

    if re.fullmatch(r"\d{1,2}", time_s):
        time_s = f"{int(time_s):02d}:00"
    if re.fullmatch(r"\d{1,2}\s*(am|pm)", time_s):
        m = re.match(r"(\d{1,2})\s*(am|pm)", time_s)
        time_s = f"{int(m.group(1))}:00 {m.group(2)}"

    time_obj = None
    for fmt in ["%H:%M", "%I:%M %p", "%I %p"]:
        try:
            time_obj = datetime.datetime.strptime(time_s, fmt).time()
            break
        except Exception:
            pass
    if time_obj is None:
        raise ValueError("Bad time")
    return datetime.datetime.combine(date_obj, time_obj)


def parse_duration(dur_s: str) -> int:
    dur_s = dur_s.strip().lower()
    if dur_s.isdigit():
        m = int(dur_s)
        if m <= 0: raise ValueError
        return m
    h = int(re.search(r"(\d+)\s*h", dur_s).group(1)) if re.search(r"(\d+)\s*h", dur_s) else 0
    m = int(re.search(r"(\d+)\s*m", dur_s).group(1)) if re.search(r"(\d+)\s*m", dur_s) else 0
    total = h * 60 + m
    if total <= 0: raise ValueError
    return total


# ─────────────────────────────────────────────
# Schedule Screen
# ─────────────────────────────────────────────
class ScheduleItemRow(BoxLayout):
    def __init__(self, ev, on_delete, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint   = (1, None)
        self.height      = dp(44)
        self.spacing     = dp(8)

        start = datetime.datetime.fromisoformat(ev["start"]).strftime("%b %d, %H:%M")
        label = Label(
            text=f"[b]{ev['type']}[/b] – {ev['title']}  ({start}, {ev['duration']} min)",
            markup=True, halign="left", valign="middle",
            size_hint=(1, 1), color=(0.1, 0.1, 0.1, 1)
        )
        label.bind(size=lambda *_: setattr(label, "text_size", label.size))
        self.add_widget(label)
        self.add_widget(small_button("✕", lambda *_: on_delete(ev), width=44))


class ScheduleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        white_bg(self)

        root = BoxLayout(orientation='vertical',
                         padding=[dp(16), dp(12), dp(16), dp(16)], spacing=dp(10))

        header = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(68), spacing=dp(2))
        header.add_widget(Label(text="STATHLETE", font_size='26sp', bold=True, color=(0, 0, 0, 1)))
        header.add_widget(Label(text="Schedule sessions", font_size='18sp', color=(0.1, 0.1, 0.1, 1)))
        root.add_widget(header)

        form = BoxLayout(orientation='vertical', spacing=dp(6), size_hint=(1, None))
        form.bind(minimum_height=form.setter('height'))

        self.title_in = rounded_text_input("Title (e.g., Upper body workout)")
        self.type_in  = rounded_text_input("Type: Workout or Study")
        self.date_in  = rounded_text_input("Date (YYYY-MM-DD or MM/DD/YYYY)")
        self.time_in  = rounded_text_input("Start time (e.g., 19:00, 7:00 pm)")
        self.dur_in   = rounded_text_input("Duration (e.g., 45, 1h 15m)")

        def center(w):
            box = AnchorLayout(anchor_x='center', size_hint=(1, None), height=w.height + dp(4))
            box.add_widget(w)
            return box

        for w in [self.title_in, self.type_in, self.date_in, self.time_in, self.dur_in]:
            form.add_widget(center(w))

        actions = BoxLayout(orientation='horizontal', spacing=dp(8),
                            size_hint=(None, None), height=dp(44), width=dp(268))
        actions.add_widget(small_button("Add Session", self.add_session, width=130))
        root_self = self
        actions.add_widget(small_button("Sync Google", lambda *_: root_self._msg_label("Google sync not configured.", ok=False), width=130))
        form.add_widget(center(actions))

        self.msg = Label(text="", color=(0.8, 0, 0, 1), font_size='12sp',
                         size_hint=(None, None), height=dp(18), width=dp(280),
                         halign='center', valign='middle')
        self.msg.bind(size=lambda *_: setattr(self.msg, "text_size", self.msg.size))
        form.add_widget(center(self.msg))
        root.add_widget(form)

        scroller = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6))
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        scroller.add_widget(self.list_box)
        root.add_widget(scroller)

        footer = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, None), height=dp(56))
        footer.add_widget(styled_button("Back to Home", lambda *_: setattr(self.manager, 'current', 'home')))
        root.add_widget(footer)

        wrapper = AnchorLayout()
        wrapper.add_widget(root)
        self.add_widget(wrapper)

    def on_pre_enter(self, *args):
        self.refresh_list()
        self.msg.text = ""

    def _msg_label(self, text, ok=False):
        self.msg.text  = text
        self.msg.color = (0, 0.5, 0, 1) if ok else (0.8, 0, 0, 1)

    def add_session(self, *_):
        self._msg_label("")
        try:
            start_dt = parse_date_time(self.date_in.text, self.time_in.text)
            duration = parse_duration(self.dur_in.text)
        except Exception:
            self._msg_label("Invalid date/time/duration.", ok=False)
            return

        typ = self.type_in.text.strip().capitalize() or "Workout"
        ev  = {
            "title":    self.title_in.text.strip() or f"{typ} Session",
            "type":     "Workout" if typ.lower().startswith("work") else
                        ("Study"  if typ.lower().startswith("study") else typ),
            "start":    start_dt.isoformat(timespec="minutes"),
            "duration": duration,
        }
        items = load_schedule()
        items.append(ev)
        items.sort(key=lambda e: e["start"])
        save_schedule(items)

        for w in [self.title_in, self.type_in, self.date_in, self.time_in, self.dur_in]:
            w.text = ""
        self.refresh_list()
        self._msg_label("Session added ✓", ok=True)

    def delete_session(self, ev):
        items = [x for x in load_schedule()
                 if not (x["title"] == ev["title"] and x["start"] == ev["start"]
                         and x["duration"] == ev["duration"])]
        save_schedule(items)
        self.refresh_list()
        self._msg_label("Session removed", ok=True)

    def refresh_list(self):
        self.list_box.clear_widgets()
        items = load_schedule()
        if not items:
            self.list_box.add_widget(Label(text="No sessions yet. Add one above.",
                                           font_size='13sp', color=(0.3, 0.3, 0.3, 1),
                                           size_hint=(1, None), height=dp(22)))
            return
        for ev in items:
            self.list_box.add_widget(ScheduleItemRow(ev, on_delete=self.delete_session))


# ─────────────────────────────────────────────
# AI Coach Screen
# ─────────────────────────────────────────────
class AICoachScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        white_bg(self)

        root = BoxLayout(orientation='vertical',
                         padding=[dp(16), dp(12), dp(16), dp(16)], spacing=dp(10))

        header = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(68), spacing=dp(2))
        header.add_widget(Label(text="STATHLETE", font_size='26sp', bold=True, color=(0, 0, 0, 1)))
        header.add_widget(Label(text="AI Coach", font_size='18sp', color=(0.1, 0.1, 0.1, 1)))
        root.add_widget(header)

        root.add_widget(Label(text="Quick Prompts", font_size='15sp', color=(0, 0, 0, 1),
                              size_hint=(1, None), height=dp(24)))

        for prompts in [
            [("Improve Speed",   "How can I improve my speed?"),
             ("Build Endurance", "How can I build endurance?")],
            [("Get Stronger",    "How can I get stronger?"),
             ("Weekly Focus",    "What should I focus on this week?")],
        ]:
            row = BoxLayout(orientation='horizontal', spacing=dp(8),
                            size_hint=(1, None), height=dp(40))
            for label, prompt in prompts:
                row.add_widget(small_button(label, lambda *_, p=prompt: self._fill(p), width=130))
            root.add_widget(row)

        root.add_widget(Label(text="Coach Chat", font_size='15sp', color=(0, 0, 0, 1),
                              size_hint=(1, None), height=dp(24)))

        self.chat_scroll = ScrollView(size_hint=(1, 1))
        self.chat_box    = BoxLayout(orientation='vertical', size_hint_y=None,
                                     spacing=dp(8), padding=[dp(4)] * 4)
        self.chat_box.bind(minimum_height=self.chat_box.setter('height'))
        self.chat_scroll.add_widget(self.chat_box)
        root.add_widget(self.chat_scroll)

        self._add_msg("Coach", "Hi! I'm your AI Coach. Ask me about speed, endurance, strength, recovery, or weekly focus.")

        self.input = TextInput(
            hint_text="Ask your coach a question…", multiline=False,
            size_hint=(1, None), height=dp(44), padding=[dp(10), dp(12)],
            background_normal='', background_active='',
            background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1), cursor_color=(0, 0, 0, 1)
        )
        self.input.bind(on_text_validate=lambda *_: self.send())
        root.add_widget(self.input)

        action_row = BoxLayout(orientation='horizontal', spacing=dp(8),
                               size_hint=(1, None), height=dp(44))
        action_row.add_widget(small_button("Send",       lambda *_: self.send(),        width=130))
        action_row.add_widget(small_button("Clear Chat", lambda *_: self._clear_chat(), width=130))
        root.add_widget(action_row)

        footer = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, None), height=dp(56))
        footer.add_widget(styled_button("Back to Home", lambda *_: setattr(self.manager, 'current', 'home')))
        root.add_widget(footer)

        wrapper = AnchorLayout()
        wrapper.add_widget(root)
        self.add_widget(wrapper)

    def _fill(self, text):
        self.input.text = text

    def _clear_chat(self):
        self.chat_box.clear_widgets()
        self._add_msg("Coach", "Chat cleared. Ask me another training question.")

    def _add_msg(self, sender, text):
        color = (0.1, 0.3, 0.6, 1) if sender == "Coach" else (0, 0, 0, 1)
        msg = Label(
            text=f"[b]{sender}:[/b] {text}", markup=True,
            halign='left', valign='top',
            size_hint=(1, None), color=color, font_size='14sp'
        )
        msg.bind(
            width=lambda inst, val: setattr(inst, "text_size", (val, None)),
            texture_size=lambda inst, val: setattr(inst, "height", val[1] + dp(12))
        )
        self.chat_box.add_widget(msg)

    def send(self):
        question = self.input.text.strip()
        if not question:
            return
        self._add_msg("You",   question)
        self._add_msg("Coach", self._respond(question))
        self.input.text = ""

    def _respond(self, question):
        q = question.lower()
        if any(w in q for w in ("speed", "faster", "sprint")):
            return ("Your speed score is 78. Focus on sprint intervals, explosive starts, and lower-body power "
                    "work like squats and lunges. Add 2 speed sessions per week.")
        if any(w in q for w in ("endurance", "stamina", "cardio")):
            return ("Your endurance score is 65 — a good area to grow. Add steady cardio, tempo runs, or longer "
                    "sessions 2–3 times a week. Build up gradually.")
        if any(w in q for w in ("strength", "stronger", "muscle")):
            return ("Your strength score is 72. Focus on compound movements: squats, push-ups, rows, deadlifts. "
                    "Train 3–4 times per week and track your progress.")
        if any(w in q for w in ("flexibility", "mobility")):
            return ("Your flexibility score is 60 — mobility work will help a lot. Add dynamic warm-ups before "
                    "training and 10 minutes of stretching after workouts.")
        if any(w in q for w in ("recover", "recovery", "rest")):
            return ("Recovery is as important as training. Prioritize sleep, hydration, stretching, and lighter "
                    "days after intense sessions.")
        if any(w in q for w in ("week", "focus", "what should i do")):
            return ("Based on your profile, your biggest opportunity is endurance. This week: one speed session, "
                    "two endurance sessions, one strength workout.")
        return ("You're doing well overall. Keep training consistently, recover properly, and focus on one "
                "weakness at a time. Ask me about speed, endurance, strength, flexibility, recovery, or weekly focus.")


# ─────────────────────────────────────────────
# App
# ─────────────────────────────────────────────
class StathleteApp(App):
    def build(self):
        sm = ScreenManager()
        sm.current_user    = None
        sm.selected_sport  = None

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(WorkoutSelectionScreen(name="workout_selection"))
        sm.add_widget(WorkoutQuestionnaireScreen(name="workout_questionnaire"))
        sm.add_widget(TrendsScreen(name="trends"))
        sm.add_widget(SelectSportScreen(name="select_sport"))
        sm.add_widget(GameStatsScreen(name="game_stats"))
        sm.add_widget(GoalsScreen(name="goals"))
        sm.add_widget(ScheduleScreen(name="schedule"))
        sm.add_widget(AICoachScreen(name="coach"))
        return sm


if __name__ == "__main__":
    StathleteApp().run()
