from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QWidget,
    QLabel,
    QComboBox,
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QButtonGroup,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QDateEdit,
    QTimeEdit,
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate
from PySide6.QtGui import QGuiApplication
import sys
import os
import json
import string
from pathlib import Path
from minicalendar import Minicalendar
from task_panel import TaskPanel
from calendar_widget import Calendar
from calendar import Calendar as Cal
from datetime import datetime
from db_setup import connect, set_up_db
import sqlite3 as sql

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".mandarina")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
config = None
with open(CONFIG_FILE, "r") as file:
    config = json.load(file)

PALETTES = {
    "Mandarina": {
        "bg": "#ffffff",
        "fg": "#394d46",
        "dark_bg": "#2a292d",
        "dark_fg": "#8bb39a",
        "accent": "#ff8f1f",
        "sec_accent": "#1fc271",
    },
    "Olive Yards":  {
        "bg": "#DCD7C9",
        "fg": "#252220",
        "dark_bg": "#252220",
        "dark_fg": "#DCD7C9",
        "accent": "#5F6F52",
        "sec_accent": "#A27B5C",
    },
    "Peach Dreams": {
        "bg": "#fff0e1",
        "fg": "#8c6d88",
        "dark_bg": "#2b262c",
        "dark_fg": "#d3adce",
        "accent": "#f599a6",
        "sec_accent": "#9ab0a7",
    },
    "Eggplant Haze":  {
        "bg": "#FFF6E0",
        "fg": "#272829",
        "dark_bg": "#272829",
        "dark_fg": "#FFF6E0",
        "accent": "#727ea2",
        "sec_accent": "#8b949d",
    },
    "Coffee Espresso":  {
        "bg": "#F8F4E1",
        "fg": "#543310",
        "dark_bg": "#1e1b1a",
        "dark_fg": "#F8F4E1",
        "accent": "#74512D",
        "sec_accent": "#AF8F6F",
    },
    "Cherry Blossom": {
        "bg": "#ebe8de",
        "fg": "#6d303b",
        "dark_bg": "#2a2627",
        "dark_fg": "#92b6a4",
        "accent": "#ff405a",
        "sec_accent": "#1fb551",
    },
    "Blueberry Sparks":  {
        "bg": "#eeecf9",
        "fg": "#4a4561",
        "dark_bg": "#2d2b36",
        "dark_fg": "#bcb5d8",
        "accent": "#826fd7",
        "sec_accent": "#4ea771",
    },
    "Grape Fusion":  {
        "bg": "#f9feff",
        "fg": "#2D336B",
        "dark_bg": "#23242e",
        "dark_fg": "#f9feff",
        "accent": "#2a48d0",
        "sec_accent": "#7886C7",
    },
    "Lemon Aid":  {
        "bg": "#fffef8",
        "fg": "#6a705a",
        "dark_bg": "#222320",
        "dark_fg": "#fbfbf3",
        "accent": "#edd239",
        "sec_accent": "#acde31",
    }
}


class Window(QMainWindow):
    MONTHS = (
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    )

    def __init__(self, conn, uid):
        super().__init__()
        screen = QGuiApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        self.setGeometry(0, 0, screen_width * 0.9,
                         screen_height * 0.9)  # 80% of screen size

        self.conn = conn
        self.user_id = uid

        self.day = datetime.today().day
        self.month = datetime.today().month
        self.year = datetime.today().year
        self.cur_date = {
            "day": self.day,
            "month": self.month,
            "year": self.year
        }
        self.theme_toggle = None
        self.selected_palette = config["palette"]
        self.dark_mode = True if config["theme"] == "dark" else False
        # Set up main widget and layout
        self.main = QWidget()
        self.main_lay = QHBoxLayout()
        self.main_lay.setContentsMargins(-5, 5, -5, 5)

        self.letf_container = QWidget()
        self.left_lay = QVBoxLayout()
        self.left_lay.setContentsMargins(0, 5, 0, 5)

        self.header = QWidget()
        self.header.setFixedSize(680, 80)
        self.header_lay = QHBoxLayout()

        views_indicator = QLabel("View as")
        views_indicator.setFixedWidth(50)
        self.header_lay.addWidget(views_indicator, Qt.AlignLeft)

        self.calendar_views = QComboBox()
        self.calendar_views.setFixedWidth(80)
        self.calendar_views.addItems(["day", "week", "month"])
        self.calendar_views.currentTextChanged.connect(self._render_view)
        self.header_lay.addWidget(
            self.calendar_views, Qt.AlignLeft)

        self.month_txt = QLabel(
            f"{self.MONTHS[self.cur_date["month"]-1]} {self.cur_date["year"]}")
        self.month_txt.setObjectName("primary")
        self.month_txt.setContentsMargins(20, 0, 20, 0)
        self.header_lay.addWidget(self.month_txt)

        new_task = QPushButton("+")
        new_task.setFixedSize(40, 40)
        new_task.setObjectName("roundedBtn")
        new_task.clicked.connect(
            lambda: self._render_side_bar("task insertion"))
        self.header_lay.addWidget(new_task, Qt.AlignRight)

        self.header.setLayout(self.header_lay)
        self.left_lay.addWidget(self.header)

        self.calendar = Calendar(self.user_id, self.conn)
        self.left_lay.addWidget(self.calendar)

        footer = QWidget()
        footer.setFixedWidth(680)
        footer_lay = QHBoxLayout()

        settings = QPushButton("⚙")
        settings.setFixedWidth(50)
        settings.setObjectName("roundedBtn")
        settings.clicked.connect(lambda: self._render_side_bar("settings"))
        footer_lay.addWidget(settings, Qt.AlignRight)

        footer.setLayout(footer_lay)
        self.left_lay.addWidget(footer)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(60000)

        self.letf_container.setLayout(self.left_lay)
        self.main_lay.addWidget(self.letf_container)

        self.right_container = QGroupBox()
        self.right_container.setFixedWidth(285)
        self.right_lay = QVBoxLayout()

        self._render_side_bar("")

        self.right_container.setLayout(self.right_lay)
        self.main_lay.addWidget(self.right_container)

        self.main.setLayout(self.main_lay)
        self.setCentralWidget(self.main)

        self._apply_changes()

    def _render_view(self):
        match self.calendar_views.currentText():
            case "day":
                self.calendar.render_day_view(self.cur_date["month"],
                                              self.cur_date["day"],
                                              self.cur_date["year"])
            case "month":
                self.cur_date["day"] = datetime.today(
                ).day
                self.cur_date["month"] = datetime.today().month
                self.calendar.render_month_view(self.cur_date["month"],
                                                self.cur_date["day"],
                                                self.cur_date["year"])
            case "week":
                self.cur_date["day"] = datetime.today().day
                self.cur_date["month"] = datetime.today().month
                self.calendar.render_week_view(self.cur_date["month"],
                                               self.cur_date["day"],
                                               self.cur_date["year"])
        self.month_txt.setText(
            f"{self.MONTHS[self.cur_date["month"]-1]} {self.cur_date["year"]}")

    def update_time(self):
        if self.day != datetime.today().day:
            self.day = datetime.today().day
        if self.month != datetime.today().month:
            self.month = datetime.today().month
        if self.year != datetime.today().year:
            self.year = datetime.today().year

    def _reset_current_date(self):
        self.cur_date["day"] = datetime.today().day
        self.cur_date["month"] = datetime.today().month
        self.cur_date["year"] = self.year = datetime.today().year

    def _render_side_bar(self, sidebar_type):
        panel = self.right_container.findChild(QWidget, "panel")
        if panel:
            self.right_lay.removeWidget(panel)
            panel.deleteLater()
        if sidebar_type == "settings":
            self._render_settings_panel()
        elif "task" in sidebar_type:
            self._render_task(sidebar_type)
        else:
            self._render_side_panel()

    def _render_settings_panel(self):
        panel = QWidget()
        panel.setObjectName("panel")
        panel.setFixedWidth(270)
        layout = QVBoxLayout()

        scrollable = QScrollArea()
        scrollable.setFixedHeight(500)
        scroll_container = QWidget()
        scroll_container.setLayout(QVBoxLayout())
        self.themes = QButtonGroup(scroll_container)

        for name, colors in PALETTES.items():
            container = QGroupBox()
            container.setFixedSize(200, 100)
            container_lay = QVBoxLayout()

            # Radio button to select the palette
            radio = QRadioButton()
            radio.setText(name)
            # Default selection
            radio.setChecked(name == self.selected_palette)
            radio.toggled.connect(
                self._on_palette_selected)  # Connect signal
            self.themes.addButton(radio)  # Add to button group
            container_lay.addWidget(radio)

            color_container = QWidget()
            color_container.setLayout(QHBoxLayout())
            # Color preview
            for attr, clr in colors.items():
                color = QLabel()
                if "dark" in attr and not self.dark_mode:
                    continue
                if "dark" not in attr and self.dark_mode:
                    if attr == "fg" or attr == "bg":
                        continue

                color.setFixedSize(25, 25)
                color.setStyleSheet(f"""
                    background-color: {clr};
                    border: solid;
                    border-color: gray;
                    border-width: 1px;
                    border-radius: 5%;""")
                color_container.layout().addWidget(color)
            container_lay.addWidget(color_container)

            container.setLayout(container_lay)
            scroll_container.layout().addWidget(container, Qt.AlignmentFlag.AlignTop)
        scrollable.setWidget(scroll_container)
        layout.addWidget(scrollable)

        self.theme_toggle = QPushButton(
            "Dark Mode" if self.dark_mode else "Light Mode")  # Default to light mode
        self.theme_toggle.setCheckable(True)
        self.theme_toggle.setChecked(self.dark_mode)  # Default to light mode
        self.theme_toggle.clicked.connect(self._switch_theme)
        layout.addWidget(self.theme_toggle)

        btn_container = QWidget()
        btn_container.setLayout(QHBoxLayout())

        # Apply button
        apply = QPushButton("Apply")
        apply.setFixedSize(120, 30)
        apply.clicked.connect(self._apply_changes)  # Connect apply button
        btn_container.layout().addWidget(apply, Qt.AlignRight)

        apply = QPushButton("Cancel")
        apply.setFixedSize(80, 30)
        # Connect apply button
        apply.clicked.connect(lambda: self._render_side_bar(""))
        btn_container.layout().addWidget(apply, Qt.AlignRight)

        layout.addWidget(btn_container)
        panel.setLayout(layout)
        self.right_lay.addWidget(panel)

    def _switch_theme(self):
        self.dark_mode = self.theme_toggle.isChecked()
        self.theme_toggle.setText(
            "Dark Mode" if self.dark_mode else "Light Mode")

    def _on_palette_selected(self):
        # Get the selected button's text (palette name)
        selected_button = self.themes.checkedButton()
        if selected_button:
            self.selected_palette = selected_button.text()

    def _apply_changes(self):
        if self.selected_palette not in PALETTES:
            return

        palette = PALETTES[self.selected_palette]

        config["palette"] = self.selected_palette
        # Toggle between dark and light mode
        config["theme"] = "dark" if self.dark_mode else "light"

        # Load and apply the correct stylesheet
        theme_file = "dark_theme.qss" if self.dark_mode else "light_theme.qss"
        with open(theme_file, "r") as file:
            # Use Template instead of format
            qss_template = string.Template(file.read())

        qss = qss_template.safe_substitute(palette)
        self.setStyleSheet(qss)

        # Save updated theme to JSON
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)

        self._render_side_bar("")

    def _render_side_panel(self):
        panel = QWidget()
        panel.setContentsMargins(-20, 0, -20, 0)
        panel.setObjectName("panel")
        panel.setFixedWidth(270)
        layout = QVBoxLayout()

        date_hdr = QLabel(
            f"{self.MONTHS[self.cur_date['month']-1]} {self.cur_date['day']}")
        date_hdr.setObjectName("primary")
        layout.addWidget(date_hdr)

        hdr = QLabel("Scheduled Today")
        hdr.setObjectName("secondary")
        layout.addWidget(hdr)

        scheduled_tasks = QScrollArea()
        scheduled_tasks.setObjectName("sched_today")
        container = QWidget()
        # logic for showing tasks
        scheduled_tasks.setWidget(container)

        layout.addWidget(scheduled_tasks)

        self.mini_calendar = Minicalendar()
        layout.addWidget(self.mini_calendar)

        panel.setLayout(layout)
        self.right_lay.addWidget(panel)

    def _render_task(self, widget_type):
        panel = QWidget()
        panel.setContentsMargins(-20, 0, -20, 0)
        panel.setObjectName("panel")
        panel.setFixedWidth(270)
        layout = QVBoxLayout()

        if widget_type == "task insertion":
            layout.addWidget(
                TaskPanel(self, widget_type, self.conn, self.user_id))

        panel.setLayout(layout)
        self.right_lay.addWidget(panel)
