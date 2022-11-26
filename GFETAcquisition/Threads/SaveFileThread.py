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
from datetime import datetime
import matplotlib.pyplot as plt


def save_dict_to_hdf5(dic, filename):
    """
    ....
    """
    with h5py.File(filename, 'w') as h5file:
        recursively_save_dict_contents_to_group(h5file, '/', dic)


def recursively_save_dict_contents_to_group(h5file, path, dic):
    """
    ....
    """
    for key, item in dic.items():
        if item is None:
            continue
        if isinstance(item, (np.ndarray, int, float, str, bytes)):
            h5file[path + key] = item
        elif isinstance(item, dict):
            recursively_save_dict_contents_to_group(h5file, path + key + '/', item)
        else:
            try:
                h5file[path + key] = str(item)
            except:
                raise ValueError('Cannot save %s type' % type(item))


def load_dict_from_hdf5(filename):
    """
    ....
    """
    with h5py.File(filename, 'r') as h5file:
        return recursively_load_dict_contents_from_group(h5file, '/')


def recursively_load_dict_contents_from_group(h5file, path):
    """
    ....
    """
    ans = {}
    for key, item in h5file[path].items():
        if isinstance(item, h5py._hl.dataset.Dataset):
            v = item[()]
            if isinstance(v, bytes):
                ans[key] = v.decode()
            else:
                ans[key] = v
        elif isinstance(item, h5py._hl.group.Group):
            ans[key] = recursively_load_dict_contents_from_group(h5file, path + key + '/')
    return ans


class FileBuffer:
    def __init__(self, FileName, MaxSize, nChannels, SampSettings, Fields=None, dtype=float):
        self.FileBase = FileName.split('.h5')[0]
        self.PartCount = 0
        self.nChannels = nChannels
        self.MaxSize = MaxSize
        self.Fields = Fields
        self.SampSettings = SampSettings
        self.dtype = dtype
        self._initFile()

    def _initFile(self):
        if self.MaxSize is not None:
            FileName = '{}_{}.h5'.format(self.FileBase, self.PartCount)
        else:
            FileName = self.FileBase + '.h5'

        self.FileName = FileName
        self.h5File = h5py.File(FileName, 'w')

        if self.PartCount == 0 and self.Fields is not None:
            recursively_save_dict_contents_to_group(self.h5File, 'Configuration/', self.Fields)

        recursively_save_dict_contents_to_group(self.h5File, 'SamplingSettings/', self.SampSettings)
        self.h5File.create_dataset('Time', data=str(datetime.now()))
        self.Dset = self.h5File.create_dataset('data',
                                               shape=(0, self.nChannels),
                                               maxshape=(None, self.nChannels),
                                               # compression="gzip",
                                               compression='lzf',
                                               dtype=self.dtype
                                               )
        self.PartCount += 1

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
    def __init__(self, **kwargs):
        super(DataSavingThread, self).__init__()
        self.NewData = None
        self.FileBuff = FileBuffer(**kwargs)

    def run(self, *args, **kwargs):
        while True:
            if self.NewData is not None:
                # print(self.NewData.shape)
                self.FileBuff.AddSample(self.NewData)
                self.NewData = None
            else:
                # print('wait')
                Qt.QThread.msleep(25)

    def AddData(self, NewData):
        if self.NewData is not None:
            print('Error Saving !!!!')
        else:
            self.NewData = NewData

    def stop(self):
        self.FileBuff.h5File.close()
        self.terminate()


if __name__ == '__main__':

    import pickle

    # data = np.random.randint(low=-10, high=10, size=(1000000, 16), dtype='int32')
    data = np.random.rand(100000, 16)
    # data = np.float32(data)
    print(data.dtype)
    Iters = 10

    conf = pickle.load(open('state.pkl', 'rb'))
    SampSet = {'Fs': 1000,
               'nCols': 32,
               'SampsCol': 10}

    file = FileBuffer(FileName='test.h5', MaxSize=1000e6, nChannels=16,
                      SampSettings=SampSet, Fields=conf, dtype=data.dtype)

    OldTime = datetime.now()

    for i in range(Iters):
        file.AddSample(data)
    file.h5File.close()

    time = datetime.now() - OldTime
    print(time, (data.size * Iters) / time.total_seconds(), 'Samps/sec')

    # should test for bad type

    hf = h5py.File('test_0.h5', 'r')
    print(hf.keys())
    ss = recursively_load_dict_contents_from_group(hf, 'SamplingSettings/')
    print(ss)

    print(hf['data'].shape)
