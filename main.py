import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout
from settings import Settings
from graph import GraphWindow


class MainW(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self._main = QWidget()
        self.setCentralWidget(self._main)
        layout = QHBoxLayout(self._main)
        self.setGeometry(0, 0, 1900, 900)
        self.setWindowTitle("Smith stub calculator")
        self.sw = Settings()
        self.gf = GraphWindow()
        layout.addWidget(self.sw)
        layout.addWidget(self.gf)
        self.show()
        self.sw.co.paramchanged.connect(self.plot_z)

    def plot_z(self):
        # self.gf.Z = self.sw.Z
        self.gf.Z = self.sw.Z
        self.gf.Y = self.sw.y * self.sw.Z0
        self.gf.Y1 = self.sw.Y1d
        self.gf.Y1array = self.sw.Y1darray
        self.gf.Y2 = self.sw.Y2d
        self.gf.Y2array = self.sw.Y2darray
        self.gf.Ztot = self.sw.Ztot
        self.gf.drawZ()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mw = MainW()
    sys.exit(app.exec_())
