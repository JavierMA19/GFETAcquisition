# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 09:25:47 2019

@author: aguimera
"""

import pyqtgraph.parametertree.parameterTypes as pTypes
import numpy as np


class AcquisitionConfig(pTypes.GroupParameter):

    def __init__(self, HardConf, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)

        def __init__(self, HardConf, **kwargs):
            pTypes.GroupParameter.__init__(self, **kwargs)

#            HardConf.on_board_sel.connect(self.on_Board_sel)

            # Add paramters
            self.addChildren(({'title': 'Cycles',
                               'name': 'Cycles',
                               'type': 'int',
                               'default': 1,
                               'value': 1},
                              {'title': 'Measure PSD',
                               'name': 'CheckPSD',
                               'type': 'bool',
                               'value': False},
                              {'title': 'Measure Bode',
                               'name': 'CheckBode',
                               'type': 'bool',
                               'value': False},
                              {'title': 'Measure Gate',
                               'name': 'CheckGate',
                               'type': 'bool',
                               'value': False},
                              ))

