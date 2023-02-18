import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from smithplot.smithaxes import SmithAxes


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        # default params
        SmithAxes.update_scParams(
            {
                "plot.marker.hack": False,
                "plot.marker.rotate": False,
                "grid.major.enable": True,
                "grid.major.fancy": False,
                "grid.major.xmaxn": 5,
                "grid.major.ymaxn": 12,
                "grid.minor.enable": True,
                "grid.minor.fancy": True,
            }
        )
        self.axes = fig.add_subplot(111, projection="smith")
        super(MplCanvas, self).__init__(fig)


class GraphWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(GraphWindow, self).__init__(*args, **kwargs)
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        layout = QVBoxLayout()
        # dodavanje grafika
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.Z = 50 + 50j

    def drawZ(self):
        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.plot(
            self.Z, label="Z", color="blue", datatype=SmithAxes.Z_PARAMETER
        )
        self.canvas.axes.plot(
            self.Y, label="Y", color="orange", datatype=SmithAxes.Z_PARAMETER
        )
        if self.Y1array is not None:
            self.canvas.axes.plot(
                self.Y1array,
                marker=",",
                color="orange",
                datatype=SmithAxes.Z_PARAMETER,
            )
            self.canvas.axes.plot(
                self.Y1,
                label="Y1",
                color="red",
                datatype=SmithAxes.Z_PARAMETER,
            )
        if self.Y2array is not None:
            self.canvas.axes.plot(
                self.Y2array,
                marker=",",
                color="green",
                datatype=SmithAxes.Z_PARAMETER,
            )
            self.canvas.axes.plot(
                self.Y2,
                label="Y2",
                color="green",
                datatype=SmithAxes.Z_PARAMETER,
            )
        if self.Ztot:
            self.canvas.axes.plot(
                self.Ztot,
                label="Ztot",
                color="blue",
                marker="x",
                datatype=SmithAxes.Z_PARAMETER,
            )
        # Trigger the canvas to update and redraw.
        self.canvas.axes.legend()
        self.canvas.draw()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    gw = GraphWindow()
    gw.show()
    sys.exit(app.exec_())
