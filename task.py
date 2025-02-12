from PySide6.QtWidgets import (
    QWidget, QScrollArea, QLabel, QGridLayout, QGroupBox,
    QPushButton, QMainWindow, QHBoxLayout, QApplication, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt


class Task(QWidget):
    def __init__(self, task_id, task_title, priority, conn):
        super().__init__()
        self.id = task_id
        self.conn = conn
        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(2)
        self.setFixedWidth(70)

        tag = QLabel()
        tag.setFixedSize(5, 5)
        match priority:
            case "High":
                tag.setStyleSheet("""
                    background-color:'#eb002e';
                    border-radius: 2%;
                """)
            case "Medium":
                tag.setStyleSheet("""
                    background-color:'#eba000';
                    border-radius: 2%;
                """)
            case "Low":
                tag.setStyleSheet("""
                    background-color:'#1bbb58';
                    border-radius: 2%;
                """)

        self.main_layout.addWidget(tag, alignment=Qt.AlignTop)

        title = QLabel(task_title)
        title.setWordWrap(True)
        title.setFixedWidth(70)
        title.setStyleSheet("font-size: 11px;")
        self.main_layout.addWidget(title)

        self.setLayout(self.main_layout)
