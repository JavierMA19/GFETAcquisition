# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 09:25:47 2019

@author: aguimera
"""

import pyqtgraph.parametertree.parameterTypes as pTypes
import numpy as np

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

    def __init__(self, HardConf, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)

        self.SwitchMatrix = None
        HardConf.on_SwitchMatrix_sel.connect(self.on_SwitchMatrix_sel)
        HardConf.on_board_sel .connect(self.on_board_sel)
        self.HardConf = HardConf

        # Add paramters
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

        self.on_FsChanged()
        self.on_AC_Sel()
        self.on_DC_Sel()

    def on_board_sel(self):
        self.on_AC_Sel()
        self.on_DC_Sel()

    def on_AC_Sel(self):
        if self.HardConf.Board.ACDCSwitch is not None:
            if self.SamplingConf.param('ACDCSel').param('AC').value():
                self.SamplingConf.param('ACDCSel').param('DC').setValue(False)

    def on_DC_Sel(self):
        if self.HardConf.Board.ACDCSwitch is not None:
            if self.SamplingConf.param('ACDCSel').param('DC').value():
                self.SamplingConf.param('ACDCSel').param('AC').setValue(False)

    def on_FsChanged(self):
        self.on_nColsChanged()

        Fs = self.SamplingConf.param('Fs').value()
        BufferSize = self.SamplingConf.param('BufferSize').value()
        self.SamplingConf.param('BufferTime').setValue(BufferSize * (1 / Fs))

    def on_BufferSizeChanged(self):
        Fs = self.SamplingConf.param('Fs').value()
        BufferSize = self.SamplingConf.param('BufferSize').value()
        self.SamplingConf.param('BufferTime').setValue(BufferSize * (1 / Fs))

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

        self.SwitchMatrix.on_SelColumnsChanged.connect(self.on_SelColumnsChanged)

    def on_SelColumnsChanged(self, Cols):
        self.SelColumns = Cols
        self.TimeMuxConf.param('nCols').setValue(len(Cols))

    def on_nColsChanged(self):
        Fs = self.SamplingConf.param('Fs').value()
        nCols = self.TimeMuxConf.param('nCols').value()
        ColSamps = self.TimeMuxConf.param('ColSamps').value()
        if nCols < 1:
            return

        self.TimeMuxConf.param('FsCol').setValue(Fs / (nCols * ColSamps))

        BufferBlocks = self.TimeMuxConf.param('BufferBlocks').value()
        self.SamplingConf.param('BufferSize').setValue(BufferBlocks * nCols * ColSamps)

        if self.SwitchMatrix is None:
            return

        dCols = np.array([], dtype=np.uint8)
        for k, v in self.SelColumns.items():
            c = np.ones((ColSamps, v.size)) * v
            dCols = np.vstack((dCols, c)) if dCols.size else c

        self.DoutCols = dCols
        self.TimeMuxConf.param('DoutCols').setValue(str(self.DoutCols))
