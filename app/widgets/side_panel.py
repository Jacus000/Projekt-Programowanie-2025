from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QLabel, QPushButton,
                             QHBoxLayout, QLineEdit, QComboBox, QGroupBox, QWidget)
from PyQt6.QtCore import pyqtSignal, Qt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


class SidePanel(QFrame):
    """Container for FilterWidget, PlotWidget"""
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Toggle button
        self.toggle_btn = QPushButton("Switch to Plot Mode")
        self.toggle_btn.clicked.connect(self.toggle_panels)
        self.layout.addWidget(self.toggle_btn)

        # Create both panels
        self.filter_widget = FilterWidget()
        self.plot_widget = PlotWidget()
        self.plot_widget.hide()

        self.layout.addWidget(self.filter_widget)
        self.layout.addWidget(self.plot_widget)
        self.layout.addStretch()

    def toggle_panels(self):
        """Switch between filter and plot panels"""
        if self.filter_widget.isVisible():
            self.filter_widget.hide()
            self.plot_widget.show()
            self.toggle_btn.setText("Switch to Filter Mode")
        else:
            self.filter_widget.show()
            self.plot_widget.hide()
            self.toggle_btn.setText("Switch to Plot Mode")

    def update_data(self, data):
        """Update both panels with new data"""
        self.filter_widget.update_controls(data)
        self.plot_widget.update_controls(data)


class FilterWidget(QFrame):
    filters_applied = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Filter data"))

        self.filter_controls_layout = QVBoxLayout()
        layout.addLayout(self.filter_controls_layout)

        self.filter_placeholder = QLabel("Filters will appear here after loading data")
        self.filter_controls_layout.addWidget(self.filter_placeholder)

        apply_btn = QPushButton("Apply filters")
        apply_btn.clicked.connect(self.on_apply_filters)
        layout.addWidget(apply_btn)

    def update_controls(self, data):
        """Update filter controls based on data"""
        self.filter_placeholder.hide()
        # TODO: fix= clear_controls() - after importing new file num type adds up
        # Clear existing controls
        for i in reversed(range(self.filter_controls_layout.count())):
            widget = self.filter_controls_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.filter_controls = {}

        if data is None:
            return

        for column in data.columns:
            label = QLabel(column)
            self.filter_controls_layout.addWidget(label)

            if pd.api.types.is_numeric_dtype(data[column]):
                min_val = data[column].min()
                max_val = data[column].max()

                min_edit = QLineEdit(str(min_val))
                max_edit = QLineEdit(str(max_val))

                hbox = QHBoxLayout()
                hbox.addWidget(QLabel("Min:"))
                hbox.addWidget(min_edit)
                hbox.addWidget(QLabel("Max:"))
                hbox.addWidget(max_edit)

                self.filter_controls_layout.addLayout(hbox)
                self.filter_controls[column] = (min_edit, max_edit)
            else:
                unique_values = data[column].unique()
                combo = NoScrollCBox()
                combo.addItem("(All)")
                combo.addItems(map(str, unique_values))
                self.filter_controls_layout.addWidget(combo)
                self.filter_controls[column] = combo


    def on_apply_filters(self):
        """Collect filter values and emit signal"""
        if not hasattr(self, 'filter_controls'):
            return

        filters = {}

        for column, control in self.filter_controls.items():
            if isinstance(control, tuple):
                min_edit, max_edit = control
                try:
                    min_val = float(min_edit.text()) if min_edit.text() else None
                    max_val = float(max_edit.text()) if max_edit.text() else None
                    filters[column] = (min_val, max_val)
                except ValueError:
                    pass
            else:
                filters[column] = control.currentText()

        self.filters_applied.emit(filters)


class PlotWidget(QFrame):
    plot_requested = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.current_data = None
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


class NoScrollCBox(QComboBox):
    """disable changing ComboBox options using scroll"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        event.ignore()