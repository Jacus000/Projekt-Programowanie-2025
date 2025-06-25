import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QComboBox, QListWidget, QHBoxLayout, \
    QListWidgetItem, QGroupBox, QSizePolicy, QMessageBox, QTextEdit
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.metrics import mean_squared_error

# Klasa do rysowania wykresu matplotlib
class MatplotligCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure, self.axes = plt.subplots(figsize=(width, height), dpi=dpi)  # tworzy figure i osie
        super().__init__(self.figure)

    def scatter_plot(self, data, x_columns, y_column):
        self.axes.clear()  # czyszczenie wykresu

        # Mapowanie długich nazw na skrócone dla legendy
        label_map = {
            "Age": "Age",
            "Yearly brutto salary (without bonus and stocks) in EUR": "Yearly brutto salary",
            "Annual brutto salary (without bonus and stocks) one year ago. Only answer if staying in the same country": "Annual brutto salary",
            "Have you been forced to have a shorter working week (Kurzarbeit)? If yes, how many hours per week": "Shorter working hours"
        }

        for x in x_columns:
            short_label = label_map.get(x, x[:25])  # jesli nie ma w mapie, skracamy
            self.axes.scatter(data[x], data[y_column], label=short_label)  # rysowanie punktow

        short_x_labels = [str(label_map.get(x, x[:25])) for x in x_columns]
        short_y_label = str(label_map.get(y_column, y_column[:25]))
        self.axes.set_xlabel(', '.join(short_x_labels))
        self.axes.set_ylabel(short_y_label)
        self.axes.legend()
        self.draw()  # aktualizacja wykresu

# Klasa glowna aplikacji regresji
class RegressionDashboard(QWidget):
    def __init__(self, data: pd.DataFrame | None = None):
        super().__init__()
        self.data = pd.DataFrame()
        if data is not None and not data.empty:
            data = self.convert_numeric_columns(data)  # konwersja na liczby
            self.data = data.select_dtypes(include='number')  # tylko kolumny liczbowe
        self.init_ui()  # inicjalizacja interfejsu

    # Konwersja kolumn tekstowych na liczbowe (jesli mozliwe)
    def convert_numeric_columns(self, data):
        data = data.copy()
        for col in data.select_dtypes(include=["string", "object"]).columns:
            try:
                data[col] = pd.to_numeric(data[col], errors="raise")
            except:
                pass
        return data

    # Tworzenie interfejsu uzytkownika
    def init_ui(self):
        main_layout = QHBoxLayout()

        # LEWA STRONA - selekcja zmiennych
        selector_box = QGroupBox("Chose your variables")
        selector_box.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        selector_box.setMaximumWidth(450)
        selector_layout = QVBoxLayout()

        self.x_selector = QListWidget()
        self.x_selector.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.x_selector.setFont(QFont("Arial", 10))
        self.x_selector.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.x_selector.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.x_selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.x_selector.setMaximumHeight(200)

        # Dodanie zmiennych X jako lista checkboxow
        for col in self.data.columns:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.x_selector.addItem(item)

        # ComboBox do wyboru zmiennej celu Y
        self.y_selector = QComboBox()
        self.y_selector.addItems(self.data.columns)

        # Wybor modelu regresji
        self.model_selector = QComboBox()
        self.model_selector.addItems(["Linear", "Ridge", "Lasso"])
        selector_layout.addWidget(QLabel("Regression model:"))
        selector_layout.addWidget(self.model_selector)

        # Pole do wprowadzenia alpha
        self.alpha_input = QLineEdit("1.0")
        self.alpha_input.setPlaceholderText("Alpha (for Ridge/Lasso)")
        selector_layout.addWidget(self.alpha_input)

        # Przycisk do rysowania wykresu
        self.plot_button = QPushButton("Scatter plot")
        self.plot_button.clicked.connect(self.plot_selected_variables)

        # Dodanie widgetow do layoutu
        selector_layout.addWidget(QLabel("Select producing variables:"))
        selector_layout.addWidget(self.x_selector)
        selector_layout.addWidget(QLabel("Select targeted variable:"))
        selector_layout.addWidget(self.y_selector)
        selector_layout.addWidget(self.plot_button)

        # Przycisk treningu modelu
        self.train_button = QPushButton("Train model")
        self.train_button.clicked.connect(self.train_model)
        selector_layout.addWidget(self.train_button)

        # Pole na wyniki modelu
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setStyleSheet("background-color: white; color: black; font-family: Consolas; font-size: 10pt;")
        selector_layout.addWidget(QLabel("Model coefficients:"))
        selector_layout.addWidget(self.result_box)

        # Grupa do przewidywania nowej wartosci
        self.predict_group = QGroupBox("Predict new value")
        predict_layout = QVBoxLayout()
        self.predict_inputs = []
        self.predict_button = QPushButton("Predict")
        self.predict_button.clicked.connect(self.predict_value)
        self.predict_result = QLabel("")
        self.predict_result.setWordWrap(True)
        self.predict_group.setLayout(predict_layout)
        selector_layout.addWidget(self.predict_group)
        self.predict_group.hide()

        selector_box.setLayout(selector_layout)

        # Opakowanie lewej kolumny
        left_layout = QVBoxLayout()
        left_layout.addWidget(selector_box)
        left_layout.addStretch()
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)

        # PRAWA STRONA - obszar rysowania
        self.canvas = MatplotligCanvas(self, width=5, height=4, dpi=100)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.canvas)
        self.setLayout(main_layout)

    # Pobranie zaznaczonych zmiennych
    def get_selected_variables(self):
        x_columns = []
        for i in range(self.x_selector.count()):
            item = self.x_selector.item(i)
            if item and item.checkState() == Qt.CheckState.Checked:
                x_columns.append(item.text())
        y_column = self.y_selector.currentText()
        return x_columns, y_column

    # Rysowanie wykresu scatter
    def plot_selected_variables(self):
        x_columns, y_column = self.get_selected_variables()
        if not x_columns or not y_column:
            QMessageBox.warning(self, "Warning", "Please select at least one variable for X and one for Y.")
            return
        self.canvas.scatter_plot(self.data, x_columns, y_column)

    # Trening modelu regresji
    def train_model(self):
        x_columns, y_column = self.get_selected_variables()
        if not x_columns or not y_column:
            QMessageBox.warning(self, "Warning", "Please select at least one variable for X and one for Y.")
            return

        try:
            X = self.data[x_columns].copy()
            y = self.data[[y_column]].copy()
            X.columns = [f"{col}_X" for col in X.columns]  # zmiana nazw kolumn X
            y.columns = [f"{y_column}_Y"]
            df = pd.concat([X, y], axis=1).dropna()  # usuniecie brakow
            X_clean = df[X.columns]
            y_clean = df[y.columns[0]]

            for col in X_clean.columns:
                X_clean.loc[:, col] = pd.to_numeric(X_clean[col], errors='raise')
            y_clean = pd.to_numeric(y_clean, errors='raise')

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_clean)  # standaryzacja

            model_type = self.model_selector.currentText().lower()
            alpha = 1.0
            if model_type in ["ridge", "lasso"]:
                try:
                    alpha = float(self.alpha_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Blad", "Alpha musi byc liczba zmiennoprzecinkowa.")
                    return

            if model_type == "linear":
                model = LinearRegression()
            elif model_type == "ridge":
                model = Ridge(alpha=alpha)
            elif model_type == "lasso":
                model = Lasso(alpha=alpha)

            model.fit(X_scaled, y_clean)  # trening
            score = model.score(X_scaled, y_clean)
            y_pred = model.predict(X_scaled)
            rmse = mean_squared_error(y_clean, y_pred, squared=False)

            # Wyswietlenie wspolczynnikow
            html = f"<b>R² Score:</b> {score:.4f}<br>"
            html += f"<b>RMSE:</b> {rmse:.4f}<br><br>"
            html += f"<b style='color:black;'>Intercept (b0):</b> {model.intercept_:.4f}<br>"
            for col, coef in zip(X_clean.columns, model.coef_):
                color = "green" if coef >= 0 else "red"
                html += f"<span style='color:{color};'>{col}: {coef:.4f}</span><br>"
            self.result_box.setHtml(html)

            # Przechowanie modelu
            self._trained_model = model
            self._trained_scaler = scaler
            self._trained_x_columns = list(X_clean.columns)
            self._trained_y_column = y_column

            # Przygotowanie interfejsu do predykcji
            self.setup_predict_inputs(x_columns)
            self.predict_group.show()

            QMessageBox.information(self, "Model Trained",
                                    f"Regression model trained successfully.\n\nR² Score: {score:.4f}\nRMSE: {rmse:.4f}")

            # Rysowanie linii regresji dla 1 zmiennej
            if len(x_columns) == 1:
                self.plot_regression_line(X_clean, y_clean, model, scaler, x_columns[0], y_column)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"An error occurred during training:\n{str(e)}")

    # Tworzenie pol do przewidywania
    def setup_predict_inputs(self, x_columns):
        layout = self.predict_group.layout()
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.predict_inputs = []
        for col in x_columns:
            h = QHBoxLayout()
            label = QLabel(col)
            edit = QLineEdit()
            edit.setPlaceholderText(f"Enter value for {col}")
            h.addWidget(label)
            h.addWidget(edit)
            layout.addLayout(h)
            self.predict_inputs.append(edit)
        layout.addWidget(self.predict_button)
        layout.addWidget(self.predict_result)

    # Przewidywanie nowej wartosci
    def predict_value(self):
        try:
            values = []
            for edit in self.predict_inputs:
                val = float(edit.text())
                values.append(val)
            X = np.array(values).reshape(1, -1)
            X_scaled = self._trained_scaler.transform(X)
            y_pred = self._trained_model.predict(X_scaled)
            self.predict_result.setText(f"Predicted {self._trained_y_column}: {y_pred[0]:.4f}")
        except Exception as e:
            self.predict_result.setText(f"Prediction error: {e}")

    # Rysowanie linii regresji (dla 1 zmiennej)
    def plot_regression_line(self, X_clean, y_clean, model, scaler, x_col, y_col):
        x_vals = X_clean[x_col + '_X'].values
        x_range = np.linspace(x_vals.min(), x_vals.max(), 100)
        X_pred = np.zeros((100, X_clean.shape[1]))
        X_pred[:, 0] = x_range
        X_pred_scaled = scaler.transform(X_pred)
        y_pred = model.predict(X_pred_scaled)
        self.canvas.axes.clear()
        self.canvas.axes.scatter(x_vals, y_clean, label='Data')
        self.canvas.axes.plot(x_range, y_pred, color='orange', label='Regression line')
        self.canvas.axes.set_xlabel(x_col)
        self.canvas.axes.set_ylabel(y_col)
        self.canvas.axes.legend()
        self.canvas.draw()
