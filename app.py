from PySide6.QtWidgets import (
    QApplication,
    QDateEdit,
    QMainWindow,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QFormLayout,
    QTextEdit,
    QTimeEdit,
    QWidget,
    QLabel,
    QComboBox,
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QButtonGroup,
    QDialogButtonBox,
    QStyleFactory,
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate
from PySide6.QtGui import QFont, QPalette, QColor
import sys
import os
import string
from pathlib import Path
from calendar_widget import Calendar
from calendar import Calendar as Cal
from datetime import datetime
import sqlite3 as sql

PALETTES = {
    "Mandarina": {
        "bg": "#ffffff",
        "fg": "#394d46",
        "accent": "#ff8f1f",
        "sec_accent": "#1fc271",
    },
    "Lavender Haze": {
        "bg": "#fffbff",
        "fg": "#4a3b66",
        "accent": "#a401e7",
        "sec_accent": "#D099E2",
    },
    "Cherry Blossom": {
        "bg": "#fff6f8",
        "fg": "#6d303b",
        "accent": "#d20a2e",
        "sec_accent": "#2c8049",
    },
    "Blueberry Sparks":  {
        "bg": "#eeecf9",
        "fg": "#4a4561",
        "accent": "#5f48c8",
        "sec_accent": "#4ea771",
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

    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 700)

        self.day = datetime.today().day
        self.month = datetime.today().month
        self.year = datetime.today().year
        self.cur_date = {
            "day": self.day,
            "month": self.month,
            "year": self.year
        }
        self.selected_palette = "Mandarina"

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

        # prev_btn = QPushButton("◀")
        # prev_btn.setFixedSize(50, 25)
        # prev_btn.clicked.connect(self._go_prev)
        # self.header_lay.addWidget(prev_btn)
        # next_btn = QPushButton("▶")
        # next_btn.setFixedSize(50, 25)
        # next_btn.clicked.connect(self._go_next)
        # self.header_lay.addWidget(next_btn)

        new_task = QPushButton("+")
        new_task.setFixedSize(40, 40)
        new_task.setObjectName("roundedBtn")
        self.header_lay.addWidget(new_task, Qt.AlignRight)

        self.header.setLayout(self.header_lay)
        self.left_lay.addWidget(self.header)

        self.calendar = Calendar()
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

        # def _go_next(self):
        #     max_day = 0
        #     for d in Cal().itermonthdays(self.cur_date["year"], self.cur_date["month"]):
        #         if d > max_day:
        #             max_day = d
        #     match self.calendar_views.currentText():
        #         case "day":
        #             self.cur_date["day"] += 1
        #         case "month":
        #             self._reset_current_date()
        #             self.cur_date["month"] += 1
        #     if self.cur_date["day"] >= max_day:
        #         self.cur_date["month"] += 1
        #         self.cur_date["day"] = 1
        #     if self.cur_date["month"] >= 12:
        #         self.cur_date["month"] = 1
        #         self.cur_date["year"] += 1
        #     self._render_view()

        # def _go_prev(self):
        #     match self.calendar_views.currentText():
        #         case "day":
        #             self.cur_date["day"] -= 1
        #         case "month":
        #             self.cur_date["month"] -= 1
        #     if self.cur_date["day"] <= 0:
        #         self.cur_date["month"] -= 1
        #         max_day = 0
        #         for d in Cal().itermonthdays(self.cur_date["year"], self.cur_date["month"]):
        #             if d > max_day:
        #                 max_day = d
        #         self.cur_date["day"] = max_day
        #     if self.cur_date["month"] <= 0:
        #         self.cur_date["month"] = 12
        #         self.cur_date["year"] -= 1
        #     self._render_view()

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
        else:
            self._render_side_panel()

    def _render_settings_panel(self):
        panel = QWidget()
        panel.setObjectName("panel")
        panel.setFixedWidth(270)
        layout = QVBoxLayout()

        self.button_group = QButtonGroup(panel)  # Group radio buttons

        for name, colors in PALETTES.items():
            container = QGroupBox()
            container.setFixedHeight(100)
            container_lay = QVBoxLayout()

            # Radio button to select the palette
            radio = QRadioButton()
            radio.setText(name)
            # Default selection
            # radio.setChecked(palette_name == self.selected_palette)
            radio.toggled.connect(
                self._on_palette_selected)  # Connect signal
            self.button_group.addButton(radio)  # Add to button group
            container_lay.addWidget(radio)

            color_container = QWidget()
            color_container.setLayout(QHBoxLayout())
            # Color preview
            for attr, clr in colors.items():
                color = QLabel()
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
            layout.addWidget(container, Qt.AlignmentFlag.AlignTop)

        # Apply button
        apply = QPushButton("Apply Changes")
        apply.setFixedSize(120, 30)
        apply.clicked.connect(self._apply_changes)  # Connect apply button
        layout.addWidget(apply, Qt.AlignRight)

        panel.setLayout(layout)
        self.right_lay.addWidget(panel)

    def _on_palette_selected(self):
        # Get the selected button's text (palette name)
        selected_button = self.button_group.checkedButton()
        if selected_button:
            self.selected_palette = selected_button.text()

    def _apply_changes(self):
        if self.selected_palette not in PALETTES:
            return

        palette = PALETTES[self.selected_palette]
        with open("light_theme.qss", "r") as file:
            qss_template = string.Template(file.read())

        qss = qss_template.safe_substitute(palette)

        # Apply the stylesheet
        app.setStyleSheet(qss)

    def _render_side_panel(self):
        panel = QWidget()
        panel.setObjectName("panel")
        panel.setFixedWidth(270)
        layout = QVBoxLayout()

        hdr = QLabel("Scheduled Today")
        hdr.setObjectName("secondary")
        layout.addWidget(hdr)

        scheduled_tasks = QScrollArea()
        scheduled_tasks.setObjectName("sched_today")
        container = QWidget()
        # logic for showing tasks
        scheduled_tasks.setWidget(container)

        layout.addWidget(scheduled_tasks)

        panel.setLayout(layout)
        self.right_lay.addWidget(panel)


app = QApplication()
app.setStyle(QStyleFactory.create("Fusion"))
win = Window()
win.show()
app.exec()
