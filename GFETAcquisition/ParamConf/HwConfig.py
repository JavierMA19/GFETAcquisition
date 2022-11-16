# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 11:14:17 2020

@author: javi8
"""

import numpy as np

###
# Boards definition
###

DefaultGains = {'DCGain': 10e3,
                'ACGain': 1e6,
                'GateGain': 2e6}

MainBoard = {'Gains': DefaultGains,
             'AnalogInputs': {'Ch01': ('ai0', 'ai8'),
                              'Ch02': ('ai1', 'ai9'),
                              'Ch03': ('ai2', 'ai10'),
                              'Ch04': ('ai3', 'ai11'),
                              'Ch05': ('ai4', 'ai12'),
                              'Ch06': ('ai5', 'ai13'),
                              'Ch07': ('ai6', 'ai14'),
                              'Ch08': ('ai7', 'ai15'),
                              'Ch09': ('ai16', 'ai24'),
                              'Ch10': ('ai17', 'ai25'),
                              'Ch11': ('ai18', 'ai26'),
                              'Ch12': ('ai19', 'ai27'),
                              'Ch13': ('ai20', 'ai28'),
                              'Ch14': ('ai21', 'ai29'),
                              'Ch15': ('ai22', 'ai30'),
                              'Ch16': ('ai23', 'ai31')
                              },
             'AnalogOutputs': {'Vs': 'ao1',
                               'Vds': 'ao0',
                               'Vg': 'ao2',
                               },
             }

MB42 = {'Gains': {'DCGain': 10e3,
                  'ACGain': 1e6,
                  },
        'AnalogInputs': {
            'Ch01': ('ai16', 'ai24'),
            'Ch02': ('ai17', 'ai25'),
            'Ch03': ('ai18', 'ai26'),
            'Ch04': ('ai19', 'ai27'),
            'Ch05': ('ai20', 'ai28'),
            'Ch06': ('ai21', 'ai29'),
            'Ch07': ('ai22', 'ai30'),
            'Ch08': ('ai23', 'ai31'),
            'Ch09': ('ai0', 'ai8'),
            'Ch10': ('ai1', 'ai9'),
            'Ch11': ('ai2', 'ai10'),
            'Ch12': ('ai3', 'ai11'),
            'Ch13': ('ai4', 'ai12'),
            'Ch14': ('ai5', 'ai13'),
            'Ch15': ('ai6', 'ai14'),
            'Ch16': ('ai7', 'ai15'),
        },
        'AnalogOutputs': {'Vs': 'ao1',
                          'Vds': 'ao0',
                          },
        }

MainBoard_v3 = {'Gains': DefaultGains,
                'AnalogInputs': {'Ch01': ('ai8',),
                                 'Ch11': ('ai12',),
                                 'Ch03': ('ai9',),
                                 'Ch09': ('ai15',),
                                 'Ch05': ('ai10',),
                                 'Ch15': ('ai14',),
                                 'Ch07': ('ai11',),
                                 'Ch13': ('ai13',),
                                 'Ch02': ('ai0',),
                                 'Ch12': ('ai4',),
                                 'Ch04': ('ai1',),
                                 'Ch10': ('ai7',),
                                 'Ch06': ('ai2',),
                                 'Ch16': ('ai6',),
                                 'Ch08': ('ai3',),
                                 'Ch14': ('ai5',),
                                 'Ch27': ('ai27',),
                                 'Ch17': ('ai29',),
                                 'Ch25': ('ai26',),
                                 'Ch19': ('ai30',),
                                 'Ch31': ('ai25',),
                                 'Ch21': ('ai31',),
                                 'Ch29': ('ai24',),
                                 'Ch23': ('ai28',),
                                 'Ch28': ('ai19',),
                                 'Ch18': ('ai21',),
                                 'Ch26': ('ai18',),
                                 'Ch20': ('ai22',),
                                 'Ch32': ('ai17',),
                                 'Ch22': ('ai23',),
                                 'Ch30': ('ai16',),
                                 'Ch24': ('ai20',)
                                 },
                'AnalogOutputs': {'Vs': 'ao1',
                                  'Vds': 'ao0',
                                  'Vg': 'ao2',
                                  },
                'ACDCSwitch': {'douts': ('port0/line0:8',),
                               'states': {'DC': np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                                                         dtype=np.uint8),
                                          'AC': np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                                         dtype=np.uint8),
                                          'Gate': np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                                           dtype=np.uint8),
                                          },
                               'GateAI': 'ai27',
                               }
                }

Boards = {'MainBoard_v3': MainBoard_v3,
          'MainBoard': MainBoard,
          'MB42': MB42,
          }


###
# Switch Matrix definition
###

def ColumnDecoder(bits=5, nCols=32):
    Cols = {}
    sform = '{' + '0:0{:d}b'.format(bits) + '}'
    for i in range(nCols):
        name = 'Col{0:02d}'.format(i + 1)
        Cols[name] = np.array([int(x) for x in list(sform.format(i))], dtype=np.uint8)
    return Cols


Decoder32Cols = {'douts': ('port0/line9:15',),
                 'Columns': ColumnDecoder(),
                 'AnalogOutputs': {'Von': 'ao2',
                                   'Voff': 'ao3',
                                   },
                 }


def ColumnInverter(nCols=16):
    Cols = {}
    for i in range(nCols):
        name = 'Col{0:02d}'.format(i + 1)
        Base = np.ones((nCols * 2), dtype=np.bool)
        Base[0::2] = False
        Base[i * 2] = True
        Base[(i * 2) + 1] = False
        Cols[name] = Base.astype(np.uint8)
    return Cols


Mos16Cols = {'douts': ('port0/line0:31',),
             'Columns': ColumnInverter(nCols=16),
             'AnalogOutputs': {'Von': 'ao2',
                               'Voff': 'ao3',
                               },
             }

SwitchMatrix = {'Decoder32Cols': Decoder32Cols,
                'Mos16Cols': Mos16Cols,
                }

# if __name__ == '__main__':
#
#     nCols = 32
#
#     Cols = {}
#     sform = '{' + '0:0{:d}b'.format(7) + '}'
#     for i in range(32):
#         name = 'Col{0:02d}'.format(i + 1)
#         Cols[name] = np.array([int(x) for x in list(sform.format(i))], dtype=np.uint8)
#
#     print(Cols)
