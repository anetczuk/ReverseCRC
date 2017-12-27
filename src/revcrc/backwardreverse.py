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


# import logging
import time

from crc.hwcrc import HwCRC
from crc.divisioncrc import DivisionCRC
from crc.modcrc import ModCRC
from revcrc.hwcrcbackward import HwCRCBackward
from revcrc.divisioncrcbackward import DivisionCRCBackward
from revcrc.reverse import Reverse, MessageCRC, CRCKey
from crc.numbermask import NumberMask
import itertools


    

##
##
class BackwardReverse(Reverse):
    
    ## crcSize  -- size of crc in bits
#     def __init__(self, crcSize, printProgress = None):
    def __init__(self, printProgress = None):
        Reverse.__init__(self, printProgress)
      
    def findSolutionList(self, dataList):

        if len(dataList) < 1:
            return

        numbersList = []
        dataSize = 0
        crcSize = 0
        for i in range(0, len(dataList)):
            dataPair = dataList[i]
            dataString = dataPair[0]
            crcString = dataPair[1]
            dataSize = max( dataSize, len(dataString)*8 )
            crcSize = max( crcSize, len(crcString)*8 )
            data = int(dataString, 16)
            crc = int(crcString, 16)
            numbersList.append((data, crc))
            
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(numbersList), dataSize, crcSize)
        self.findSolution(numbersList, dataSize, crcSize)
        
    def findSolution(self, dataList, dataSize, crcSize, searchRange = 0):
        if len(dataList) < 2:
            return []
        
        retList = []
        comb = list( itertools.combinations( dataList, 2 ) )
        
        cLen = len(comb)
        for i in range(0, cLen):
            combPair = comb[i]
            dataPair1 = combPair[0]
            dataPair2 = combPair[1]
            
            data1 = dataPair1[0]
            crc1 = dataPair1[1]
            data2 = dataPair2[0]
            crc2 = dataPair2[1]
            keys = self.findCRCKey(data1, crc1, data2, crc2, dataSize, crcSize, searchRange)
            
            retList += keys
            
        return retList
      
    def findCRCKey(self, data1, crc1, data2, crc2, dataSize=-1, crcSize=-1, searchRange=0):
        if dataSize < 0:
            dataSize = max( data1.bit_length(), data2.bit_length() )
        if crcSize < 0:
            crcSize = max( crc1.bit_length(), crc2.bit_length() )
        polyList = self.findXOR(data1, crc1, data2, crc2, dataSize, crcSize)
        
        searchStart = dataSize-searchRange
        
        retList = []
        for polyPair in polyList:
            poly = polyPair[0]
            polyMask = NumberMask(poly, crcSize)
            reversedMode = polyPair[1]
            polyAdded = False
            for ds in range(searchStart, dataSize+1):
                d1 = NumberMask(data1, ds)
                cb1 = self.createBackwardCRCProcessor(d1, crc1, polyMask)
                cb1.setReversed(reversedMode)
                backList = cb1.calculate()
                if len(backList) < 1:
                    continue
                
                for back in backList:
                    initVal = back.register
                    crcProc = self.createCRCProcessor()
                    crcProc.setReversed(reversedMode)
                    crcProc.setRegisterInitValue(initVal)
                    verifyCrc = crcProc.calculate3(d1, polyMask)
                    if (verifyCrc != crc1):
                        continue
    #                 if self.progress:
    #                     sys.stdout.write("\r")
    #                     print "Found init: 0b{0:b} 0x{0:X}".format(initVal)
                    retList.append( CRCKey(poly, reversedMode, initVal, -1, -1, ds) )
                    polyAdded = True
            if polyAdded == False:
                ret = CRCKey()
                ret.poly = poly
                retList.append(ret)
                
        return retList
    
    def findXOR(self, data1, crc1, data2, crc2, dataSize = -1, crcSize = -1):
        inputData = data1 ^ data2
        inputCRC = crc1 ^ crc2

        if crcSize < 0:
            crcSize = max(crc1.bit_length(), crc2.bit_length())
        
        if self.progress:
            messageFormat = "xor-ed input: {:b} {:0" + str(crcSize) + "b}"
            print messageFormat.format(inputData, inputCRC)

#         messageFormat = "xor-ed input: {:X} {:0" + str(self.crcSize) + "b}"
#         print messageFormat.format(inputData, inputCRC)
        
        if dataSize < 0:
            dataSize = max(data1.bit_length(), data2.bit_length())
        
        dataCrc = MessageCRC(inputData, dataSize, inputCRC, crcSize)
        return self.bruteForceData(dataCrc)
      
    def calculateNumberCRC(self, polyMask, reverse, initReg, xorOut, dataMask):
        crcProc = self.createCRCProcessor()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue(xorOut)
        crcProc.setRegisterInitValue(initReg)
        return crcProc.calculate3(dataMask, polyMask)
        
    def createCRCProcessor(self):
        raise NotImplementedError
    
    def createBackwardCRCProcessor(self, dataMask, crc, polyMask):
        raise NotImplementedError
    
        
class RevHwCRC(BackwardReverse):
    def __init__(self, printProgress = None):
        BackwardReverse.__init__(self, printProgress)

    def createCRCProcessor(self):
        return HwCRC()
        
    def createBackwardCRCProcessor(self, dataMask, crc, polyMask):        
        return HwCRCBackward( dataMask, crc, polyMask )
    
    
class RevDivisionCRC(BackwardReverse):
    def __init__(self, printProgress = None):
        BackwardReverse.__init__(self, printProgress)

    def createCRCProcessor(self):
        return DivisionCRC()
        
    def createBackwardCRCProcessor(self, dataMask, crc, polyMask):     
        return DivisionCRCBackward( dataMask, crc, polyMask )
    
    
class RevModCRC(BackwardReverse):
    def __init__(self, printProgress = None):
        BackwardReverse.__init__(self, printProgress)

    def createCRCProcessor(self):
        return ModCRC()        
        
    def createBackwardCRCProcessor(self, dataMask, crc, polyMask):        
        return DivisionCRCBackward( dataMask, crc, polyMask )
        
### ================================================================
        
        
class RightSubstringChain:
    def __init__(self, processor, startSize = 1):
        self.processor = processor
        self.startSize = startSize-1
    
    def calculate(self, dataCrc):
#         print "R Input:", dataCrc
        testMessage = 0
        bitMask = 1
        for i in range(0, dataCrc.dataSize):
            testMessage |= (bitMask & dataCrc.dataNum)
            bitMask <<= 1
            if i < self.startSize:
                continue
            tmpData = MessageCRC(testMessage, i+1, dataCrc.crcNum, dataCrc.crcSize)
#             print "R Item:", tmpData
            self.processor.calculate(tmpData)
    
    
class LeftSubstringChain:
    def __init__(self, processor):
        self.processor = processor
    
    def calculate(self, dataCrc):
#         print "L Input:", dataCrc
        testMessage = 0
        bitMask = 1 << (dataCrc.dataSize-1)
        for i in range(0, dataCrc.dataSize):
            testMessage = testMessage << 1
            if bitMask & dataCrc.dataNum:
                testMessage = testMessage | 0b1
            tmpData = MessageCRC(testMessage, i+1, dataCrc.crcNum, dataCrc.crcSize)
#             print "L Item:", tmpData
            self.processor.calculate(tmpData)
            bitMask = bitMask >> 1


class SideSubstringChain:
    def __init__(self, processor):
        self.processor = RightSubstringChain( LeftSubstringChain(processor) )
        #self.processor = RightSubstringChain( processor )
    
    def calculate(self, dataCrc):
        self.processor.calculate(dataCrc)


class RevBFReceiver:
    def __init__(self):
        pass
    
    def calculate(self, dataCrc):
        ##self.processor.calculate(dataCrc)
        print "Finding poly for data: {}".format(dataCrc)
        tstamp = time.time()
        calc = RevHwCRC(True)
        calc.bruteForceData(dataCrc)
        timeDiff = (time.time()-tstamp)*1000.0
        print "Time: {:13.8f}ms".format(timeDiff)


class BruteForceChain:
    def __init__(self):
        self.processor = RightSubstringChain( RevBFReceiver(), 30*4 )
    
    def calculate(self, dataCrc):
        self.processor.calculate(dataCrc)
    
    