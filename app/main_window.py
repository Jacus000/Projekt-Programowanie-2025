# main_window.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QMainWindow, QSplitter, QFrame, QStatusBar, QTabWidget, QVBoxLayout, QFileDialog, QLabel,
                             QMessageBox)
from PyQt6.QtGui import QAction
import pandas as pd
from tabs.data_tab import DataTab
from tabs.plot_tab import PlotTab
from tabs.regression_tab import RegressionDashboard
from widgets.filter_panel import FilterPanel
from tools.plot_generator import PlotGenerator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Shovel")
        self.setGeometry(100, 100, 1200, 800)
        self.current_data = None
        self.filtered_data = None

        self.init_ui()
        self.create_menu_bar()

    def init_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Main frame with tabs
        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.StyledPanel)
        main_layout = QVBoxLayout(main_frame)

        self.main_tabs = QTabWidget()
        self.data_tab = DataTab()
        self.plot_tab = PlotTab()
        

        self.main_tabs.addTab(self.data_tab, "Data")
        self.main_tabs.addTab(self.plot_tab, "Plots")
        

        main_layout.addWidget(self.main_tabs)

        # Filter frame
        self.filter_panel = FilterPanel()

        # Add to splitter
        splitter.addWidget(main_frame)
        splitter.addWidget(self.filter_panel)
        splitter.setSizes([800, 200])

        self.setCentralWidget(splitter)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Connect signals
        self.filter_panel.filters_applied.connect(self.apply_filters)
        self.plot_tab.plot_requested.connect(self.generate_plot)

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
        self.data_tab.update_data(self.current_data)
        self.filter_panel.update_controls(self.current_data)
        self.plot_tab.update_controls(self.current_data)
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
        if self.filtered_data is None:
            QMessageBox.warning(self, "Warning", "No data available to plot")
            return

        try:
            PlotGenerator.generate(
                data=self.filtered_data,
                **plot_params
            )
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