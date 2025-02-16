from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QWidget,
    QLabel,
    QSpacerItem,
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QButtonGroup,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QDateEdit,
    QTimeEdit,
    QMessageBox,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate
from PySide6.QtGui import QFont, QPalette, QColor
from datetime import datetime
import sqlite3 as sql


class TaskPanel(QWidget):
    def __init__(self, owner, type, conn, uid, task_id):
        super().__init__()

        self.conn = conn
        self.cur = self.conn.cursor()
        self.owner = owner
        self.user_id = uid
        self.lay = QVBoxLayout()
        self.setLayout(self.lay)
        if type == "task insertion":
            self._render_insertion()
        elif type == "task info":
            self._render_info(task_id)
        else:
            self._render_edit(task_id)

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
        cancel.clicked.connect(lambda: self.owner._render_side_bar(" ", 0))
        footer_lay.addWidget(cancel, alignment=Qt.AlignmentFlag.AlignRight)

        footer.setLayout(footer_lay)
        container_lay.addWidget(footer)

        container.setLayout(container_lay)
        self.lay.addWidget(container)

    def _render_info(self, id):
        query = f"""
            SELECT task_name, content, priority, 
                    status, date, hour, minute FROM task 
            WHERE id = {id};
        """
        self.cur.execute(query)
        info = self.cur.fetchone()

        (title, content, priority, status, date, hour, minute) = info

        container = QWidget()
        container.setObjectName("info")
        container.setFixedWidth(250)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        # Title
        t = QLabel(title)
        t.setFixedWidth(225)
        t.setWordWrap(True)
        t.setObjectName("primary")
        t.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addWidget(t, alignment=Qt.AlignTop)

        # Deadline
        deadline = QLabel(date)
        deadline.setWordWrap(True)
        deadline.setObjectName("secondary")
        deadline.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addWidget(deadline, alignment=Qt.AlignTop)

        # Content
        labels = [
            f"Content: {content}",
            f"Status: {status}",
            f"Hour: {hour:02d}:{minute:02d}",
            f"Priority: {priority}",
        ]

        for text in labels:
            label = QLabel(text)
            label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            label.setWordWrap(True)
            if "Priority" in text:
                label.setObjectName("accented")
            layout.addWidget(label, alignment=Qt.AlignTop)

        btns = QWidget()
        btns_layout = QHBoxLayout()

        cancel = QPushButton("Go Back")
        cancel.setFixedWidth(80)
        cancel.clicked.connect(lambda: self.owner._render_side_bar("", 0))
        btns_layout.addWidget(cancel)

        edit = QPushButton("✎")
        edit.clicked.connect(
            lambda: self.owner._render_side_bar("task edit", id))
        edit.setFixedWidth(50)
        btns_layout.addWidget(edit)

        delete = QPushButton("⌫")
        delete.setFixedWidth(25)
        delete.clicked.connect(lambda: self._delete(id))
        btns_layout.addWidget(delete)

        completed = QPushButton("✓")
        completed.setFixedWidth(25)
        completed.clicked.connect(lambda: self._mark_as_complete(id))
        btns_layout.addWidget(completed)

        btns.setLayout(btns_layout)
        layout.addWidget(btns)

        layout.setSizeConstraint(QVBoxLayout.SetFixedSize)
        container.setLayout(layout)

        self.lay.addWidget(container, alignment=Qt.AlignTop)

    def _on_priority_selected(self):
        selected_button = self.priorities.checkedButton()
        if selected_button:
            self.priority = selected_button.text()

    def _delete(self, id):
        query = f"""
        DELETE FROM task 
        WHERE id = '{id}' 
        AND user_id = '{self.user_id}'"""
        self.cur.execute(query)
        self.conn.commit()

        self.owner._render_view()
        self.owner._render_side_bar("", 0)

    def _insert_task(self):
        if self.title.text() == "":
            QMessageBox.warning(self, "Mandarina 🍊 says: Wait!",
                                "Title cannot have an empty value.")
            return
        # if not self.title.text().isalnum() or not self.comment.toPlainText().isalnum():
        #     QMessageBox.warning(self, "Mandarina 🍊 says: Wait!",
        #                         "Title and content need alphanumeric characters.")
        #     return

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

        self.owner._render_view()
        self.owner._render_side_bar("", 0)

    def _mark_as_complete(self, id):
        query = f"UPDATE task SET status = 'Completed' WHERE id = {id}"
        self.cur.execute(query)
        self.conn.commit()
        self.owner._render_view()
        self.owner._render_side_bar("", 0)

    def _render_edit(self, id):
        query = f"""
            SELECT task_name, content, priority, 
                    status, date, hour, minute FROM task 
            WHERE id = {id};
        """
        self.cur.execute(query)
        info = self.cur.fetchone()

        (title, content, priority, status, date, hour, minute) = info

        container = QWidget()
        container_lay = QVBoxLayout()

        hdr = QLabel("Edit Mode")
        hdr.setObjectName("primary")
        container_lay.addWidget(hdr)

        form = QGroupBox()
        form_lay = QFormLayout()

        self.edit_title = QLineEdit()
        self.edit_title.setText(title)
        form_lay.addRow("Title", self.edit_title)
        self.comment = QTextEdit()
        self.comment.setText(content)
        form_lay.addRow("Content", self.comment)
        self.edit_date = QDateEdit()
        d = QDate(int(date[:4]), int(date[5:7]), int(date[8:]))
        self.edit_date.setDate(d)
        form_lay.addRow("Date", self.edit_date)
        self.edit_time = QTimeEdit()
        t = QTime(int(hour), int(minute), 0)
        self.edit_time.setTime(t)
        form_lay.addRow("Time", self.edit_time)
        self.priorities = QButtonGroup(form)
        btns = QWidget()
        btns.setLayout(QVBoxLayout())
        for p in ["Low", "Medium", "High"]:
            radio = QRadioButton()
            radio.setText(p)
            self.priorities.addButton(radio)
            if priority == p:
                radio.setChecked(True)
            radio.toggled.connect(self._on_priority_selected)
            btns.layout().addWidget(radio)
        form_lay.addRow("Priority", btns)
        form.setLayout(form_lay)
        container_lay.addWidget(form)

        footer = QWidget()
        footer_lay = QHBoxLayout()

        save = QPushButton("Save")
        save.setFixedWidth(80)
        save.clicked.connect(lambda: self._update_task(id))
        footer_lay.addWidget(save, alignment=Qt.AlignmentFlag.AlignRight)

        cancel = QPushButton("Cancel")
        cancel.setFixedWidth(80)
        cancel.clicked.connect(lambda: self.owner._render_side_bar(" ", 0))
        footer_lay.addWidget(cancel, alignment=Qt.AlignmentFlag.AlignRight)

        footer.setLayout(footer_lay)
        container_lay.addWidget(footer)

        container.setLayout(container_lay)
        self.lay.addWidget(container)

    def _update_task(self, id):
        if self.edit_title.text() == "":
            QMessageBox.warning(self, "Mandarina 🍊 says: Wait!",
                                "Title cannot have an empty value.")
            return

        title = self.edit_title.text()
        content = self.comment.toPlainText()
        priority = self.priorities.checkedButton().text()
        deadline = self.edit_date.date().toString("yyyy-MM-dd")
        hour = self.edit_time.time().hour()
        minute = self.edit_time.time().minute()

        query = f"""
            UPDATE task SET 
                task_name = '{title}',
                content = '{content}',
                date = '{deadline}',
                hour = {hour},
                minute = {minute},
                priority = '{priority}'
            WHERE id = {id};
        """
        self.cur.execute(query)
        self.conn.commit()

        self.owner._render_view()
        self.owner._render_side_bar("", 0)
