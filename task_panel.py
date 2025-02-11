from curses.ascii import isalnum
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
    QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate
from PySide6.QtGui import QFont, QPalette, QColor
from datetime import datetime
import sqlite3 as sql


class TaskPanel(QWidget):
    def __init__(self, owner, type, conn, uid):
        super().__init__()

        self.conn = conn
        self.cur = self.conn.cursor()
        self.owner = owner
        self.user_id = uid
        self.setLayout(QVBoxLayout())
        if type == "task insertion":
            self._render_insertion()

    def _render_insertion(self):
        container = QWidget()
        container_lay = QVBoxLayout()

        hdr = QLabel("Inserting Task")
        hdr.setObjectName("secondary")
        container_lay.addWidget(hdr)

        form = QGroupBox()
        form_lay = QFormLayout()

        self.title = QLineEdit()
        form_lay.addRow("Title", self.title)
        self.comment = QTextEdit()
        form_lay.addRow("Content", self.comment)
        self.date = QDateEdit()
        self.date.setDate(
            QDate(datetime.now().year,
                  datetime.now().month,
                  datetime.now().day)
        )
        form_lay.addRow("Date", self.date)
        self.time = QTimeEdit()
        form_lay.addRow("Time", self.time)
        self.priorities = QButtonGroup(form)
        btns = QWidget()
        btns.setLayout(QVBoxLayout())
        for p in ["Low", "Medium", "High"]:
            radio = QRadioButton()
            radio.setText(p)
            self.priorities.addButton(radio)
            radio.toggled.connect(self._on_priority_selected)
            btns.layout().addWidget(radio)
        form_lay.addRow("Priority", btns)
        form.setLayout(form_lay)
        container_lay.addWidget(form)

        footer = QWidget()
        footer_lay = QHBoxLayout()

        save = QPushButton("Save")
        save.setFixedWidth(80)
        save.clicked.connect(self._insert_task)
        footer_lay.addWidget(save, alignment=Qt.AlignmentFlag.AlignRight)

        cancel = QPushButton("Cancel")
        cancel.setFixedWidth(80)
        cancel.clicked.connect(lambda: self.owner._render_side_bar(" "))
        footer_lay.addWidget(cancel, alignment=Qt.AlignmentFlag.AlignRight)

        footer.setLayout(footer_lay)
        container_lay.addWidget(footer)

        container.setLayout(container_lay)
        self.layout().addWidget(container)

    def _on_priority_selected(self):
        selected_button = self.priorities.checkedButton()
        if selected_button:
            self.priority = selected_button.text()

    def _insert_task(self):
        if self.title.text() == "":
            QMessageBox.warning(self, "Mandarina 🍊 says: Wait!",
                                "Title cannot have an empty value.")
        if not self.title.text().isalnum() or not self.comment.toPlainText().isalnum:
            QMessageBox.warning(self, "Mandarina 🍊 says: Wait!",
                                "Title and content need alphanumeric characters.")

        title = self.title.text()
        content = self.comment.toPlainText()
        priority = self.priority
        deadline = self.date.date().toString("yyyy-MM-dd")
        hour = self.time.time().hour()
        minute = self.time.time().minute()

        query = f"""INSERT INTO task (task_name, content, priority, status, date, hour, minute, user_id)
                        VALUES (
                            '{title}', 
                            '{content}', 
                            '{priority}',
                            'Pending', 
                            '{deadline}',
                            '{hour}',
                            '{minute}',
                            {self.user_id}
                        );"""

        try:
            self.cur.execute(query)
            self.conn.commit()
        except sql.Error as e:
            print(e)
            QMessageBox.warning(self, "Mandarina 🍊 says: Wait!",
                                "Please provide accepted values.")
            return

        self.owner._render_side_bar("")
