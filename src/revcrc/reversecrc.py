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
import sys
import time

import itertools

from crc.hwcrc import HwCRC
from crc.divisioncrc import DivisionCRC
from crc.modcrc import ModCRC
from revcrc.hwcrcbackward import HwCRCBackward
from revcrc.divisioncrcbackward import DivisionCRCBackward
from crc.numbermask import NumberMask



class MessageCRC:
    def __init__(self, data, dataSize, crc, crcSize):
        self.dataNum = data
        self.dataSize = dataSize
        self.crcNum = crc
        self.crcSize = crcSize
        
    def __repr__(self):
        return "<MessageCRC {:X} {} {:X} {}>".format(self.dataNum, self.dataSize, self.crcNum, self.crcSize)


class CRCKey:
    def __init__(self, poly=-1, rev=False, init=-1, xor=-1, dataPos=-1, dataLen=-1):
        self.poly = poly
        self.rev = rev
        self.init = init
        self.xor = xor
        self.dataPos = dataPos
        self.dataLen = dataLen

    def __repr__(self):
        return "<CRCKey p:0x{:X} dP:{:} dL:{:} r:{:} i:0x{:X} x:0x{:X}>".format(self.poly, self.dataPos, self.dataLen, self.rev, self.init, self.xor)
    
    def __eq__(self, other):
        if self.poly != other.poly:
            return False
        if self.rev != other.rev:
            return False
        if self.init != other.init:
            return False
        if self.xor != other.xor:
            return False
        if self.dataPos != other.dataPos:
            return False
        if self.dataLen != other.dataLen:
            return False
        return True
    
    def __ne__(self, other):
        return ((self == other) == False)
    
    def __hash__(self):
        return hash(str(self.poly) + str(self.init) + str(self.xor))
    

##
##
class RevCRCBase:
    
    ## crcSize  -- size of crc in bits
    def __init__(self, crcSize, printProgress = None):
        self.crcSize = crcSize
        self.polyBase = 0b1 << crcSize
        self.polyMax = self.polyBase << 1
        if printProgress == None:
            self.progress = False
        else:
            self.progress = printProgress
    
    def bruteForce(self, data, crc, dataSize = -1):
        if dataSize < 0:
            dataSize = data.bit_length()
        dataCrc = MessageCRC(data, dataSize, crc, self.crcSize)
        return self.bruteForceData(dataCrc)
    
    def bruteForceData(self, dataCrc):
        retList = []
        retList += self.bruteForceMode(dataCrc, False)
        retList += self.bruteForceMode(dataCrc, True)
        return retList
    
    def bruteForceMode(self, dataCrc, reverseMode=False):
        crcProc = self.createCRCProcessor()
        crcProc.setReversed(reverseMode)
        crc = dataCrc.crcNum
        dataMask = NumberMask(dataCrc.dataNum, dataCrc.dataSize)
#         if reverseMode:
#             dataMask.reverseBytes()
        poly = self.polyBase + 1
        retList = []
        while poly < self.polyMax:
            if self.progress and (poly % 16384) == 16383:
                sys.stdout.write("\r{:b}".format(poly))
                sys.stdout.flush()

            polyCRC = crcProc.calculate3(dataMask, poly)
            if polyCRC == crc:
                ##print "Detected poly: {:b}".format(retPoly)
#                 if self.progress:
#                     sys.stdout.write("\r")
#                     print "Found poly: 0b{0:b} 0x{0:X}".format(retPoly)
#                 if reverseMode:
#                     revPoly = reverseBits(poly, self.crcSize)
#                     retList.append( (revPoly, reverseMode))
#                 else:
#                     retList.append( (poly, reverseMode))
                retList.append( (poly, reverseMode))
            poly += 1
        
        if self.progress:
            sys.stdout.write("\r")
            sys.stdout.flush()
        return retList
    
    @staticmethod
    def bruteForcePair(inputPair, printInfo = None):
        dataString = inputPair[0]
        crcString = inputPair[1]

        data = int(dataString, 16)
        crc = int(crcString, 16)
        crcSize = len(crcString) * 4
        
        reverse = RevHwCRC(crcSize, printProgress = printInfo)
        return reverse.bruteForce(data, crc)
    
    def findXOR(self, data1, crc1, data2, crc2, dataSize = -1):
        inputData = data1 ^ data2
        inputCRC = crc1 ^ crc2
        
        if self.progress:
            messageFormat = "xor-ed input: {:b} {:0" + str(self.crcSize) + "b}"
            print messageFormat.format(inputData, inputCRC)

#         messageFormat = "xor-ed input: {:X} {:0" + str(self.crcSize) + "b}"
#         print messageFormat.format(inputData, inputCRC)
        
        if dataSize < 0:
            dataSize = max(data1.bit_length(), data2.bit_length())
        
        dataCrc = MessageCRC(inputData, dataSize, inputCRC, self.crcSize)
        return self.bruteForceData(dataCrc)
    
    def findSolution(self, dataList, dataSize, searchRange):
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
            keys = self.findCRCKey(data1, crc1, data2, crc2, dataSize, searchRange)
            
            retList += keys
            
        return retList
    
    def findCRCKey(self, data1, crc1, data2, crc2, dataSize=-1, searchRange=0):
        if dataSize < 0:
            dataSize = max( data1.bit_length(), data2.bit_length() )
        polyList = self.findXOR(data1, crc1, data2, crc2, dataSize)
        
        searchStart = dataSize-searchRange
        
        retList = []
        for polyPair in polyList:
            poly = polyPair[0]
            reversedMode = polyPair[1]
            polyAdded = False
            for ds in range(searchStart, dataSize+1):
                d1 = NumberMask(data1, ds)
                cb1 = self.createBackwardCRCProcessor(d1, crc1, poly)
                cb1.setReversed(reversedMode)
                backList = cb1.calculate()
                if len(backList) < 1:
                    continue
                
                for back in backList:
                    initVal = back.register
                    crcProc = self.createCRCProcessor()
                    crcProc.setReversed(reversedMode)
                    crcProc.setRegisterInitValue(initVal)
                    verifyCrc = crcProc.calculate3(d1, poly)
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
                
    @staticmethod
    def findSubstring(dataNum, crcNum, polyUnderTest, polySize):
        dataSize = dataNum.bit_length()
         
        testMessage = 0
        bitMask = 1
        for _ in range(0, dataSize):
            testMessage = testMessage | (bitMask & dataNum)
            bitMask = bitMask << 1
             
            ## print "Testing: 0x{:X}".format(testMessage)
             
            crcProc = HwCRC( polySize )
            crc = crcProc.calculate(testMessage, polyUnderTest)
            ##print "Found: {} {}".format(crc, crcNum)
            if crc == crcNum:
                return testMessage
        return -1
        
    def createCRCProcessor(self):
        return None
    
    def createBackwardCRCProcessor(self):
        return None
    
        
class RevHwCRC(RevCRCBase):
    def __init__(self, crcSize, printProgress = None):
        RevCRCBase.__init__(self, crcSize, printProgress)

    def createCRCProcessor(self):
        return HwCRC(self.crcSize)        
        
    def createBackwardCRCProcessor(self, data, crc, poly):        
        return HwCRCBackward( data, crc, self.crcSize, poly )
    
    
class RevDivisionCRC(RevCRCBase):
    def __init__(self, crcSize, printProgress = None):
        RevCRCBase.__init__(self, crcSize, printProgress)

    def createCRCProcessor(self):
        return DivisionCRC(self.crcSize)        
        
    def createBackwardCRCProcessor(self, data, crc, poly):        
        return DivisionCRCBackward( data, crc, self.crcSize, poly )
    
    
class RevModCRC(RevCRCBase):
    def __init__(self, crcSize, printProgress = None):
        RevCRCBase.__init__(self, crcSize, printProgress)

    def createCRCProcessor(self):
        return ModCRC(self.crcSize)        
        
    def createBackwardCRCProcessor(self, data, crc, poly):        
        return DivisionCRCBackward( data, crc, self.crcSize, poly )
        
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
        calc = RevHwCRC(dataCrc.crcSize, True)
        calc.bruteForceData(dataCrc)
        timeDiff = (time.time()-tstamp)*1000.0
        print "Time: {:13.8f}ms".format(timeDiff)


class BruteForceChain:
    def __init__(self):
        self.processor = RightSubstringChain( RevBFReceiver(), 30*4 )
    
    def calculate(self, dataCrc):
        self.processor.calculate(dataCrc)
    
    