from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QTableView, QLineEdit, QComboBox, QTabWidget, QPushButton
from PyQt6.QtWidgets import QToolButton, QMenu, QCheckBox, QWidgetAction
from PyQt6.QtGui import QIcon, QFont, QAction
from PyQt6.QtCore import Qt
from logic.showdata import PandasModel
import pandas as pd
import os
#ogolnie niech ktos zajmie sie stylem bo wyglada to nie najlepiej aktualnie /frontend/ :(
class MainWindow(QMainWindow):
    def __init__(self,file_path: str):
        super().__init__()
        self.setWindowTitle("Data Shovel")
        self.center_window()
        self.setWindowIcon(QIcon("gui/logo.jpg"))
        self.setStyleSheet("background-color: gray")
        
        self.file_path=file_path
        self.data=None

        self.load_data()

        if self.data is not None:
            self.tabs=QTabWidget()
            self.setCentralWidget(self.tabs)
            self.add_view_tab()
            self.add_tools_tab()
            self.show()
        else:
            self.close()

    def load_data(self):
        try:
            self.data=pd.read_csv(self.file_path)
            if self.data.empty:
                raise ValueError("Plik CSV is empty")
            return True
        except Exception as e:
            QMessageBox.critical(self,"Loading error", f"Nie można wczytać pliku CSV:\n{str(e)}")
            self.data=None
            return False
    def add_view_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.table_view: QTableView = QTableView()
        """ chcialem poprawic plynnosc scrolowania tabeli ale visual nie znajduje tej pierwszej funkcji zobaczcie czy u was dziala
        self.table_view.setUniformRowHeights(True)
        self.table_view.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.table_view.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        """
        self.model = PandasModel(self.data)
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

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search for a value...")
        self.search_field.setFixedSize(200, 30)
        self.search_field.textChanged.connect(self.search_item)

        self.chose_column = QComboBox()
        self.chose_column.addItems(self.data.columns)
        self.visible_columns = list(self.data.columns)

        main_layout = QHBoxLayout()
        main_layout.addWidget(QLabel("Search: "))
        main_layout.addWidget(self.search_field)
        main_layout.addWidget(QLabel("from column: "))
        main_layout.addWidget(self.chose_column)
        self.column_selector = self.create_column_selector()
        main_layout.addWidget(self.column_selector)
        
        layout.addLayout(main_layout)
        layout.addWidget(self.table_view)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Data viewer")
        
    def add_tools_tab(self):
        tab=QWidget()
        layout=QVBoxLayout()
        label=QLabel("Data purifing tools: ")
        label.setStyleSheet("font-size: 16px; color: black")
        btn=QPushButton("something button")
        #btn.setStyleSheet()

        layout.addWidget(label)
        layout.addWidget(btn)

        tab.setLayout(layout)

        self.tabs.addTab(tab,"Data tools")

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