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
        options.layout().addWidget(QLabel("Priority:"))
        self.priority = QComboBox()
        self.priority.addItems(["Low", "Medium", "High"])
        options.layout().addWidget(self.priority)
        options.layout().addWidget(QLabel("Status:"))
        self.status = QComboBox()
        self.status.addItems(["Pending", "Completed"])
        options.layout().addWidget(self.status)
        options.layout().addWidget(QLabel("Time Frame:"))
        self.time_frame = QComboBox()
        self.time_frame.addItems(["Morning", "Afternoon", "Night"])
        options.layout().addWidget(self.time_frame)
        self.filter_btn = QPushButton("Filter")
        self.filter_btn.setFixedWidth(80)
        self.filter_btn.clicked.connect(self.filter)
        options.layout().addWidget(self.filter_btn, alignment=Qt.AlignRight)

        lay.addWidget(options)

        lay.addWidget(self._create_chart())

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
    
    def filter(self):
        keyword = self.keyword.text()
        priority = self.priority.currentText()
        status = self.status.currentText()
        time_frame = self.time_frame.currentText()

        times = {
            "Morning": [0, 12],
            "Afternoon": [13, 18],
            "Night": [19, 23]
        }

        filtered = f"""SELECT task_name, date, hour, content, priority, status
                        FROM task 
                        WHERE task_name LIKE '%{keyword}%' 
                            AND priority == '{priority}' 
                            AND status == '{status}'
                            AND hour BETWEEN {times[time_frame][0]} AND {times[time_frame][1]}
                    """
        self.cur.execute(filtered)
        filtered_tasks = self.cur.fetchall()
        
        self._render_tasks(filtered_tasks)

    def _render_tasks(self, tasks):
        container = QWidget()
        container.setLayout(QVBoxLayout())
        print(tasks)
        for task in tasks:
            w = QWidget()
            w.setLayout(QVBoxLayout())
            for i in range(len(task)):
                l = QLabel(task[i])
                l.setFixedWidth(200)
                l.setWordWrap(True)
                if i == 0:
                    l.setObjectName("accented")
                w.layout().addWidget(l)
            container.layout().addWidget(w)
        self.tasks_found.setWidget(container)
                
                
