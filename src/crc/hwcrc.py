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

from crc.crcproc import CRCProc, CRCOperator

from crc.flush import flush_string

from fastcrc.ctypes.fastcrc8 import hw_crc8_calculate, hw_crc8_calculate_range
from fastcrc.ctypes.fastcrc16 import hw_crc16_calculate, hw_crc16_calculate_range
from fastcrc.ctypes.utils import convert_to_msb_list, convert_to_lsb_list
from crc.numbermask import reverse_number


USE_FAST_CRC = True
# USE_FAST_CRC = False


if USE_FAST_CRC is False:
    print "WARNING: fast CRC is disabled!!!"


##
##
class HwCRC( CRCProc ):

    def __init__(self):
        CRCProc.__init__(self)
        
    ## override
    def setReversed(self, value = True):
        CRCProc.setReversed(self, value)
        ## optimize execution time by reducing one level of function call
        if value is False:
            if USE_FAST_CRC:
                self.calculate3 = self.calculateMSB
            else:
                self.calculate3 = self.calculateMSBClassic
        else:
            if USE_FAST_CRC:
                self.calculate3 = self.calculateLSB
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

    def calculateMSB(self, dataMask, polyMask):
#         return self.calculateMSBClassic(dataMask, polyMask)
        if dataMask.dataSize % 8 != 0:
            ## fast crc only supports full bytes
            return self.calculateMSBClassic(dataMask, polyMask)
        
        if polyMask.dataSize == 8:
            bytesList = convert_to_msb_list( dataMask.dataNum, dataMask.dataSize / 8 )
            return hw_crc8_calculate( bytesList, polyMask.dataNum, self.registerInit, self.xorOut )
        
        if polyMask.dataSize == 16:
            bytesList = convert_to_msb_list( dataMask.dataNum, dataMask.dataSize / 8 )
            return hw_crc16_calculate( bytesList, polyMask.dataNum, self.registerInit, self.xorOut )
        
        ## fast crc only supports CRC8
        return self.calculateMSBClassic(dataMask, polyMask)

    def calculateLSB(self, dataMask, polyMask):
#         return self.calculateLSBClassic(dataMask, polyMask)
        if dataMask.dataSize % 8 != 0:
            ## fast crc only supports full bytes
            return self.calculateLSBClassic(dataMask, polyMask)
        
        if polyMask.dataSize == 8:
            bytesList = convert_to_lsb_list( dataMask.dataNum, dataMask.dataSize / 8 )
            poly      = reverse_number( polyMask.dataNum, polyMask.dataSize )
            
            initReg = reverse_number( self.registerInit, polyMask.dataSize )
            xor_val = reverse_number( self.xorOut, polyMask.dataSize )

            calc_crc = hw_crc8_calculate( bytesList, poly, initReg, xor_val )
            
            return reverse_number( calc_crc, polyMask.dataSize )
        
        if polyMask.dataSize == 16:
            bytesList = convert_to_lsb_list( dataMask.dataNum, dataMask.dataSize / 8 )
            poly      = reverse_number( polyMask.dataNum, polyMask.dataSize )
            
            initReg = reverse_number( self.registerInit, polyMask.dataSize )
            xor_val = reverse_number( self.xorOut, polyMask.dataSize )

            calc_crc = hw_crc16_calculate( bytesList, poly, initReg, xor_val )
            
            return reverse_number( calc_crc, polyMask.dataSize )
        
        ## fast crc only supports CRC8
        return self.calculateLSBClassic(dataMask, polyMask)

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
    
    ## inputData: List[ (NumberMask, NumberMask) ]
    def createOperator(self, crcSize, inputData):
        if USE_FAST_CRC is False:
            print "fast CRC disabled"
            return CRCProc.createOperator(self, crcSize, inputData)
            
        if crcSize == 8:
            dataList = self.morphData( inputData, crcSize )
            if dataList:
                print "creating Forward8FastHwOperator"
                return Forward8FastHwOperator( self, dataList )
        if crcSize == 16:
            dataList = self.morphData( inputData, crcSize )
            if dataList:
                print "creating Forward16FastHwOperator"
                return Forward16FastHwOperator( self, dataList )
                
        print "unable to morph -- unsupported crc size: ", crcSize
        return CRCProc.createOperator(self, crcSize, inputData)


    def morphData(self, inputData, crcSize):
        dataList = []
        for data in inputData:
            dataMask = data[0]
            if dataMask.dataSize % 8 != 0:
                print "unable to morph data -- unsupported data size"
                #return CRCProc.createOperator(self, crcSize, inputData)
                return []
            crcMask = data[1]
            if crcMask.dataSize != crcSize:
                print "unable to morph data -- unsupported crc"
                #return CRCProc.createOperator(self, crcSize, inputData)
                return []
            
#             crcMask = data[1]
            bytesList = convert_to_msb_list( dataMask.dataNum, dataMask.dataSize / 8 )
            dataList.append( (bytesList, crcMask.dataNum) )
            #rev_crc = reverse_number( crcMask.dataNum, crcSize )
            #dataList.append( (bytesList, rev_crc) )
        return dataList


##
##
##
class Forward8FastHwOperator( CRCOperator ):
    
    def __init__(self, crcProcessor, inputData):
        CRCOperator.__init__(self)
        self.processor = crcProcessor
        self.data = inputData                   ## List[ bytes_list ]

    def calculate(self, polyMask):
        retList = []
        for item in self.data:
            bytes_list = item[0]
            crc = hw_crc8_calculate( bytes_list, polyMask.dataNum, self.processor.registerInit, self.processor.xorOut )
            retList.append( crc )
        return retList
    
    def verify(self, polyMask):
        for item in self.data:
            bytes_list = item[0]
            dataCRC    = item[1]
            crc = hw_crc8_calculate( bytes_list, polyMask.dataNum, self.processor.registerInit, self.processor.xorOut )
            if dataCRC != crc:
                return False
            
        ## all CRC matches
        return True
    
    def verifyRange(self, polyMask, intRegStart, intRegEnd, xorStart, xorStop):
#         print "verify input:", intRegStart, intRegEnd, xorStart, xorStop

        found_data = set()
        for item in self.data:
            bytes_list = item[0]
            dataCRC    = item[1]
            crc_match = hw_crc8_calculate_range( bytes_list, dataCRC, polyMask.dataNum, intRegStart, intRegEnd, xorStart, xorStop )
            if not crc_match:
                ## no result found -- return
                return False
            
            if not found_data:
                ## empty set 
                found_data.update( crc_match )
                continue
            
            common = found_data.intersection( crc_match )
            if not common:
                ## no common results -- return
                return False
            found_data = common
            
        for item in found_data:
            initReg = item[0]
            xorVal  = item[1]
            flush_string( "Found CRC - poly: 0x{:X} initVal: 0x{:X} xorVal: 0x{:X}\n".format( polyMask.dataNum, initReg, xorVal ) )

        if not found_data:
            return False
        return True


##
##
##
class Forward16FastHwOperator( CRCOperator ):
    
    def __init__(self, crcProcessor, inputData):
        CRCOperator.__init__(self)
        self.processor = crcProcessor
        self.data = inputData                   ## List[ bytes_list ]

    def calculate(self, polyMask):
        retList = []
        for item in self.data:
            bytes_list = item[0]
            crc = hw_crc16_calculate( bytes_list, polyMask.dataNum, self.processor.registerInit, self.processor.xorOut )
            retList.append( crc )
        return retList
    
    def verify(self, polyMask):
        for item in self.data:
            bytes_list = item[0]
            dataCRC    = item[1]
            crc = hw_crc16_calculate( bytes_list, polyMask.dataNum, self.processor.registerInit, self.processor.xorOut )
            if dataCRC != crc:
                return False
            
        ## all CRC matches
        return True
    
    def verifyRange(self, polyMask, intRegStart, intRegEnd, xorStart, xorStop):
        found_data = set()
        for item in self.data:
            bytes_list = item[0]
            dataCRC    = item[1]
            crc_match = hw_crc16_calculate_range( bytes_list, dataCRC, polyMask.dataNum, intRegStart, intRegEnd, xorStart, xorStop )
            if not crc_match:
                ## no result found -- return
                return False
            
            if not found_data:
                ## empty set 
                found_data.update( crc_match )
                continue
            
            common = found_data.intersection( crc_match )
            if not common:
                ## no common results -- return
                return False
            found_data = common
            
        for item in found_data:
            initReg = item[0]
            xorVal  = item[1]
            flush_string( "Found CRC - poly: 0x{:X} initVal: 0x{:X} xorVal: 0x{:X}\n".format( polyMask.dataNum, initReg, xorVal ) )

        if not found_data:
            return False
        return True
