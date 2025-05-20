from PyQt6.QtWidgets import QApplication
from gui.start_window import WelcomeMenu
import sys

if __name__=="__main__":
    app=QApplication(sys.argv)
    window=WelcomeMenu()
    window.show()
    sys.exit(app.exec())