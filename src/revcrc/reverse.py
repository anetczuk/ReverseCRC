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
from crc.numbermask import NumberMask
import sys
import itertools
from crc.crcproc import CRCKey, PolyKey
from crc.hwcrc import HwCRC
from crc.divisioncrc import DivisionCRC
from crc.modcrc import ModCRC



class MessageCRC:
    def __init__(self, data, dataSize, crc, crcSize):
        self.dataNum = data
        self.dataSize = dataSize
        self.crcNum = crc
        self.crcSize = crcSize
      
    def dataMask(self):
        return NumberMask(self.dataNum, self.dataSize)
    
    def crcMask(self):
        return NumberMask(self.crcNum, self.crcSize)
        
    def __repr__(self):
        return "<MessageCRC {:X} {} {:X} {}>".format(self.dataNum, self.dataSize, self.crcNum, self.crcSize)



class Reverse(object):
    '''
    Base class for reverse algorithms
    '''
    
    def __init__(self, printProgress = None):
        self.returnFirst = False
        if printProgress == None:
            self.progress = False
        else:
            self.progress = printProgress
    
    def setReturnOnFirst(self):
        self.returnFirst = True
        
        
    ## ==========================================================
        
    
    def bruteForceInput(self, inputData, searchRange = 0):
        if inputData.empty():
            return
        if inputData.ready() == False:
            return
        
        numbersList = inputData.numbersList
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(numbersList), inputData.dataSize, inputData.crcSize)
        
        retList = []
        comb = list( itertools.combinations( numbersList, 2 ) )
        cLen = len(comb)
        
        if (self.progress):
            print "Combinations number:", cLen
        
        for i in range(0, cLen):
            combPair = comb[i]
            numberPair1 = combPair[0]
            numberPair2 = combPair[1]
            
            keys = self.findBruteForce(numberPair1, numberPair2, inputData.dataSize, inputData.crcSize, searchRange)

            if (self.progress):
                print "Found keys:", keys

            retList += keys
            
        return retList

    def findPolysInput(self, inputData, searchRange = 0):
        if inputData.empty():
            return
        if inputData.ready() == False:
            return
        
        numbersList = inputData.numbersList
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(numbersList), inputData.dataSize, inputData.crcSize)
        
        retList = set()
        comb = list( itertools.combinations( numbersList, 2 ) )
        cLen = len(comb)
        
        if (self.progress):
            print "Combinations number:", cLen
        
        for i in range(0, cLen):
            combPair = comb[i]
            numberPair1 = combPair[0]
            numberPair2 = combPair[1]
            
            data1 = numberPair1[0]
            crc1 = numberPair1[1]
            data2 = numberPair2[0]
            crc2 = numberPair2[1]
            
            keys = self.findPolysXOR(data1, crc1, data2, crc2, inputData.dataSize, inputData.crcSize, searchRange)

            if (self.progress):
                keysSet = set(keys)
                print "Found polys:", keysSet

            retList.update( keys )
            
        return retList

    def findCommonInput(self, inputData, searchRange = 0):
        if inputData.empty():
            return
        if inputData.ready() == False:
            return
            
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(inputData.numbersList), inputData.dataSize, inputData.crcSize)
            
        return self.findCommon(inputData.numbersList, inputData.dataSize, inputData.crcSize, searchRange)
    
    ## searchRange=0 means exact length (no subvalues)
    def findCommon(self, dataList, dataSize, crcSize, searchRange = 0):
        if len(dataList) < 1: 
            return set()
        
        dataPair = dataList[0]
        dataMask = NumberMask(dataPair[0], dataSize)
        retList = self.findCRCKeyBits( dataMask, dataPair[1], crcSize, searchRange)
        
        for i in xrange(1, len(dataList)):
            dataPair = dataList[i]
            dataMask = NumberMask(dataPair[0], dataSize)
            keys = self.findCRCKeyBits( dataMask, dataPair[1], crcSize, searchRange)
            retList.intersection( keys )
            
        return retList
        
    def findCRCKeyBits(self, dataMask, crcNum, crcSize, searchRange):
        if self.progress:
            print "Checking {:X} {:X}".format(dataMask.dataNum, crcNum)
            
        retList = set()
                
        subList = dataMask.generateSubnumbers(0, dataMask.dataSize - searchRange)
        for sub in subList:
#             if self.progress:
#                 subnum = asciiToInt(substr)
#                 print "Checking substring {:X}".format(subnum)
            crcMask = NumberMask(crcNum, crcSize)
            subRet = self.findCRC(sub, crcMask)
            for key in subRet:
                key.dataPos = sub.pos
                key.dataLen = sub.size
            retList |= subRet
            
        if self.progress and len(retList)>0:
            print "Found keys:", retList
            
        return retList
        
    def findCRC(self, subNum, crcMask):
        retList = set()
        if crcMask.dataSize == 8:
            self.checkCRC(subNum, crcMask, CRCKey(0x107, False, 0x0, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x139, True, 0x0, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x11D, False, 0xFD, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x107, False, 0x55, 0x55), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x131, True, 0x0, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x107, True, 0xFF, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x19B, True, 0x0, 0x0), retList)
        elif crcMask.dataSize == 16:
            self.checkCRC(subNum, crcMask, CRCKey(0x18005, True, 0x0, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x18005, False, 0x0, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x18005, False, 0x800D, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x10589, False, 0x0001, 0x0001), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x13D65, True, 0xFFFF, 0xFFFF), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x13D65, False, 0xFFFF, 0xFFFF), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x11021, False, 0x0, 0xFFFF), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x18005, True, 0xFFFF, 0xFFFF), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x11021, True, 0xFFFF, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x11021, True, 0x554D, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x18BB7, False, 0x0, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x1A097, False, 0x0, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x18005, True, 0x0, 0xFFFF), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x11021, True, 0x0, 0xFFFF), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x11021, False, 0x0, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x18005, True, 0xFFFF, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x11021, True, 0x0, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x11021, False, 0xFFFF, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x11021, False, 0x1D0F, 0x0), retList)
        elif crcMask.dataSize == 24:
            self.checkCRC(subNum, crcMask, CRCKey(0x1864CFB, False, 0xB704CE, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x15D6DCB, False, 0xFEDCBA, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x15D6DCB, False, 0xABCDEF, 0x0), retList)
        elif crcMask.dataSize == 32:
            self.checkCRC(subNum, crcMask, CRCKey(0x104C11DB7, True, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x104C11DB7, False, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x11EDC6F41, True, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x1A833982B, True, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x104C11DB7, False, 0xFFFFFFFF, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x104C11DB7, False, 0xFFFFFFFF, 0xFFFFFFFF), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x1814141AB, False, 0x0, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x104C11DB7, True, 0xFFFFFFFF, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x1000000AF, False, 0x0, 0x0), retList)
        elif crcMask.dataSize == 64:
            self.checkCRC(subNum, crcMask, CRCKey(0x1000000000000001B, True, 0x0, 0x0), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x142F0E1EBA9EA3693, False, 0x0, 0xFFFFFFFFFFFFFFFF), retList)
            self.checkCRC(subNum, crcMask, CRCKey(0x1AD93D23594C935A9, True, 0xFFFFFFFFFFFFFFFF, 0x0), retList)
        return retList
 
    def checkCRC(self, subNum, crcMask, crcKey, retList):
        ## subNum: SubNumber
        ## crcMask: NumberMask
        ## crcKey: CRCKey
        
        ##print "Checking data:", subNum, crc, crcMaskKey
    
        crcProc = self.createCRCProcessor()
        crcProc.setValues(crcKey)
        
        polyCRC = crcProc.calculate2(subNum.data, subNum.size, crcKey.poly, crcMask.dataSize)
        if polyCRC == crcMask.dataNum:
            retList.add( crcKey )


    ## ==========================================================


    def findBruteForce(self, dataCrcPair1, dataCrcPair2, dataSize, crcSize, searchRange = 0):
        data1 = dataCrcPair1[0]
        crc1 = dataCrcPair1[1]
        data2 = dataCrcPair2[0]
        crc2 = dataCrcPair2[1]
        
        keyList = self.findPolysXOR(data1, crc1, data2, crc2, dataSize, crcSize, searchRange)
        
#         print "keys:", keyList
        
        ## finding xor value

        dataCrc1 = MessageCRC(data1, dataSize, crc1, crcSize)
        dataCrc2 = MessageCRC(data2, dataSize, crc2, crcSize)

        retList = []
        for key in keyList:
            paramsList = self.findBruteForceParams(dataCrc1, dataCrc2, key)
            if len(paramsList) < 1:
                continue
            if self.progress:
                sys.stdout.write("\r")
                print "Found keys: {}".format( paramsList )
            retList += paramsList
        return retList

    def findBruteForceParams(self, dataCrc1, dataCrc2, polyKey):
        crcProc = self.createCRCProcessor()
        crcProc.setReversed( polyKey.rev )
         
        crcSize = dataCrc1.crcSize
        dataMask1 = dataCrc1.dataMask()
        dataMask2 = dataCrc2.dataMask()
        polyMask = NumberMask(polyKey.poly, crcSize)
        crc1 = dataCrc1.crcNum
        crc2 = dataCrc2.crcNum
        
        initVal = -1
        paramMax = (0x1 << crcSize)
                  
        retList = []
        while initVal < paramMax:
            initVal += 1
            
            if self.progress:
                sys.stdout.write("\r{:b}".format(initVal))
                sys.stdout.flush()
                
            crcProc.setRegisterInitValue( initVal )
            
            xorVal = -1
            while xorVal < paramMax:
                xorVal += 1

                crcProc.setXorOutValue( xorVal )
                
                polyCRC = crcProc.calculate3(dataMask1, polyMask)
                if polyCRC != crc1:
                    continue
                polyCRC = crcProc.calculate3(dataMask2, polyMask)
                if polyCRC != crc2:
                    continue
                
                newKey = CRCKey(polyKey.poly, polyKey.rev, initVal, xorVal, polyKey.dataPos, polyKey.dataLen)
                
                if self.progress:
                    sys.stdout.write("\r")
                    print "Found key: {}".format(newKey)
                    
                retList.append( newKey )
         
        if self.progress:
            sys.stdout.write("\r")
            sys.stdout.flush()
        return retList
    
    def findPolysXOR(self, data1, crc1, data2, crc2, dataSize, crcSize, searchRange = 0):
        if self.progress:
            print "Checking {:X} {:X} xor {:X} {:X}, {} {}".format(data1, crc1, data2, crc2, dataSize, crcSize)
        xorData = data1 ^ data2
        xorCRC = crc1 ^ crc2
        dataCrc = MessageCRC(xorData, dataSize, xorCRC, crcSize)
        polyList = []
        polyList += self.findBruteForcePoly(dataCrc, False, searchRange)
        polyList += self.findBruteForcePoly(dataCrc, True, searchRange)
        return polyList

    def findBruteForcePoly(self, dataCrc, reverseMode, searchRange = 0):
        crcProc = self.createCRCProcessor()
        crcProc.setReversed(reverseMode)
        crc = dataCrc.crcNum
        dataMask = dataCrc.dataMask()
        poly = (0x1 << dataCrc.crcSize)
        polyMax = (poly << 1) 
        polyMask = dataCrc.crcMask()
        retList = []
        while poly < polyMax:
#             if self.progress and (poly % 16384) == 16383:
            if self.progress and (poly % 8192) == 8191:
                sys.stdout.write("\r{:b}".format(poly))
                sys.stdout.flush()

            polyMask.setNumber(poly)
            polyCRC = crcProc.calculate3(dataMask, polyMask)
            if polyCRC == crc:
#                 if self.progress:
#                     sys.stdout.write("\r")
#                     print "Found poly: 0b{0:b} 0x{0:X}".format(poly)
                retList.append( PolyKey(poly, reverseMode, 0, dataCrc.dataSize) )
            poly += 1
        
        if self.progress:
            sys.stdout.write("\r")
            sys.stdout.flush()
        return retList

    
    ##============================================================


    def createCRCProcessor(self):
        raise NotImplementedError

    
    
## ===================================================================



class RevHwCRC(Reverse):
    def __init__(self, printProgress = None):
        Reverse.__init__(self, printProgress)

    def createCRCProcessor(self):
        return HwCRC()
        
#     def createBackwardCRCProcessor(self, dataMask, crc):        
#         return HwCRCBackward( dataMask, crc )
    
    
class RevDivisionCRC(Reverse):
    def __init__(self, printProgress = None):
        Reverse.__init__(self, printProgress)

    def createCRCProcessor(self):
        return DivisionCRC()
        
#     def createBackwardCRCProcessor(self, dataMask, crc):     
#         return DivisionCRCBackward( dataMask, crc )
    
    
class RevModCRC(Reverse):
    def __init__(self, printProgress = None):
        Reverse.__init__(self, printProgress)

    def createCRCProcessor(self):
        return ModCRC()

    