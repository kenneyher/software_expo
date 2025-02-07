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
    QDialog,
    QDialogButtonBox,
    QStyleFactory,
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate
from PySide6.QtGui import QFont, QPalette, QColor
import sys
import os
from pathlib import Path
from calendar_widget import Calendar 
from calendar import Calendar as Cal
from datetime import datetime
import sqlite3 as sql


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 700)

        self.day = datetime.today().day
        self.month = datetime.today().month
        self.year = datetime.today().year

        # Set up main widget and layout
        self.main = QWidget()
        self.main_lay = QVBoxLayout()

        self.calendar_views = QComboBox()
        self.calendar_views.addItems(["day", "week", "month"])
        self.calendar_views.currentTextChanged.connect(self._render_view)
        self.main_lay.addWidget(self.calendar_views)

        self.calendar = Calendar()
        self.main_lay.addWidget(self.calendar)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(60000)

        self.main.setLayout(self.main_lay)
        self.setCentralWidget(self.main)

        with open("./light_theme.qss", "r") as file:
            self.setStyleSheet(file.read())

    def _render_view(self):
        match self.calendar_views.currentText():
            case "day":
                self.calendar.render_day_view(self.month, self.day, self.year)
            case "month":
                self.calendar.render_month_view(
                    self.month, self.day, self.year)
            case "week":
                self.calendar.render_week_view(self.month, self.day, self.year)

    def update_time(self):
        if self.day != datetime.today().day:
            self.day = datetime.today().day
        if self.month != datetime.today().month:
            self.month = datetime.today().month
        if self.year != datetime.today().year:
            self.year = datetime.today().year


app = QApplication()
app.setStyle(QStyleFactory.create("Fusion"))
win = Window()
win.show()
app.exec()
