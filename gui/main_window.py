from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QTableView, QLineEdit, QComboBox, QTabWidget, QPushButton, QFrame
from PyQt6.QtWidgets import QToolButton, QMenu, QCheckBox, QWidgetAction
from PyQt6.QtGui import QIcon, QFont, QAction
from PyQt6.QtCore import Qt
from logic.showdata import PandasModel
from logic.regression import RegressionDashboard
import pandas as pd

#ogolnie niech ktos zajmie sie stylem bo wyglada to nie najlepiej aktualnie /frontend/ :(
class MainWindow(QMainWindow):
    def __init__(self,file_path: str):
        super().__init__()
        self.setWindowTitle("Data Shovel")
        self.center_window()
        self.setWindowIcon(QIcon("gui/logo.jpg"))
        self.setStyleSheet("""
            QMainWindow {
            background-color: #f4f6f9;
            }
    

            QTableView {
            background-color: white;
            alternate-background-color: #e8edf2;
            selection-background-color: #007acc;
            selection-color: white;
            color: #2c3e50;
            font-size: 13px;
            gridline-color: #d0d0d0;
            border: 1px solid #ccc;
            }

            QHeaderView::section {
            background-color: #34495e;
            color: white;
            font-weight: bold;
            padding: 4px;
            border: 1px solid #aaa;
            }

            QLineEdit {
            padding: 6px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 13px;
            background-color: white;
            }

            QComboBox {
            padding: 5px;
            border: 1px solid #aaa;
            border-radius: 4px;
            background-color: white;
            }

            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #3498db;
            }

            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #ecf0f1;
            }

            QLabel {
                font-size: 14px;
                color: #2c3e50;
            }

            QMenu {
                background-color: white;
                border: 1px solid #ccc;
            }

            QCheckBox {
                padding: 4px;
                font-size: 13px;
            }

            QTabBar::tab {
                background: #dce3ea;
                border: 1px solid #aaa;
                padding: 8px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
                font-weight: bold;
                min-width: 100px;
            }

            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom-color: white;
            }

            QTabWidget::pane {
                border: 1px solid #aaa;
                top: -1px;
                background: #ffffff;
            }
        """)

        menu_bar=self.menuBar()
        file_menu=menu_bar.addMenu("File")
        help_menu=menu_bar.addMenu("Help")
        self.file_path=file_path
        self.data=None

        self.load_data()

        if self.data is not None:
            self.tabs=QTabWidget()
            self.setCentralWidget(self.tabs)
            self.add_view_tab()
            self.add_tools_tab()
            self.regression_tab(self.data)
            self.plot_data()
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
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
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

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search for a value...")
        self.search_field.setFixedSize(200, 30) 
        self.search_field.textChanged.connect(self.search_item)

        self.chose_column = QComboBox()
        self.chose_column.addItems(self.data.columns)
        self.visible_columns = list(self.data.columns)
        
        ## usuwanie kolumn ##
        self.selector=QComboBox()
        self.selector.addItems(self.data.columns)

        self.remove_button=QPushButton()
        self.remove_button.setText("Remove chosen column")
        self.remove_button.clicked.connect(self.confirm_removal)
        
        ## ustawianie layoutu ##
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(9)
        main_layout.addWidget(QLabel("Search: "))
        main_layout.addWidget(self.search_field)
        main_layout.addWidget(QLabel("from column:"))
        main_layout.addWidget(self.chose_column)
        main_layout.addWidget(QLabel("Remove columns:"))
        main_layout.addWidget(self.selector)
        main_layout.addWidget(self.remove_button)
        self.column_selector = self.create_column_selector()
        main_layout.addWidget(self.column_selector)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #ccc; margin: 5px 0;")

        layout.addLayout(main_layout)
        layout.addWidget(line)
        layout.addWidget(self.table_view)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Data viewer")

    ## potwierdzenie usuniecia kolumny ##    
    def confirm_removal(self):
        selected_column=self.selector.currentText()
        reply=QMessageBox.question(self,"Confirmation",f"Are you sure, you want to delete {selected_column}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.remove_column(selected_column)
    ## usuniecie kolumny i aktualizacja widgetow w ktorej ta kolumna wystepowala ##
    def remove_column(self, column_name):
        self.data.drop(column_name,axis=1,inplace=True)

        self.model.updateData(self.data)

        self.selector.clear()
        self.selector.addItems(self.data.columns)

        self.chose_column.clear()
        self.chose_column.addItems(self.data.columns)
        
        self.selector.removeItem(self.selector.currentIndex())
        QMessageBox.information(self,"Succes",f"Column {column_name} got succesfully removed")
        if self.selector.count()==0:
            self.remove_button.setEnabled(False)
    ## zakladka z wykresami ##
    def plot_data(self):
        tab=QWidget()
        layout=QHBoxLayout()

        self.tabs.addTab(tab, "Data plotter")

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
    ## zakladka z regresja ##
    def regression_tab(self, data):
        regression_widget = RegressionDashboard(data)
        self.tabs.addTab(regression_widget, "Regression Dashboard")
    ## szukanie wartosci w tabeli ##
    def search_item(self,value):
        column_name=self.chose_column.currentText()
        column_index=self.data.columns.get_loc(column_name)
        for row_index in range(self.model.rowCount()):
            cell_content=self.model.index(row_index,column_index).data()
            self.table_view.setRowHidden(row_index, value.lower() not in cell_content.lower())
    ## wybor kolumn do pokazania ##
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
    ## wysrodkowanie okna
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