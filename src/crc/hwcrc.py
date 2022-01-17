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

from fastcrc.ctypes.fastcrc import hw_crc8_calculate, convert_to_msb_list,\
    hw_crc8_calculate_range

from crc.flush import flush_string


USE_FAST_CRC = True
# USE_FAST_CRC = False


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
        if polyMask.dataSize != 8:
            ## fast crc only supports CRC8
            return self.calculateMSBClassic(dataMask, polyMask)
        if dataMask.dataSize % 8 != 0:
            ## fast crc only supports full bytes
            return self.calculateMSBClassic(dataMask, polyMask)
        bytesList = convert_to_msb_list( dataMask.dataNum, dataMask.dataSize / 8 )
        return hw_crc8_calculate( bytesList, polyMask.dataNum, self.registerInit, self.xorOut )

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

    def calculateLSB(self, dataMask, polyMask):
        return self.calculateLSBClassic( dataMask, polyMask )

    ## 'poly' without leading '1'
    ## 'dataMask' and 'polyMask' have to be reversed
    def calculateLSBClassic(self, dataMask, polyMask):
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
    
    ## inputData: List[ (NumberMask, NumberMask) ]
    def createOperator(self, crcSize, inputData):
        if USE_FAST_CRC is False:
            print( "fast CRC disabled" )
            return CRCProc.createOperator(self, crcSize, inputData)
            
        if crcSize != 8:
            print( "unable to morph -- unsupported crc size: ", crcSize )
            return CRCProc.createOperator(self, crcSize, inputData)
#         return CRCProc.createOperator(self, crcSize, inputData)

        dataList = []
        for data in inputData:
            dataMask = data[0]
            if dataMask.dataSize % 8 != 0:
                print( "unable to morph -- unsupported data size" )
                return CRCProc.createOperator(self, crcSize, inputData)
            crcMask = data[1]
            if crcMask.dataSize != crcSize:
                print( "unable to morph -- unsupported crc" )
                return CRCProc.createOperator(self, crcSize, inputData)
            
#             crcMask = data[1]
            bytesList = convert_to_msb_list( dataMask.dataNum, dataMask.dataSize / 8 )
            dataList.append( (bytesList, crcMask.dataNum) )
        
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
            
            def verifyRange(self, polyMask, xorStart, xorStop):
                xorSet = set()
                for item in self.data:
                    bytes_list = item[0]
                    dataCRC    = item[1]
                    crc_match = hw_crc8_calculate_range( bytes_list, dataCRC, polyMask.dataNum, self.processor.registerInit, xorStart, xorStop )
                    if not crc_match:
                        ## no result found -- return
                        return False
                    
                    if not xorSet:
                        ## empty set 
                        xorSet.update( crc_match )
                        continue
                    
                    common = xorSet.intersection( crc_match )
                    if not common:
                        ## no common results -- return
                        return False
                    xorSet = common
                    
                for item in xorSet:
#                             initReg = item[0]
                    flush_string( "Found CRC - poly: 0x{:X} initVal: 0x{:X} xorVal: 0x{:X}\n".format( polyMask.dataNum, self.processor.registerInit, item ) )
                if not xorSet:
                    return False
                return True
            
        print( "creating Forward8FastHwOperator" )
        return Forward8FastHwOperator( self, dataList )
