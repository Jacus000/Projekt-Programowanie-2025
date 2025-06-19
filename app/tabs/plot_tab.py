from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class PlotTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_figure = None
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Create matplotlib Figure and FigureCanvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # Add navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

    def display_plot(self, figure):
        """Display a new plot in the tab"""
        # Clear current figure
        self.figure.clear()

        # Special handling for FacetGrid
        if hasattr(figure, 'axes'):
            # Copying axes
            for i, ax in enumerate(figure.axes):
                new_ax = self.figure.add_subplot(figure.axes[i].get_subplotspec())
                for line in ax.lines:
                    new_ax.plot(line.get_xdata(), line.get_ydata(),
                                color=line.get_color(), linestyle=line.get_linestyle())
                if ax.get_legend():
                    handles, labels = ax.get_legend_handles_labels()
                    new_ax.legend(handles, labels, title=ax.get_legend().get_title().get_text())
        else:
            # Regular plots
            ax = figure.axes[0]
            new_ax = self.figure.add_subplot(111)

            # Copy plot elements
            for line in ax.lines:
                new_ax.plot(line.get_xdata(), line.get_ydata(),
                            color=line.get_color(), linestyle=line.get_linestyle())

            for collection in ax.collections:
                new_ax.add_collection(collection)

            # Axis properties
            new_ax.set_title(ax.get_title())
            new_ax.set_xlabel(ax.get_xlabel())
            new_ax.set_ylabel(ax.get_ylabel())
            new_ax.set_xticks(ax.get_xticks())
            new_ax.set_yticks(ax.get_yticks())
            new_ax.set_xticklabels(ax.get_xticklabels())
            new_ax.set_yticklabels(ax.get_yticklabels())

        if ax.get_legend():
            handles, labels = ax.get_legend_handles_labels()
            new_ax.legend(handles, labels, title=ax.get_legend().get_title().get_text())

        self.canvas.draw()
        self.current_figure = figure

    def save_plot(self):
        """Save the current plot to a file"""
        if not self.current_figure:
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Plot", "",
            "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf);;SVG (*.svg)")

        if file_name:
            self.current_figure.savefig(file_name)

    def clear_plot(self):
        """Clear the current plot"""
        self.figure.clear()
        self.canvas.draw()
        self.current_figure = None