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

from crc.crcproc import CRCProcessor, CRCProcessorFactory
from crc.divisioncrcbackward import DivisionCRCBackward


## ===================================================================


class DivisionCRCProcessorFactory( CRCProcessorFactory ):

    # crcSize -- int, number of bits
    # return CRCProcessor
    def createForwardProcessor(self, crcSize=None):
        return DivisionCRC()

    # crcSize -- int, number of bits
    # return CRCInvertProcessor
    def createInvertProcessor(self, crcSize=None):
        return DivisionCRCBackward()

    # crcSize -- int, number of bits
    # inputData: List[ (NumberMask, NumberMask) ]
    # return CRCOperator
    def createOperator(self, crcSize, inputData):
        raise NotImplementedError( "DivisionCRC -- not implemented" )


## ===================================================================


class DivisionCRC( CRCProcessor ):
    def __init__(self):
        CRCProcessor.__init__(self)

    def calculate3(self, dataMask, polyMask):
        if self._reversed == False:
            return self.calculateMSB(dataMask, polyMask)
        else:
            return self.calculateLSB(dataMask, polyMask)

    ## old implementation is very helpful when defining backward algorithm
    ## 'poly' without leading '1'
    def calculateMSB(self, dataMask, polyMask):
        ## MSB first

        ## with leading '1' to xor out bit on shifting
        polyMasterBit = polyMask.masterBit
        genPoly = polyMask.dataNum | polyMasterBit
        dataNum = dataMask.dataNum

        ## init shift register
        initShift = min(polyMask.dataSize, dataMask.dataSize)
        register = dataMask.getMSB(initShift) ^ self.registerInit
        dataBit = (dataMask.masterBit >> (initShift+1))

        ## divide
        for _ in xrange(initShift, dataMask.dataSize):
            register <<= 1
            if (dataNum & dataBit) > 0:
                register |= 1
            if (register & polyMasterBit) > 0:
                register ^= genPoly
            dataBit >>= 1

        ### shift crc zeros
        for _ in xrange(0, polyMask.dataSize):
            register <<= 1
            if (register & polyMasterBit) > 0:
                register ^= genPoly

        return (register ^ self.xorOut) & polyMask.dataMask

    ## old implementation is very helpful when defining backward algorithm
    ## 'poly' without leading '1'
    ## 'dataMask' and 'polyMask' have to be reversed
    def calculateLSB(self, dataMask, polyMask):
        ## LSB first

        dataNum = dataMask.dataNum
        polyNum = polyMask.dataNum
        polyMasterBit = polyMask.masterBit

        ## init shift register
        initShift = min(polyMask.dataSize, dataMask.dataSize)
        register = dataMask.getLSB(initShift) ^ self.registerInit
        dataBit = (1 << initShift)

        ## divide
        for _ in xrange(initShift, dataMask.dataSize):
            if (dataNum & dataBit) > 0:
                register |= polyMasterBit
            lastBit = register & 1
            register >>= 1
            if lastBit > 0:
                register ^= polyNum
            dataBit <<= 1

        ### shift crc zeros
        for _ in xrange(0, polyMask.dataSize):
            lastBit = register & 1
            register >>= 1
            if lastBit > 0:
                register ^= polyNum

        return (register ^ self.xorOut) & polyMask.dataMask
