from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox
from PyQt6.QtGui import QIcon
import pandas as pd
import os

class MainWindow(QMainWindow):
    def __init__(self,file_path: str):
        super().__init__()
        self.setWindowTitle("Data Shovel")
        #self.setGeometry(screen_size,1800,900)
        self.center_window()
        self.setWindowIcon(QIcon("gui/logo.jpg"))
        self.setStyleSheet("background-color:gray")
        
        self.file_path=file_path
        self.df=None
        
        try:
            self.df=pd.read_csv(self.file_path)
        except Exception as e:
            QMessageBox.critical(self, "Load error", f"Could not load CSV:\n{str(e)}")

    def center_window(self,percentage_of_window_width=0.65,percentage_of_window_height=0.7):
        screen_size=self.screen().availableGeometry()
        screen_width=screen_size.width()
        screen_height=screen_size.height()

        window_width=int(screen_width*percentage_of_window_width)
        window_height=int(screen_height*percentage_of_window_height)
        x=(screen_width-window_width)//2
        y=(screen_height-window_height)//2

        self.setGeometry(x,y,window_width,window_height)

        return window_width, window_height
