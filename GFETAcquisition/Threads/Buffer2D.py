import numpy as np


class Buffer2D(np.ndarray):

    def __new__(subtype, Fs, nChannels, ViewBuffer,
                dtype=float, buffer=None, offset=0,
                strides=None, order=None, info=None):
        # Create the ndarray instance of our type, given the usual
        # ndarray input arguments.  This will call the standard
        # ndarray constructor, but return an object of our type.
        # It also triggers a call to InfoArray.__array_finalize__
        BufferSize = int(ViewBuffer * Fs)
        shape = (BufferSize, nChannels)
        obj = super(Buffer2D, subtype).__new__(subtype, shape, dtype,
                                               buffer, offset, strides,
                                               order)
        # set the new 'info' attribute to the value passed
        obj.counter = 0
        obj.totalind = 0
        obj.Fs = float(Fs)
        obj.Ts = 1 / obj.Fs
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None:
            return
        self.counter = getattr(obj, 'counter', None)
        self.totalind = getattr(obj, 'totalind', None)
        self.Fs = getattr(obj, 'Fs', None)
        self.Ts = getattr(obj, 'Ts', None)

    # def AddData(self, NewData):
    #     newsize = NewData.shape[0]
    #     shift = newsize * np.ones((NewData.shape[1]), dtype='int')
    #     self = np.roll(self, shift, axis=0)
    #     self[-newsize:, :] = NewData
    #     self.counter += NewData.shape[0]
    #     self.totalind += NewData.shape[0]

    def AddData(self, NewData):
        newsize = NewData.shape[0]
        if newsize > self.shape[0]:
            self[:, :] = NewData[:self.shape[0], :]
        else:
            self[0:-newsize, :] = self[newsize:, :]
            self[-newsize:, :] = NewData
        self.counter += newsize
        self.totalind += newsize

    def IsFilled(self):
        return self.counter >= self.shape[0]

    def GetTimes(self, Size):
        stop = self.Ts * self.totalind
        start = stop - self.Ts * Size
        times = np.arange(start, stop, self.Ts)
        return times[-Size:]

    def Reset(self):
        self.counter = 0


if __name__ == '__main__':

    # MyB = Buffer2D(Fs=1000, nChannels=10, ViewBuffer=10)*np.nan
    # data = np.ones((100, 10))
    #
    # for i in range(5):
    #     MyB.AddData(data)
    #     print(MyB)

    MyB = np.ones((20, 3))

    for i in range(30):
        nd = np.ones((2, 3))*i
        shift = -nd.shape[0] * np.ones((nd.shape[1]), dtype='int')
        MyB = np.roll(MyB, shift)
        MyB[-nd.shape[0]:, :] = nd





