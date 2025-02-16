from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QGridLayout, QGroupBox,
    QApplication, QMainWindow, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from datetime import datetime
from calendar import Calendar as Cal
from task import Task
import sqlite3 as sql


class Calendar(QWidget):
    DAYS = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')

    def __init__(self, owner, uid, conn):
        super().__init__()

        screen = QGuiApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        self.width = screen_width * 0.7 - 50
        self.height = screen_height * 0.7 - 50

        self.user_id = uid
        self.conn = conn
        self.cur = self.conn.cursor()
        self.owner = owner

        self.main_layout = QVBoxLayout()

        self.setFixedSize(self.width, self.height)
        self.setLayout(self.main_layout)
        self.main_widget = None
        self.render_day_view(
            datetime.today().month, datetime.today().day, datetime.today().year)

    def render_day_view(self, month: int, day: int, year: int):
        if self.main_widget:
            self.main_layout.removeWidget(self.main_widget)
            self.main_widget.deleteLater()

        self.main_widget = QWidget()
        layout = QVBoxLayout()

        week_day = self._get_week_day(year, month, day)
        layout.addWidget(self._create_day_header(week_day, day))

        # Scroll area setup
        scroll_area = QScrollArea()

        container = QWidget()
        container_layout = QVBoxLayout()

        query = f"""
                SELECT id, task_name, date, hour, priority, status FROM task 
                WHERE strftime('%m', date) = '{month:02d}'
                AND strftime('%d', date) = '{day:02d}'
                AND strftime('%Y', date) = '{year}'
                AND user_id = '{self.user_id}';
                """
        self.cur.execute(query)
        tasks = self.cur.fetchall()
        container_layout.addWidget(self._create_hourly_schedule(day, tasks))

        container.setLayout(container_layout)
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

        self.main_widget.setLayout(layout)
        self.main_layout.addWidget(self.main_widget)

    def _get_week_day(self, year: int, month: int, day: int) -> str:
        for date, week_day in Cal().itermonthdays2(year, month):
            if date == day:
                return self.DAYS[week_day].upper()
        return ""

    def _create_day_header(self, week_day: str, day: int) -> QWidget:
        header = QWidget()
        header_layout = QHBoxLayout()

        day_label = QLabel(
            f"{week_day}")
        day_label.setObjectName("secondary")
        header_layout.addWidget(day_label)

        circle_label = QLabel(f"{day}")
        circle_label.setFixedSize(25, 25)
        circle_label.setAlignment(Qt.AlignCenter)
        circle_label.setObjectName("dayLabel")
        header_layout.addWidget(circle_label)
        header_layout.addStretch()

        header.setLayout(header_layout)
        return header

    def _create_hourly_schedule(self, day: int, tasks: list) -> QWidget:
        schedule_widget = QWidget()
        schedule_layout = QVBoxLayout()
        schedule_layout.setSpacing(0)

        for hour in range(24):
            container = QWidget()
            container_lay = QHBoxLayout()
            container_lay.setContentsMargins(0, 0, 0, 0)
            time_24 = datetime.strptime(
                f"{hour}:00", "%H:%M")  # Create a time object
            time_12 = time_24.strftime("%I:%M %p")
            hour_label = QLabel(time_12)
            container_lay.addWidget(hour_label)

            hour_group = QGroupBox()
            hour_layout = QVBoxLayout()
            hour_layout.setSpacing(2)

            for t in tasks:
                if t[3] == hour:
                    task_info = Task(self.owner, t[0], t[1], t[-2], t[-1])
                    hour_layout.addWidget(task_info)

            hour_group.setFixedWidth(self.width - 150)
            hour_group.setLayout(hour_layout)
            container_lay.addWidget(hour_group)
            container.setLayout(container_lay)
            schedule_layout.addWidget(container)

        schedule_widget.setLayout(schedule_layout)
        return schedule_widget

    def render_week_view(self, month: int, day: int, year: int):
        if self.main_widget:
            self.main_layout.removeWidget(self.main_widget)
            self.main_widget.deleteLater()

        self.main_widget = QScrollArea()
        container = QWidget()
        container.setFixedWidth(self.width - 100)
        container_layout = QGridLayout()

        week = self._get_week_of_month(year, month, day)

        for h in range(24):
            time_24 = datetime.strptime(
                f"{h}", "%H")  # Create a time object
            time_12 = time_24.strftime("%I:%M%p")
            hour_label = QLabel(time_12)
            container_layout.addWidget(hour_label, h+1, 0)

        for i, weekday in enumerate(week):
            day_info = QWidget()
            day_info.setFixedHeight(80)
            day_layout = QVBoxLayout()

            day_name = QLabel(self.DAYS[weekday[1]].upper())
            day_name.setAlignment(Qt.AlignCenter)
            day_layout.addWidget(day_name)

            day_date = QLabel(f"{weekday[0]}")
            day_date.setAlignment(Qt.AlignCenter)
            if weekday[0] == day:
                day_name.setObjectName("secondary")
                day_date.setObjectName("dayLabel")
            day_layout.addWidget(day_date)

            day_info.setLayout(day_layout)
            container_layout.addWidget(day_info, 0, i+1)

            query = f"""
                SELECT id, task_name, date, hour, priority, status FROM task 
                WHERE strftime('%m', date) = '{month:02d}'
                AND strftime('%d', date) = '{weekday[0]:02d}'
                AND strftime('%Y', date) = '{year}'
                AND user_id = '{self.user_id}';
                """
            self.cur.execute(query)
            tasks = self.cur.fetchall()

            for j in range(24):
                hour_group = QGroupBox()
                hour_layout = QVBoxLayout()
                hour_layout.setSpacing(0)
                hour_layout.setContentsMargins(5, 0, 5, 0)

                for t in tasks:
                    if t[3] == j:
                        task_info = Task(self.owner, t[0], t[1], t[-2], t[-1])
                        hour_layout.addWidget(task_info)

                hour_group.setLayout(hour_layout)
                container_layout.addWidget(hour_group, j+1, i+1)

        container.setLayout(container_layout)
        self.main_widget.setWidget(container)
        self.main_layout.addWidget(self.main_widget)

    def _get_week_of_month(self, year: int, month: int, day: int):
        cal = Cal(firstweekday=6)  # Sunday as first day of the week
        found_week = []

        for week in cal.monthdays2calendar(year, month):
            if any(date == day for date, _ in week):
                found_week = week
                break

        found_week = [(d, wd) for d, wd in found_week if d != 0]

        # If the week is incomplete at the start, fill with previous month's days
        if len(found_week) < 7 and found_week[0][1] > 0:
            prev_month = month - 1 if month > 1 else 12
            prev_year = year if month > 1 else year - 1
            prev_month_weeks = cal.monthdays2calendar(prev_year, prev_month)
            last_week_prev_month = [(d, wd)
                                    for d, wd in prev_month_weeks[-1] if d != 0]
            missing_days = 7 - len(found_week)
            found_week = last_week_prev_month[-missing_days:] + found_week

        # If the week is incomplete at the end, fill with next month's days
        if len(found_week) < 7:
            next_month = month + 1 if month < 12 else 1
            next_year = year if month < 12 else year + 1
            next_month_weeks = cal.monthdays2calendar(next_year, next_month)
            first_week_next_month = [(d, wd)
                                     for d, wd in next_month_weeks[0] if d != 0]
            missing_days = 7 - len(found_week)
            found_week += first_week_next_month[:missing_days]

        return found_week

    def render_month_view(self, month: int, day: int, year: int):
        if self.main_widget:
            self.main_layout.removeWidget(self.main_widget)
            self.main_widget.deleteLater()

        # Create main widget and layout
        self.main_widget = QWidget()
        # self.main_widget.setFixedSize(600, 450)
        main_layout = QGridLayout()
        main_layout.setSpacing(1)  # xr

        # Define weekdays order (starting from Sunday)
        weekday_order = [6, 0, 1, 2, 3, 4, 5]

        # Add weekday headers
        for col, weekday_index in enumerate(weekday_order):
            label = QLabel(self.DAYS[weekday_index].upper())
            label.setFixedHeight(80)
            label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(label, 0, col)

        # Initialize calendar and tasks
        cal = Cal(firstweekday=6)
        # tasks = self.get_tasks(month)

        # Iterate through the days of the month
        row, col = 1, 0
        for date in cal.itermonthdays(year, month):
            if col == 7:
                row += 1
                col = 0

            if date == 0:
                col += 1
                continue

            # Create day container
            day_container = QScrollArea()
            day_container.setContentsMargins(0, 0, 0, 0)
            day_container.setFixedSize(self.width/8, self.height/7)

            container = QWidget()
            container_layout = QVBoxLayout()
            container_layout.setSpacing(0)

            # Create day label
            day_label = QLabel(str(date))
            day_label.setFixedSize(25, 25)
            day_label.setAlignment(Qt.AlignCenter)
            # Highlight current day
            if date == day:
                day_label.setObjectName("dayLabel")
            container_layout.addWidget(day_label)

            query = f"""
                SELECT id, task_name, date, hour, priority, status FROM task 
                WHERE strftime('%m', date) = '{month:02d}'
                AND strftime('%d', date) = '{date:02d}'
                AND strftime('%Y', date) = '{year}'
                AND user_id = '{self.user_id}';
                """
            self.cur.execute(query)
            tasks = self.cur.fetchall()

            for t in tasks:
                if t[2][-2:] == f'{date:02d}':
                    task_info = Task(self.owner, t[0], t[1], t[-2], t[-1])
                    container_layout.addWidget(task_info)

            # Set layout and add to main layout
            container.setLayout(container_layout)
            day_container.setWidget(container)
            main_layout.addWidget(day_container, row, col)

            col += 1

        self.main_widget.setLayout(main_layout)
        self.main_layout.addWidget(self.main_widget)
