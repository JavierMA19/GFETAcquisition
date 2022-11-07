# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 10:56:29 2020

@author: Javier
"""

# from PyQt5 import Qt
import pyqtgraph.parametertree.parameterTypes as pTypes
from PyQt5 import Qt

import GFETAcquisition.ParamConf.HwConfig as BoardConf


class HwGainsConfig(pTypes.GroupParameter):
    def __init__(self, Gains, **kwargs):
        super(HwGainsConfig, self).__init__(**kwargs)
        for n, v in Gains.items():
            self.addChild({'name': n,
                           'type': 'float',
                           'value': v,
                           'default': v,
                           'siPrefix': True,
                           'suffix': ' '}, )

    def GetGains(self):
        Gains = {}
        for p in self.children():
            Gains[p.name()] = p.value()
        return Gains


class AInputsConfig(pTypes.GroupParameter):
    def __init__(self, AInputs, **kwargs):
        super(AInputsConfig, self).__init__(**kwargs)

        self.addChild({'name': 'SelAll',
                       'type': 'action',
                       'title': 'Un-Select all'})
        self.addChild({'name': 'SelInvert',
                       'type': 'action',
                       'title': 'Invert Selection'})
        self.seltrufalse = True
        self.param('SelAll').sigActivated.connect(self.on_SelAll)
        self.param('SelInvert').sigActivated.connect(self.on_SelInvert)

        for n, v in sorted(AInputs.items()):
            self.addChild({'name': n,
                           'type': 'bool',
                           'value': True,
                           'aiDC': v[0],
                           'aiAC': v[-1],
                           }, )

    def on_SelAll(self):
        self.seltrufalse = not self.seltrufalse
        for p in self.children():
            if p.type() == 'action':
                continue
            p.setValue(self.seltrufalse)

    def on_SelInvert(self):
        for p in self.children():
            if p.type() == 'action':
                continue
            p.setValue(not p.value())

    def GetDCChannels(self):
        DCChannels = {}
        for p in self.children():
            if p.type() == 'action':
                continue
            if p.value():
                DCChannels[p.name()] = p.opts['aiDC']
        return DCChannels

    def GetACChannels(self):
        ACChannels = {}
        for p in self.children():
            if p.type() == 'action':
                continue
            if p.value():
                ACChannels[p.name()] = p.opts['aiAC']
        return ACChannels


class AOutputsConfig(pTypes.GroupParameter):
    def __init__(self, AOutputs, **kwargs):
        super(AOutputsConfig, self).__init__(**kwargs)
        for n, v in AOutputs.items():
            self.addChild({'name': n,
                           'type': 'group',
                           # 'expanded': False,
                           'children': [{'name': 'Output',
                                         'type': 'str',
                                         'default': v,
                                         'value': v,
                                         },
                                        {'name': 'Selected',
                                         'type': 'bool',
                                         'value': True,
                                         'default': True,
                                         },
                                        {'name': 'Value',
                                         'type': 'float',
                                         'value': 0,
                                         'default': 0,
                                         'step': 0.01,
                                         'siPrefix': True,
                                         'suffix': 'V'
                                         }]
                           })
            # self.addChild({'name': n,
            #                'type': 'str',
            #                'value': v,
            #                }, )

    def GetAOuts(self):
        Aouts = {}
        for p in self.children():
            if p.param('Selected').value():
                Aouts[p.name()] = {'Output': p.param('Output').value(),
                                   'Value': p.param('Value').value()}
        return Aouts


class ACDCSwitchConfig(pTypes.GroupParameter):
    def __init__(self, ACDCSwitch, **kwargs):
        super(ACDCSwitchConfig, self).__init__(**kwargs)

        self.douts = ACDCSwitch['douts']
        self.addChild({'name': 'douts',
                       'type': 'str',
                       'readonly': True,
                       'value': str(ACDCSwitch['douts']),
                       })
        self.GateAI = ACDCSwitch['GateAI']
        self.addChild({'name': 'GateAI',
                       'type': 'str',
                       'readonly': True,
                       'value': str(ACDCSwitch['GateAI']),
                       })

        self.States = ACDCSwitch['states']
        StateChilds = []
        for n, v in ACDCSwitch['states'].items():
            StateChilds.append({'name': n,
                                'type': 'str',
                                'readonly': True,
                                'value': str(v),
                                }, )
        self.addChild({'name': 'States',
                       'type': 'group',
                       'expanded': True,
                       'children': StateChilds,
                       })


class BoardConfig(pTypes.GroupParameter):
    def __init__(self, Board, **kwargs):
        super(BoardConfig, self).__init__(**kwargs)

        self.Gains = HwGainsConfig(Gains=Board['Gains'],
                                   name='Gains',
                                   expanded=False, )
        self.AInputs = AInputsConfig(AInputs=Board['AnalogInputs'],
                                     name='AInputs',
                                     title='Analog Inputs',
                                     expanded=False, )
        self.AOutputs = AOutputsConfig(AOutputs=Board['AnalogOutputs'],
                                       name='AOutputs',
                                       title='Analog Outputs',
                                       expanded=False, )
        self.addChildren((self.Gains,
                          self.AInputs,
                          self.AOutputs))

        if 'ACDCSwitch' in Board:
            self.ACDCSwitch = ACDCSwitchConfig(ACDCSwitch=Board['ACDCSwitch'],
                                               name='ACDCSwitch',
                                               # title='Analog Outputs',
                                               expanded=False, )
            self.addChildren((self.ACDCSwitch,))
        else:
            self.ACDCSwitch = None


class ColumnsConfig(pTypes.GroupParameter):
    def __init__(self, Columns, **kwargs):
        super(ColumnsConfig, self).__init__(**kwargs)

        self.addChild({'name': 'SelAll',
                       'type': 'action',
                       'title': 'Un-Select all'})
        self.addChild({'name': 'SelInvert',
                       'type': 'action',
                       'title': 'Invert Selection'})
        self.seltruefalse = True
        self.param('SelAll').sigActivated.connect(self.on_SelAll)
        self.param('SelInvert').sigActivated.connect(self.on_SelInvert)

        for n, v in sorted(Columns.items()):
            self.addChild({'name': n,
                           'type': 'bool',
                           'value': True,
                           'dout': v,
                           }, )

    def on_SelAll(self):
        self.seltruefalse = not self.seltruefalse
        for p in self.children():
            if p.type() == 'action':
                continue
            p.setValue(self.seltrufalse)

    def on_SelInvert(self):
        for p in self.children():
            if p.type() == 'action':
                continue
            p.setValue(not p.value())

    def GetColumns(self):
        Cols = {}
        for p in self.children():
            if p.type() == 'action':
                continue
            if p.value():
                Cols[p.name()] = p.opts['dout']
        return Cols


class SwitchMatrixConfig(pTypes.GroupParameter):
    def __init__(self, Board, **kwargs):
        super(SwitchMatrixConfig, self).__init__(**kwargs)
        if Board is None:
            self.SwitchMatrixPresent = False
            return
        self.SwitchMatrixPresent = True

        self.douts = Board['douts']
        self.addChild({'name': 'douts',
                       'type': 'str',
                       'readonly': True,
                       'value': str(Board['douts']),
                       })

        self.Columns = ColumnsConfig(Columns=Board['Columns'],
                                     name='Columns',
                                     title='Columns Selection',
                                     expanded=False, )

        self.AOutputs = AOutputsConfig(AOutputs=Board['AnalogOutputs'],
                                       name='AOutputs',
                                       title='Analog Outputs',
                                       expanded=False, )

        self.addChildren((self.AOutputs, self.Columns))


class HardwareConfig(pTypes.GroupParameter):
    on_board_sel = Qt.pyqtSignal(object)

    def __init__(self, **kwargs):
        super(HardwareConfig, self).__init__(**kwargs)
        self.addChild({'name': 'BoardSel',
                       'title': 'Board Selection',
                       'type': 'list',
                       'values': BoardConf.Boards.keys(),
                       })

        self.param('BoardSel').sigValueChanged.connect(self.on_BoardSel)
        self.Add_Board()

        self.addChild({'name': 'SwitchMatrixSel',
                       'title': 'Switch Matrix Selection',
                       'type': 'list',
                       'values': ['None', ] + list(BoardConf.SwitchMatrix.keys()),
                       'value': 'None',
                       })
        self.param('SwitchMatrixSel').sigValueChanged.connect(self.on_SwitchMatrixSel)
        self.Add_SwitchSel()

    def on_BoardSel(self):
        self.param('BoardConf').remove()
        self.Add_Board()
        self.on_board_sel.emit(self.param('BoardConf'))

    def Add_Board(self):
        Board = self.param('BoardSel').value()
        self.addChild(BoardConfig(Board=BoardConf.Boards[Board],
                                  name='BoardConf',
                                  title='Hardware Configuration'))

    def on_SwitchMatrixSel(self):
        self.param('SwitchMatrixConf').remove()
        self.Add_SwitchSel()

    def Add_SwitchSel(self):
        Switch = self.param('SwitchMatrixSel').value()
        if Switch == 'None':
            Board = None
        else:
            Board = BoardConf.SwitchMatrix[Switch]

        self.addChild(SwitchMatrixConfig(Board=Board,
                                         name='SwitchMatrixConf',
                                         title='Switch Matrix Configuration'))
