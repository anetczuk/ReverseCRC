# MIT License
#
# Copyright (c) 2017 Arkadiusz Netczuk <dev.arnet@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from crc.hwcrc import HwCRC
from crc.numbermask import NumberMask
from crc.crcproc import CRCProc



GlobalLookupTables = {}

class LookupCRC(CRCProc):
    def __init__(self, lookupSize):
        CRCProc.__init__(self)
        self.lookupSize = lookupSize

    def calculate3(self, dataMask, polyMask):
        lookup = self.prepareTable(polyMask)

        dataSize = max(dataMask.dataSize, self.lookupSize)
        assert (dataSize % self.lookupSize) == 0

        register = 0
        rep = dataSize / self.lookupSize
        crcMask = (1 << polyMask.dataSize) - 1
        lookupMask = (1 << self.lookupSize) - 1
        valMask = lookupMask << (dataSize - self.lookupSize)

        indexShift = polyMask.dataSize - self.lookupSize
        indexMask = lookupMask << indexShift

        inputData = dataMask.dataNum
        for i in range(0, rep):
            val = (inputData & valMask) >> self.lookupSize*(rep-i-1)
            valMask >>= self.lookupSize
#             print "val: {1:X} {1:04b}".format(valMask, val)
            index = (register & indexMask) >> indexShift
            index ^= val
            ##index = (register & lookupMask) ^ val
            register = (register << self.lookupSize) & crcMask
            register ^= lookup[index]

        return register

    def prepareTable(self, polyMask):
        lookup = {}
        crcProc = HwCRC()
        maxVal = 1 << self.lookupSize
        for i in range(0, maxVal):
            data = NumberMask(i, self.lookupSize)
            lookup[i] = crcProc.calculate3(data, polyMask)
        return lookup

