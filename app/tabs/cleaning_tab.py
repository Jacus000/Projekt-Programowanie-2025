from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QStackedWidget, QTableView, QLineEdit,
    QComboBox, QCheckBox, QRadioButton, QButtonGroup,
    QDoubleSpinBox, QTableWidget, QSplitter, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.models.pandas_model import PandasModel
import pandas as pd
import numpy as np


class DataCleaningTab(QWidget):
    cleaning_applied = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.df_original = None
        self.df_cleaned = None
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        self.setWindowTitle("Data Cleaning Tool")
        self.setMinimumSize(800, 600)
        
        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel with operations
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Operation selection
        left_layout.addWidget(QLabel("Cleaning Operations:"))
        self.operation_list = QListWidget()
        self.operation_list.addItems([
            "Manage Missing Values",
            "Remove Duplicates",
            "Change Data Type",
            "Clean Text"
        ])
        left_layout.addWidget(self.operation_list)
        
        left_layout.addWidget(QLabel("Operation Configuration:"))
        self.operation_stack = QStackedWidget()
        self.create_operation_panels()
        left_layout.addWidget(self.operation_stack)
        
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)

        splitter.addWidget(left_panel)
        splitter.addWidget(self.table_view)
        splitter.setStretchFactor(1, 2)
        
        button_panel = QWidget()
        button_layout = QHBoxLayout(button_panel)
        self.apply_btn = QPushButton("Apply Changes")
        self.reset_btn = QPushButton("Reset")
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.reset_btn)
        
        main_layout.addWidget(splitter)
        main_layout.addWidget(button_panel)

    def setup_connections(self):
        """Connect signals and slots"""
        self.operation_list.currentRowChanged.connect(self.operation_stack.setCurrentIndex)
        self.apply_btn.clicked.connect(self.apply_changes)
        self.reset_btn.clicked.connect(self.reset_data)
        self.fill_btn.clicked.connect(self.fill_missing_values)
        self.remove_rows_with_any_missing_btn.clicked.connect(self.remove_rows_with_any_missing)
        self.remove_cols_by_threshold_btn.clicked.connect(self.remove_cols_by_threshold)
        self.remove_dup_btn.clicked.connect(self.remove_duplicates)
        self.convert_btn.clicked.connect(self.change_dtype)
        self.clean_text_btn.clicked.connect(self.clean_text)

    def create_operation_panels(self):
        """Initialize all operation panels"""
        self.operation_stack.addWidget(self.create_missing_values_panel())
        self.operation_stack.addWidget(self.create_duplicates_panel())
        self.operation_stack.addWidget(self.create_dtype_panel())
        self.operation_stack.addWidget(self.create_text_clean_panel())

    def create_missing_values_panel(self):
        """Panel for handling missing values"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Missing value summary
        self.missing_summary = QLabel("No data loaded")
        self.missing_summary.setWordWrap(True)
        layout.addWidget(self.missing_summary)
        
        #Threshold control
        threshold_layout = QFormLayout()
        self.missing_threshold = QDoubleSpinBox()
        self.missing_threshold.setRange(0, 100)
        self.missing_threshold.setValue(5)
        self.missing_threshold.setSuffix("%")
        threshold_layout.addRow("Missing value threshold:", self.missing_threshold)
        layout.addLayout(threshold_layout)
        
 
        self.missing_column_cb = QComboBox()
        self.missing_column_cb.setPlaceholderText("Select column")
        layout.addWidget(QLabel("Column to fill:"))
        layout.addWidget(self.missing_column_cb)
        
        self.fill_method_cb = QComboBox()
        self.fill_method_cb.addItems(["Mean", "Median", "Mode", "Constant Value", "Forward Fill", "Backward Fill"])
        layout.addWidget(QLabel("Fill method:"))
        layout.addWidget(self.fill_method_cb)
        
        # Custom value
        self.custom_value = QLineEdit()
        self.custom_value.setPlaceholderText("Enter custom fill value")
        layout.addWidget(QLabel("Custom value (if applicable):"))
        layout.addWidget(self.custom_value)
        
        btn_layout = QHBoxLayout()
        self.fill_btn = QPushButton("Fill Selected")
        self.fill_all_btn = QPushButton("Fill All Columns")
        self.remove_rows_with_any_missing_btn = QPushButton("Remove All Rows with Any Missing Values")
        self.remove_cols_by_threshold_btn = QPushButton("Remove Columns by Threshold")
        btn_layout.addWidget(self.fill_btn)
        btn_layout.addWidget(self.fill_all_btn)
        btn_layout.addWidget(self.remove_rows_with_any_missing_btn)
        btn_layout.addWidget(self.remove_cols_by_threshold_btn)
        layout.addLayout(btn_layout)
        
        return panel

    def create_duplicates_panel(self):
        """Panel for removing duplicates"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Column selection
        self.dup_columns = QListWidget()
        self.dup_columns.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(QLabel("Columns to check:"))
        layout.addWidget(self.dup_columns)

        self.keep_group = QButtonGroup()
        self.keep_first = QRadioButton("Keep first")
        self.keep_last = QRadioButton("Keep last")
        self.keep_none = QRadioButton("Remove all")
        self.keep_first.setChecked(True)
        
        for i, btn in enumerate([self.keep_first, self.keep_last, self.keep_none]):
            self.keep_group.addButton(btn, i)
            layout.addWidget(btn)
        
        self.remove_dup_btn = QPushButton("Remove Duplicates")
        layout.addWidget(self.remove_dup_btn)
        
        return panel

    def create_dtype_panel(self):
        """Panel for changing data types"""
        panel = QWidget()
        layout = QFormLayout(panel)
        
        self.dtype_column = QComboBox()
        self.dtype_target = QComboBox()
        self.dtype_target.addItems(["str", "int", "float", "bool", "datetime"])
        
        layout.addRow("Column:", self.dtype_column)
        layout.addRow("Convert to:", self.dtype_target)
        
        self.convert_btn = QPushButton("Convert")
        layout.addRow(self.convert_btn)
        
        return panel

    def create_text_clean_panel(self):
        """Panel for text cleaning"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        self.text_column = QComboBox()
        layout.addWidget(QLabel("Text column:"))
        layout.addWidget(self.text_column)
        self.trim_ws = QCheckBox("Trim whitespace")
        self.lowercase = QCheckBox("Convert to lowercase")
        self.remove_special = QCheckBox("Remove special characters")
        for cb in [self.trim_ws, self.lowercase, self.remove_special]:
            layout.addWidget(cb)
        self.clean_text_btn = QPushButton("Clean Text")
        layout.addWidget(self.clean_text_btn)
        return panel

    def set_data(self, df: pd.DataFrame):
        """Set the data to be cleaned"""
        self.df_original = df.copy()
        self.df_cleaned = df.copy()
        self.update_ui()
        
    def update_ui(self):
        """Update all UI elements based on current data"""
        self.update_table_view()
        self.update_missing_values_panel()
        self.update_duplicates_panel()
        self.update_dtype_panel()
        self.update_text_clean_panel()
        
    def update_table_view(self):
        """Update the table view with current data"""
        if self.df_cleaned is not None:
            model = PandasModel(self.df_cleaned)
            self.table_view.setModel(model)
            self.table_view.resizeColumnsToContents()

    def update_missing_values_panel(self):
        """Update missing values panel with current data"""
        if self.df_cleaned is None:
            return
        missing_counts = self.df_cleaned.isnull().sum()
        total_missing = missing_counts.sum()
        total_cells = self.df_cleaned.size
        summary = f"Missing values: {total_missing}/{total_cells} ({total_missing/total_cells:.1%})\n"
        summary += "\nColumns with missing values:\n"
        summary += "\n".join(f"• {col}: {count} ({count/len(self.df_cleaned):.1%})" 
                           for col, count in missing_counts.items() if count > 0)
        self.missing_summary.setText(summary)
        self.missing_column_cb.clear()
        self.missing_column_cb.addItems(
            [col for col in self.df_cleaned.columns if np.any(self.df_cleaned[col].isnull())]
        )

    def update_duplicates_panel(self):
        """Update duplicates panel with current data"""
        if self.df_cleaned is None:
            return
            
        self.dup_columns.clear()
        self.dup_columns.addItems(self.df_cleaned.columns)

    def update_dtype_panel(self):
        """Update dtype panel with current data"""
        if self.df_cleaned is None:
            return
            
        self.dtype_column.clear()
        self.dtype_column.addItems(self.df_cleaned.columns)

    def update_text_clean_panel(self):
        """Update text cleaning panel with current data"""
        if self.df_cleaned is None:
            return
            
        self.text_column.clear()
        self.text_column.addItems(
            col for col in self.df_cleaned.columns 
            if pd.api.types.is_string_dtype(self.df_cleaned[col])
        )

    def fill_missing_values(self):
        """Fill missing values in selected column"""
        if self.df_cleaned is None:
            return
        col = self.missing_column_cb.currentText()
        method = self.fill_method_cb.currentText()
        
        if not col:
            return
            
        value = None
        if method == "Mean":
            value = self.df_cleaned[col].mean()
        elif method == "Median":
            value = self.df_cleaned[col].median()
        elif method == "Mode":
            value = self.df_cleaned[col].mode().iloc[0] if not self.df_cleaned[col].mode().empty else None
        elif method == "Constant Value":
            value = self.custom_value.text()
            try:
                value = eval(value)
            except:
                pass
        elif method == "Forward Fill":
            self.df_cleaned[col] = self.df_cleaned[col].fillna(method='ffill')
            self.update_ui()
            return
        elif method == "Backward Fill":
            self.df_cleaned[col] = self.df_cleaned[col].fillna(method='bfill')
            self.update_ui()
            return
            
        if value is not None:
            self.df_cleaned[col] = self.df_cleaned[col].fillna(value)
            self.update_ui()
            self.update_table_view()

    def remove_rows_with_any_missing(self):
        if self.df_cleaned is None:
            return
        self.df_cleaned = self.df_cleaned.dropna().copy()
        self.update_ui()

    def remove_cols_by_threshold(self):
        if self.df_cleaned is None:
            return
        threshold = self.missing_threshold.value() / 100.0
        self.df_cleaned = self.df_cleaned.loc[:, self.df_cleaned.isnull().mean() < threshold].copy()
        self.update_ui()

    def remove_duplicates(self):
        """Remove duplicate rows"""
        if self.df_cleaned is None:
            return
        subset = [item.text() for item in self.dup_columns.selectedItems()] or None
        keep = {
            0: 'first',
            1: 'last',
            2: False
        }[self.keep_group.checkedId()]
        
        self.df_cleaned = self.df_cleaned.drop_duplicates(subset=subset, keep=keep).copy()
        self.update_ui()

    def change_dtype(self):
        if self.df_cleaned is None:
            return
        col = self.dtype_column.currentText()
        target_type = self.dtype_target.currentText()
        if not col:
            return
        try:
            if target_type == 'datetime':
                self.df_cleaned[col] = pd.to_datetime(self.df_cleaned[col], errors='coerce')
            else:
                self.df_cleaned[col] = self.df_cleaned[col].astype(target_type)
            self.update_ui()
        except Exception:
            pass

    def clean_text(self):
        if self.df_cleaned is None:
            return
        col = self.text_column.currentText()
        if not col:
            return
        series = self.df_cleaned[col].astype(str)
        if self.trim_ws.isChecked():
            series = series.str.strip()
        if self.lowercase.isChecked():
            series = series.str.lower()
        if self.remove_special.isChecked():
            series = series.str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
        self.df_cleaned[col] = series
        self.update_ui()

    def apply_changes(self):
        """Apply all changes"""
        if self.df_cleaned is None:
            return
        self.df_original = self.df_cleaned.copy()
        self.update_ui()
        self.cleaning_applied.emit()

    def reset_data(self):
        """Reset to original data"""
        if self.df_original is not None:
            self.df_cleaned = self.df_original.copy()
            self.update_ui()