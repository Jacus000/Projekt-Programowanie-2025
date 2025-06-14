from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import pyqtSignal


class PlotTab(QWidget):
    plot_requested = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(['bar', 'line', 'scatter', 'box', 'violin', 'hist', 'heatmap'])
        layout.addWidget(QLabel("Plot Type:"))
        layout.addWidget(self.plot_type_combo)

        self.x_axis_combo = QComboBox()
        layout.addWidget(QLabel("X Axis:"))
        layout.addWidget(self.x_axis_combo)

        self.y_axis_combo = QComboBox()
        layout.addWidget(QLabel("Y Axis:"))
        layout.addWidget(self.y_axis_combo)

        self.hue_combo = QComboBox()
        self.hue_combo.addItem("None")
        layout.addWidget(QLabel("Hue (color by):"))
        layout.addWidget(self.hue_combo)

        plot_btn = QPushButton("Generate Plot")
        plot_btn.clicked.connect(self.on_plot_requested)
        layout.addWidget(plot_btn)

    def update_controls(self, data):
        """Update the plot controls when new data is loaded"""
        self.x_axis_combo.clear()
        self.y_axis_combo.clear()
        self.hue_combo.clear()

        self.x_axis_combo.addItem("None")
        self.y_axis_combo.addItem("None")
        self.hue_combo.addItem("None")

        if data is not None:
            for column in data.columns:
                self.x_axis_combo.addItem(column)
                self.y_axis_combo.addItem(column)
                self.hue_combo.addItem(column)

    def on_plot_requested(self):
        """Emit signal with plot parameters"""
        plot_params = {
            'plttype': self.plot_type_combo.currentText(),
            'x': self.x_axis_combo.currentText() if self.x_axis_combo.currentText() != "None" else None,
            'y': self.y_axis_combo.currentText() if self.y_axis_combo.currentText() != "None" else None,
            'hue': self.hue_combo.currentText() if self.hue_combo.currentText() != "None" else None
        }
        self.plot_requested.emit(plot_params)