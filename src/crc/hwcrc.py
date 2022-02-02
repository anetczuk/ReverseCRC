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

from crc.crcproc import CRCProcessor, CRCOperator, CRCProcessorFactory,\
    StandardCRCOperator

from crc.numbermask import reverse_number
from collections import Counter
from crc.hwcrcbackward import create_backward_processor

from fastcrc.utils import convert_to_msb_list, convert_to_lsb_list


## ===================================================================


class HwCRCProcessorFactory( CRCProcessorFactory ):

    # crcSize -- int, number of bits
    # return CRCProcessor
    def createForwardProcessor(self, crcSize=None):
        return create_processor(crcSize)

    # crcSize -- int, number of bits
    # return CRCInvertProcessor
    def createInvertProcessor(self, crcSize=None):
        return create_backward_processor( crcSize )

    # crcSize -- int, number of bits
    # inputData: List[ (NumberMask, NumberMask) ]
    # return CRCOperator
    def createOperator(self, crcSize, inputData):
        processor = create_processor(crcSize)
        return processor.createOperator( crcSize, inputData )


## ===================================================================


##
## standard implementation done in pure Python
class HwCRC( CRCProcessor ):

    def __init__(self):
        CRCProcessor.__init__(self)

    ## override
    def setReversed(self, value = True):
        CRCProcessor.setReversed(self, value)
        ## optimize execution time by reducing one level of function call
        if value is False:
            self.calculate3 = self.calculateMSBClassic
        else:
            self.calculate3 = self.calculateLSBClassic

    ## leave methon not overriden -- it will be changed during call to 'setReversed()'
#     ## dataMask: NumberMask
#     ## polyMask: NumberMask
#     def calculate3(self, dataMask, polyMask):
#         if self._reversed == False:
#             return self.calculateMSB(dataMask, polyMask)
#         else:
#             return self.calculateLSBClassic(dataMask, polyMask)

    ## 'poly' without leading '1'
    def calculateMSBClassic(self, dataMask, polyMask):
        register = self.registerInit

        dataNum = dataMask.dataNum
        dataBit = dataMask.masterBit >> 1
        polyMasterBit = polyMask.masterBit

        crcMSB = polyMask.masterBit >> 1
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
    ## 'dataMask' and 'polyMask' have to be reversed -- NumberMask
    def calculateLSBClassic(self, dataMask, polyMask):
#         return self.calculateLSBUsingMSB( dataMask, polyMask )

        register = self.registerInit

        dataNum  = dataMask.dataNum
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

    def calculateLSBUsingMSB(self, dataMask, polyMask):
        revData = dataMask.reversed()
        revPoly = polyMask.reversed()

        oldInit = self.registerInit
        oldXor  = self.xorOut

        self.registerInit = reverse_number( self.registerInit, polyMask.dataSize )
        self.xorOut       = reverse_number( self.xorOut, polyMask.dataSize )

        calc_crc = self.calculateMSBClassic( revData, revPoly )

        self.registerInit = oldInit
        self.xorOut       = oldXor

        return reverse_number( calc_crc, polyMask.dataSize )

    # inputData: List[ (NumberMask, NumberMask) ]
    # return CRCOperator
    def createOperator(self, crcSize, inputData):
        return CRCProcessor.createOperator(self, crcSize, inputData)

    def morphData(self, inputData, crcSize):
        dataList = []
        for data in inputData:
            dataMask = data[0]
            if dataMask.dataSize % 8 != 0:
                print "unable to morph data -- unsupported data size"
                #return CRCProcessor.createOperator(self, crcSize, inputData)
                return []
            crcMask = data[1]
            if crcMask.dataSize != crcSize:
                print "unable to morph data -- unsupported crc:", crcMask.dataSize
                #return CRCProcessor.createOperator(self, crcSize, inputData)
                return []

#             crcMask = data[1]
            bytesList = convert_to_msb_list( dataMask.dataNum, dataMask.dataSize / 8 )
            dataList.append( (bytesList, crcMask.dataNum) )
            #rev_crc = reverse_number( crcMask.dataNum, crcSize )
            #dataList.append( (bytesList, rev_crc) )
        return dataList


## ==========================================================


def create_processor(crcSize):
    if crcSize is None:
        return HwCRC()

    if crcSize == 8:
        try:
            from crc.fasthwcrc import Fast8HwCRC

            return Fast8HwCRC()

    #     except ImportError as ex:
        except ImportError:
            ## disable fastcrc -- there were problem with importing fastcrc
    #         print "unable to import fastcrc:", ex
    #         print "WARNING: fast CRC is disabled!!!"
            return HwCRC()

    elif crcSize == 16:
        try:
            from crc.fasthwcrc import Fast16HwCRC

            return Fast16HwCRC()

    #     except ImportError as ex:
        except ImportError:
            ## disable fastcrc -- there were problem with importing fastcrc
    #         print "unable to import fastcrc:", ex
    #         print "WARNING: fast CRC is disabled!!!"
            return HwCRC()

    return HwCRC()
