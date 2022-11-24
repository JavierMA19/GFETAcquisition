#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 23:27:55 2022

@author: aguimera
"""

import pickle
import os

import pyqtgraph.parametertree.parameterTypes as pTypes
from PyQt5.QtWidgets import QFileDialog
from datetime import datetime

class SaveDataConf(pTypes.GroupParameter):
    def __init__(self, QTparent, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)

        self.QTparent = QTparent
        self.addChildren(({'name': 'SelFile',
                           'title': '...',
                           'type': 'action'},
                          {'name': 'bSave',
                           'title': 'Save Recording',
                           'type': 'bool',
                           'value': False,
                           'default': False},
                          {'name': 'FileName',
                           'title': 'Data File',
                           'type': 'str',
                           'value': ''},))

        self.param('SelFile').sigActivated.connect(self.on_Save)
        self.FileName = None

    def CheckFile(self, Col=None):
        if self.FileName is None:
            return

        pathfile, file = os.path.split(self.FileName)
        filename, extension = os.path.splitext(file)
        counter = 1
        filename = filename.split('-T_')[0]

        self.FileName = '{}-T_{}.{}'.format(filename,
                                            datetime.now(),
                                            extension)
        self.param('FileName').setValue(self.FileName)

    def on_Save(self):
        RecordFile, _ = QFileDialog.getSaveFileName(self.QTparent,
                                                    "Data File")
        if RecordFile:
            if not RecordFile.endswith('.h5'):
                RecordFile = RecordFile + '.h5'
            self.param('FileName').setValue(RecordFile)
            self.FileName = RecordFile
            self.param('bSave').setValue(True)
        else:
            self.param('FileName').setValue('')
            self.FileName = None
            self.param('bSave').setValue(False)


class SaveSateParams(pTypes.GroupParameter):
    def __init__(self, QTparent, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)

        self.QTparent = QTparent
        self.addChildren(({'name': 'SaveSweepConf',
                           'title': 'Save Sweep Configuration',
                           'type': 'action'},
                          {'name': 'LoadSweepConf',
                           'title': 'Load Sweep Configuration',
                           'type': 'action'},))

        self.param('SaveSweepConf').sigActivated.connect(self.on_SaveSweepConf)
        self.param('LoadSweepConf').sigActivated.connect(self.on_LoadSweepConf)

    def _GetParent(self):
        parent = self.parent()
        return parent

    def on_LoadSweepConf(self):
        RecordFile, _ = QFileDialog.getOpenFileName(self.QTparent,
                                                    "Open state File")
        if RecordFile:
            parent = self._GetParent().param('SweepsConfig')
            parent.restoreState(pickle.load(open(RecordFile, 'rb'))['Restore'])

    def on_SaveSweepConf(self):
        RecordFile, _ = QFileDialog.getSaveFileName(self.QTparent,
                                                    "Save state File")

        if RecordFile:
            parent = self._GetParent().param('SweepsConfig')
            Data = {'Restore': parent.saveState(filter='user')}
            pickle.dump(Data, open(RecordFile, 'wb'))
