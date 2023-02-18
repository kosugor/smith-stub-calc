import sys
import numpy as np
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QObject

from utils import (
    WL,
    cableVP,
    cableWL,
    complexReciprocal,
    z2RefCoef,
    z2RefCoefAmp,
    z2RefCoefPhDeg,
    vswr,
    beta,
    Zi,
    C,
)

from graph import GraphWindow


class Communicate(QObject):
    """
    Communication object which sends a signal to refresh the graph if settings are changed
    """

    paramchanged = pyqtSignal()


qtCreatorFile = "settings.ui"  # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class Settings(QtWidgets.QWidget, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # connect the events
        self.co = Communicate()
        self.cbFreq.currentIndexChanged.connect(self.refresh_display)
        self.leZ0.editingFinished.connect(self.Z0changed)
        self.leY0.editingFinished.connect(self.Y0changed)
        self.leZRe.editingFinished.connect(self.Zchanged)
        self.leZIm.editingFinished.connect(self.Zchanged)
        self.leYRe.editingFinished.connect(self.Ychanged)
        self.leYIm.editingFinished.connect(self.Ychanged)
        self.dialL1.valueChanged.connect(self.LL1changed)
        self.dialL2.valueChanged.connect(self.LL2changed)
        self.pbLL1Up.clicked.connect(self.LL1Up)
        self.pbLL1Down.clicked.connect(self.LL1Down)
        self.pbLL2Up.clicked.connect(self.LL2Up)
        self.pbLL2Down.clicked.connect(self.LL2Down)
        # initialize variables
        self.Z0 = 50
        self.Y0 = 0.02
        self.Z = complex(50, 0)
        self.Y = complex(0.02, 0)
        self.z = self.Z / self.Z0
        self.y = self.Y / self.Y0
        self.Z1 = self.Z
        self.Y1 = complexReciprocal(self.Z1)
        self.Y1d = None
        self.Y1darray = None
        self.Z2 = complex("inf")
        self.Y2 = 0
        self.Y2d = None
        self.Y2darray = None
        self.Ztot = self.Z
        self.dialL1.setValue(0)
        self.dialL2.setValue(0)
        self.refresh_display()
        self.refresh_display_LL1()
        self.refresh_display_LL2()

    def Z0changed(self):
        self.Z0 = float(self.leZ0.text())
        self.Y0 = 1 / self.Z0
        self.z = self.Z / self.Z0
        self.y = self.Y / self.Y0
        self.refresh_display()
        self.LL1changed()

    def Y0changed(self):
        self.Y0 = float(self.leZ0.text())
        self.Z0 = 1 / self.Y0
        self.z = self.Z / self.Z0
        self.y = self.Y / self.Y0
        self.refresh_display()
        self.LL1changed()

    def Zchanged(self):
        self.Z = float(self.leZRe.text()) + float(self.leZIm.text()) * 1j
        self.Y = complexReciprocal(self.Z)
        self.z = self.Z / self.Z0
        self.y = self.Y / self.Y0
        self.refresh_display()
        self.LL1changed()

    def Ychanged(self):
        self.Y = float(self.leYRe.text()) + float(self.leYIm.text()) * 1j
        self.Z = complexReciprocal(self.Y)
        self.z = self.Z / self.Z0
        self.y = self.Y / self.Y0
        self.refresh_display()
        self.LL1changed()

    def LL1changed(self):
        self.lld1 = self.dialL1.value()
        self.leLL1Degrees.setText(str(round(self.lld1, 0)))
        lll = self.lld1 / 360
        # cable wavelength
        cwl = cableWL(self.vp, self.freq)
        # line length in regard to lambda
        self.leLL1Lambda.setText(str(round(lll, 3)))
        # line length in meters
        ll = cwl * lll
        self.leLL1cm.setText(str(round(ll * 100, 1)))
        # calculate new Z and Y
        self.Y1 = Zi(self.Y0, self.Y, self.vp, self.freq, ll)
        self.Y1d = Zi(self.Z0, self.y * self.Z0, self.vp, self.freq, ll)
        self.Z1 = complexReciprocal(self.Y1)

        if ll > 0.01:
            llarray = np.arange(0.01, ll, 0.01)
            self.Y1darray = Zi(self.Z0, self.y * self.Z0, self.vp, self.freq, llarray)

        self.refresh_display_LL1()
        self.Ztot = complexReciprocal(self.Y1 + self.Y2)
        self.refresh_display_tot()
        self.co.paramchanged.emit()

    def LL2changed(self):
        self.lld2 = self.dialL2.value()
        self.leLL2Degrees.setText(str(round(self.lld2, 0)))
        lll = self.lld2 / 360
        # cable wavelength
        cwl = cableWL(self.vp, self.freq)
        # line length in regard to lambda
        self.leLL2Lambda.setText(str(round(lll, 3)))
        # line length in meters
        ll = cwl * lll
        self.leLL2cm.setText(str(round(ll * 100, 1)))
        # calculate new Z and Y
        self.Z2 = Zi(self.Z0, 0, self.vp, self.freq, ll)
        self.Y2 = complexReciprocal(self.Z2)
        self.Y2d = (self.Y2 / self.Y0) * self.Z0
        llarray = np.arange(0, ll, 0.01)
        self.Z2array = Zi(self.Z0, 0, self.vp, self.freq, llarray)
        self.Y2darray = ((1 / self.Z2array) / self.Y0) * self.Z0
        self.refresh_display_LL2()
        self.Ztot = complexReciprocal(self.Y1 + self.Y2)
        self.refresh_display_tot()
        self.co.paramchanged.emit()

    def LL1Up(self):
        if self.dialL1.value() < 180:
            self.dialL1.setValue(self.dialL1.value() + 1)
            self.LL1changed()

    def LL1Down(self):
        if self.dialL1.value() > 0:
            self.dialL1.setValue(self.dialL1.value() - 1)
            self.LL1changed()

    def LL2Up(self):
        if self.dialL2.value() < 180:
            self.dialL2.setValue(self.dialL2.value() + 1)
            self.LL2changed()

    def LL2Down(self):
        if self.dialL2.value() > 0:
            self.dialL2.setValue(self.dialL2.value() - 1)
            self.LL2changed()

    def refresh_display(self):
        """
        Refresh display of params
        """
        self.freq = float(self.cbFreq.currentText()) * (10**6)
        self.vp = cableVP(self.cbCable.currentText())
        self.lcdWavelength.display(WL(self.freq))
        self.lcdVr.display(self.vp / C)
        self.lcdWavelengthCable.display(cableWL(self.vp, self.freq))
        self.leZ0.setText(str(self.Z0))
        self.leY0.setText(str(self.Y0))
        self.leZRe.setText(str(round(self.Z.real, 2)))
        self.leZIm.setText(str(round(self.Z.imag, 2)))
        self.leZnormRe.setText(str(round(self.z.real, 2)))
        self.leZnormIm.setText(str(round(self.z.imag, 2)))
        self.leYRe.setText(str(round(self.Y.real, 2)))
        self.leYIm.setText(str(round(self.Y.imag, 2)))
        self.leYnormRe.setText(str(round(self.y.real, 2)))
        self.leYnormIm.setText(str(round(self.y.imag, 2)))
        self.leGammaAbs.setText(str(round(z2RefCoefAmp(self.z), 2)))
        self.leGammaAngle.setText(str(round(z2RefCoefPhDeg(self.z), 2)))
        self.leVSWR.setText(str(round(vswr(z2RefCoef(self.z)), 2)))
        self.lcdBeta.display(beta(self.vp, self.freq))
        self.refresh_display_tot()
        self.co.paramchanged.emit()

    def refresh_display_LL1(self):
        self.leZ1Re.setText(str(round(self.Z1.real, 2)))
        self.leZ1Im.setText(str(round(self.Z1.imag, 2)))
        self.leZ1normRe.setText(str(round(self.Z1.real / self.Z0, 2)))
        self.leZ1normIm.setText(str(round(self.Z1.imag / self.Z0, 2)))
        self.leY1Re.setText(str(round(self.Y1.real, 2)))
        self.leY1Im.setText(str(round(self.Y1.imag, 2)))
        self.leY1normRe.setText(str(round(self.Y1.real / self.Y0, 2)))
        self.leY1normIm.setText(str(round(self.Y1.imag / self.Y0, 2)))

    def refresh_display_LL2(self):
        self.leZ2Re.setText(str(round(self.Z2.real, 2)))
        self.leZ2Im.setText(str(round(self.Z2.imag, 2)))
        self.leZ2normRe.setText(str(round(self.Z2.real / self.Z0, 2)))
        self.leZ2normIm.setText(str(round(self.Z2.imag / self.Z0, 2)))
        self.leY2Re.setText(str(round(self.Y2.real, 2)))
        self.leY2Im.setText(str(round(self.Y2.imag, 2)))
        self.leY2normRe.setText(str(round(self.Y2.real / self.Y0, 2)))
        self.leY2normIm.setText(str(round(self.Y2.imag / self.Y0, 2)))

    def refresh_display_tot(self):
        """
        Refresh display of end values
        """
        self.leZReT.setText(str(round(self.Ztot.real, 2)))
        self.leZImT.setText(str(round(self.Ztot.imag, 2)))
        self.zt = self.Ztot / self.Z0
        self.leZnormReT.setText(str(round(self.zt.real, 2)))
        self.leZnormImT.setText(str(round(self.zt.imag, 2)))
        self.Ytot = complexReciprocal(self.Ztot)
        self.leYReT.setText(str(round(self.Ytot.real, 2)))
        self.leYImT.setText(str(round(self.Ytot.imag, 2)))
        self.yt = self.Ytot / self.Y0
        self.leYnormReT.setText(str(round(self.yt.real, 2)))
        self.leYnormImT.setText(str(round(self.yt.imag, 2)))
        self.leGammaAbsT.setText(str(round(z2RefCoefAmp(self.zt), 2)))
        self.leGammaAngleT.setText(str(round(z2RefCoefPhDeg(self.zt), 2)))
        self.leVSWRT.setText(str(round(vswr(z2RefCoef(self.zt)), 2)))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Settings()
    window.show()
    sys.exit(app.exec_())
