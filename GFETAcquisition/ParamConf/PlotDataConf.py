import pyqtgraph.parametertree.parameterTypes as pTypes
from GFETAcquisition.Threads.Plotters import TimePlotConfig, PSDPlotConfig

from PyQt5 import Qt
import GFETAcquisition.ParamConf.HwConfig as BoardConf

PlotDataConf = {'name': 'BiasConf',
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


class PlotDataConfig(pTypes.GroupParameter):

    def __init__(self, AcquisitionConfig, **kwargs):
        pTypes.GroupParameter.__init__(self, **kwargs)

        self.pRefresh = self.addChild({'name': 'RegenPlots',
                                       'title': 'Refresh Plots',
                                       'type': 'action'})

        self.pRawTime = self.addChild({'name': 'RawDataTime',
                                       'title': 'Plot Time Raw',
                                       'type': 'bool',
                                       'value': False})
        self.pRawPSD = self.addChild({'name': 'RawPSD',
                                      'title': 'PSD Raw',
                                      'type': 'bool',
                                      'value': False})
        self.pDemuxTime = self.addChild({'name': 'DemuxTime',
                                         'title': 'Plot Time Demux',
                                         'type': 'bool',
                                         'value': False})
        self.pDemuxPSD = self.addChild({'name': 'DemuxPSD',
                                        'title': 'PSD Demux',
                                        'type': 'bool',
                                        'value': False})

        self.pRawTime.sigValueChanged.connect(self.on_update_bools)
        self.pRawPSD.sigValueChanged.connect(self.on_update_bools)
        self.pDemuxTime.sigValueChanged.connect(self.on_update_bools)
        self.pDemuxPSD.sigValueChanged.connect(self.on_update_bools)

        self.RawPlotTimeConf = self.addChild(TimePlotConfig(name='RawTimePlotConf',
                                                            title='Raw Time',
                                                            visible=False))

        self.RawPlotPSDConf = self.addChild(PSDPlotConfig(name='RawPlotPSDConf',
                                                          tittle='Raw PSD',
                                                          visible=False))

        self.DemuxPlotTimeConf = self.addChild(TimePlotConfig(name='DemuxPlotTimeConf',
                                                              title='Demux Time',
                                                              visible=False))

        self.DemuxPlotPSDConf = self.addChild(PSDPlotConfig(name='DemuxPlotPSDConf',
                                                            tittle='Demux PSD',
                                                            visible=False))

        self.AcqConf = AcquisitionConfig
        self.AcqConf.sigFsChanged.connect(self.on_sigFsChanged)
        self.AcqConf.sigAcqChannelsChanged.connect(self.on_sigAcqChannelsChanged)
        self.AcqConf.sigHardwareChanged.connect(self.on_sigHardwareChanged)

        self.on_update_bools()
        self.on_sigHardwareChanged()
        self.on_sigFsChanged()

    def on_sigFsChanged(self):
        Fs = self.AcqConf.SamplingConf.param('Fs').value()
        self.RawPlotTimeConf.param('Fs').setValue(Fs)
        self.RawPlotPSDConf.param('Fs').setValue(Fs)

        FsDem = self.AcqConf.TimeMuxConf.param('FsCol').value()
        self.DemuxPlotTimeConf.param('Fs').setValue(FsDem)
        self.DemuxPlotPSDConf.param('Fs').setValue(FsDem)

    def on_sigAcqChannelsChanged(self, AcqChannels):
        self.RawPlotTimeConf.SetChannels(AcqChannels['RawChannels'])
        nch = self.RawPlotTimeConf.param('nChannels').value()
        self.RawPlotPSDConf.param('nChannels').setValue(nch)

    def on_sigHardwareChanged(self):
        if self.AcqConf.HardConf.SwitchMatrix.SwitchMatrixPresent:
            self.pDemuxTime.setOpts(**{'enabled': True})
            self.pDemuxPSD.setOpts(**{'enabled': True})
        else:
            self.pDemuxTime.setOpts(**{'enabled': False,
                                       'value': False})
            self.pDemuxPSD.setOpts(**{'enabled': False,
                                      'value': False})

    def on_update_bools(self):
        self.bRawTime = self.pRawTime.value()
        self.bRawPSD = self.pRawPSD.value()
        self.bDemuxTime = self.pDemuxTime.value()
        self.bDemuxPSD = self.pDemuxPSD.value()

        self.RawPlotTimeConf.setOpts(**{'visible': self.bRawTime})
        self.DemuxPlotTimeConf.setOpts(**{'visible': self.bDemuxTime})
        self.RawPlotPSDConf.setOpts(**{'visible': self.bRawPSD})
        self.DemuxPlotPSDConf.setOpts(**{'visible': self.bDemuxPSD})
