from PySide6.QtWidgets import (
    QApplication,
    QStyleFactory,
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate
from PySide6.QtGui import QFont, QPalette, QColor
import os
import string
import json
from login import Login
from calendar import Calendar as Cal
from db_setup import connect, set_up_db
import sqlite3 as sql


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

# Ensuring datbase is set up
set_up_db()

# Stablishing connection with database
conn = connect()
cursor = conn.cursor()

# Define the path for the hidden directory and JSON file
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".mandarina")
# change to mandarina.json
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
config = None

# Default configuration
DEFAULT_CONFIG = {
    "palette": "Mandarina",
    "hour_format": 12,
    "theme": "light"
}

# Ensure the directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

# If the config file doesn't exist, create it with default values
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as file:
        json.dump(DEFAULT_CONFIG, file, indent=4)

# Load the existing configuration
with open(CONFIG_FILE, "r") as file:
    config = json.load(file)

app = QApplication()
theme_file = "dark_theme.qss" if config["theme"] == "dark" else "Light_theme.qss"
palette = PALETTES[config["palette"]]
with open(theme_file, "r") as file:
    # Use Template instead of format
    qss_template = string.Template(file.read())
qss = qss_template.safe_substitute(palette)
app.setStyleSheet(qss)
app.setStyle(QStyleFactory.create("Fusion"))
win = Login(conn)
win.show()
app.exec()
