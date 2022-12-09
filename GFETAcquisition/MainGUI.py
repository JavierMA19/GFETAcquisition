# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 10:26:32 2020

@author: aguimera
"""
#

from PyQt5 import Qt
from qtpy import QtWidgets

from pyqtgraph.parametertree import ParameterTree, Parameter

from GFETAcquisition.ParamConf.HardwareConf import HardwareConfig
from GFETAcquisition.ParamConf.AcquisitionConf import AcquisitionConfig
from GFETAcquisition.ParamConf.PlotDataConf import PlotDataConfig
from GFETAcquisition.AcquisitionCore import AcquisitionMachine
from GFETAcquisition import __version__

import sys



class MainWindow(Qt.QWidget):
    ''' Main Window '''

    def __init__(self):
        super(MainWindow, self).__init__()
        layout = Qt.QVBoxLayout(self)

        self.setGeometry(650, 20, 400, 800)
        self.setWindowTitle('GFET Recording v' + __version__)

        # Add objects to main window
        # start Button
        self.btnAcq = Qt.QPushButton("Start Recording")
        layout.addWidget(self.btnAcq)

        self.HardConf = HardwareConfig(name='HardConf',
                                       title='Hardware Config',
                                       expanded=False)

        self.AcqConf = AcquisitionConfig(QTparent=self,
                                         HardConf=self.HardConf,
                                         name='AcqConfig',
                                         title='Acquisition Configuration',
                                         expanded=False)

        self.PlotDataConf = PlotDataConfig(AcquisitionConfig=self.AcqConf,
                                           name='PlotDataConf',
                                           title='Plotting Configuration',
                                           expanded=False)

        self.Parameters = Parameter.create(name='App Parameters',
                                           type='group',
                                           children=(
                                               # self.InfoStr,
                                               self.HardConf,
                                               self.AcqConf,
                                               self.PlotDataConf,
                                               # self.SaveStateConf,
                                           ))

        self.treepar = ParameterTree()
        self.treepar.setParameters(self.Parameters, showTop=False)

        layout.addWidget(self.treepar)

        self.AcqMach = AcquisitionMachine(AcquisitionConf=self.AcqConf,
                                          PlotDataConf=self.PlotDataConf)

        self.btnAcq.clicked.connect(self.on_btnStart)

    def on_btnStart(self):
        self.AcqMach.StartAcquisition()

        if self.AcqMach.AcqRunning:
            self.btnAcq.setText('Stop Recording')
        else:
            self.btnAcq.setText('Start Recording')



def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
