import os

from PyQt6.QtCore import Qt
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QMainWindow, QSplitter, QFrame, QStatusBar, QTabWidget, QVBoxLayout, QFileDialog, QLabel,
                             QMessageBox)
from PyQt6.QtGui import QAction, QIcon
import pandas as pd

from app.tabs.data_tab import DataTab
from app.tabs.plot_tab import PlotTab
from app.tabs.regression_tab import RegressionDashboard
from app.widgets.side_panel import SidePanel, FilterWidget, PlotWidget
from app.tools.plot_generator import PlotGenerator
from app.tabs.cleaning_tab import DataCleaningTab

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Shovel")
        self.setWindowIcon(QIcon(f'{BASE_DIR}/logo.png'))
        self.setGeometry(100, 100, 1200, 800)
        self.current_data = None
        self.filtered_data = None

        self.init_ui()
        self.create_menu_bar()

        QTimer.singleShot(0, self.showMaximized)


    def init_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Main frame with tabs
        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.StyledPanel)
        main_layout = QVBoxLayout(main_frame)

        self.main_tabs = QTabWidget()
        self.data_tab = DataTab()
        self.plot_tab = PlotTab()
        self.cleaning_tab = DataCleaningTab()
        self.regression_tab = None  # Będzie tworzony przy ładowaniu danych

        self.main_tabs.addTab(self.data_tab, "Data")
        self.main_tabs.addTab(self.plot_tab, "Plots")
        self.main_tabs.addTab(self.cleaning_tab, "Data Cleaning")

        main_layout.addWidget(self.main_tabs)

        # Side panel
        self.side_panel = SidePanel()

        # Add to splitter
        splitter.addWidget(main_frame)
        splitter.addWidget(self.side_panel)
        splitter.setSizes([800, 200])

        self.setCentralWidget(splitter)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Connect signals
        self.side_panel.filter_widget.filters_applied.connect(self.apply_filters)
        self.side_panel.plot_widget.plot_requested.connect(self.generate_plot)
        self.cleaning_tab.cleaning_applied.connect(self.update_after_cleaning)

        # Connect tab change signal
        self.main_tabs.currentChanged.connect(self.handle_tab_change)

    def handle_tab_change(self, index):
        """Handle tab changes to show/hide side panel"""
        current_tab = self.main_tabs.tabText(index)

        if current_tab in ["Data Cleaning", "Regression"]:
            # Ukryj cały side panel dla tych zakładek
            self.side_panel.hide()
        else:
            # Pokaż side panel dla innych zakładek
            self.side_panel.show()

            # Dodatkowa logika dla zakładek z panelami bocznymi
            if current_tab == "Plots":
                self.side_panel.filter_widget.hide()
                self.side_panel.plot_widget.show()
            else:  # Dla "Data" i innych
                self.side_panel.plot_widget.hide()
                self.side_panel.filter_widget.show()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def open_file(self):
        options = QFileDialog.Option.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Data File", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)",
            options=options)

        if file_name:
            try:
                if file_name.endswith('.csv'):
                    self.current_data = pd.read_csv(file_name)
                else:
                    self.current_data = pd.read_excel(file_name)

                if self.current_data is not None:
                    self.update_ui_with_data()
                    self.status_bar.addPermanentWidget(QLabel(f"Loaded {len(self.current_data)} rows"))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")

    def update_ui_with_data(self):
        """Update all UI elements when new data is loaded"""
        if self.current_data is None:
            return
        self.data_tab.update_data(self.current_data)
        self.side_panel.update_data(self.current_data)
        self.cleaning_tab.set_data(self.current_data)
        self.filtered_data = self.current_data.copy()

        for i in range(self.main_tabs.count()):
            if self.main_tabs.tabText(i) == "Regression":
                self.main_tabs.removeTab(i)
                break

        self.regression_tab = RegressionDashboard(self.current_data)
        self.main_tabs.addTab(self.regression_tab, "Regression")

    def apply_filters(self, filters):
        """Apply filters to the data"""
        if self.current_data is None:
            return

        filtered_data = self.current_data.copy()

        for column, filter_value in filters.items():
            if pd.api.types.is_numeric_dtype(self.current_data[column]):
                min_val, max_val = filter_value
                if min_val is not None:
                    filtered_data = filtered_data[filtered_data[column] >= min_val]
                if max_val is not None:
                    filtered_data = filtered_data[filtered_data[column] <= max_val]
            else:
                if filter_value != "(All)":
                    filtered_data = filtered_data[filtered_data[column].astype(str) == filter_value]

        self.filtered_data = filtered_data
        self.data_tab.update_data(filtered_data)
        self.status_bar.showMessage(f"Filtered data: {len(filtered_data)} rows", 3000)

    def generate_plot(self, plot_params):
        """Generate plot based on parameters"""
        if self.filtered_data is None or self.filtered_data.empty:
            QMessageBox.warning(self, "Warning", "No data available to plot")
            return

        try:
            figure = PlotGenerator.generate(data=self.filtered_data,  **plot_params)

            if figure:
                self.plot_tab.display_plot(figure)
            else:
                QMessageBox.warning(self, "Warning", "Failed to generate plot")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate plot:\n{str(e)}")

    def show_about(self):
        QMessageBox.about(self, "About",
                          "A basic data analysis tool with:\n"
                          "- Data importing and exporting\n"
                          "- Data cleaning\n"
                          "- Statistical analysis\n"
                          "- Linear regression\n"
                          "- Visualise with plots")

    def update_after_cleaning(self):
        """Called when cleaning tab applies changes"""
        if self.cleaning_tab.df_cleaned is not None:
            self.current_data = self.cleaning_tab.df_cleaned.copy()
            self.update_ui_with_data()