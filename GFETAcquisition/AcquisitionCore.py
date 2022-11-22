from PyQt5 import Qt
from GFETAcquisition.Threads.DaqInterface import WriteDigital, ReadAnalog, WriteAnalog
from GFETAcquisition.Threads.Plotters import Plotter as TimePlotter
from GFETAcquisition.Threads.Plotters import PSDPlotter
from GFETAcquisition.Threads.SaveFileThread import DataSavingThread
from datetime import datetime


class SwitchMatrixInterface:
    def __init__(self, HardConf):
        if HardConf.param('SwitchMatrixConf').SwitchMatrixPresent:
            self.Active = True
            self.ColsSel = HardConf.param('SwitchMatrixConf').Columns.GetColumns()
            self.ColsList = list(self.ColsSel)
            self.SwitchDout = WriteDigital(HardConf.param('SwitchMatrixConf').douts)
            self.CurrentColumn = 'ColXX'
            self.cAouts = HardConf.param('SwitchMatrixConf').AOutputs.GetAOuts()
            self.InitAouts()
        else:
            self.Active = False
            self.ColsSel = None
            self.ColsList = None
            self.SwitchDout = None
            self.CurrentColumn = ''

    def InitAouts(self):
        self.Aouts = {}
        for n, c in self.cAouts.items():
            self.Aouts[n] = WriteAnalog((c['Output'],))
            self.Aouts[n].SetVal(c['Value'])

    def SetSwitchCol(self, Col):
        print(Col, self.ColsSel[Col])
        succes = self.SwitchDout.SetDigitalSignal(self.ColsSel[Col])
        if succes:
            self.CurrentColumn = Col
        return succes


class HardwareInterface(Qt.QObject):
    SigRawData = Qt.pyqtSignal(object)

    def __init__(self, AcquisitionConf):
        super(HardwareInterface, self).__init__()

        self.ACDCSwDouts = None
        self.ACDCSwitch = None
        self.BiasVd = None
        self.Board = AcquisitionConf.HardConf.param('BoardConf')
        self.cAouts = self.Board.AOutputs.GetAOuts()
        self.cGains = self.Board.Gains.GetGains()

        self.AcqConf = AcquisitionConf

        self.InitAouts()
        self.InitAinputs()
        self.Init_ACDCSwitch()

        # self.aiChNames = self.cDCChannels.keys()
        # self.cDCChannels = self.Board.AInputs.GetDCChannels()
        # self.cACChannels = self.Board.AInputs.GetACChannels()

        # print(self.Aouts)
        # print(self.cDCChannels)
        # print(self.cDCChannels)

    def Init_ACDCSwitch(self):
        self.ACDCSwitch = self.Board.ACDCSwitch
        if self.ACDCSwitch is not None:
            self.ACDCSwDouts = WriteDigital(self.ACDCSwitch.douts)

    def Select_ACDCSwitch(self, State):
        if self.ACDCSwitch is not None:
            val = self.ACDCSwitch.States[State]
            self.ACDCSwDouts.SetDigitalSignal(val)

    def InitAouts(self):
        self.Aouts = {}
        for n, c in self.cAouts.items():
            self.Aouts[n] = WriteAnalog((c['Output'],))
            self.Aouts[n].SetVal(c['Value'])

    def SetBias(self, Vgs, Vds):
        self.Aouts['Vs'].SetVal(-Vgs)
        self.Aouts['Vds'].SetVal(Vds)
        self.BiasVd = Vds - Vgs

    # def SetTestSignal(self, Sig):
    #     if 'Vg' in self.Aouts:
    #         self.Aouts['Vg'].SetSignal(Signal=Sig,
    #                                    nSamps=Sig.size)
    # def StopTestSignal(self):
    #     if 'Vg' in self.Aouts:
    #         self.Aouts['Vg'].ClearTask()
    #         self.Aouts['Vg'] = WriteAnalog((self.cAouts['Vg']['Output'],))
    #         self.Aouts['Vg'].SetVal(0)

    def InitAinputs(self):
        Channels = self.AcqConf.GetAcqChannels()
        self.aiIns = ReadAnalog(Channels['aiChannels'])

    def StartRead(self):
        # self.Ains = ReadAnalog(self.aiAC)
        # self.Select_ACDCSwitch('AC')
        self.aiIns.EveryNEvent = self.on_RawData
        # self.Ains.DoneEvent = self.on_AC_Data
        Fs = self.AcqConf.SamplingConf.param('Fs').value()
        nSamps = self.AcqConf.SamplingConf.param('BufferSize').value()
        self.aiIns.ReadContData(Fs=Fs, EverySamps=nSamps)

    def on_RawData(self, Data):
        Ids = Data / self.cGains['ACGain']
        self.SigRawData.emit(Ids)

    def StopRead(self):
        self.aiIns.StopTask()


class AcquisitionMachine(Qt.QObject):

    def __init__(self, AcquisitionConf, PlotDataConf):
        super(AcquisitionMachine, self).__init__()

        self.FileName = None
        self.thRawTime = None
        self.thRawPSD = None
        self.OldTime = datetime.now()
        self.HardInt = None

        self.AcqConf = AcquisitionConf

        self.PlotConf = PlotDataConf

        self.AcqRunning = False

    def InitPlots(self):
        if self.PlotConf.bRawTime:
            kwargs = self.PlotConf.RawPlotTimeConf.GetParams()
            self.thRawTime = TimePlotter(**kwargs)
            self.thRawTime.start()
        else:
            self.thRawTime = None

        if self.PlotConf.bRawPSD:
            pkw = self.PlotConf.RawPlotTimeConf.GetParams()
            kwargs = self.PlotConf.RawPlotPSDConf.GetParams()
            self.thRawPSD = PSDPlotter(ChannelConf=pkw['ChannelConf'], **kwargs)
            self.thRawPSD.start()
        else:
            self.thRawPSD = None

        # if self.PlotConf.bDemuxTime:
        #
        # if self.PlotConf.bDemuxPSD:

    def StartAcquisition(self):
        if self.AcqRunning:
            self.HardInt.StopRead()
            self.AcqRunning = False
        else:
            self.CheckSave()
            # self.HardInt = HardwareInterface(self.AcqConf)
            # self.HardInt.SigRawData.connect(self.on_RawData)
            # self.HardInt.StartRead()
            # self.InitPlots()
            # self.AcqRunning = True

    def CheckSave(self):
        if not self.AcqConf.FileConf.param('bSave').value():
            self.AcqConf.FileConf.on_Save()
        self.AcqConf.FileConf.CheckFile()

        self.FileName = self.AcqConf.FileConf.FileName

    def on_RawData(self, Data):
        time = datetime.now()
        print(time-self.OldTime)
        self.OldTime = time
        if self.thRawTime is not None:
            self.thRawTime.AddData(Data)
        if self.thRawPSD is not None:
            self.thRawPSD.AddData(Data)
