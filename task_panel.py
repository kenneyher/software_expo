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
    QTimeEdit
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate
from PySide6.QtGui import QFont, QPalette, QColor
from datetime import datetime

class TaskPanel(QWidget):
    def __init__(self, owner, type, conn):
        super().__init__()

        self.conn = conn
        self.owner = owner
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
        self.content = QTextEdit()
        form_lay.addRow("Content", self.content)
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
        form_lay.addRow("Priorities", btns)
        form.setLayout(form_lay)
        container_lay.addWidget(form)

        footer = QWidget()
        footer_lay = QHBoxLayout()

        save = QPushButton("Save")
        save.setFixedWidth(80)
        footer_lay.addWidget(save, alignment=Qt.AlignmentFlag.AlignRight)

        cancel = QPushButton("Cancel")
        cancel.setFixedWidth(80)
        cancel.clicked.connect(lambda:self.owner._render_side_bar(" "))
        footer_lay.addWidget(cancel, alignment=Qt.AlignmentFlag.AlignRight)

        footer.setLayout(footer_lay)
        container_lay.addWidget(footer)
        
        container.setLayout(container_lay)
        self.layout().addWidget(container)

    def _on_priority_selected(self):
        pass