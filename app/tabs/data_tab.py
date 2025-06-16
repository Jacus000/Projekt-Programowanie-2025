from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QLabel
from PyQt6.QtCore import Qt

from models.pandas_model import PandasModel


class DataTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.data_table = QTableView()
        self.data_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.data_table.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.hide()

        self.no_data_label = QLabel("No imported data set")
        self.no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.data_table)
        layout.addWidget(self.no_data_label)

    def update_data(self, data):
        """Update the data displayed in the table"""
        if data is not None:
            self.no_data_label.hide()
            self.data_table.show()

            model = PandasModel(data)
            self.data_table.setModel(model)
            self.data_table.resizeColumnsToContents()
        else:
            self.no_data_label.show()
            self.data_table.hide()