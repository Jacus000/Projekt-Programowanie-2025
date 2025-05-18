from PyQt6.QtWidgets import QApplication, QWidget
from gui.main_window import MainWindow
import sys

if __name__=="__main__":
    app=QApplication(sys.argv)
    window=MainWindow()
    window.show()
    sys.exit(app.exec())