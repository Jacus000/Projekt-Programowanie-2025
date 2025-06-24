from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout
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

        # Add buttons
        self.button_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear Plot")
        self.clear_button.clicked.connect(self.clear_plot)

        self.button_layout.addWidget(self.clear_button)

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.layout.addLayout(self.button_layout)

    def display_plot(self, figure):
        """Display a new plot in the tab"""
        # Clear current figure
        self.figure.clear()
        self.canvas.draw()
        self.current_figure = None
        self.current_figure = figure

        # If figure is a FacetGrid or similar
        if hasattr(figure, 'axes'):
            # For FacetGrid and similar multi-plot figures
            for i, ax in enumerate(figure.axes):
                new_ax = self.figure.add_subplot(figure.axes[i].get_subplotspec())

                # Copy all plot elements
                for artist in ax.get_children():
                    if hasattr(artist, 'get_xdata'):
                        # Line plots
                        new_ax.plot(artist.get_xdata(), artist.get_ydata(),
                                    color=artist.get_color(),
                                    linestyle=artist.get_linestyle())
                    elif hasattr(artist, 'get_offsets'):
                        # Scatter plots
                        new_ax.scatter(artist.get_offsets()[:, 0],
                                       artist.get_offsets()[:, 1],
                                       color=artist.get_facecolor())
                    elif hasattr(artist, 'get_paths'):
                        # Bar plots, box plots, etc.
                        for path in artist.get_paths():
                            new_ax.add_patch(artist.__class__(path))

                # Copy axis properties
                new_ax.set_title(ax.get_title())
                new_ax.set_xlabel(ax.get_xlabel())
                new_ax.set_ylabel(ax.get_ylabel())

                # Copy legend if exists
                if ax.get_legend():
                    handles, labels = ax.get_legend_handles_labels()
                    new_ax.legend(handles, labels, title=ax.get_legend().get_title().get_text())
        else:
            # For single plots
            if len(figure.axes) > 0:
                ax = figure.axes[0]
                new_ax = self.figure.add_subplot(111)

                # Copy all plot elements
                for artist in ax.get_children():
                    if hasattr(artist, 'get_xdata'):
                        # Line plots
                        new_ax.plot(artist.get_xdata(), artist.get_ydata(),
                                    color=artist.get_color(),
                                    linestyle=artist.get_linestyle())
                    elif hasattr(artist, 'get_offsets'):
                        # Scatter plots
                        new_ax.scatter(artist.get_offsets()[:, 0],
                                       artist.get_offsets()[:, 1],
                                       color=artist.get_facecolor())
                    elif hasattr(artist, 'get_paths'):
                        # Bar plots, box plots, etc.
                        for path in artist.get_paths():
                            new_ax.add_patch(artist.__class__(path))

                # Copy axis properties
                new_ax.set_title(ax.get_title())
                new_ax.set_xlabel(ax.get_xlabel())
                new_ax.set_ylabel(ax.get_ylabel())
                new_ax.set_xticks(ax.get_xticks())
                new_ax.set_yticks(ax.get_yticks())
                new_ax.set_xticklabels(ax.get_xticklabels())
                new_ax.set_yticklabels(ax.get_yticklabels())

                # Copy legend if exists
                if ax.get_legend():
                    handles, labels = ax.get_legend_handles_labels()
                    new_ax.legend(handles, labels, title=ax.get_legend().get_title().get_text())

        self.canvas.draw()


    def clear_plot(self):
        """Clear the current plot"""
        self.figure.clear()
        self.canvas.draw()
        self.current_figure = None