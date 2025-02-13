from PySide6.QtWidgets import (
    QWidget, QScrollArea, QLabel, QGridLayout, QGroupBox,
    QPushButton, QMainWindow, QHBoxLayout, QApplication, QSizePolicy,
    QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt


class Task(QWidget):
    def __init__(self, owner, task_id, task_title, priority, status):
        super().__init__()
        self.id = task_id
        self.owner = owner
        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(2)
        self.setFixedWidth(100)

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
        title.setFixedWidth(90)
        font = title.font()
        if status == "Completed":
            opacity_effect = QGraphicsOpacityEffect()
            title.setGraphicsEffect(opacity_effect)
            title.graphicsEffect().setProperty("opacity", 0.25)
        font.setPointSize(11)
        title.setFont(font)
        self.main_layout.addWidget(title)

        self.setLayout(self.main_layout)

    def mousePressEvent(self, a0) -> None:
        self.owner._render_side_bar("task info", self.id)
