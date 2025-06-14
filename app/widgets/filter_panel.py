# widgets/filter_panel.py
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit, QComboBox
from PyQt6.QtCore import pyqtSignal
import pandas as pd


class FilterPanel(QFrame):
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
                combo = QComboBox()
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
            if isinstance(control, tuple):  # Numeric filter
                min_edit, max_edit = control
                try:
                    min_val = float(min_edit.text()) if min_edit.text() else None
                    max_val = float(max_edit.text()) if max_edit.text() else None
                    filters[column] = (min_val, max_val)
                except ValueError:
                    pass
            else:  # Categorical filter
                filters[column] = control.currentText()

        self.filters_applied.emit(filters)