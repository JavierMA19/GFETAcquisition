from PyQt5 import Qt
from GFETAcquisition.Threads.DaqInterface import WriteDigital, ReadAnalog, WriteAnalog


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

    def StartRead(self ):
        # self.Ains = ReadAnalog(self.aiAC)
        # self.Select_ACDCSwitch('AC')
        self.aiIns.EveryNEvent = self.on_RawData
        # self.Ains.DoneEvent = self.on_AC_Data
        self.aiIns.ReadContData(Fs=1000,
                           EverySamps=1000)

    def on_RawData(self, Data):
        Ids = Data / self.cGains['ACGain']
        self.SigRawData.emit(Ids)

    def StopRead(self):
        self.Ains.ClearTask()


class AcquisitionMachine(Qt.QObject):

    def __init__(self, AcquisitionConf):
        super(AcquisitionMachine, self).__init__()

        self.HardInt = HardwareInterface(AcquisitionConf)
        self.HardInt.SigRawData.connect(self.on_RawData)

    def StartAcquisition(self):
        self.HardInt.StartRead()

    def on_RawData(self, Data):
        print(Data.shape)


