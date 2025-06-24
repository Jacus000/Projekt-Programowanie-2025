import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QComboBox, QListWidget, QHBoxLayout, \
    QListWidgetItem, QGroupBox, QSizePolicy, QMessageBox, QTextEdit
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from sklearn.preprocessing import StandardScaler

class MatplotligCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure, self.axes = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.figure)
    def scatter_plot(self, data, x_columns, y_column):
        self.axes.clear()

        # Mapowanie długich nazw na skrócone dla legendy
        label_map = {
            "Age": "Age",
            "Yearly brutto salary (without bonus and stocks) in EUR": "Yearly brutto salary",
            "Annual brutto salary (without bonus and stocks) one year ago. Only answer if staying in the same country": "Annual brutto salary",
            "Have you been forced to have a shorter working week (Kurzarbeit)? If yes, how many hours per week": "Shorter working hours"
        }

        for x in x_columns:
            short_label = label_map.get(x, x[:25])  # jeśli nie w mapie, skróć do 25 znaków
            self.axes.scatter(data[x], data[y_column], label=short_label)
        short_x_labels = [str(label_map.get(x, x[:25])) for x in x_columns]
        short_y_label = str(label_map.get(y_column, y_column[:25]))
        self.axes.set_xlabel(', '.join(short_x_labels))
        self.axes.set_ylabel(short_y_label)

        self.axes.legend()
        self.draw()


class RegressionDashboard(QWidget):
    def __init__(self, data: pd.DataFrame | None = None):
        super().__init__()
        self.data = pd.DataFrame()
        if data is not None and not data.empty:
            data = self.convert_numeric_columns(data)
            self.data = data.select_dtypes(include='number')
        self.init_ui()

    #zamiana wszystkich danych postaci np 43 na 43.0
    def convert_numeric_columns(self,data):
        data=data.copy()
        for col in data.select_dtypes(include=["string","object"]).columns:
            try:
                data[col]=pd.to_numeric(data[col],errors="raise")
            except:
                pass
        return data

    def init_ui(self):
        main_layout = QHBoxLayout()
        ## lewa strona wybor zmiennych
        selector_box=QGroupBox("Chose your variables")
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

        for col in self.data.columns:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.x_selector.addItem(item)

        self.y_selector = QComboBox()
        self.y_selector.addItems(self.data.columns)

        # Dodajemy rozwijane menu z wyborem modelu regresji
        self.model_selector = QComboBox()
        self.model_selector.addItems(["Linear", "Ridge", "Lasso"])
        selector_layout.addWidget(QLabel("Regression model:"))
        selector_layout.addWidget(self.model_selector)

        # Pole na alpha
        self.alpha_input = QLineEdit("1.0")
        self.alpha_input.setPlaceholderText("Alpha (for Ridge/Lasso)")
        selector_layout.addWidget(self.alpha_input)

        self.plot_button=QPushButton("Scatter plot")
        self.plot_button.clicked.connect(self.plot_selected_variables)

        selector_layout.addWidget(QLabel("Select producing variables:"))
        selector_layout.addWidget(self.x_selector)
        selector_layout.addWidget(QLabel("Select targeted variable:"))
        selector_layout.addWidget(self.y_selector)
        selector_layout.addWidget(self.plot_button)

        # Przycisk trenowania modelu regresji liniowej
        self.train_button = QPushButton("Train model")
        self.train_button.clicked.connect(self.train_model)
        selector_layout.addWidget(self.train_button)

        # Pole na wyniki regresji
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setStyleSheet("background-color: white; color: black; font-family: Consolas; font-size: 10pt;")
        selector_layout.addWidget(QLabel("Model coefficients:"))
        selector_layout.addWidget(self.result_box)

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
            if item and item.checkState()==Qt.CheckState.Checked:
                x_columns.append(item.text())
        y_column=self.y_selector.currentText()
        return x_columns, y_column

    def train_model(self):
        x_columns, y_column = self.get_selected_variables()
        if not x_columns or not y_column:
            QMessageBox.warning(self, "Warning", "Please select at least one variable for X and one for Y.")
            return

        try:
            # Tworzymy kopię danych X i Y
            X = self.data[x_columns].copy()
            y = self.data[[y_column]].copy()  # nawet jeśli Y == X, tworzymy jako DataFrame

            # Tymczasowo zmieniamy nazwy kolumn na unikalne (dodajemy suffix)
            X.columns = [f"{col}_X" for col in X.columns]
            y.columns = [f"{y_column}_Y"]

            # Łączymy dane i usuwamy NaN
            df = pd.concat([X, y], axis=1).dropna()

            # Oddzielamy dane czyste
            X_clean = df[X.columns]
            y_clean = df[y.columns[0]]

            # Konwersja do typów liczbowych
            for col in X_clean.columns:
                X_clean.loc[:, col] = pd.to_numeric(X_clean[col], errors='raise')
            y_clean = pd.to_numeric(y_clean, errors='raise')

            # Skalowanie cech (standaryzacja)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_clean)

            # Pobierz model z wyboru użytkownika
            model_type = self.model_selector.currentText().lower()
            alpha = 1.0  # domyślna wartość

            if model_type in ["ridge", "lasso"]:
                try:
                    alpha = float(self.alpha_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Błąd", "Alpha musi być liczbą zmiennoprzecinkową.")
                    return

            # Wybierz i trenuj odpowiedni model
            if model_type == "linear":
                model = LinearRegression()
            elif model_type == "ridge":
                model = Ridge(alpha=alpha)
            elif model_type == "lasso":
                model = Lasso(alpha=alpha)

            model.fit(X_scaled, y_clean)
            score = model.score(X_scaled, y_clean)

            # Zbuduj tekst z wynikami
            coef_info = "Intercept (b0): {:.4f}\n".format(model.intercept_)
            for col, coef in zip(X_clean.columns, model.coef_):
                coef_info += f"{col}: {coef:.4f}\n"

            html = f"<b>R² Score:</b> {score:.4f}<br><br>"
            html += f"<b style='color:black;'>Intercept (b0):</b> {model.intercept_:.4f}<br>"

            for col, coef in zip(X_clean.columns, model.coef_):
                color = "green" if coef >= 0 else "red"
                html += f"<span style='color:{color};'>{col}: {coef:.4f}</span><br>"

            self.result_box.setHtml(html)

            QMessageBox.information(self, "Model Trained",
                                    f"Regression model trained successfully.\n\nR² Score: {score:.4f}")

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"An error occurred during training:\n{str(e)}")
