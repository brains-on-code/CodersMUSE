import matplotlib
import numpy

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # figure out how to set this
        # plt.style.use('seaborn-darkgrid')

        matplotlib.rcParams.update({'font.size': 8})

        self.fig = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        # not sure if this is necessary
        # FigureCanvas.setSizePolicy(self,
        #                           QtWidgets.QSizePolicy.Expanding,
        #                           QtWidgets.QSizePolicy.Expanding)
        # FigureCanvas.updateGeometry(self)


class PhysiologicalPlot(MyMplCanvas):
    """Simple canvas with a sine plot."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super().__init__(parent, width, height, dpi)
        self.aspan = None
        self.plot = None
        self.all_y_values = None

    def set_y_values(self, y_values, start_pos, end_pos):
        self.all_y_values = y_values
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.update_plot()

    def update_plot(self, current_time=0, span=1200, highlight_span=50, full_plot=False):
        self.figure.clf()
        ax1 = self.figure.add_subplot(111)

        if full_plot:
            self.draw_full_plot(ax1)
        else:
            minimum = self.start_pos + current_time - span
            maximum = self.start_pos + current_time + span
            if minimum < 0:
                minimum = 0

            plot_y_values = self.all_y_values[minimum:maximum]
            y_values_mask = numpy.isfinite(plot_y_values)

            if len(plot_y_values) < (maximum - minimum):
                maximum = len(plot_y_values) + minimum

            x_axis = numpy.arange(minimum, maximum, 1)

            self.plot = ax1.plot(x_axis[y_values_mask], plot_y_values[y_values_mask])

            # todo evaluate adding a horizontal line for average condition and/or average of entire session

            # add backgrounds for condition visualization
            task_start = minimum
            if self.start_pos > minimum:
                task_start = self.start_pos

            task_end = maximum
            if maximum > self.end_pos:
                task_end = self.end_pos

            self.aspan = ax1.axvspan(task_start, task_end, color='blue', alpha=0.05)

            # highlight current time
            self.aspan = ax1.axvspan(self.start_pos + current_time - highlight_span, self.start_pos + current_time + highlight_span, color='red', alpha=0.2)

        ax1.set_ylim(min(self.all_y_values), max(self.all_y_values))

        self.fig.canvas.draw_idle()

    def draw_full_plot(self, ax1):
        y_values_mask = numpy.isfinite(self.all_y_values)
        x_axis = numpy.arange(0, len(self.all_y_values), 1)
        self.plot = ax1.plot(x_axis[y_values_mask], self.all_y_values[y_values_mask])

