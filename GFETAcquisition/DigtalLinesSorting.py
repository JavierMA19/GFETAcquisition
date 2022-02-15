# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 14:14:07 2020

@author: user
"""

HwMap = {'aiChannels': {'Ch01': ('ai0', 'ai8'),
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
                                  'Ch16': ('ai23', 'ai31')},

                   'aoChannels': {'ChVs': 'ao1',
                                  'ChVds': 'ao0',
                                  'ChAo2': None,
                                  'ChAo3': None, },

        'ColOuts': { 'Col05': ('line0', 'line1'),
                        'Col06': ('line2', 'line3'),
                        'Col08': ('line4', 'line5'),
                        'Col07': ('line6', 'line7'),
                        'Col02': ('line8', 'line9'),
                        'Col04': ('line10', 'line11'),
                        'Col01': ('line12', 'line13'),
                        'Col03': ('line14', 'line15'),
                        'Col16': ('line16', 'line17'),
                        'Col15': ('line18', 'line19'),
                        'Col13': ('line20', 'line21'),
                        'Col14': ('line22', 'line23'),
                        'Col11': ('line24', 'line25'),
                        'Col09': ('line26', 'line27'),
                        'Col12': ('line28', 'line29'),
                        'Col10': ('line30', 'line31'),
                       },

                    }, 

import numpy as np

# samples per column
nSampsCo = 1

# hardware mapping
doColumns = HwMap[0]['ColOuts']

# columns to Mux
# DigColumns = (
#               'Col01',
#               'Col02',
#               'Col03',
#               'Col04',
#               'Col05',
#               'Col06',
#               'Col07',
#               'Col08',
#               'Col09',
#               'Col10',
#               'Col11',
#               'Col12',
#               'Col13',
#               'Col14',
#               'Col15',
#               'Col16'
#             )

DigColumns = tuple(doColumns)
## function implementation
## def SetDigitalOutputs(self, nSampsCo):

IndexDigitalLines = {}
hwLinesMap = {}
i = 0
for ColName, hwLine in doColumns.items():
    print(ColName)
    il = int(hwLine[0][4:])
    hwLinesMap[il] = (ColName, hwLine)

j = 0
NewInd = {}
for i, c in sorted(hwLinesMap.items()):
    for n in DigColumns:
        if n == c[0]:
            NewInd[j] = c[0]
            j += 1

# Gen inverted control output, should be the next one of the digital line ('lineX', 'lineX+1')
if len(doColumns[ColName]) > 1:
    GenInvert = True
else:
    GenInvert = False

# GenInvert = False

# Gen sorted indexes for demuxing
SortIndDict = {}
for ic, coln in enumerate(sorted(DigColumns)):
    SortIndDict[coln] = ic

DOut = np.array([], dtype=np.bool)
SortDInds = np.zeros((len(DigColumns), nSampsCo), dtype=np.int8)
SwitchOrder = 0
for il, (nLine, (LineName, hwLine)) in enumerate(sorted(hwLinesMap.items())):
    Lout = np.zeros((1, nSampsCo*len(DigColumns)), dtype=np.bool)    
    if LineName in DigColumns:
        print(il, nLine, hwLine, LineName)
        Lout[0, nSampsCo * SwitchOrder: nSampsCo * (SwitchOrder + 1)] = True
        SortDInds[SortIndDict[LineName], : ] = np.arange(nSampsCo * SwitchOrder,
                                                     nSampsCo * (SwitchOrder + 1) )
        SwitchOrder += 1
    
    if GenInvert:
        Cout = np.vstack((Lout, ~Lout))
    else:
        Cout = Lout        
    DOut = np.vstack((DOut, Cout)) if DOut.size else Cout

    
# # Vigila amb el sorting dels canal per demux... segurament dependrà de l'ordre de les lines

# if GenInvert:
#     for line in DOut[0:-1:2, :]:
#         if True in line:
#             SortDInds.append(np.where(line))
# else:
#     for line in DOut:
#         if True in line:
#             SortDInds.append(np.where(line))

SortDIndsL = [inds for inds in SortDInds]
    

Dout = DOut.astype(np.uint8)
