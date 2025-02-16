from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QGridLayout, QGroupBox,
    QPushButton, QMainWindow, QHBoxLayout, QApplication, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt
from datetime import datetime
from calendar import Calendar as Cal


class Minicalendar(QWidget):
    __DAYS = (
        'S',
        'M',
        'T',
        'W',
        'T',
        'F',
        'S',
    )
    __MONTHS = (
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "October", "September", "November", "December"
    )

    def __init__(self):
        super().__init__()

        self.curdate = {
            'day': datetime.today().day,
            'month': datetime.today().month,
            'year': datetime.today().year,
        }

        self.setContentsMargins(-20, 0, -20, 0)
        self.setFixedWidth(250)
        self.main_lay = QVBoxLayout()

        header = QWidget()
        header_lay = QHBoxLayout()
        header_lay.setContentsMargins(0, 0, 0, 0)
        header_lay.setSpacing(1)

        self.month = QLabel(
            f"{self.__MONTHS[self.curdate['month']-1]} {self.curdate['year']}"
        )
        self.month.setObjectName("secondary")
        header_lay.addWidget(self.month)

        prev_btn = QPushButton("◀")
        prev_btn.setContentsMargins(10, 0, 10, 0)
        prev_btn.setFixedSize(25, 25)
        prev_btn.clicked.connect(self._go_prev)
        header_lay.addWidget(prev_btn)

        next_btn = QPushButton("▶")
        next_btn.setContentsMargins(10, 0, 10, 0)
        next_btn.setFixedSize(25, 25)
        next_btn.clicked.connect(self._go_next)
        header_lay.addWidget(next_btn)

        header.setLayout(header_lay)
        self.main_lay.addWidget(header)

        self.calendar = None
        self._render_calendar(self.curdate['month'],
                              self.curdate['year'])

        self.setLayout(self.main_lay)

    def _render_calendar(self, month, year):
        if self.calendar:
            self.main_lay.removeWidget(self.calendar)
            self.calendar.deleteLater()
            self.calendar = None

        self.month.setText(
            f"{self.__MONTHS[self.curdate['month']-1]} {self.curdate['year']}")
        self.calendar = QWidget()
        self.calendar.setObjectName("minical")
        self.calendar.setFixedHeight(200)
        layout = QGridLayout()
        layout.setSpacing(0)

        col = 0
        for day in self.__DAYS:
            label = QLabel(day)
            if day == 'S':
                label.setObjectName("accented")
                opacity_effect = QGraphicsOpacityEffect()
                label.setGraphicsEffect(opacity_effect)
                label.graphicsEffect().setProperty("opacity", 0.5)
            layout.addWidget(label, 0, col, alignment=Qt.AlignCenter)
            col += 1

        cal = Cal()
        cal.setfirstweekday(6)
        row = 1
        col = 0
        for i in cal.itermonthdays(year, month):
            if col == 7:
                row += 1
                col = 0
            if i == 0:
                col += 1
                continue

            label = QLabel(f"{'' if i == 0 else i}")
            if col == 0 or col == 6:
                label.setObjectName("accented")
                opacity_effect = QGraphicsOpacityEffect()
                label.setGraphicsEffect(opacity_effect)
                label.graphicsEffect().setProperty("opacity", 0.7)
            if (i == datetime.today().day and datetime.today().month == self.curdate['month']
                    and datetime.today().year == self.curdate['year']):
                label.setObjectName("dayLabel")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label, row, col)
            col += 1

        self.calendar.setLayout(layout)
        self.main_lay.addWidget(self.calendar)

    def _go_next(self):
        self.curdate['month'] += 1
        if self.curdate['month'] >= 12:
            self.curdate['year'] += 1
            self.curdate['month'] = 1
        self._render_calendar(self.curdate['month'],
                              self.curdate['year'])

    def _go_prev(self):
        self.curdate['month'] -= 1
        if self.curdate['month'] <= 0:
            self.curdate['year'] -= 1
            self.curdate['month'] = 12
        self._render_calendar(self.curdate['month'],
                              self.curdate['year'])
