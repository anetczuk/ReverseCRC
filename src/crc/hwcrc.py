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


from crc.crcproc import CRCProc


##
##
class HwCRC( CRCProc ):
    def __init__(self):
        CRCProc.__init__(self)

    def calculate3(self, dataMask, polyMask):
        if self.reversed == False:
            return self.calculateMSB(dataMask, polyMask)
        else:
            return self.calculateLSB(dataMask, polyMask)

    ## 'poly' without leading '1'
    def calculateMSB(self, dataMask, polyMask):
        register = self.registerInit

        dataNum = dataMask.dataNum
        dataBit = (dataMask.masterBit >> 1)
        polyMasterBit = polyMask.masterBit

        crcMSB = (polyMask.masterBit >> 1)
        poly = polyMask.dataNum | polyMasterBit

        while(dataBit > 0):                             ## while is faster than 'for'
            if (dataNum & dataBit) > 0:
                register ^= crcMSB
            dataBit >>= 1
            register <<= 1
            if (register & polyMasterBit) > 0:
                register ^= poly                        ## master bit will be xor-ed out to '0'

        return (register ^ self.xorOut) & polyMask.dataMask

    ## 'poly' without leading '1'
    ## 'dataMask' and 'polyMask' have to be reversed
    def calculateLSB(self, dataMask, polyMask):
        register = self.registerInit

        dataNum = dataMask.dataNum
        dataSize = dataMask.dataSize
        polyNum = polyMask.dataNum
        dataBit = 1

        for _ in xrange(0, dataSize):          ## for is faster than while
            if (dataNum & dataBit) > 0:
                register ^= 1
            lastBit = register & 1
            register >>= 1
            if lastBit > 0:
                register ^= polyNum
            dataBit <<= 1

        return (register ^ self.xorOut) & polyMask.dataMask
