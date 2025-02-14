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
    def __init__(self, parent, conn, id):
        super().__init__(parent)
        screen = QGuiApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        self.setFixedSize(screen_width*0.5, screen_height*0.4)
        self.conn = conn
        self.cur = self.conn.cursor()
        self.user_id = id

        window = QWidget()
        lay = QHBoxLayout()
        lay.setSpacing(0)
        lay.setContentsMargins(5, 0, 5, 0)

        results = QWidget()
        results.setLayout(QVBoxLayout())

        results.layout().addWidget(QLabel("Sort by:"))
        self.sortby = QComboBox()
        self.sortby.addItems(["Name", "Date", "Hour"])
        self.sortby.setMaximumWidth(100)
        results.layout().addWidget(self.sortby)

        self.tasks_found = QScrollArea()
        self.tasks_found.setFixedWidth(150)
        results.layout().addWidget(self.tasks_found)

        lay.addWidget(results)

        options = QWidget()
        options.setFixedWidth(150)
        options.setLayout(QVBoxLayout())

        options.layout().addWidget(QLabel("Keyword:"))
        self.keyword = QLineEdit()
        options.layout().addWidget(self.keyword)
        options.layout().addWidget(QLabel("Date:"))
        self.date = QDateEdit()
        options.layout().addWidget(self.date)
        options.layout().addWidget(QLabel("Priority:"))
        self.priority = QComboBox()
        self.priority.addItems(["Low", "Medium", "High"])
        options.layout().addWidget(self.priority)
        options.layout().addWidget(QLabel("Status:"))
        self.status = QComboBox()
        self.status.addItems(["Pending", "Completed"])
        options.layout().addWidget(self.status)
        options.layout().addWidget(QLabel("Time Frame:"))
        self.status = QComboBox()
        self.status.addItems(["Morning", "Afternoon", "Night"])
        options.layout().addWidget(self.status)
        self.filter = QPushButton("Filter")
        self.filter.setFixedWidth(80)
        options.layout().addWidget(self.filter, alignment=Qt.AlignRight)

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
        slice.setPen(QPen(QColor.fromRgb(66, 155, 94), 2))
        slice.setBrush(QColor.fromRgb(66, 155, 94))
        slice = QPieSlice()
        slice = series.slices()[1]
        slice.setPen(QPen(QColor.fromRgb(255, 141, 69), 2))
        slice.setBrush(QColor.fromRgb(255, 141, 69))

        chart = QChart()
        # chart.setMaximumSize(200, 200)
        chart.setFont(QFont('Arial', 10))
        chart.legend().hide()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle("Tasks Completion State:")

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)

        return chartview
