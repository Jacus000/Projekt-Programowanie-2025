
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QComboBox, QListWidget, QHBoxLayout, QListWidgetItem,QGroupBox,QSizePolicy,QMessageBox
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MatplotligCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure, self.axes = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.figure)
    def scatter_plot(self, data, x_columns, y_column):
        self.axes.clear()
        for x in x_columns:
            self.axes.scatter(data[x], data[y_column], label=x)
        self.axes.set_xlabel(', '.join(x_columns))
        self.axes.set_ylabel(y_column)
        self.axes.legend()
        self.draw()
class RegressionDashboard(QWidget):
    def __init__(self, data: pd.DataFrame=None):
        super().__init__()
        self.data = data.select_dtypes(include='number')
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        ## lewa strona wybor zmiennych
        selector_box=QGroupBox("Chose your variables")
        selector_box.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        selector_layout = QVBoxLayout()
        
        self.x_selector = QListWidget()
        self.x_selector.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.x_selector.setFont(QFont("Arial", 10))
        self.x_selector.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.x_selector.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.x_selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.x_selector.setMaximumHeight(150)

        for col in self.data.columns:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.x_selector.addItem(item)
        
        self.y_selector = QComboBox()
        self.y_selector.addItems(self.data.columns)
        
        self.plot_button=QPushButton("Scatter plot")
        self.plot_button.clicked.connect(self.plot_selected_variables)

        selector_layout.addWidget(QLabel("Select producing variables:"))
        selector_layout.addWidget(self.x_selector)
        selector_layout.addWidget(QLabel("Select targeted variable:"))
        selector_layout.addWidget(self.y_selector)
        selector_layout.addWidget(self.plot_button)

        selector_box.setLayout(selector_layout)

        left_layout=QVBoxLayout()
        left_layout.addWidget(selector_box)
        left_layout.addStretch()
        left_widget=QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        
        #prawa strona wykres
        self.canvas = MatplotligCanvas(self, width=5, height=4, dpi=100)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        main_layout.addWidget(left_widget)
        right_placeholder = QWidget()
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)
    
    def plot_selected_variables(self):
        x_columns, y_column = self.get_selected_variables()
        if not x_columns or not y_column:
            QMessageBox.warning(self, "Warning", "Please select at least one variable for X and one for Y.")
            return
        self.canvas.scatter_plot(self.data, x_columns, y_column)
        
        
    def get_selected_variables(self):
        x_columns=[]
        for i in range(self.x_selector.count()):
            item= self.x_selector.item(i)
            if item.checkState()==Qt.CheckState.Checked:
                x_columns.append(item.text())
        y_column=self.y_selector.currentText()
        return x_columns, y_column
    
    def train_model(self):
        # Placeholder for model training logic
        #elf.result_label.setText("Training model... (this is a placeholder)")
        pass