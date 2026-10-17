

"""Student Activities Management System - offline desktop GUI.

Requirements: Python 3.9+ (Tkinter and SQLite are included in standard Python installs).
Run: python student_activities_ui.py
The SQLite database is created beside this script as student_activities.db.
"""

import csv
import sqlite3
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "student_activities.db"

YEARS = {1: "1st Year", 2: "2nd Year", 3: "3rd Year", 4: "4th Year"}
YEAR_OPTIONS = ["All Years", "1st Year", "2nd Year", "3rd Year", "4th Year"]
YEAR_TO_VALUE = {v: k for k, v in YEARS.items()}
YEAR_TO_VALUE["All Years"] = 0
CATEGORIES = [
    "Technical", "Cultural", "Sports", "Workshop", "Hackathon",
    "Project", "Internship", "Certification", "Research", "Other"
]
STATUSES = ["Registered", "Completed", "Cancelled"]

# UI palette
NAVY = "#182338"
NAVY_LIGHT = "#24334E"
BLUE = "#4263EB"
BLUE_HOVER = "#3451CC"
BG = "#F3F5FA"
WHITE = "#FFFFFF"
TEXT = "#202B3C"
MUTED = "#718096"
BORDER = "#E1E6EF"
GREEN = "#16845B"
RED = "#C2414B"


def db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    with db_connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            year INTEGER NOT NULL CHECK(year BETWEEN 1 AND 4),
            email TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            activity_date TEXT NOT NULL,
            venue TEXT DEFAULT '',
            description TEXT DEFAULT '',
            target_year INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS participation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            activity_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Registered',
            achievement TEXT DEFAULT '',
            UNIQUE(student_id, activity_id),
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY(activity_id) REFERENCES activities(id) ON DELETE CASCADE
        );
        """)
        # Upgrade an existing database created by the earlier console version.
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(activities)")}
        if "target_year" not in columns:
            conn.execute("ALTER TABLE activities ADD COLUMN target_year INTEGER NOT NULL DEFAULT 0")


class StudentActivitiesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Activities | Management System")
        self.geometry("1220x780")
        self.minsize(980, 650)
        self.configure(bg=BG)
        self.current_page = "Dashboard"
        self._style_ttk()
        self._build_shell()
        self.show_page("Dashboard")

    def _style_ttk(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background=WHITE, fieldbackground=WHITE,
                        foreground=TEXT, rowheight=34, bordercolor=BORDER,
                        borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#EDF1F7", foreground="#48566B",
                        font=("Segoe UI", 9, "bold"), relief="flat", padding=(10, 9))
        style.map("Treeview", background=[("selected", "#DFE7FF")],
                  foreground=[("selected", TEXT)])
        style.configure("TCombobox", padding=7, font=("Segoe UI", 10))
        style.configure("TEntry", padding=8, font=("Segoe UI", 10))
        style.configure("Vertical.TScrollbar", background="#D9DFE9", troughcolor=BG, arrowsize=12)

    def _build_shell(self):
        self.sidebar = tk.Frame(self, bg=NAVY, width=228)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg=NAVY)
        brand.pack(fill="x", padx=20, pady=(26, 30))
        logo = tk.Label(brand, text="SA", bg=BLUE, fg=WHITE,
                        font=("Segoe UI", 16, "bold"), width=3, height=1, pady=8)
        logo.pack(side="left", padx=(0, 11))
        brand_text = tk.Frame(brand, bg=NAVY)
        brand_text.pack(side="left")
        tk.Label(brand_text, text="Student Activities", bg=NAVY, fg=WHITE,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(brand_text, text="OFFLINE MANAGER", bg=NAVY, fg="#AAB7CC",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(4, 0))

        tk.Label(self.sidebar, text="WORKSPACE", bg=NAVY, fg="#8190A8",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=22, pady=(0, 10))
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "▦"),
            ("Students", "♙"),
            ("Activities", "✦"),
            ("Participation", "✓"),
            ("Reports", "▤"),
        ]
        for label, symbol in nav_items:
            button = tk.Button(
                self.sidebar, text=f"  {symbol}    {label}", anchor="w",
                bg=NAVY, fg="#CFD7E6", activebackground=NAVY_LIGHT,
                activeforeground=WHITE, relief="flat", bd=0,
                font=("Segoe UI", 10), padx=15, pady=12, cursor="hand2",
                command=lambda name=label: self.show_page(name)
            )
            button.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[label] = button

        bottom = tk.Frame(self.sidebar, bg=NAVY)
        bottom.pack(side="bottom", fill="x", padx=20, pady=20)
        tk.Frame(bottom, bg="#34415A", height=1).pack(fill="x", pady=(0, 13))
        tk.Label(bottom, text="●  LOCAL DATABASE", bg=NAVY, fg="#8EE0BA",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(bottom, text="Your data stays on this computer.", bg=NAVY,
                 fg="#AAB7CC", font=("Segoe UI", 8), wraplength=180,
                 justify="left").pack(anchor="w", pady=(7, 0))

        self.main_area = tk.Frame(self, bg=BG)
        self.main_area.pack(side="left", fill="both", expand=True)
        self.header = tk.Frame(self.main_area, bg=BG)
        self.header.pack(fill="x", padx=30, pady=(24, 17))
        self.page_title = tk.Label(self.header, text="Dashboard", bg=BG, fg=TEXT,
                                   font=("Segoe UI", 22, "bold"))
        self.page_title.pack(anchor="w")
        self.page_subtitle = tk.Label(self.header, text="A clear overview of your college activities.",
                                      bg=BG, fg=MUTED, font=("Segoe UI", 10))
        self.page_subtitle.pack(anchor="w", pady=(5, 0))
        self.page_body = tk.Frame(self.main_area, bg=BG)
        self.page_body.pack(fill="both", expand=True, padx=30, pady=(0, 28))

    def show_page(self, name):
        self.current_page = name
        for nav_name, button in self.nav_buttons.items():
            if nav_name == name:
                button.configure(bg=BLUE, fg=WHITE, activebackground=BLUE_HOVER)
            else:
                button.configure(bg=NAVY, fg="#CFD7E6", activebackground=NAVY_LIGHT)
        subtitles = {
            "Dashboard": "A clear overview of your college activities.",
            "Students": "Manage student records across all four academic years.",
            "Activities": "Create and organize college activities and events.",
            "Participation": "Track student registrations, completion and achievements.",
            "Reports": "Review year-wise totals and export participation data.",
        }
        self.page_title.configure(text=name)
        self.page_subtitle.configure(text=subtitles.get(name, ""))
        for child in self.page_body.winfo_children():
            child.destroy()
        page_methods = {
            "Dashboard": self._dashboard_page,
            "Students": self._students_page,
            "Activities": self._activities_page,
            "Participation": self._participation_page,
            "Reports": self._reports_page,
        }
        page_methods[name]()

    def _card(self, parent, title, value, note, accent=BLUE):
        card = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        tk.Frame(card, bg=accent, height=4).pack(fill="x")
        inner = tk.Frame(card, bg=WHITE)
        inner.pack(fill="both", expand=True, padx=18, pady=15)
        tk.Label(inner, text=title.upper(), bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(inner, text=str(value), bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=(5, 2))
        tk.Label(inner, text=note, bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w")
        return card

    def _section(self, parent, title, action_text=None, action=None):
        frame = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        top = tk.Frame(frame, bg=WHITE)
        top.pack(fill="x", padx=17, pady=(15, 10))
        tk.Label(top, text=title, bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        if action_text and action:
            self._button(top, action_text, action, compact=True).pack(side="right")
        return frame

    def _button(self, parent, text, command, kind="primary", compact=False):
        if kind == "primary":
            bg, fg, active = BLUE, WHITE, BLUE_HOVER
        elif kind == "danger":
            bg, fg, active = "#FCE8E9", RED, "#F8D5D7"
        elif kind == "success":
            bg, fg, active = "#E2F6ED", GREEN, "#C9EEDD"
        else:
            bg, fg, active = WHITE, TEXT, "#EDF1F7"
        return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                         activebackground=active, activeforeground=fg,
                         relief="flat", bd=0, cursor="hand2",
                         font=("Segoe UI", 9, "bold"),
                         padx=12 if compact else 15,
                         pady=7 if compact else 10)

    def _make_tree(self, parent, columns, headings, widths=None, height=10):
        wrap = tk.Frame(parent, bg=WHITE)
        wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        tree = ttk.Treeview(wrap, columns=columns, show="headings", height=height, selectmode="browse")
        widths = widths or [150] * len(columns)
        for col, heading, width in zip(columns, headings, widths):
            tree.heading(col, text=heading)
            tree.column(col, width=width, minwidth=75, stretch=True)
        yscroll = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=yscroll.set)
        tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        return tree

    def _empty_state(self, parent, title, detail):
        frame = tk.Frame(parent, bg=WHITE)
        tk.Label(frame, text=title, bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(22, 5))
        tk.Label(frame, text=detail, bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 10)).pack(pady=(0, 22))
        return frame

    def _dashboard_page(self):
        with db_connect() as conn:
            student_count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
            activity_count = conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
            registration_count = conn.execute("SELECT COUNT(*) FROM participation").fetchone()[0]
            complete_count = conn.execute("SELECT COUNT(*) FROM participation WHERE status='Completed'").fetchone()[0]
            year_counts = {year: conn.execute("SELECT COUNT(*) FROM students WHERE year=?", (year,)).fetchone()[0]
                           for year in YEARS}
            recent = conn.execute("""SELECT id, title, category, activity_date, target_year
                                    FROM activities ORDER BY activity_date DESC, id DESC LIMIT 6""").fetchall()

        cards = tk.Frame(self.page_body, bg=BG)
        cards.pack(fill="x")
        card_specs = [
            ("Total Students", student_count, "Across all four years", BLUE),
            ("Total Activities", activity_count, "Activities created", "#8B5CF6"),
            ("Registrations", registration_count, "Student participation records", "#E59A24"),
            ("Completed", complete_count, "Activities completed by students", GREEN),
        ]
        for i, spec in enumerate(card_specs):
            card = self._card(cards, *spec)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0 if i == 3 else 8))
            cards.grid_columnconfigure(i, weight=1, uniform="cards")

        middle = tk.Frame(self.page_body, bg=BG)
        middle.pack(fill="both", expand=True, pady=(18, 0))
        years_box = self._section(middle, "Students by academic year")
        years_box.pack(side="left", fill="both", expand=True, padx=(0, 9))
        year_body = tk.Frame(years_box, bg=WHITE)
        year_body.pack(fill="both", expand=True, padx=17, pady=(3, 17))
        for year, label in YEARS.items():
            row = tk.Frame(year_body, bg=WHITE)
            row.pack(fill="x", pady=8)
            tk.Label(row, text=label, bg=WHITE, fg=TEXT,
                     font=("Segoe UI", 10)).pack(side="left")
            tk.Label(row, text=str(year_counts[year]), bg=WHITE, fg=TEXT,
                     font=("Segoe UI", 10, "bold")).pack(side="right")
            bar_bg = tk.Frame(year_body, bg="#E9EDF5", height=6)
            bar_bg.pack(fill="x", pady=(0, 3))
            bar_bg.pack_propagate(False)
            max_count = max(year_counts.values()) if max(year_counts.values(), default=0) else 1
            bar = tk.Frame(bar_bg, bg=BLUE, height=6, width=max(3, int(300 * year_counts[year] / max_count)))
            bar.pack(side="left", fill="y")

        recent_box = self._section(middle, "Recent activities", "View all", lambda: self.show_page("Activities"))
        recent_box.pack(side="left", fill="both", expand=True, padx=(9, 0))
        recent_frame = tk.Frame(recent_box, bg=WHITE)
        recent_frame.pack(fill="both", expand=True, padx=17, pady=(0, 12))
        if not recent:
            tk.Label(recent_frame, text="No activities yet", bg=WHITE, fg=MUTED,
                     font=("Segoe UI", 10)).pack(anchor="w", pady=12)
        else:
            for item in recent:
                line = tk.Frame(recent_frame, bg=WHITE)
                line.pack(fill="x", pady=7)
                tk.Label(line, text=item["title"], bg=WHITE, fg=TEXT,
                         font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x")
                scope = YEARS.get(item["target_year"], "All Years") if item["target_year"] else "All Years"
                tk.Label(line, text=f'{item["category"]}  ·  {item["activity_date"]}  ·  {scope}',
                         bg=WHITE, fg=MUTED, font=("Segoe UI", 8), anchor="w").pack(fill="x", pady=(2, 0))

        quick = tk.Frame(self.page_body, bg=BG)
        quick.pack(fill="x", pady=(17, 0))
        tk.Label(quick, text="QUICK ACTIONS", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 9))
        actions = tk.Frame(quick, bg=BG)
        actions.pack(anchor="w")
        self._button(actions, "+ Add student", lambda: self.student_dialog(refresh=self._refresh_current_page)).pack(side="left", padx=(0, 8))
        self._button(actions, "+ Add activity", lambda: self.activity_dialog(refresh=self._refresh_current_page)).pack(side="left", padx=8)
        self._button(actions, "+ Register participation", lambda: self.participation_dialog(refresh=self._refresh_current_page), kind="secondary").pack(side="left", padx=8)

    def _refresh_current_page(self):
        self.show_page(self.current_page)

    def _students_page(self):
        toolbar = tk.Frame(self.page_body, bg=BG)
        toolbar.pack(fill="x", pady=(0, 12))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=search_var, width=30)
        search_entry.pack(side="left", ipady=3)
        search_entry.insert(0, "")
        year_var = tk.StringVar(value="All Years")
        year_box = ttk.Combobox(toolbar, textvariable=year_var, values=YEAR_OPTIONS,
                                state="readonly", width=14)
        year_box.pack(side="left", padx=9)
        self._button(toolbar, "Search / Filter", lambda: refresh()).pack(side="left")
        self._button(toolbar, "+ Add Student", lambda: self.student_dialog(refresh=refresh)).pack(side="right")
        self._button(toolbar, "Delete", lambda: delete_selected(), kind="danger").pack(side="right", padx=(0, 8))
        self._button(toolbar, "Edit", lambda: edit_selected(), kind="secondary").pack(side="right", padx=(0, 8))

        box = self._section(self.page_body, "Student directory")
        box.pack(fill="both", expand=True)
        tree = self._make_tree(box, ("roll", "name", "department", "year", "email"),
                               ("ROLL NUMBER", "STUDENT NAME", "DEPARTMENT", "YEAR", "EMAIL"),
                               [130, 210, 140, 110, 230], height=13)

        def refresh(*_):
            for row in tree.get_children(): tree.delete(row)
            term = search_var.get().strip()
            selected_year = YEAR_TO_VALUE[year_var.get()]
            sql = "SELECT * FROM students WHERE (roll_no LIKE ? OR name LIKE ? OR department LIKE ?)"
            params = [f"%{term}%", f"%{term}%", f"%{term}%"]
            if selected_year:
                sql += " AND year=?"
                params.append(selected_year)
            sql += " ORDER BY year, name"
            with db_connect() as conn:
                rows = conn.execute(sql, params).fetchall()
            for row in rows:
                tree.insert("", "end", iid=str(row["id"]), values=(row["roll_no"], row["name"], row["department"], YEARS[row["year"]], row["email"]))

        def selected_id():
            selection = tree.selection()
            if not selection:
                messagebox.showinfo("Select a student", "Please select a student row first.", parent=self)
                return None
            return int(selection[0])

        def edit_selected():
            sid = selected_id()
            if sid is not None: self.student_dialog(sid, refresh)

        def delete_selected():
            sid = selected_id()
            if sid is None: return
            if messagebox.askyesno("Delete student", "Delete this student and their participation records?", parent=self):
                with db_connect() as conn: conn.execute("DELETE FROM students WHERE id=?", (sid,))
                refresh()
                messagebox.showinfo("Deleted", "Student record deleted.", parent=self)

        search_entry.bind("<Return>", refresh)
        year_box.bind("<<ComboboxSelected>>", refresh)
        tree.bind("<Double-1>", lambda _e: edit_selected())
        refresh()

    def _activities_page(self):
        toolbar = tk.Frame(self.page_body, bg=BG)
        toolbar.pack(fill="x", pady=(0, 12))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=search_var, width=32)
        search_entry.pack(side="left", ipady=3)
        year_var = tk.StringVar(value="All Years")
        year_box = ttk.Combobox(toolbar, textvariable=year_var, values=YEAR_OPTIONS,
                                state="readonly", width=14)
        year_box.pack(side="left", padx=9)
        self._button(toolbar, "Search / Filter", lambda: refresh()).pack(side="left")
        self._button(toolbar, "+ Add Activity", lambda: self.activity_dialog(refresh=refresh)).pack(side="right")
        self._button(toolbar, "Delete", lambda: delete_selected(), kind="danger").pack(side="right", padx=(0, 8))
        self._button(toolbar, "Edit", lambda: edit_selected(), kind="secondary").pack(side="right", padx=(0, 8))

        box = self._section(self.page_body, "Activity calendar")
        box.pack(fill="both", expand=True)
        tree = self._make_tree(box, ("title", "category", "date", "scope", "venue", "description"),
                               ("ACTIVITY", "CATEGORY", "DATE", "FOR YEAR", "VENUE", "DESCRIPTION"),
                               [190, 130, 110, 110, 150, 230], height=13)

        def refresh(*_):
            for row in tree.get_children(): tree.delete(row)
            term = search_var.get().strip()
            target = YEAR_TO_VALUE[year_var.get()]
            sql = "SELECT * FROM activities WHERE (title LIKE ? OR category LIKE ? OR venue LIKE ?)"
            params = [f"%{term}%", f"%{term}%", f"%{term}%"]
            if target:
                sql += " AND (target_year=0 OR target_year=?)"
                params.append(target)
            sql += " ORDER BY activity_date DESC, id DESC"
            with db_connect() as conn: rows = conn.execute(sql, params).fetchall()
            for row in rows:
                scope = YEARS.get(row["target_year"], "All Years") if row["target_year"] else "All Years"
                tree.insert("", "end", iid=str(row["id"]), values=(row["title"], row["category"], row["activity_date"], scope, row["venue"], row["description"]))

        def selected_id():
            selection = tree.selection()
            if not selection:
                messagebox.showinfo("Select an activity", "Please select an activity row first.", parent=self)
                return None
            return int(selection[0])

        def edit_selected():
            aid = selected_id()
            if aid is not None: self.activity_dialog(aid, refresh)

        def delete_selected():
            aid = selected_id()
            if aid is None: return
            if messagebox.askyesno("Delete activity", "Delete this activity and its participation records?", parent=self):
                with db_connect() as conn: conn.execute("DELETE FROM activities WHERE id=?", (aid,))
                refresh()
                messagebox.showinfo("Deleted", "Activity deleted.", parent=self)

        search_entry.bind("<Return>", refresh)
        year_box.bind("<<ComboboxSelected>>", refresh)
        tree.bind("<Double-1>", lambda _e: edit_selected())
        refresh()

    def _participation_page(self):
        toolbar = tk.Frame(self.page_body, bg=BG)
        toolbar.pack(fill="x", pady=(0, 12))
        year_var = tk.StringVar(value="All Years")
        year_box = ttk.Combobox(toolbar, textvariable=year_var, values=YEAR_OPTIONS,
                                state="readonly", width=14)
        year_box.pack(side="left")
        status_var = tk.StringVar(value="All Statuses")
        status_box = ttk.Combobox(toolbar, textvariable=status_var,
                                  values=["All Statuses"] + STATUSES,
                                  state="readonly", width=16)
        status_box.pack(side="left", padx=9)
        self._button(toolbar, "Filter", lambda: refresh()).pack(side="left")
        self._button(toolbar, "+ Register Student", lambda: self.participation_dialog(refresh=refresh)).pack(side="right")
        self._button(toolbar, "Delete", lambda: delete_selected(), kind="danger").pack(side="right", padx=(0, 8))
        self._button(toolbar, "Mark Completed", lambda: mark_completed(), kind="success").pack(side="right", padx=(0, 8))

        box = self._section(self.page_body, "Participation records")
        box.pack(fill="both", expand=True)
        tree = self._make_tree(box, ("roll", "student", "year", "activity", "date", "status", "achievement"),
                               ("ROLL NO.", "STUDENT", "YEAR", "ACTIVITY", "DATE", "STATUS", "ACHIEVEMENT"),
                               [100, 160, 95, 190, 105, 115, 180], height=13)

        def refresh(*_):
            for row in tree.get_children(): tree.delete(row)
            year = YEAR_TO_VALUE[year_var.get()]
            status = status_var.get()
            sql = """SELECT p.id, s.roll_no, s.name, s.year, a.title, a.activity_date,
                            p.status, p.achievement
                     FROM participation p JOIN students s ON s.id=p.student_id
                     JOIN activities a ON a.id=p.activity_id WHERE 1=1"""
            params = []
            if year:
                sql += " AND s.year=?"; params.append(year)
            if status != "All Statuses":
                sql += " AND p.status=?"; params.append(status)
            sql += " ORDER BY a.activity_date DESC, s.year, s.name"
            with db_connect() as conn: rows = conn.execute(sql, params).fetchall()
            for row in rows:
                tree.insert("", "end", iid=str(row["id"]), values=(row["roll_no"], row["name"], YEARS[row["year"]], row["title"], row["activity_date"], row["status"], row["achievement"]))

        def selected_id():
            selection = tree.selection()
            if not selection:
                messagebox.showinfo("Select a record", "Please select a participation record first.", parent=self)
                return None
            return int(selection[0])

        def mark_completed():
            pid = selected_id()
            if pid is None: return
            with db_connect() as conn:
                conn.execute("UPDATE participation SET status='Completed' WHERE id=?", (pid,))
            refresh()

        def delete_selected():
            pid = selected_id()
            if pid is None: return
            if messagebox.askyesno("Delete registration", "Delete this participation record?", parent=self):
                with db_connect() as conn: conn.execute("DELETE FROM participation WHERE id=?", (pid,))
                refresh()

        year_box.bind("<<ComboboxSelected>>", refresh)
        status_box.bind("<<ComboboxSelected>>", refresh)
        refresh()

    def _reports_page(self):
        with db_connect() as conn:
            year_data = []
            for year, label in YEARS.items():
                student_count = conn.execute("SELECT COUNT(*) FROM students WHERE year=?", (year,)).fetchone()[0]
                reg_count = conn.execute("""SELECT COUNT(*) FROM participation p JOIN students s ON s.id=p.student_id
                                            WHERE s.year=?""", (year,)).fetchone()[0]
                completed = conn.execute("""SELECT COUNT(*) FROM participation p JOIN students s ON s.id=p.student_id
                                           WHERE s.year=? AND p.status='Completed'""", (year,)).fetchone()[0]
                year_data.append((label, student_count, reg_count, completed))
            category_data = conn.execute("""SELECT category, COUNT(*) AS total FROM activities
                                            GROUP BY category ORDER BY total DESC, category""").fetchall()

        top = tk.Frame(self.page_body, bg=BG)
        top.pack(fill="x", pady=(0, 14))
        note = tk.Frame(top, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        note.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(note, text="Year-wise summary", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=17, pady=(15, 5))
        tk.Label(note, text="Compare student counts and recorded participation by year.",
                 bg=WHITE, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=17, pady=(0, 12))
        self._button(top, "Export participation CSV", self.export_participation_csv).pack(side="right", padx=(8, 0), pady=12, anchor="n")

        year_box = self._section(self.page_body, "Academic year performance")
        year_box.pack(fill="x", pady=(0, 14))
        tree = self._make_tree(year_box, ("year", "students", "registrations", "completed"),
                               ("ACADEMIC YEAR", "STUDENTS", "PARTICIPATION RECORDS", "COMPLETED"),
                               [220, 150, 230, 180], height=4)
        for row in year_data:
            tree.insert("", "end", values=row)

        category_box = self._section(self.page_body, "Activities by category")
        category_box.pack(fill="both", expand=True)
        cat_tree = self._make_tree(category_box, ("category", "count"),
                                   ("CATEGORY", "NUMBER OF ACTIVITIES"), [300, 220], height=6)
        if not category_data:
            cat_tree.insert("", "end", values=("No activities yet", 0))
        else:
            for row in category_data:
                cat_tree.insert("", "end", values=(row["category"], row["total"]))

    def student_dialog(self, student_id=None, refresh=None):
        is_edit = student_id is not None
        existing = None
        if is_edit:
            with db_connect() as conn:
                existing = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
            if not existing:
                messagebox.showerror("Not found", "This student record no longer exists.", parent=self)
                return

        win = tk.Toplevel(self)
        win.title("Edit Student" if is_edit else "Add Student")
        win.configure(bg=WHITE)
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        outer = tk.Frame(win, bg=WHITE, padx=25, pady=22)
        outer.pack(fill="both", expand=True)
        tk.Label(outer, text="Edit student details" if is_edit else "Add a student",
                 bg=WHITE, fg=TEXT, font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        tk.Label(outer, text="Fields marked with * are required.", bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9)).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 16))
        values = {
            "Roll number *": existing["roll_no"] if existing else "",
            "Student name *": existing["name"] if existing else "",
            "Department *": existing["department"] if existing else "CSE",
            "Email": existing["email"] if existing else "",
        }
        entries = {}
        row_num = 2
        for label, value in values.items():
            tk.Label(outer, text=label, bg=WHITE, fg="#4B586B",
                     font=("Segoe UI", 9, "bold")).grid(row=row_num, column=0, sticky="w", pady=6, padx=(0, 18))
            entry = ttk.Entry(outer, width=34)
            entry.grid(row=row_num, column=1, sticky="ew", pady=6)
            entry.insert(0, value)
            entries[label] = entry
            row_num += 1
        tk.Label(outer, text="Academic year *", bg=WHITE, fg="#4B586B",
                 font=("Segoe UI", 9, "bold")).grid(row=row_num, column=0, sticky="w", pady=6, padx=(0, 18))
        year_var = tk.StringVar(value=YEARS[existing["year"]] if existing else "1st Year")
        ttk.Combobox(outer, textvariable=year_var, values=list(YEARS.values()),
                     state="readonly", width=31).grid(row=row_num, column=1, sticky="ew", pady=6)
        row_num += 1

        def save():
            roll = entries["Roll number *"].get().strip()
            name = entries["Student name *"].get().strip()
            dept = entries["Department *"].get().strip()
            email = entries["Email"].get().strip()
            if not roll or not name or not dept:
                messagebox.showwarning("Required fields", "Roll number, name and department are required.", parent=win)
                return
            year = YEAR_TO_VALUE[year_var.get()]
            try:
                with db_connect() as conn:
                    if is_edit:
                        conn.execute("""UPDATE students SET roll_no=?, name=?, department=?, year=?, email=?
                                        WHERE id=?""", (roll, name, dept, year, email, student_id))
                    else:
                        conn.execute("""INSERT INTO students(roll_no, name, department, year, email)
                                        VALUES (?, ?, ?, ?, ?)""", (roll, name, dept, year, email))
            except sqlite3.IntegrityError:
                messagebox.showerror("Could not save", "That roll number already exists or the data is invalid.", parent=win)
                return
            win.destroy()
            if refresh: refresh()

        buttons = tk.Frame(outer, bg=WHITE)
        buttons.grid(row=row_num, column=0, columnspan=2, sticky="e", pady=(18, 0))
        self._button(buttons, "Cancel", win.destroy, kind="secondary", compact=False).pack(side="right", padx=(8, 0))
        self._button(buttons, "Save Student", save, compact=False).pack(side="right")
        win.update_idletasks()
        self._center_window(win)

    def activity_dialog(self, activity_id=None, refresh=None):
        is_edit = activity_id is not None
        existing = None
        if is_edit:
            with db_connect() as conn:
                existing = conn.execute("SELECT * FROM activities WHERE id=?", (activity_id,)).fetchone()
            if not existing:
                messagebox.showerror("Not found", "This activity no longer exists.", parent=self)
                return
        win = tk.Toplevel(self)
        win.title("Edit Activity" if is_edit else "Add Activity")
        win.configure(bg=WHITE)
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        outer = tk.Frame(win, bg=WHITE, padx=25, pady=22)
        outer.pack(fill="both", expand=True)
        tk.Label(outer, text="Edit activity" if is_edit else "Create an activity",
                 bg=WHITE, fg=TEXT, font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 17))
        fields = [
            ("Activity title *", existing["title"] if existing else ""),
            ("Date (YYYY-MM-DD) *", existing["activity_date"] if existing else str(date.today())),
            ("Venue", existing["venue"] if existing else ""),
        ]
        entries = {}
        r = 1
        for label, val in fields:
            tk.Label(outer, text=label, bg=WHITE, fg="#4B586B", font=("Segoe UI", 9, "bold")).grid(row=r, column=0, sticky="w", pady=6, padx=(0, 18))
            entry = ttk.Entry(outer, width=38)
            entry.grid(row=r, column=1, sticky="ew", pady=6)
            entry.insert(0, val)
            entries[label] = entry
            r += 1
        tk.Label(outer, text="Category *", bg=WHITE, fg="#4B586B", font=("Segoe UI", 9, "bold")).grid(row=r, column=0, sticky="w", pady=6, padx=(0, 18))
        category_var = tk.StringVar(value=existing["category"] if existing else CATEGORIES[0])
        ttk.Combobox(outer, textvariable=category_var, values=CATEGORIES, state="readonly", width=35).grid(row=r, column=1, sticky="ew", pady=6)
        r += 1
        tk.Label(outer, text="Target year", bg=WHITE, fg="#4B586B", font=("Segoe UI", 9, "bold")).grid(row=r, column=0, sticky="w", pady=6, padx=(0, 18))
        scope_var = tk.StringVar(value=YEARS.get(existing["target_year"], "All Years") if existing and existing["target_year"] else "All Years")
        ttk.Combobox(outer, textvariable=scope_var, values=YEAR_OPTIONS, state="readonly", width=35).grid(row=r, column=1, sticky="ew", pady=6)
        r += 1
        tk.Label(outer, text="Description", bg=WHITE, fg="#4B586B", font=("Segoe UI", 9, "bold")).grid(row=r, column=0, sticky="nw", pady=6, padx=(0, 18))
        description = tk.Text(outer, width=38, height=4, wrap="word", font=("Segoe UI", 10), relief="solid", bd=1, highlightthickness=0)
        description.grid(row=r, column=1, sticky="ew", pady=6)
        if existing: description.insert("1.0", existing["description"] or "")
        r += 1

        def save():
            title = entries["Activity title *"].get().strip()
            activity_day = entries["Date (YYYY-MM-DD) *"].get().strip()
            venue = entries["Venue"].get().strip()
            try:
                date.fromisoformat(activity_day)
            except ValueError:
                messagebox.showwarning("Invalid date", "Enter the date in YYYY-MM-DD format.", parent=win)
                return
            if not title:
                messagebox.showwarning("Required field", "Activity title is required.", parent=win)
                return
            category = category_var.get()
            target_year = YEAR_TO_VALUE[scope_var.get()]
            desc = description.get("1.0", "end").strip()
            with db_connect() as conn:
                if is_edit:
                    conn.execute("""UPDATE activities SET title=?, category=?, activity_date=?, venue=?,
                                    description=?, target_year=? WHERE id=?""",
                                 (title, category, activity_day, venue, desc, target_year, activity_id))
                else:
                    conn.execute("""INSERT INTO activities(title, category, activity_date, venue, description, target_year)
                                    VALUES (?, ?, ?, ?, ?, ?)""",
                                 (title, category, activity_day, venue, desc, target_year))
            win.destroy()
            if refresh: refresh()

        buttons = tk.Frame(outer, bg=WHITE)
        buttons.grid(row=r, column=0, columnspan=2, sticky="e", pady=(16, 0))
        self._button(buttons, "Cancel", win.destroy, kind="secondary").pack(side="right", padx=(8, 0))
        self._button(buttons, "Save Activity", save).pack(side="right")
        win.update_idletasks()
        self._center_window(win)

    def participation_dialog(self, refresh=None):
        with db_connect() as conn:
            students = conn.execute("SELECT id, roll_no, name, year FROM students ORDER BY year, name").fetchall()
            activities = conn.execute("SELECT id, title, activity_date, target_year FROM activities ORDER BY activity_date DESC, title").fetchall()
        if not students:
            messagebox.showinfo("No students", "Add a student before registering participation.", parent=self)
            return
        if not activities:
            messagebox.showinfo("No activities", "Add an activity before registering participation.", parent=self)
            return

        win = tk.Toplevel(self)
        win.title("Register Participation")
        win.configure(bg=WHITE)
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        outer = tk.Frame(win, bg=WHITE, padx=25, pady=22)
        outer.pack(fill="both", expand=True)
        tk.Label(outer, text="Register student participation", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 17))
        student_labels = [f'{s["id"]} | {s["roll_no"]} | {s["name"]} | {YEARS[s["year"]]}' for s in students]
        student_by_label = {label: s for label, s in zip(student_labels, students)}
        activity_labels = [f'{a["id"]} | {a["title"]} | {a["activity_date"]}' for a in activities]
        activity_by_label = {label: a for label, a in zip(activity_labels, activities)}

        def add_field(label, row, widget):
            tk.Label(outer, text=label, bg=WHITE, fg="#4B586B", font=("Segoe UI", 9, "bold")).grid(row=row, column=0, sticky="w", pady=8, padx=(0, 18))
            widget.grid(row=row, column=1, sticky="ew", pady=8)

        student_var = tk.StringVar(value=student_labels[0])
        student_box = ttk.Combobox(outer, textvariable=student_var, values=student_labels, state="readonly", width=43)
        add_field("Student *", 1, student_box)
        activity_var = tk.StringVar()
        activity_box = ttk.Combobox(outer, textvariable=activity_var, values=activity_labels, state="readonly", width=43)
        add_field("Activity *", 2, activity_box)
        status_var = tk.StringVar(value="Registered")
        status_box = ttk.Combobox(outer, textvariable=status_var, values=STATUSES, state="readonly", width=40)
        add_field("Status", 3, status_box)
        tk.Label(outer, text="Achievement / notes", bg=WHITE, fg="#4B586B", font=("Segoe UI", 9, "bold")).grid(row=4, column=0, sticky="nw", pady=8, padx=(0, 18))
        achievement = tk.Text(outer, width=43, height=3, wrap="word", font=("Segoe UI", 10), relief="solid", bd=1, highlightthickness=0)
        achievement.grid(row=4, column=1, sticky="ew", pady=8)
        hint = tk.Label(outer, text="Choose a student to see activities open to their year.", bg=WHITE, fg=MUTED, font=("Segoe UI", 8))
        hint.grid(row=5, column=1, sticky="w")

        def update_activity_options(*_):
            selected = student_by_label.get(student_var.get())
            if not selected: return
            year = selected["year"]
            eligible = [a for a in activities if a["target_year"] == 0 or a["target_year"] == year]
            labels = [label for label, a in activity_by_label.items() if a in eligible]
            activity_box.configure(values=labels)
            if activity_var.get() not in labels:
                activity_var.set(labels[0] if labels else "")
            hint.configure(text=f"{YEARS[year]} student · {len(labels)} eligible activities")

        student_box.bind("<<ComboboxSelected>>", update_activity_options)
        update_activity_options()

        def save():
            student = student_by_label.get(student_var.get())
            activity = activity_by_label.get(activity_var.get())
            if not student or not activity:
                messagebox.showwarning("Choose records", "Select a valid student and activity.", parent=win)
                return
            if activity["target_year"] not in (0, student["year"]):
                messagebox.showwarning("Year mismatch", "This activity is not assigned to the student's year.", parent=win)
                return
            try:
                with db_connect() as conn:
                    conn.execute("INSERT INTO participation(student_id, activity_id, status, achievement) VALUES (?, ?, ?, ?)",
                                 (student["id"], activity["id"], status_var.get(), achievement.get("1.0", "end").strip()))
            except sqlite3.IntegrityError:
                messagebox.showerror("Already registered", "This student is already registered for that activity.", parent=win)
                return
            win.destroy()
            if refresh: refresh()

        buttons = tk.Frame(outer, bg=WHITE)
        buttons.grid(row=6, column=0, columnspan=2, sticky="e", pady=(16, 0))
        self._button(buttons, "Cancel", win.destroy, kind="secondary").pack(side="right", padx=(8, 0))
        self._button(buttons, "Save Registration", save).pack(side="right")
        win.update_idletasks()
        self._center_window(win)

    def export_participation_csv(self):
        path = filedialog.asksaveasfilename(
            parent=self, title="Export participation report", defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")], initialfile="student_participation_report.csv"
        )
        if not path: return
        with db_connect() as conn:
            rows = conn.execute("""SELECT s.roll_no, s.name, s.department, s.year,
                                  a.title, a.category, a.activity_date, p.status, p.achievement
                                  FROM participation p JOIN students s ON s.id=p.student_id
                                  JOIN activities a ON a.id=p.activity_id
                                  ORDER BY s.year, s.name, a.activity_date""").fetchall()
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(["Roll Number", "Student Name", "Department", "Year",
                                 "Activity", "Category", "Activity Date", "Status", "Achievement"])
                for r in rows:
                    writer.writerow([r["roll_no"], r["name"], r["department"], YEARS[r["year"]],
                                     r["title"], r["category"], r["activity_date"], r["status"], r["achievement"]])
            messagebox.showinfo("Export complete", f"CSV report saved to:\n{path}", parent=self)
        except OSError as error:
            messagebox.showerror("Export failed", str(error), parent=self)

    def _center_window(self, win):
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = self.winfo_rootx() + (self.winfo_width() - width) // 2
        y = self.winfo_rooty() + (self.winfo_height() - height) // 2
        win.geometry(f"+{max(0, x)}+{max(0, y)}")


if __name__ == "__main__":
    initialize_database()
    app = StudentActivitiesApp()
    app.mainloop()

