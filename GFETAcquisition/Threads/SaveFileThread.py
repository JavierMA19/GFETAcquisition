#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 17:42:36 2019

@author: aguimera
"""

import pyqtgraph.parametertree.parameterTypes as pTypes
from PyQt5.QtWidgets import QFileDialog
import h5py
from PyQt5 import Qt
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt


class FileBuffer:
    def __init__(self, FileName, MaxSize, nChannels, Fields):
        self.FileBase = FileName.split('.h5')[0]
        self.PartCount = 0
        self.nChannels = nChannels
        self.MaxSize = MaxSize
        self.Fields = Fields
        self._initFile()

    def _initFile(self):
        if self.MaxSize is not None:
            FileName = '{}_{}.h5'.format(self.FileBase, self.PartCount)
        else:
            FileName = self.FileBase + '.h5'

        self.FileName = FileName
        self.PartCount += 1
        self.h5File = h5py.File(FileName, 'w')
        for k, v in self.Fields:
            self.h5File.create_dataset(k, data=v)

        self.Dset = self.h5File.create_dataset('data',
                                               shape=(0, self.nChannels),
                                               maxshape=(None, self.nChannels),
                                               # compression="gzip",
                                               compression='lzf',
                                               )

    def AddSample(self, Sample):
        nSamples = Sample.shape[0]
        FileInd = self.Dset.shape[0]
        self.Dset.resize((FileInd + nSamples, self.nChannels))
        self.Dset[FileInd:, :] = Sample
        self.h5File.flush()

        stat = os.stat(self.FileName)
        if stat.st_size > self.MaxSize:
            self.h5File.close()
            self._initFile()

    # def RefreshPlot(self):
    #     plt.figure()
    #     x, y = self.Dset.shape
    #     Time = np.linspace(0, x/self.Fs, x)
    #     plt.plot(Time, self.Dset)


class DataSavingThread(Qt.QThread):
    def __init__(self, FileName, nChannels, Fields,
                 MaxSize=None, dtype='float'):
        super(DataSavingThread, self).__init__()
        self.NewData = None
        self.FileBuff = FileBuffer(FileName=FileName,
                                   nChannels=nChannels,
                                   MaxSize=MaxSize,
                                   Fields=Fields)

    def run(self, *args, **kwargs):
        while True:
            if self.NewData is not None:
                self.FileBuff.AddSample(self.NewData)
                self.NewData = None
            else:
                Qt.QThread.msleep(100)

    def AddData(self, NewData):
        if self.NewData is not None:
            print('Error Saving !!!!')
        else:
            self.NewData = NewData

    def stop(self):
        self.FileBuff.h5File.close()
        self.terminate()
