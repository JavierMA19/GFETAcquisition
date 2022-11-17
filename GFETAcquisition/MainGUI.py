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

import sys

_version = '0.2.0.b2'


class MainWindow(Qt.QWidget):
    ''' Main Window '''

    def __init__(self):
        super(MainWindow, self).__init__()
        layout = Qt.QVBoxLayout(self)

        self.setGeometry(650, 20, 400, 800)
        self.setWindowTitle('GFET Characterization v' + _version)

        # Add objects to main window
        # start Button
        self.btnAcq = Qt.QPushButton("Start Measure")
        layout.addWidget(self.btnAcq)
        #
        # self.InfoStr = Parameter.create(**{'name': 'InfoStr',
        #                                    'title': 'Status Info',
        #                                    'type': 'text',
        #                                    'expanded': True,
        #                                    'readonly': True})

        # self.SaveStateConf = SaveSateParams(QTparent=self,
        #                                     name='SaveStateConf',
        #                                     title='Save Load State',
        #                                     expanded=False)

        # self.SaveFileConf = SaveDataParams(QTparent=self,
        #                                    name='SaveFileConf',
        #                                    title='Save Data',
        #                                    expanded=True)

        self.HardConf = HardwareConfig(name='HardConf',
                                       title='Hardware Config',
                                       expanded=False)

        self.AcqConf = AcquisitionConfig(HardConf=self.HardConf,
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

        self.AcqMach = AcquisitionMachine(AcquisitionConf=self.AcqConf)

        #
        # self.Charact = CharacterizationMachine(SweepsConf=self.SweepsConf,
        #                                        InfoOut=self.InfoStr)
        #
        # self.Charact.CharactFinished.connect(self.on_CharactFinished)
        self.btnAcq.clicked.connect(self.on_btnStart)

    def on_btnStart(self):
        print('ButStart')

        self.AcqMach.StartAcquisition()

        # if self.Charact.ChactRunning:
        #     self.SweepsConf.Cycles.setValue(1)
        #     self.Charact.StopCharact()
        # else:
        #     self.Charact.StartCharact(HardConf=self.HardConf,
        #                               SaveFileConf=self.SaveFileConf)
        #     self.btnAcq.setText('Stop Measure')

    # def on_CharactFinished(self):
    #     self.btnAcq.setText('Start Measure')
    #     Cy = self.SweepsConf.Cycles.value() - 1
    #     self.SweepsConf.Cycles.setValue(Cy)
    #     if Cy > 0:
    #         self.on_btnStart()


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
