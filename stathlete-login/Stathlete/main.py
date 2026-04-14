from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.scrollview import ScrollView

from datetime import datetime
import json, os, re

# Google Calendar helper
from gcalendar_helper import sync_events_with_google

# -----------------------------
# Window / simple persistence
# -----------------------------
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

GOALS_DB = "goals.json"
if not os.path.exists(GOALS_DB):
    with open(GOALS_DB, "w") as f:
        json.dump([], f, indent=2)

def load_goals():
    with open(GOALS_DB, "r") as f:
        return json.load(f)

def save_goals(goals):
    with open(GOALS_DB, "w") as f:
        json.dump(goals, f, indent=2)

SCHEDULE_DB = "schedule.json"
if not os.path.exists(SCHEDULE_DB):
    with open(SCHEDULE_DB, "w") as f:
        json.dump([], f, indent=2)

def load_schedule():
    with open(SCHEDULE_DB, "r") as f:
        return json.load(f)

def save_schedule(items):
    with open(SCHEDULE_DB, "w") as f:
        json.dump(items, f, indent=2)

# -----------------------------
# Shared UI helpers
# -----------------------------
class OutlinedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.after:
            Color(0.2, 0.2, 0.6, 1)
            self._outline = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.2)
        self.bind(pos=self._update_outline, size=self._update_outline)

    def _update_outline(self, *args):
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

def small_button(text, on_press_fn, width=100):
    btn = Button(
        text=text,
        size_hint=(None, None),
        width=dp(width),
        height=dp(36),
        background_normal='',
        background_color=(0.1, 0.3, 0.6, 1),
        color=(1, 1, 1, 1),
        font_size='14sp'
    )
    btn.bind(on_press=on_press_fn)
    return btn

def screen_layout(title_text, elements):
    layout = BoxLayout(
        orientation='vertical',
        spacing=dp(12),
        size_hint=(1, None),
        height=dp(600)
    )
    layout.padding = [dp(0), dp(40)]
    layout.add_widget(Label(
        text="STATHLETE",
        font_size='32sp',
        bold=True,
        color=(0, 0, 0, 1),
        size_hint=(1, None),
        height=dp(50)
    ))
    layout.add_widget(Label(
        text=title_text,
        font_size='22sp',
        color=(0, 0, 0, 1),
        size_hint=(1, None),
        height=dp(36)
    ))
    for el in elements:
        box = AnchorLayout(anchor_x='center')
        box.add_widget(el)
        layout.add_widget(box)
    return layout

# -----------------------------
# Auth Screens
# -----------------------------
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_background()

        self.username = rounded_text_input("Username or Email")
        self.password = rounded_text_input("Password")
        self.password.password = True

        layout = screen_layout("Login", [
            self.username,
            self.password,
            styled_button("Log In", self.login),
            Label(
                text="or",
                font_size='14sp',
                color=(0.4, 0.4, 0.4, 1),
                size_hint=(None, None),
                height=dp(20)
            ),
            styled_button("Sign Up", self.go_to_signup)
        ])

        wrapper = AnchorLayout(anchor_x='center', anchor_y='top')
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def login(self, *args):
        users = load_users()
        uname = self.username.text.strip()
        pword = self.password.text.strip()
        if uname in users and users[uname] == pword:
            self.manager.current = "home"
        else:
            print("Invalid login")

    def go_to_signup(self, *args):
        self.manager.current = "signup"

    def _set_background(self):
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self._update_bg)

    def _update_bg(self, *args):
        self.bg_rect.size = self.size

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_background()

        self.username = rounded_text_input("Username")
        self.email = rounded_text_input("Email")
        self.password = rounded_text_input("Password")
        self.password.password = True

        layout = screen_layout("Sign Up", [
            self.username,
            self.email,
            self.password,
            styled_button("Sign Up", self.register),
            Label(
                text="Already have an account?",
                font_size='14sp',
                color=(0.4, 0.4, 0.4, 1),
                size_hint=(None, None),
                height=dp(20)
            ),
            styled_button("Log In", self.go_to_login)
        ])

        wrapper = AnchorLayout(anchor_x='center', anchor_y='top')
        wrapper.add_widget(layout)
        self.add_widget(wrapper)

    def register(self, *args):
        users = load_users()
        uname = self.username.text.strip()
        pword = self.password.text.strip()
        if not uname or not pword:
            print("Missing username/password")
            return
        if uname in users:
            print("Username already exists")
        else:
            users[uname] = pword
            save_users(users)
            print("User registered")
            self.manager.current = "login"

    def go_to_login(self, *args):
        self.manager.current = "login"

    def _set_background(self):
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self._update_bg)

    def _update_bg(self, *args):
        self.bg_rect.size = self.size

# -----------------------------
# Home
# -----------------------------
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_background()

        root = BoxLayout(
            orientation='vertical',
            padding=[dp(16), dp(12), dp(16), dp(16)],
            spacing=dp(12)
        )

        header = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(68),
            spacing=dp(2)
        )
        header.add_widget(Label(
            text="STATHLETE",
            font_size='26sp',
            bold=True,
            color=(0, 0, 0, 1)
        ))
        header.add_widget(Label(
            text="Your daily performance hub",
            font_size='13sp',
            color=(0.3, 0.3, 0.3, 1)
        ))
        root.add_widget(header)

        qa = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            padding=[0, dp(6), 0, dp(6)],
            size_hint=(1, None)
        )
        qa.bind(minimum_height=qa.setter('height'))

        qa.add_widget(Label(
            text="Quick Actions",
            font_size='16sp',
            color=(0, 0, 0, 1),
            size_hint=(1, None),
            height=dp(24)
        ))

        def centered_row_button(text, fn):
            row = AnchorLayout(
                anchor_x='center',
                anchor_y='center',
                size_hint=(1, None),
                height=dp(48)
            )
            row.add_widget(styled_button(text, fn))
            return row

        qa.add_widget(centered_row_button("Start Workout", lambda *_: print("Start Workout")))
        qa.add_widget(centered_row_button("Log Stats", lambda *_: print("Log Stats")))
        qa.add_widget(centered_row_button("View Trends", lambda *_: print("View Trends")))
        qa.add_widget(centered_row_button("Goals", self.open_goals))
        qa.add_widget(centered_row_button("Schedule", self.open_schedule))
        qa.add_widget(centered_row_button("AI Coach", self.open_ai_coach))
        root.add_widget(qa)

        root.add_widget(Label(size_hint=(1, None), height=dp(8)))

        recent = BoxLayout(
            orientation='vertical',
            spacing=dp(4),
            size_hint=(1, None),
            padding=[0, 0, 0, dp(4)]
        )
        recent.bind(minimum_height=recent.setter('height'))
        recent.add_widget(Label(
            text="Recent Activity",
            font_size='16sp',
            color=(0, 0, 0, 1),
            size_hint=(1, None),
            height=dp(22)
        ))
        for line in [
            "• Upper body workout – 45 min",
            "• Sprint drills – 20 min",
            "• Logged recovery & hydration",
        ]:
            recent.add_widget(Label(
                text=line,
                font_size='12sp',
                color=(0.2, 0.2, 0.2, 1),
                size_hint=(1, None),
                height=dp(20)
            ))
        root.add_widget(recent)

        root.add_widget(Label(size_hint=(1, 1)))

        logout_box = AnchorLayout(
            anchor_x='center',
            anchor_y='bottom',
            size_hint=(1, None),
            height=dp(56)
        )
        logout_box.add_widget(styled_button("Logout", self.logout))
        root.add_widget(logout_box)

        wrapper = AnchorLayout()
        wrapper.add_widget(root)
        self.add_widget(wrapper)

    def open_goals(self, *_):
        self.manager.current = "goals"

    def open_schedule(self, *_):
        self.manager.current = "schedule"

    def open_ai_coach(self, *_):
        self.manager.current = "coach"

    def logout(self, *args):
        self.manager.current = "login"

    def _set_background(self):
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=Window.size)
        self.bind(size=self._update_bg)

    def _update_bg(self, *args):
        self.bg_rect.size = self.size

# -----------------------------
# Goals
# -----------------------------
class GoalsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        root = BoxLayout(
            orientation='vertical',
            padding=[dp(16), dp(12), dp(16), dp(16)],
            spacing=dp(10)
        )

        header = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(68),
            spacing=dp(2)
        )
        header.add_widget(Label(
            text="STATHLETE",
            font_size='26sp',
            bold=True,
            color=(0, 0, 0, 1)
        ))
        header.add_widget(Label(
            text="Goals",
            font_size='18sp',
            color=(0.1, 0.1, 0.1, 1)
        ))
        root.add_widget(header)

        add_row = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(48),
            spacing=dp(8)
        )
        self.input = TextInput(
            hint_text="Add a new goal…",
            multiline=False,
            size_hint=(1, None),
            height=dp(44),
            padding=[dp(10), dp(12)],
            background_normal='',
            background_active='',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0, 0, 0, 1)
        )
        add_btn = Button(
            text="Add",
            size_hint=(None, None),
            width=dp(80),
            height=dp(44),
            background_normal='',
            background_color=(0.1, 0.3, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        add_btn.bind(on_press=self.add_goal)
        self.input.bind(on_text_validate=lambda *_: self.add_goal(None))
        add_row.add_widget(self.input)
        add_row.add_widget(add_btn)
        root.add_widget(add_row)

        scroller = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(6),
            padding=[0, dp(4), 0, dp(4)]
        )
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        scroller.add_widget(self.list_box)
        root.add_widget(scroller)

        back_box = AnchorLayout(
            anchor_x='center',
            anchor_y='bottom',
            size_hint=(1, None),
            height=dp(56)
        )
        back_btn = Button(
            text="Back to Home",
            size_hint=(None, None),
            width=dp(280),
            height=dp(44),
            background_normal='',
            background_color=(0.1, 0.3, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        back_btn.bind(on_press=lambda *_: setattr(self.manager, "current", "home"))
        back_box.add_widget(back_btn)
        root.add_widget(back_box)

        wrapper = AnchorLayout()
        wrapper.add_widget(root)
        self.add_widget(wrapper)

    def on_pre_enter(self, *args):
        self.refresh_list()

    def add_goal(self, *_):
        text = self.input.text.strip()
        if not text:
            return
        goals = load_goals()
        goals.append(text)
        save_goals(goals)
        self.input.text = ""
        self.refresh_list()

    def refresh_list(self):
        self.list_box.clear_widgets()
        goals = load_goals()
        if not goals:
            self.list_box.add_widget(Label(
                text="No goals yet. Add your first one above.",
                font_size='13sp',
                color=(0.3, 0.3, 0.3, 1),
                size_hint=(1, None),
                height=dp(22)
            ))
            return
        for g in goals:
            self.list_box.add_widget(Label(
                text=f"• {g}",
                font_size='14sp',
                color=(0.1, 0.1, 0.1, 1),
                size_hint=(1, None),
                height=dp(22)
            ))

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

# -----------------------------
# Schedule helpers
# -----------------------------
def parse_date_time(date_s: str, time_s: str) -> datetime:
    date_s = date_s.strip()
    time_s = time_s.strip().lower()

    date_formats = ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y"]
    date_obj = None
    for fmt in date_formats:
        try:
            date_obj = datetime.strptime(date_s, fmt).date()
            break
        except Exception:
            pass
    if date_obj is None:
        raise ValueError("Bad date")

    time_obj = None
    if re.fullmatch(r"\d{1,2}", time_s):
        time_s = f"{int(time_s):02d}:00"

    if re.fullmatch(r"\d{1,2}\s*(am|pm)", time_s):
        m = re.match(r"(\d{1,2})\s*(am|pm)", time_s)
        time_s = f"{int(m.group(1))}:00 {m.group(2)}"

    time_formats = ["%H:%M", "%I:%M %p", "%I %p"]
    for fmt in time_formats:
        try:
            time_obj = datetime.strptime(time_s, fmt).time()
            break
        except Exception:
            pass
    if time_obj is None:
        raise ValueError("Bad time")

    return datetime.combine(date_obj, time_obj)

def parse_duration(dur_s: str) -> int:
    dur_s = dur_s.strip().lower()
    if dur_s.isdigit():
        m = int(dur_s)
        if m <= 0:
            raise ValueError
        return m

    h = 0
    m = 0
    mh = re.search(r"(\d+)\s*h", dur_s)
    mm = re.search(r"(\d+)\s*m", dur_s)
    if mh:
        h = int(mh.group(1))
    if mm:
        m = int(mm.group(1))

    total = h * 60 + m
    if total <= 0:
        raise ValueError
    return total

# -----------------------------
# Schedule UI
# -----------------------------
class ScheduleItemRow(BoxLayout):
    def __init__(self, ev, on_delete, **kwargs):
        super().__init__(**kwargs)
        self.ev = ev
        self.orientation = "horizontal"
        self.size_hint = (1, None)
        self.height = dp(44)
        self.spacing = dp(8)

        start = datetime.fromisoformat(ev["start"]).strftime("%b %d, %H:%M")
        label = Label(
            text=f"[b]{ev['type']}[/b] – {ev['title']}  ({start}, {ev['duration']} min)",
            markup=True,
            halign="left",
            valign="middle",
            size_hint=(1, 1),
            color=(0.1, 0.1, 0.1, 1)
        )
        label.bind(size=lambda *_: setattr(label, "text_size", label.size))

        del_btn = small_button("✕", lambda *_: on_delete(ev), width=44)

        self.add_widget(label)
        self.add_widget(del_btn)

class ScheduleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        root = BoxLayout(
            orientation='vertical',
            padding=[dp(16), dp(12), dp(16), dp(16)],
            spacing=dp(10)
        )

        header = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(68),
            spacing=dp(2)
        )
        header.add_widget(Label(
            text="STATHLETE",
            font_size='26sp',
            bold=True,
            color=(0, 0, 0, 1)
        ))
        header.add_widget(Label(
            text="Schedule sessions",
            font_size='18sp',
            color=(0.1, 0.1, 0.1, 1)
        ))
        root.add_widget(header)

        form = BoxLayout(
            orientation='vertical',
            spacing=dp(6),
            size_hint=(1, None)
        )
        form.bind(minimum_height=form.setter('height'))

        self.title_in = rounded_text_input("Title (e.g., Upper body workout)")
        self.type_in  = rounded_text_input("Type: Workout or Study")
        self.date_in  = rounded_text_input("Date (YYYY-MM-DD or MM/DD/YYYY)")
        self.time_in  = rounded_text_input("Start time (e.g., 19:00, 7:00 pm)")
        self.dur_in   = rounded_text_input("Duration (e.g., 45, 1h 15m)")

        def center(w, extra_h=dp(4)):
            box = AnchorLayout(
                anchor_x='center',
                size_hint=(1, None),
                height=w.height + extra_h
            )
            box.add_widget(w)
            return box

        form.add_widget(center(self.title_in))
        form.add_widget(center(self.type_in))
        form.add_widget(center(self.date_in))
        form.add_widget(center(self.time_in))
        form.add_widget(center(self.dur_in))

        actions = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint=(None, None),
            height=dp(44),
            width=dp(268)
        )
        actions.add_widget(small_button("Add Session", self.add_session, width=130))
        actions.add_widget(small_button("Sync with Google", self.sync_with_google, width=130))
        form.add_widget(center(actions, extra_h=0))

        self.msg = Label(
            text="",
            color=(0.8, 0.0, 0.0, 1),
            font_size='12sp',
            size_hint=(None, None),
            height=dp(18),
            width=dp(280),
            halign='center',
            valign='middle'
        )
        self.msg.bind(size=lambda *_: setattr(self.msg, "text_size", self.msg.size))
        form.add_widget(center(self.msg, extra_h=0))

        root.add_widget(form)

        scroller = ScrollView(size_hint=(1, 1))
        self.list_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(6)
        )
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        scroller.add_widget(self.list_box)
        root.add_widget(scroller)

        footer = AnchorLayout(
            anchor_x='center',
            anchor_y='bottom',
            size_hint=(1, None),
            height=dp(56)
        )
        footer.add_widget(styled_button("Back to Home", lambda *_: setattr(self.manager, "current", "home")))
        root.add_widget(footer)

        wrapper = AnchorLayout()
        wrapper.add_widget(root)
        self.add_widget(wrapper)

    def on_pre_enter(self, *args):
        self.refresh_list()
        self.msg.text = ""

    def _set_msg(self, text, ok=False):
        self.msg.text = text
        self.msg.color = (0, 0.5, 0, 1) if ok else (0.8, 0, 0, 1)

    def add_session(self, *_):
        self._set_msg("")
        title = self.title_in.text.strip()
        typ = self.type_in.text.strip().capitalize() or "Workout"
        date_s = self.date_in.text.strip()
        time_s = self.time_in.text.strip()
        dur_s = self.dur_in.text.strip()

        try:
            start_dt = parse_date_time(date_s, time_s)
            duration = parse_duration(dur_s)
        except Exception:
            self._set_msg("Invalid date/time/duration. Try 2025-11-06 + 7:30 pm + 45", ok=False)
            return

        ev = {
            "title": title or f"{typ} Session",
            "type": "Workout" if typ.lower().startswith("work") else ("Study" if typ.lower().startswith("study") else typ),
            "start": start_dt.isoformat(timespec="minutes"),
            "duration": duration
        }

        items = load_schedule()
        items.append(ev)
        items.sort(key=lambda e: e["start"])
        save_schedule(items)

        self.title_in.text = ""
        self.type_in.text = ""
        self.date_in.text = ""
        self.time_in.text = ""
        self.dur_in.text = ""

        self.refresh_list()
        self._set_msg("Session added ✓", ok=True)

    def delete_session(self, ev):
        items = load_schedule()
        items = [x for x in items if not (
            x["title"] == ev["title"] and
            x["start"] == ev["start"] and
            x["duration"] == ev["duration"]
        )]
        save_schedule(items)
        self.refresh_list()
        self._set_msg("Session removed", ok=True)

    def refresh_list(self):
        self.list_box.clear_widgets()
        items = load_schedule()
        if not items:
            self.list_box.add_widget(Label(
                text="No sessions yet. Add one above.",
                font_size='13sp',
                color=(0.3, 0.3, 0.3, 1),
                size_hint=(1, None),
                height=dp(22)
            ))
            return

        for ev in items:
            row = ScheduleItemRow(ev, on_delete=self.delete_session)
            self.list_box.add_widget(row)

    def sync_with_google(self, *_):
        items = load_schedule()
        if not items:
            self._set_msg("No sessions to sync.", ok=False)
            return

        try:
            sync_events_with_google(items)
        except Exception as e:
            print("Error syncing with Google Calendar:", e)
            self._set_msg("Failed to sync with Google. Check console.", ok=False)
            return

        self._set_msg("Synced to Google Calendar ✓", ok=True)

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

# -----------------------------
# AI Coach
# -----------------------------
class AICoachScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_background()

        root = BoxLayout(
            orientation='vertical',
            padding=[dp(16), dp(12), dp(16), dp(16)],
            spacing=dp(10)
        )

        header = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(68),
            spacing=dp(2)
        )
        header.add_widget(Label(
            text="STATHLETE",
            font_size='26sp',
            bold=True,
            color=(0, 0, 0, 1)
        ))
        header.add_widget(Label(
            text="AI Coach",
            font_size='18sp',
            color=(0.1, 0.1, 0.1, 1)
        ))
        root.add_widget(header)

        preset_title = Label(
            text="Quick Prompts",
            font_size='15sp',
            color=(0, 0, 0, 1),
            size_hint=(1, None),
            height=dp(24)
        )
        root.add_widget(preset_title)

        preset_row_1 = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint=(1, None),
            height=dp(40)
        )
        preset_row_1.add_widget(small_button("Improve Speed", lambda *_: self.fill_prompt("How can I improve my speed?"), width=130))
        preset_row_1.add_widget(small_button("Build Endurance", lambda *_: self.fill_prompt("How can I build endurance?"), width=130))
        root.add_widget(preset_row_1)

        preset_row_2 = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint=(1, None),
            height=dp(40)
        )
        preset_row_2.add_widget(small_button("Get Stronger", lambda *_: self.fill_prompt("How can I get stronger?"), width=130))
        preset_row_2.add_widget(small_button("Weekly Focus", lambda *_: self.fill_prompt("What should I focus on this week?"), width=130))
        root.add_widget(preset_row_2)

        chat_label = Label(
            text="Coach Chat",
            font_size='15sp',
            color=(0, 0, 0, 1),
            size_hint=(1, None),
            height=dp(24)
        )
        root.add_widget(chat_label)

        self.chat_scroll = ScrollView(size_hint=(1, 1))
        self.chat_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(8),
            padding=[dp(4), dp(4), dp(4), dp(4)]
        )
        self.chat_box.bind(minimum_height=self.chat_box.setter('height'))
        self.chat_scroll.add_widget(self.chat_box)
        root.add_widget(self.chat_scroll)

        self.add_message("Coach", "Hi! I'm your AI Coach. Ask about speed, endurance, strength, recovery, or weekly training focus.")

        self.input = TextInput(
            hint_text="Ask your coach a question...",
            multiline=False,
            size_hint=(1, None),
            height=dp(44),
            padding=[dp(10), dp(12)],
            background_normal='',
            background_active='',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0, 0, 0, 1)
        )
        self.input.bind(on_text_validate=lambda *_: self.send_message())
        root.add_widget(self.input)

        action_row = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint=(1, None),
            height=dp(44)
        )
        action_row.add_widget(small_button("Send", lambda *_: self.send_message(), width=130))
        action_row.add_widget(small_button("Clear Chat", lambda *_: self.clear_chat(), width=130))
        root.add_widget(action_row)

        footer = AnchorLayout(
            anchor_x='center',
            anchor_y='bottom',
            size_hint=(1, None),
            height=dp(56)
        )
        footer.add_widget(styled_button("Back to Home", lambda *_: setattr(self.manager, "current", "home")))
        root.add_widget(footer)

        wrapper = AnchorLayout()
        wrapper.add_widget(root)
        self.add_widget(wrapper)

    def _set_background(self):
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def fill_prompt(self, text):
        self.input.text = text

    def clear_chat(self):
        self.chat_box.clear_widgets()
        self.add_message("Coach", "Chat cleared. Ask me another training question.")

    def add_message(self, sender, text):
        color = (0.1, 0.3, 0.6, 1) if sender == "Coach" else (0, 0, 0, 1)
        msg = Label(
            text=f"[b]{sender}:[/b] {text}",
            markup=True,
            halign='left',
            valign='top',
            size_hint=(1, None),
            color=color,
            font_size='14sp'
        )
        msg.bind(
            width=lambda instance, value: setattr(instance, "text_size", (value, None)),
            texture_size=lambda instance, value: setattr(instance, "height", value[1] + dp(12))
        )
        self.chat_box.add_widget(msg)

    def send_message(self):
        question = self.input.text.strip()
        if not question:
            return

        self.add_message("You", question)
        response = self.generate_response(question)
        self.add_message("Coach", response)
        self.input.text = ""

    def generate_response(self, question):
        q = question.lower()

        # Example built-in athlete profile
        speed = 78
        endurance = 65
        strength = 72
        flexibility = 60

        if "speed" in q or "faster" in q or "sprint" in q:
            return (
                f"Your speed score is {speed}, which is solid. To improve more, focus on sprint intervals, "
                "explosive starts, and lower-body power work like squats and lunges. Add 2 speed sessions per week."
            )

        elif "endurance" in q or "stamina" in q or "cardio" in q:
            return (
                f"Your endurance score is {endurance}, so that is a good area to improve. Add steady cardio, "
                "tempo runs, or longer training sessions 2–3 times a week. Build up gradually to avoid burnout."
            )

        elif "strength" in q or "stronger" in q or "muscle" in q:
            return (
                f"Your strength score is {strength}. To get stronger, focus on compound movements like squats, "
                "push-ups, rows, and deadlifts. Train consistently 3–4 times per week and track progress."
            )

        elif "flexibility" in q or "mobility" in q:
            return (
                f"Your flexibility score is {flexibility}, so mobility work could help a lot. Add dynamic warmups "
                "before training and 10 minutes of stretching after workouts."
            )

        elif "recover" in q or "recovery" in q or "rest" in q:
            return (
                "Recovery is just as important as training. Prioritize sleep, hydration, stretching, and lighter "
                "recovery days after intense sessions."
            )

        elif "week" in q or "focus" in q or "what should i do" in q:
            return (
                "Based on your current profile, your biggest opportunity is endurance. This week, focus on one speed session, "
                "two endurance sessions, and one strength workout."
            )

        elif "goal" in q or "improve" in q:
            return (
                "A strong plan is to pick one main focus area for the next 2 weeks. Right now, endurance and mobility "
                "look like the best places to improve while maintaining your speed and strength."
            )

        else:
            return (
                "You are doing well overall. Keep training consistently, recover properly, and focus on one weakness at a time. "
                "Ask me about speed, endurance, strength, flexibility, recovery, or weekly focus."
            )

# -----------------------------
# App
# -----------------------------
class StathleteApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(GoalsScreen(name="goals"))
        sm.add_widget(ScheduleScreen(name="schedule"))
        sm.add_widget(AICoachScreen(name="coach"))
        return sm

if __name__ == "__main__":
    StathleteApp().run()
