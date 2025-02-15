from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QWidget,
    QLabel,
    QGroupBox,
    QVBoxLayout,
    QStyleFactory,
    QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate
from PySide6.QtGui import QFont, QPalette, QColor
import sys
from pathlib import Path
from main_window import Window
from minicalendar import Minicalendar
from calendar_widget import Calendar
from datetime import datetime
import sqlite3 as sql

# Login class will be called by app.py


class Login(QMainWindow):
    # conn will stand for the DB connection
    def __init__(self, conn):
        super().__init__()
        self.setFixedSize(300, 300)
        self.setWindowTitle("Mandarina – Task Manager")
        self.main = None
        self.conn = conn
        self.cur = self.conn.cursor()

        self._render_login()

    def _render_login(self):
        if self.main:
            self.layout().removeWidget(self.main)
            self.main.deleteLater()

        self.main = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Welcome back to Mandarina! Your trustful Task Manager")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)

        new_user = QPushButton("New User? Register")
        new_user.clicked.connect(self._render_registration)
        layout.addWidget(new_user)

        form = QGroupBox()
        form_layout = QFormLayout()

        self.username = QLineEdit()
        form_layout.addRow("Username:", self.username)

        self.passwd = QLineEdit()
        self.passwd.setEchoMode(QLineEdit.Password)
        self.passwd.returnPressed.connect(self.login)
        form_layout.addRow("Password:", self.passwd)

        form.setLayout(form_layout)
        layout.addWidget(form)

        login = QPushButton("Log in!")
        login.clicked.connect(self.login)
        login.setFixedWidth(100)
        layout.addWidget(login, alignment=Qt.AlignmentFlag.AlignRight)
        self.main.setLayout(layout)

        self.setCentralWidget(self.main)

    def _render_registration(self):
        if self.main:
            self.layout().removeWidget(self.main)
            self.main.deleteLater()

        self.main = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Welcome to Mandarina! Fill the following to start.")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self._render_login)
        layout.addWidget(cancel)

        form = QGroupBox()
        form_layout = QFormLayout()

        self.username = QLineEdit()
        form_layout.addRow("Username:", self.username)

        self.passwd = QLineEdit()
        self.passwd.setEchoMode(QLineEdit.Password)
        self.passwd.returnPressed.connect(self.login)
        form_layout.addRow("Password:", self.passwd)

        form.setLayout(form_layout)
        layout.addWidget(form)

        register = QPushButton("Register!")
        register.setFixedWidth(100)
        layout.addWidget(register, alignment=Qt.AlignmentFlag.AlignRight)
        register.clicked.connect(self._register_new_user)
        layout.addWidget(register)
        self.main.setLayout(layout)

        self.setCentralWidget(self.main)

    def _register_new_user(self):
        # getting data from windows
        username = self.username.text()
        password = self.passwd.text()

        if username == "" or password == "":
            QMessageBox.warning(
                self, "Mandarina 🍊 says: Wait!", "All fields are required")
            return

        query = f"SELECT password FROM user WHERE username = '{username}'"
        self.cur.execute(query)
        result = self.cur.fetchone()
        if result:
            QMessageBox.warning(
                self, "Mandarina 🍊 says: Uh-oh!", "Username already exists")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "Mandarina 🍊 says: Uh-oh!",
                                "Password must contain at least 8 characters.")
            return

        insertion = f"INSERT INTO user (username, password) VALUES ('{username}', '{password}')"
        self.cur.execute(insertion)
        self.conn.commit()
        self.login()

    def login(self):
        username = self.username.text()
        password = self.passwd.text()

        if username == "" or password == "":
            QMessageBox.warning(
                self, "Mandarina 🍊 says: Wait!", "All fields are required")
            return

        query = f"SELECT user_id, password FROM user WHERE username = '{username}'"
        self.cur.execute(query)
        info = self.cur.fetchone()

        if not info:
            QMessageBox.warning(
                self, "Mandarina 🍊 says: Wait!", "Invalid credentials. Make sure you are registered.")
            return

        # This must be replaced with an if
        if password == info[1]:
            win = Window(self.conn, info[0])
            win.show()
            self.close()
        else:
            QMessageBox.warning(self, "Mandarina 🍊 says:Uh-oh!",
                                "Something went wrong! 😟\nPlease check your username and password.")
