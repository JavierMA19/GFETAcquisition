# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 09:25:47 2019

@author: aguimera
"""

import pyqtgraph.parametertree.parameterTypes as pTypes
import numpy as np
from PyQt5 import Qt
import math
from GFETAcquisition.ParamConf.SaveFileConf import SaveDataConf

BiasConf = {'name': 'BiasConf',
            'title': 'Bias Voltages',
            'type': 'group',
            'children': [
                {'name': 'Vds',
                 'title': 'Vds',
                 'type': 'float',
                 'value': 0.05,
                 'default': 0.05,
                 'siPrefix': True,
                 'suffix': 'V'},
                {'name': 'Vgs',
                 'title': 'Vgs',
                 'type': 'float',
                 'value': 0,
                 'default': 0,
                 'siPrefix': True,
                 'suffix': 'V'}, ]}

SamplingConf = {'name': 'SamplingConf',
                'title': 'Sampling Configuration',
                'type': 'group',
                'children': [
                    {'name': 'Fs',
                     'title': 'Sampling Rate',
                     'type': 'float',
                     'value': 30e3,
                     'default': 30e3,
                     'siPrefix': True,
                     'suffix': 'Hz'},
                    {'name': 'BufferTime',
                     'title': 'Interrupt Period',
                     'type': 'float',
                     'value': 0,
                     'readonly': True,
                     'siPrefix': True,
                     'suffix': 's'},
                    {'name': 'BufferSize',
                     'title': 'Buffer Samples',
                     'type': 'int',
                     'value': 15000,
                     'default': 15000,
                     'readonly': False,
                     'siPrefix': True,
                     },
                    {'name': 'ACDCSel',
                     'title': 'AC-DC Selection',
                     'type': 'group',
                     'children': [{'name': 'AC',
                                   'type': 'bool',
                                   'value': True},
                                  {'name': 'DC',
                                   'type': 'bool',
                                   'value': True}]
                     },
                ]
                }

TimeMuxConf = {'name': 'TDMConf',
               'title': 'Time Mux Configuration',
               'type': 'group',
               'visible': False,
               'children': [
                   {'name': 'ColSamps',
                    'title': 'Samples per Column',
                    'type': 'int',
                    'value': 30,
                    'default': 30,
                    'limits': (1, 10000),
                    },
                   {'name': 'nCols',
                    'title': 'Number of Columns',
                    'type': 'int',
                    'readonly': True,
                    'value': 1,
                    'limits': (1, 64),
                    },
                   {'name': 'BufferBlocks',
                    'title': 'Blocks in Buffer',
                    'type': 'int',
                    'value': 30,
                    'default': 30,
                    },
                   {'name': 'FsCol',
                    'title': 'Column Sampling Rate',
                    'type': 'float',
                    'value': 0,
                    'default': 0,
                    'siPrefix': True,
                    'readonly': True,
                    'suffix': 'Hz'},
                   {'name': 'DoutCols',
                    'title': 'Digital Control',
                    'type': 'text',
                    'readonly': True,
                    },
               ]
               }


class AcquisitionConfig(pTypes.GroupParameter):
    sigFsChanged = Qt.pyqtSignal()
    sigAcqChannelsChanged = Qt.pyqtSignal(object)
    sigHardwareChanged = Qt.pyqtSignal(object)

    def __init__(self, QTparent, HardConf, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)

        self.DigitalMuxSignal = None
        self.SelColumns = {}
        self.SwitchMatrix = None
        self.HardConf = HardConf

        # Add paramters
        self.FileConf = self.addChild(SaveDataConf(QTparent=QTparent,
                                                   name='FileConf',
                                                   title='Data File'))
        self.BiasConf = self.addChild(BiasConf)
        self.SamplingConf = self.addChild(SamplingConf)
        self.TimeMuxConf = self.SamplingConf.addChild(TimeMuxConf)

        self.TimeMuxConf.param('nCols').sigValueChanged.connect(self.on_nColsChanged)
        self.TimeMuxConf.param('ColSamps').sigValueChanged.connect(self.on_nColsChanged)
        self.TimeMuxConf.param('BufferBlocks').sigValueChanged.connect(self.on_nColsChanged)

        self.SamplingConf.param('Fs').sigValueChanged.connect(self.on_FsChanged)
        self.SamplingConf.param('BufferSize').sigValueChanged.connect(self.on_BufferSizeChanged)
        self.SamplingConf.param('ACDCSel').param('AC').sigValueChanged.connect(self.on_AC_Sel)
        self.SamplingConf.param('ACDCSel').param('DC').sigValueChanged.connect(self.on_DC_Sel)
        self.SamplingConf.param('BufferTime').sigValueChanged.connect(self.on_BufferTimeChanged)

        self.HardConf.sigSwitchMatrixSelected.connect(self.on_SwitchMatrix_sel)
        self.HardConf.sigBoardSelected.connect(self.on_board_sel)
        self.SwitchMatrix = self.HardConf.SwitchMatrix

        self.on_FsChanged()
        self.on_AC_Sel()
        self.on_DC_Sel()

    def on_board_sel(self):
        self.HardConf.Board.sigAInputsChanged.connect(self.on_sigAInputsChanged)
        self.on_AC_Sel()
        self.on_DC_Sel()

    def on_AC_Sel(self):
        if self.HardConf.Board.ACDCSwitch is not None:
            if self.SamplingConf.param('ACDCSel').param('AC').value():
                self.SamplingConf.param('ACDCSel').param('DC').setValue(False)

        self.on_sigAInputsChanged()

    def on_DC_Sel(self):
        if self.HardConf.Board.ACDCSwitch is not None:
            if self.SamplingConf.param('ACDCSel').param('DC').value():
                self.SamplingConf.param('ACDCSel').param('AC').setValue(False)

        self.on_sigAInputsChanged()

    def on_FsChanged(self):
        self.on_nColsChanged()

        Fs = self.SamplingConf.param('Fs').value()
        BufferSize = self.SamplingConf.param('BufferSize').value()
        self.SamplingConf.param('BufferTime').setValue(BufferSize * (1 / Fs))

        self.sigFsChanged.emit()

    def on_BufferSizeChanged(self):
        Fs = self.SamplingConf.param('Fs').value()
        BufferSize = self.SamplingConf.param('BufferSize').value()
        self.SamplingConf.param('BufferTime').setValue(BufferSize * (1 / Fs))

    def on_BufferTimeChanged(self):
        bt = self.SamplingConf.param('BufferTime').value()
        Fs = self.SamplingConf.param('Fs').value()
        nCols = self.TimeMuxConf.param('nCols').value()
        ColSamps = self.TimeMuxConf.param('ColSamps').value()

        if bt < 0.3:
            bs = math.ceil(0.3 * Fs)
            if self.SwitchMatrix.SwitchMatrixPresent:
                self.TimeMuxConf.param('BufferBlocks').setValue(bs/(ColSamps*nCols))
            else:
                self.SamplingConf.param('BufferSize').setValue(bs)

    def on_SwitchMatrix_sel(self, SwitchMatrix):
        self.SwitchMatrix = SwitchMatrix
        if SwitchMatrix.SwitchMatrixPresent:
            self.TimeMuxConf.setOpts(**{'visible': True})
            self.SamplingConf.param('BufferSize').setOpts(**{'readonly': True})
            self.on_SelColumnsChanged(self.SwitchMatrix.Columns.GetColumns())
        else:
            self.TimeMuxConf.setOpts(**{'visible': False})
            self.SamplingConf.param('BufferSize').setOpts(**{'readonly': False})
            self.TimeMuxConf.param('nCols').setValue(1)

        self.SwitchMatrix.sigSelColumnsChanged.connect(self.on_SelColumnsChanged)
        self.sigHardwareChanged.emit(None)

    def on_SelColumnsChanged(self, Cols):
        self.SelColumns = Cols
        self.TimeMuxConf.param('nCols').setValue(len(Cols))
        self.on_sigAInputsChanged()
        self.sigFsChanged.emit()

    def on_nColsChanged(self):
        Fs = self.SamplingConf.param('Fs').value()
        nCols = self.TimeMuxConf.param('nCols').value()
        ColSamps = self.TimeMuxConf.param('ColSamps').value()
        if nCols < 1:
            return

        self.TimeMuxConf.param('FsCol').setValue(Fs / (nCols * ColSamps))

        BufferBlocks = self.TimeMuxConf.param('BufferBlocks').value()
        self.SamplingConf.param('BufferSize').setValue(BufferBlocks * nCols * ColSamps)

        self.CalcDigitalMuxSignal()

    def CalcDigitalMuxSignal(self):
        if not self.SwitchMatrix.SwitchMatrixPresent:
            self.DigitalMuxSignal = None
            self.TimeMuxConf.param('DoutCols').setValue('')
            self.SelColumns = {}
            return

        self.SelColumns = self.SwitchMatrix.Columns.GetColumns()
        ColSamps = self.TimeMuxConf.param('ColSamps').value()

        dCols = np.array([], dtype=np.uint8)
        for k, v in self.SelColumns.items():
            c = np.ones((ColSamps, v.size)) * v
            dCols = np.vstack((dCols, c)) if dCols.size else c

        self.DigitalMuxSignal = dCols
        self.TimeMuxConf.param('DoutCols').setValue(str(self.DigitalMuxSignal))

    def on_sigAInputsChanged(self):
        self.sigAcqChannelsChanged.emit(self.GetAcqChannels())

    def GetAcqChannels(self):
        aiChannels = []
        ChNames = []

        if self.SamplingConf.param('ACDCSel').param('DC').value():
            DCInputs = self.HardConf.Board.AInputs.GetDCChannels()
            for chn, ai in DCInputs.items():
                aiChannels.append(ai)
                ChNames.append(chn + 'DC')

        if self.SamplingConf.param('ACDCSel').param('AC').value():
            ACInputs = self.HardConf.Board.AInputs.GetACChannels()
            for chn, ai in ACInputs.items():
                aiChannels.append(ai)
                ChNames.append(chn + 'AC')

        RawChannels = {}
        for i, chn in enumerate(ChNames):
            RawChannels[chn] = i

        self.CalcDigitalMuxSignal()

        DemuxChannels = {}
        for chn, i in RawChannels.items():
            for ic, (col, d) in enumerate(self.SelColumns.items()):
                DemuxChannels[chn + col] = i * (ic + 1)

        return {'RawChannels': RawChannels,
                'DemuxChannels': DemuxChannels,
                'aiChannels': aiChannels,
                'ChNames': ChNames,
                'Columns': self.SelColumns,
                'DigitalMuxSignal': self.DigitalMuxSignal,
                }




