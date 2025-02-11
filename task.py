from PySide6.QtWidgets import (
    QWidget, QScrollArea, QLabel, QGridLayout, QGroupBox,
    QPushButton, QMainWindow, QHBoxLayout, QApplication, QGraphicsOpacityEffect
)

class task(QWidget):
    def __init__(self, task_id, task_title, priority, conn):
        super().__init__
        self.id = task_id
        self.conn = conn
        self.main_layout = QHBoxLayout()

        tag = QLabel()
        match priority: 
            case "High":
                tag.setStyleSheet("""
                    background-color:'#b002e'                
                """)
            case "Medium":
                tag.setStyleSheet("""
                    background-color:'#eba000'                
                """)
            case "Low":
                tag.setStyleSheet("""
                    background-color:'#1bbb58'                
                """)
    
        self.main_layout.addWidget(tag)
        title = QLabel(title)
        self.main_layout.addWidget(title)
        


