from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt6.QtGui import QIcon

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Shovel")
        self.setGeometry(500,500,1800,900)
        self.setWindowIcon(QIcon("gui/logo.jpg"))
        self.setStyleSheet("background-color:gray")