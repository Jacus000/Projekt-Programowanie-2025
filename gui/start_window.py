from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QFileDialog, QMessageBox
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt,QSize
from gui.main_window import MainWindow
import pandas as pd
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))#pelna sciezka do pliku start_window nie wazne skad uruchamiamy czyt. z maina

class WelcomeMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data shovel - upload your data")
        self.center_window(0.25, 0.30)
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR, "logo.jpg")))
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        #Powitalne wiadomosci 
        self.label = QLabel("Welcome! - to start upload your file")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font=QFont("Times",16,QFont.Weight.Bold)
        self.label.setFont(font)

        self.label2 = QLabel("Get started by adding your .csv file below")
        self.label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font2=QFont("Times",10,QFont.Weight.Medium)
        self.label2.setFont(font2)

        #Specjalna przestrzen do przycisku do dodawania pliku i potem dodanego pliku
        file_selection_layout=QHBoxLayout()
        file_selection_layout.setSpacing(10)

        self.add_file_btn=QPushButton("Add file")
        self.add_file_btn.setFont(QFont("Times", 14, QFont.Weight.Bold))
        self.add_file_btn.setIcon(QIcon(os.path.join(BASE_DIR, "add_icon.png")))
        self.add_file_btn.setIconSize(QSize(26,36))
        self.add_file_btn.setFixedSize(150,60)
        self.add_file_btn.clicked.connect(self.browse_files)

        self.file_display_frame=QFrame()
        self.file_display_frame.setFixedSize(300,60)

        file_display_layout = QHBoxLayout()
        file_display_layout.setContentsMargins(10, 0, 10, 0)

        self.file_name_label=QLabel("No file selected")
        self.file_name_label.setStyleSheet("color: white; font-style: italic")

        self.delete_file_btn=QPushButton()
        self.delete_file_btn.setIcon(QIcon(os.path.join(BASE_DIR, "close_red.png")))
        #self.delete_file_btn.setText("X")
        #self.delete_file_btn.setStyleSheet("color: darkred; font-weight: bold; font-size: 18px; background-color: transparent;")
        self.delete_file_btn.setIconSize(QSize(30,30))
        self.delete_file_btn.setFixedSize(40,40)
        self.delete_file_btn.setToolTip("Remove file")
        self.delete_file_btn.setStyleSheet("QToolTip {color: black; background-color: white; border: 1px solid black;}")
        self.delete_file_btn.hide()
        self.delete_file_btn.clicked.connect(self.clear_file)

        file_display_layout.addWidget(self.file_name_label, 1, Qt.AlignmentFlag.AlignLeft)
        file_display_layout.addWidget(self.delete_file_btn)
        self.file_display_frame.setLayout(file_display_layout)
        
        file_selection_layout.addWidget(self.add_file_btn)
        file_selection_layout.addWidget(self.file_display_frame)

        self.proceed_btn=QPushButton("Proceed")
        self.proceed_btn.setFont(QFont("Times",14,QFont.Weight.Bold))
        self.proceed_btn.setEnabled(False)
        self.proceed_btn.setFixedHeight(40)
        self.proceed_btn.clicked.connect(self.proceed_button)

        main_layout.addWidget(self.label)
        main_layout.addWidget(self.label2)
        main_layout.addLayout(file_selection_layout)
        main_layout.addWidget(self.proceed_btn)
        main_layout.addStretch()

        self.selected_file_path=None
        
        self.setLayout(main_layout)

    def center_window(self, percentage_of_window_width=0.65, percentage_of_window_height=0.7):
        screen_size = self.screen().availableGeometry()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        window_width = int(screen_width * percentage_of_window_width)
        window_height = int(screen_height * percentage_of_window_height)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.setGeometry(x, y, window_width, window_height)
        return window_width, window_height
    #po przekazaniu pliku
    def update_after_file(self,file_path):
        if file_path:
            file_name=file_path.split("/")[-1]
            self.file_name_label.setText(file_name)
            self.file_name_label.setStyleSheet("color: darkslategray; font-style: normal;")
            self.file_display_frame.setStyleSheet("""
                background-color: lightgray;
                border: 2px solid gray;
                border-radius: 5px;
            """)
            self.delete_file_btn.show()
            self.proceed_btn.setEnabled(True)
        else:
            self.file_name_label.setText("No file selected")
            self.file_name_label.setStyleSheet("color: darkgray; font-style: italic;")
            self.file_display_frame.setStyleSheet("""
                background-color: whitesmoke;
                border: 2px dashed gray;
                border-radius: 5px;
            """)
            self.delete_file_btn.hide()
            self.proceed_btn.setEnabled(False)
    def browse_files(self):
        file_search=QFileDialog(self)
        file_search.setWindowTitle("Select CSV file")
        file_search.setNameFilter("CSV Files (*.csv);;All Files (*)")
        file_search.setFileMode(QFileDialog.FileMode.ExistingFile)

        if file_search.exec():#przechodzi dalej gdy uzytkownik przejdzie dalej a nie anuluje
            selected_file = file_search.selectedFiles()
            if selected_file:
                self.selected_file_path = selected_file[0]
                self.update_after_file(self.selected_file_path)

    def clear_file(self):
        self.selected_file_path = None
        self.update_after_file(None)
    
    def proceed_button(self):
        if self.selected_file_path:
            try:
                test_data=pd.read_csv(self.selected_file_path)
                if test_data.empty:
                    raise ValueError("File is empty")
                self.main_window=MainWindow(self.selected_file_path)
                self.close()
            except pd.errors.EmptyDataError:
                QMessageBox.critical(self, "Błąd danych", "Wybrany plik CSV jest pusty")
            except pd.errors.ParserError:
                QMessageBox.critical(self, "Błąd składni", "Nieprawidłowy format pliku CSV")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie można wczytać pliku:\n{str(e)}")

