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

from crc.numbermask import reverse_number
from crc.crcproc import CRCProcessor, CRCDataOperator
from collections import Counter

from crc.hwcrc import HwCRC

from fastcrc.utils import convert_to_msb_list, convert_to_lsb_list
from fastcrc.binding import Data8Operator, Data16Operator
from fastcrc.binding import hw_crc8_calculate
from fastcrc.binding import hw_crc16_calculate


##====================================================


def morph_data(inputData, crcSize):
    dataList = []
    for data in inputData:
        dataMask = data[0]
        if dataMask.dataSize % 8 != 0:
            print "unable to morph data -- unsupported data size"
            return []
        crcMask = data[1]
        if crcMask.dataSize != crcSize:
            print "unable to morph data -- unsupported crc:", crcMask.dataSize
            return []

#             crcMask = data[1]
        bytesList = convert_to_msb_list( dataMask.dataNum, dataMask.dataSize / 8 )
        dataList.append( (bytesList, crcMask.dataNum) )
        #rev_crc = reverse_number( crcMask.dataNum, crcSize )
        #dataList.append( (bytesList, rev_crc) )
    return dataList


##====================================================


##
## assuming that CRC is 8 bit
class Fast8HwCRC( HwCRC ):

    def __init__(self):
        HwCRC.__init__(self)

    ## override
    def setReversed(self, value = True):
        CRCProcessor.setReversed(self, value)
        ## optimize execution time by reducing one level of function call
        if value is False:
            self.calculate3 = self.calculateMSB
        else:
            self.calculate3 = self.calculateLSB

    def calculateMSB(self, dataMask, polyMask):
#         return self.calculateMSBClassic(dataMask, polyMask)
        if dataMask.dataSize % 8 != 0:
            ## fast crc only supports full bytes
            return self.calculateMSBClassic(dataMask, polyMask)

        bytesList = convert_to_msb_list( dataMask.dataNum, dataMask.dataSize / 8 )
        return hw_crc8_calculate( bytesList, polyMask.dataNum, self.registerInit, self.xorOut )

    def calculateLSB(self, dataMask, polyMask):
#         return self.calculateLSBClassic(dataMask, polyMask)
        if dataMask.dataSize % 8 != 0:
            ## fast crc only supports full bytes
            return self.calculateLSBClassic(dataMask, polyMask)

        bytesList = convert_to_lsb_list( dataMask.dataNum, dataMask.dataSize / 8 )
        poly      = reverse_number( polyMask.dataNum, polyMask.dataSize )

        initReg = reverse_number( self.registerInit, polyMask.dataSize )
        xor_val = reverse_number( self.xorOut, polyMask.dataSize )

        calc_crc = hw_crc8_calculate( bytesList, poly, initReg, xor_val )

        return reverse_number( calc_crc, polyMask.dataSize )

    # inputData: List[ (NumberMask, NumberMask) ]
    # return CRCDataOperator
    def createDataOperator(self, crcSize, inputData):
        dataList = morph_data( inputData, crcSize )
        if dataList:
            return Fast8HwCRCDataOperator( self, dataList )

        if not inputData:
            print "unable to morph to Fast8HwCRCDataOperator -- empty input data"
        else:
            print "unable to morph -- unsupported crc size:", crcSize
        return CRCProcessor.createDataOperator(self, crcSize, inputData)


##
##
##
class Fast8HwCRCDataOperator( CRCDataOperator ):

    def __init__(self, crcProcessor, inputData):
        CRCDataOperator.__init__(self)
        self.processor = crcProcessor               ## CRCProcessor
        self.data = []
        for item in inputData:
            self.data.append( Data8Operator( item[0], item[1] ) )

    def calculate(self, polyMask):
        retList = []
        for data_operator in self.data:
            crc = data_operator.calculate( polyMask.dataNum, self.processor.registerInit, self.processor.xorOut )
            retList.append( crc )
        return retList

    def verify(self, polyMask):
        for data_operator in self.data:
            crc = data_operator.calculate( polyMask.dataNum, self.processor.registerInit, self.processor.xorOut )
            if crc != data_operator.dataCRC:
                return False

        ## all CRC matches
        return True

    ## return CRC if matches any data
    def calculateRange(self, polyMask, intRegStart, intRegEnd, xorStart, xorEnd):
#         print "verify input: 0x%X 0x%X 0x%X 0x%X 0x%X" % ( polyMask.dataNum, intRegStart, intRegEnd, xorStart, xorEnd )

        results = Counter()

        for data_operator in self.data:
            crc_match = data_operator.calculateRange( polyMask.dataNum, intRegStart, intRegEnd, xorStart, xorEnd )
            results.update( crc_match )

        return results

    ## return # List[ (int, int) ] -- initReg and xorVal for found CRCs
    def verifyRange(self, polyMask, intRegStart, intRegEnd, xorStart, xorEnd):
#         print "verify input: 0x%X 0x%X 0x%X 0x%X 0x%X" % ( polyMask.dataNum, intRegStart, intRegEnd, xorStart, xorEnd )

        if not self.data:
            return []

        ## first item -- standard iteration
        data_operator = self.data[0]

        ## no results from previous data item -- standard iteration
        # List[ (int, int) ]
        results = data_operator.calculateRange( polyMask.dataNum, intRegStart, intRegEnd, xorStart, xorEnd )
        if not results:
            ## no common result found -- return
            return []

        ##
        ## iterate over rest elements
        ##
        for data_operator in self.data[1:]:
            dataCRC    = data_operator.dataCRC

            ## results from previous data item -- reuse
            crc_match = []
            for item in results:
                initReg = item[0]
                xorVal  = item[1]
                crc = data_operator.calculate( polyMask.dataNum, initReg, xorVal )
                if crc == dataCRC:
                    crc_match.append( ( initReg, xorVal ) )

            results = crc_match
            if not results:
                ## no common result found -- return
                return []

        return results


## ================================================================


##
## assuming that CRC is 16 bit
class Fast16HwCRC( HwCRC ):

    def __init__(self):
        CRCProcessor.__init__(self)

    ## override
    def setReversed(self, value = True):
        HwCRC.setReversed(self, value)
        ## optimize execution time by reducing one level of function call
        if value is False:
            self.calculate3 = self.calculateMSB
        else:
            self.calculate3 = self.calculateLSB

    def calculateMSB(self, dataMask, polyMask):
#         return self.calculateMSBClassic(dataMask, polyMask)
        if dataMask.dataSize % 8 != 0:
            ## fast crc only supports full bytes
            return self.calculateMSBClassic(dataMask, polyMask)

        bytesList = convert_to_msb_list( dataMask.dataNum, dataMask.dataSize / 8 )
        return hw_crc16_calculate( bytesList, polyMask.dataNum, self.registerInit, self.xorOut )

    def calculateLSB(self, dataMask, polyMask):
#         return self.calculateLSBClassic(dataMask, polyMask)
        if dataMask.dataSize % 8 != 0:
            ## fast crc only supports full bytes
            return self.calculateLSBClassic(dataMask, polyMask)

        bytesList = convert_to_lsb_list( dataMask.dataNum, dataMask.dataSize / 8 )
        poly      = reverse_number( polyMask.dataNum, polyMask.dataSize )

        initReg = reverse_number( self.registerInit, polyMask.dataSize )
        xor_val = reverse_number( self.xorOut, polyMask.dataSize )

        calc_crc = hw_crc16_calculate( bytesList, poly, initReg, xor_val )

        return reverse_number( calc_crc, polyMask.dataSize )

    # inputData: List[ (NumberMask, NumberMask) ]
    # return CRCDataOperator
    def createDataOperator(self, crcSize, inputData):
        dataList = morph_data( inputData, crcSize )
        if dataList:
            return Fast16HwCRCDataOperator( self, dataList )

        if not inputData:
            print "unable to morph to Fast16HwCRCDataOperator -- empty input data"
        else:
            print "unable to morph -- unsupported crc size:", crcSize
        return CRCProcessor.createDataOperator(self, crcSize, inputData)


##
##
##
class Fast16HwCRCDataOperator( CRCDataOperator ):

    def __init__(self, crcProcessor, inputData):
        CRCDataOperator.__init__(self)
        self.processor = crcProcessor               ## CRCProcessor
        self.inputData = inputData
        self.data = []
        for item in inputData:
            data_operator = Data16Operator( item[0], item[1] )
            data_operator.bytesList = item[0]
            self.data.append( data_operator )
#        self.data = inputData                       ## List[ bytes_list ]

    def calculate(self, polyMask):
        retList = []
        for data_operator in self.data:
            crc = data_operator.calculate( polyMask.dataNum, self.processor.registerInit, self.processor.xorOut )
            retList.append( crc )
        return retList

    ## return True if matches for all data
    def verify(self, polyMask):
        for data_operator in self.data:
            dataCRC = data_operator.dataCRC
            crc = data_operator.calculate( polyMask.dataNum, self.processor.registerInit, self.processor.xorOut )
            if crc != dataCRC:
                return False

        ## all CRC matches
        return True

    ## return CRC if matches any data
    def calculateRange(self, polyMask, intRegStart, intRegEnd, xorStart, xorEnd):
#         print "verify input: 0x%X 0x%X 0x%X 0x%X 0x%X" % ( polyMask.dataNum, intRegStart, intRegEnd, xorStart, xorEnd )

        results = Counter()

        for data_operator in self.data:
            crc_match = data_operator.calculateRange( polyMask.dataNum, intRegStart, intRegEnd, xorStart, xorEnd )
            results.update( crc_match )

        return results

    ## return CRC if matches for all data
    def verifyRange(self, polyMask, intRegStart, intRegEnd, xorStart, xorEnd):
#         print "verify input: 0x%X 0x%X 0x%X 0x%X 0x%X" % ( polyMask.dataNum, intRegStart, intRegEnd, xorStart, xorEnd )

        if not self.data:
            return []

        ## first item -- standard iteration
        data_operator = self.data[0]

        ## no results from previous data item -- standard iteration
        # List[ (int, int) ]
        results = data_operator.calculateRange( polyMask.dataNum, intRegStart, intRegEnd, xorStart, xorEnd )
        if not results:
            ## no common result found -- return
            return []

        ##
        ## iterate over rest elements
        ##
        for data_operator in self.data[1:]:
            dataCRC    = data_operator.dataCRC

            ## results from previous data item -- reuse
            crc_match = []
            for item in results:
                initReg = item[0]
                xorVal  = item[1]
                crc = data_operator.calculate( polyMask.dataNum, initReg, xorVal )
                if crc == dataCRC:
                    crc_match.append( ( initReg, xorVal ) )

            results = crc_match
            if not results:
                ## no common result found -- return
                return []

        return results
