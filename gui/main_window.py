from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QTableView, QLineEdit, QComboBox, QListView
from PyQt6.QtWidgets import QToolButton, QMenu, QCheckBox, QWidgetAction
from PyQt6.QtGui import QIcon, QStandardItemModel, QStandardItem, QFont, QAction
from PyQt6.QtCore import Qt
from logic.showdata import PandasModel
import pandas as pd
import os

class MainWindow(QMainWindow):
    def __init__(self,file_path: str):
        super().__init__()
        self.setWindowTitle("Data Shovel")
        self.center_window()
        self.setWindowIcon(QIcon("gui/logo.jpg"))
        self.setStyleSheet("background-color: black")
        
        self.file_path=file_path
        self.data=None
        #Potrzebujemy tutaj wiecej bramek sprawdzajacych plik albo jeszcze wczesniej w start_window
        try:
            self.data=pd.read_csv(self.file_path)
        except Exception as e:
            QMessageBox.critical(self, "Load error", f"Could not load CSV:\n{str(e)}")
        #data=pd.DataFrame(self.data)
        
        self.table_view=QTableView()
        self.model=PandasModel(self.data)
        self.table_view.setModel(self.model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setAlternatingRowColors(True)
        font = QFont("Segoe UI", 10)
        self.table_view.setFont(font)
        self.table_view.resizeColumnsToContents()
        self.table_view.setStyleSheet("""
             QTableView {
                background-color: white;
                alternate-background-color: #bab5b5;
                selection-background-color: #007acc;
                selection-color: white;
                color: black;
                font-size: 14px;
                gridline-color: #ccc;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                border: 1px solid #888;
                padding: 4px;
            }
        """)

        self.search_field=QLineEdit()
        self.search_field.setPlaceholderText("Search for a value...")
        self.search_field.setFixedSize(200,30)
        self.search_field.textChanged.connect(self.search_item)

        self.chose_column=QComboBox()
        self.chose_column.addItems(self.data.columns)
        #kolumny do wyboru
        self.visible_columns=list(self.data.columns)

        main_layout=QHBoxLayout()
        main_layout.addWidget(QLabel("Search: "))
        main_layout.addWidget(self.search_field)
        main_layout.addWidget(QLabel("from column: "))
        main_layout.addWidget(self.chose_column)
        self.column_selector=self.create_column_selector()
        #main_layout.addWidget(QLabel("Select columns:"))
        main_layout.addWidget(self.column_selector)
        
        layout=QVBoxLayout()
        layout.addLayout(main_layout)
        layout.addWidget(self.table_view)

        central_widget=QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def search_item(self,value):
        column_name=self.chose_column.currentText()
        column_index=self.data.columns.get_loc(column_name)
        for row_index in range(self.model.rowCount()):
            cell_content=self.model.index(row_index,column_index).data()
            self.table_view.setRowHidden(row_index, value.lower() not in cell_content.lower())

    def create_column_selector(self):
        self.column_selector=QToolButton()#rozwijana lista jednym slowem
        self.column_selector.setText("Select columns")
        self.column_selector.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        menu=QMenu(self)
        self.column_checkboxes=[]

        select_all=QAction("Select all", self)
        select_all.triggered.connect(self.select_all_columns)
        menu.addAction(select_all)

        deselect_all=QAction("Deselect all", self)
        deselect_all.triggered.connect(self.deselect_all_columns)
        menu.addAction(deselect_all)
        menu.addSeparator()

        for i, column in enumerate(self.data.columns):
            checkbox=QCheckBox(column)
            checkbox.setChecked(True)

            def switch(state,column=i):#state-zaznaczony checkbox czy nie
                self.table_view.setColumnHidden(column ,not state)
            checkbox.stateChanged.connect(switch)
            action = QWidgetAction(self)
            action.setDefaultWidget(checkbox)
            menu.addAction(action)
            self.column_checkboxes.append((checkbox,i))

        self.column_selector.setMenu(menu)
        return self.column_selector
    def select_all_columns(self):
        for checkbox, column_index in self.column_checkboxes:
            checkbox.setChecked(True)
            self.table_view.setColumnHidden(column_index,False)
    def deselect_all_columns(self):
        for checkbox, column_index in self.column_checkboxes:
            checkbox.setChecked(False)
            self.table_view.setColumnHidden(column_index,True)

    def center_window(self,percentage_of_window_width=1,percentage_of_window_height=1):
        screen_size=self.screen().availableGeometry()
        screen_width=screen_size.width()
        screen_height=screen_size.height()

        window_width=int(screen_width*percentage_of_window_width)
        window_height=int(screen_height*percentage_of_window_height)
        x=(screen_width-window_width)//2
        y=(screen_height-window_height)//2

        self.setGeometry(x,y,window_width,window_height)

        return window_width, window_height
