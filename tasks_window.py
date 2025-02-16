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
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate
from PySide6.QtGui import QGuiApplication, QFont, QPainter, QPen, QColor
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from datetime import datetime


class TasksWindow(QMainWindow):
    def __init__(self, parent, conn, id, palette, theme):
        super().__init__(parent)
        screen = QGuiApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        self.setFixedSize(screen_width*0.5, screen_height*0.4)
        self.conn = conn
        self.cur = self.conn.cursor()
        self.user_id = id
        self.theme = theme
        self.palette = palette

        window = QWidget()
        lay = QHBoxLayout()
        lay.setSpacing(0)
        lay.setContentsMargins(5, 0, 5, 0)

        results = QWidget()
        results.setFixedWidth(screen_width*0.5*0.4 - 50)
        results.setLayout(QVBoxLayout())

        results.layout().addWidget(QLabel("Sort by:"))
        self.sortby = QComboBox()
        self.sortby.addItems(["Name", "Date", "Hour"])
        self.sortby.setMaximumWidth(100)
        results.layout().addWidget(self.sortby)

        self.tasks_found = QScrollArea()
        # self.tasks_found.setFixedWidth()
        results.layout().addWidget(self.tasks_found)

        lay.addWidget(results)

        options = QWidget()
        options.setFixedWidth(screen_width*0.5 * 0.4 - 50)
        options.setLayout(QVBoxLayout())

        options.layout().addWidget(QLabel("Keyword:"))
        self.keyword = QLineEdit()
        options.layout().addWidget(self.keyword)
        self.filter_by_kw = QPushButton("Filter by Keyword")
        self.filter_by_kw.clicked.connect(lambda: self.filter("keyword"))
        self.filter_by_kw.setFixedWidth(120)
        options.layout().addWidget(self.filter_by_kw)

        options.layout().addWidget(QLabel("Priority:"))
        self.priority = QComboBox()
        self.priority.addItems(["Low", "Medium", "High"])
        self.filter_by_priority = QPushButton("Filter by Priority")
        self.filter_by_priority.setFixedWidth(120)
        self.filter_by_priority.clicked.connect(
            lambda: self.filter("priority"))
        options.layout().addWidget(self.priority)
        options.layout().addWidget(self.filter_by_priority)

        options.layout().addWidget(QLabel("Status:"))
        self.status = QComboBox()
        self.status.addItems(["Pending", "Completed"])
        options.layout().addWidget(self.status)
        self.filter_by_status = QPushButton("Filter by Status")
        self.filter_by_status.setFixedWidth(120)
        self.filter_by_status.clicked.connect(
            lambda: self.filter("status"))
        options.layout().addWidget(self.filter_by_status)

        options.layout().addWidget(QLabel("Time Frame:"))
        self.time_frame = QComboBox()
        self.time_frame.addItems(["Morning", "Afternoon", "Night"])
        options.layout().addWidget(self.time_frame)
        self.filter_by_time = QPushButton("Filter by Time")
        self.filter_by_time.setFixedWidth(120)
        self.filter_by_time.clicked.connect(
            lambda: self.filter("time"))
        options.layout().addWidget(self.filter_by_time)

        lay.addWidget(options)

        lay.addWidget(self._create_chart())

        self._render_tasks(self._get_tasks())

        window.setLayout(lay)
        self.setCentralWidget(window)

    def _create_chart(self):
        series = QPieSeries()
        completed = 0
        pending = 0

        query = f"""
            SELECT status
            FROM task
            WHERE
                user_id = {self.user_id}
        """
        self.cur.execute(query)
        filtered_tasks = self.cur.fetchall()

        for task in filtered_tasks:
            if task[0] == 'Completed':
                completed += 1
            else:
                pending += 1

        series.append("Completed", completed)
        series.append("Pending", pending)

        # adding slice
        slice = QPieSlice()
        slice = series.slices()[0]
        slice.setExploded(True)
        slice.setPen(QPen(QColor.fromString(self.palette["accent"]), 2))
        slice.setBrush(QColor.fromString(self.palette["accent"]))
        slice = QPieSlice()
        slice = series.slices()[1]
        slice.setPen(QPen(QColor.fromString(self.palette["sec_accent"]), 2))
        slice.setBrush(QColor.fromString(self.palette["sec_accent"]))

        chart = QChart()
        chart.legend().hide()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle("Tasks Completion State:")

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        bg = "dark_bg" if self.theme == "dark" else "bg"
        chart.setBackgroundBrush(QColor.fromString(self.palette[bg]))

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)

        return chartview

    def _get_tasks(self):
        query = f"SELECT task_name, date, hour, minute, content, priority, status FROM task WHERE user_id = {self.user_id}"
        self.cur.execute(query)
        all_tasks = self.cur.fetchall()

        return all_tasks

    def _get_ordering(self):
        match self.sortby.currentText():
            case "Name":
                return "task_name"
            case "Date":
                return "date"
            case "Hour":
                return "hour"
        return ""

    def filter(self, type):
        query = f"""SELECT task_name, date, hour, minute, content, priority, status
                    FROM task
                    WHERE user_id = {self.user_id}
                    ORDER BY {self._get_ordering()} ASC;"""
        match type:
            case "keyword":
                query = f"""
                    SELECT task_name, date, hour, minute, content, priority, status
                    FROM task
                    WHERE user_id = {self.user_id}
                        AND (task_name LIKE '%{self.keyword.text()}%'
                        OR content LIKE '%{self.keyword.text()}%')
                        ORDER BY {self._get_ordering()} ASC;
                """
            case "priority":
                query = f"""
                    SELECT task_name, date, hour, minute, content, priority, status
                    FROM task
                    WHERE user_id = {self.user_id}
                        AND priority = '{self.priority.currentText()}'
                        ORDER BY {self._get_ordering()} ASC;
                """
            case "status":
                query = f"""
                    SELECT task_name, date, hour, minute, content, priority, status
                    FROM task
                    WHERE user_id = {self.user_id}
                        AND status = '{self.status.currentText()}'
                        ORDER BY {self._get_ordering()};
                """
            case "time":
                time_frames = {
                    "Morning": [0, 12],
                    "Afternoon": [13, 18],
                    "Night": [19, 23]
                }
                query = f"""
                    SELECT task_name, date, hour, minute, content, priority, status
                    FROM task
                    WHERE user_id = {self.user_id}
                        AND hour BETWEEN {time_frames[self.time_frame.currentText()][0]}
                            AND {time_frames[self.time_frame.currentText()][1]}
                    ORDER BY {self._get_ordering()};
                """
        self.cur.execute(query)
        tasks = self.cur.fetchall()

        self._render_tasks(tasks)

    def _render_tasks(self, tasks):
        container = QWidget()
        container.setLayout(QVBoxLayout())
        if len(tasks) < 1:
            container.layout().addWidget(QLabel("No tasks found c:"))
            self.tasks_found.setWidget(container)
            return
        for task in tasks:
            w = QWidget()
            w.setLayout(QVBoxLayout())

            title = QLabel(task[0])
            title.setFixedWidth(150)
            title.setWordWrap(True)
            title.setObjectName("secondary")
            w.layout().addWidget(title)

            date = QLabel(task[1])
            date.setObjectName("accented")
            w.layout().addWidget(date)

            hour = QLabel(f"{task[2]:02d}:{task[3]:02d}")
            w.layout().addWidget(hour)

            for field in [task[4], task[5], task[6]]:
                l = QLabel(field)
                l.setFixedWidth(150)
                l.setWordWrap(True)
                w.layout().addWidget(l)

            container.layout().addWidget(w)
        self.tasks_found.setWidget(container)
