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
import copy
from collections import Counter


def flush_number( num, bitSize ):
    formatStr = "\r{:0%sb}" % bitSize
    sys.stdout.write( formatStr.format(num) )
    sys.stdout.flush()


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
        self.crcProc = self.createCRCProcessor()
    
    def setReturnOnFirst(self):
        self.returnFirst = True
        
        
    ## ==========================================================
        
    
    def bruteForceStandardInput(self, inputData, searchRange = 0):
        if inputData.empty():
            return
        if inputData.ready() == False:
            return
        
        numbersList = inputData.numbersList
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(numbersList), inputData.dataSize, inputData.crcSize)
        
        retList = Counter()
        
        for num in numbersList:
            keys = self.findBruteForceStandard( num, inputData.dataSize, inputData.crcSize, searchRange )

            if (self.progress):
                print "Found keys:", len( keys )

            retList.update( keys )
            
        return retList

    def findBruteForceStandard(self, dataCrcPair, dataSize, crcSize, searchRange = 0):
        data1 = dataCrcPair[0]
        crc1  = dataCrcPair[1]

        if self.progress:
            print "Checking {:X} {:X}, {} {}".format(data1, crc1, dataSize, crcSize)
        
        dataMask = NumberMask(data1, dataSize)
        crcMask  = NumberMask(crc1, crcSize)
        
        polyList = []
        
        initVal = -1
        paramMax = (0x1 << crcSize) - 1
                  
        while initVal < paramMax:
            initVal += 1
            
            if self.progress:
                flush_number( initVal, crcSize )
                
            self.crcProc.setRegisterInitValue( initVal )
            
            xorVal = -1
            while xorVal < paramMax:
                xorVal += 1
                self.crcProc.setXorOutValue( xorVal )
                
#                 if self.progress:
#                     sys.stdout.write("\r{:b}".format( xorVal ))
#                     sys.stdout.flush()
                
                polyList += self.findBruteForcePoly(dataMask, crcMask, False)
#                 polyList += self.findBruteForcePoly(dataMask, crcMask, True)            
#                 polyList += self.findBruteForcePolyReverse(dataMask, crcMask)

        for key in polyList:
            key.dataPos = 0
            key.dataLen = dataSize
            
        return polyList

    ## ==========================================================
    
    def bruteForcePairsInput(self, inputData, searchRange = 0):
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
            
            keys = self.findBruteForcePairs(numberPair1, numberPair2, inputData.dataSize, inputData.crcSize, searchRange)

            if (self.progress):
                print "Found keys:", len( keys )

            retList += keys
            
        return retList

    def findBruteForcePairs(self, dataCrcPair1, dataCrcPair2, dataSize, crcSize, searchRange = 0):
        data1 = dataCrcPair1[0]
        crc1 = dataCrcPair1[1]
        data2 = dataCrcPair2[0]
        crc2 = dataCrcPair2[1]
        
        keyList = self.findPolysXOR(data1, crc1, data2, crc2, dataSize, crcSize, searchRange)
        
        if (self.progress):
            print "Found {} potential polynomials to check".format( len(keyList) )
        
        ## finding xor value

        dataCrc1 = MessageCRC(data1, dataSize, crc1, crcSize)
        dataCrc2 = MessageCRC(data2, dataSize, crc2, crcSize)

        retList = []
        for key in keyList:
            paramsList = self.findBruteForceParams(dataCrc1, dataCrc2, key)
            if len(paramsList) < 1:
                continue
            #if self.progress:
            #    sys.stdout.write("\r")
            #    print "Found keys: {}".format( paramsList )
            retList += paramsList
        return retList

    def findBruteForceParams(self, dataCrc1, dataCrc2, polyKey):
        self.crcProc.setReversed( polyKey.rev )
         
        crcSize = dataCrc1.crcSize
        dataMask1 = dataCrc1.dataMask()
        dataMask2 = dataCrc2.dataMask()
        polyMask = NumberMask(polyKey.poly, crcSize)
        crc1 = dataCrc1.crcNum
        crc2 = dataCrc2.crcNum
        
        initVal = -1
        paramMax = (0x1 << crcSize) - 1
                  
        retList = []
        while initVal < paramMax:
            initVal += 1
            
            if self.progress:
                flush_number( initVal, crcSize )
                
            self.crcProc.setRegisterInitValue( initVal )
            
            xorVal = -1
            while xorVal < paramMax:
                xorVal += 1

                self.crcProc.setXorOutValue( xorVal )
                
                polyCRC = self.crcProc.calculate3(dataMask1, polyMask)
                if polyCRC != crc1:
                    continue
                polyCRC = self.crcProc.calculate3(dataMask2, polyMask)
                if polyCRC != crc2:
                    continue
                
                newKey = CRCKey(polyKey.poly, polyKey.rev, initVal, xorVal, polyKey.dataPos, polyKey.dataLen)
                
                #if self.progress:
                #    sys.stdout.write("\r")
                #    print "Found key: {}".format(newKey)
                    
                retList.append( newKey )
         
        if self.progress:
            sys.stdout.write("\r")
            sys.stdout.flush()
        return retList

    ## =============================================================

    def findPolysInput(self, inputData, searchRange = 0):
        if inputData.empty():
            return
        if inputData.ready() == False:
            return
        
        numbersList = inputData.numbersList
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(numbersList), inputData.dataSize, inputData.crcSize)
        
        ##retList = set()
        retList = Counter()
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

#             if (self.progress):
#                 keysSet = set(keys)
#                 print "Found polys:", keysSet

            retList.update( keys )
            
        return retList

    def findCommonInput(self, inputData, searchRange = -1):
        if inputData.empty():
            return
        if inputData.ready() == False:
            return
        if searchRange < 0:
            searchRange = inputData.dataSize-1
            
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(inputData.numbersList), inputData.dataSize, inputData.crcSize)
            
        return self.findCommon(inputData.numbersList, inputData.dataSize, inputData.crcSize, searchRange)
    
    ## searchRange=0 means exact length (no subvalues)
    def findCommon(self, dataList, dataSize, crcSize, searchRange = 0):
        retList = Counter()
        
        if len(dataList) < 1: 
            return retList
        
        for i in xrange(0, len(dataList)):
            dataPair = dataList[i]
            dataMask = NumberMask(dataPair[0], dataSize)
            keys = self.findCRCKeyBits( dataMask, dataPair[1], crcSize, searchRange)
            retList.update( keys )
            
        return retList
        
    def findCRCKeyBits(self, dataMask, crcNum, crcSize, searchRange):
        if self.progress:
            print "Checking {:X} {:X}".format(dataMask.dataNum, crcNum)
            
        crcMask = NumberMask(crcNum, crcSize)
        
        retList = set()
                
        subList = dataMask.generateSubnumbers(dataMask.dataSize - searchRange, 0)
        for sub in subList:
#             print "Checking subnumber {}".format(sub)
#             if self.progress:
#                 print "Checking substring {:X}".format(sub.dataNum)
            subRet = self.findCRC(sub, crcMask)
            if len(subRet) < 1:
                continue
            for key in subRet:
                key.dataPos = sub.pos
                key.dataLen = sub.size
            retList |= subRet
#             print "Found sub:", subRet, sub
            
        #if self.progress and len(retList)>0:
        #    print "Found keys:", retList
            
        return retList
        
    def findCRC(self, subNum, crcMask):
        dataMask = subNum.toNumberMask()
        retList = set()
        if crcMask.dataSize == 8:
            self.checkCRC(dataMask, crcMask, CRCKey(0x107, False, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x139, True, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11D, False, 0xFD, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x107, False, 0x55, 0x55), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x131, True, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x107, True, 0xFF, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x19B, True, 0x0, 0x0), retList)
        elif crcMask.dataSize == 16:
            self.checkCRC(dataMask, crcMask, CRCKey(0x18005, True, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x18005, False, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x18005, False, 0x800D, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x10589, False, 0x0001, 0x0001), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x13D65, True, 0xFFFF, 0xFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x13D65, False, 0xFFFF, 0xFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, False, 0x0, 0xFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x18005, True, 0xFFFF, 0xFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, True, 0xFFFF, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, True, 0x554D, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x18BB7, False, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x1A097, False, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x18005, True, 0x0, 0xFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, True, 0x0, 0xFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, False, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x18005, True, 0xFFFF, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, True, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, False, 0xFFFF, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, False, 0x1D0F, 0x0), retList)
        elif crcMask.dataSize == 24:
            self.checkCRC(dataMask, crcMask, CRCKey(0x1864CFB, False, 0xB704CE, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x15D6DCB, False, 0xFEDCBA, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x15D6DCB, False, 0xABCDEF, 0x0), retList)
        elif crcMask.dataSize == 32:
            self.checkCRC(dataMask, crcMask, CRCKey(0x104C11DB7, True, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x104C11DB7, False, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11EDC6F41, True, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x1A833982B, True, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x104C11DB7, False, 0xFFFFFFFF, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x104C11DB7, False, 0xFFFFFFFF, 0xFFFFFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x1814141AB, False, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x104C11DB7, True, 0xFFFFFFFF, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x1000000AF, False, 0x0, 0x0), retList)
        elif crcMask.dataSize == 64:
            self.checkCRC(dataMask, crcMask, CRCKey(0x1000000000000001B, True, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x142F0E1EBA9EA3693, False, 0x0, 0xFFFFFFFFFFFFFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x1AD93D23594C935A9, True, 0xFFFFFFFFFFFFFFFF, 0x0), retList)
        return retList
 
    def checkCRC(self, dataMask, crcMask, crcKey, retList):
        ## dataMask: NumberMask
        ## crcMask: NumberMask
        ## crcKey: CRCKey
        
        ##print "Checking data:", dataMask, crc, crcMaskKey
    
        self.crcProc.setValues(crcKey)
        
        polyMask = NumberMask(crcKey.poly, crcMask.dataSize)
        
        polyCRC = self.crcProc.calculate3(dataMask, polyMask)
        if polyCRC == crcMask.dataNum:
            retList.add( crcKey )
            ## we assume that if key was found then testing on reversed input will fail
            return
            
        if crcKey.rev == False:
            return
        
        #TODO: try to achieve compatibility without reversing 
        ## check reversed input (crcmod compatibility)
        self.crcProc.setInitCRC( crcKey.init, crcMask.dataSize )        
        revDataMask = dataMask.reversedBytes()
        polyMask.reverse()
            
        polyCRC = self.crcProc.calculate3(revDataMask, polyMask)
        if polyCRC == crcMask.dataNum:
            retList.add( crcKey )
        
    ## ==========================================================
    
    def findPolysXOR(self, data1, crc1, data2, crc2, dataSize, crcSize, searchRange = 0):
        xorData = data1 ^ data2
        xorCRC = crc1 ^ crc2
        if self.progress:
            print "Checking {:X} {:X} xor {:X} {:X} = {:X} {:X}, {} {}".format(data1, crc1, data2, crc2, xorData, xorCRC, dataSize, crcSize)
        xorMask = NumberMask(xorData, dataSize)
        crcMask = NumberMask(xorCRC, crcSize)
        
        retList = []
        
        subList = xorMask.generateSubnumbers(xorMask.dataSize - searchRange, 0)
        listLen = len(subList)
        ind = 0
        for sub in subList:
            ind += 1
#             print "Checking subnumber {}".format(sub)
            if self.progress:
                #print "Checking substring {:X}".format(sub.dataNum)
                sys.stdout.write( "\r{}/{} checking substring {}\n".format(ind, listLen, sub) )
                sys.stdout.flush()
            
            dataMask = sub.toNumberMask()
            
            polyList = []
            polyList += self.findBruteForcePoly(dataMask, crcMask, False)
            polyList += self.findBruteForcePoly(dataMask, crcMask, True)            
            polyList += self.findBruteForcePolyReverse(dataMask, crcMask)

            if len(polyList) < 1:
                continue
            for key in polyList:
                key.dataPos = sub.pos
                key.dataLen = sub.size
            retList += polyList
#             print "Found sub:", subRet, sub
             
#         if self.progress:
#             sys.stdout.write("\r")
#             sys.stdout.flush()
             
        return retList
    
    def findBruteForcePoly(self, dataMask, crcMask, reverseMode):
        self.crcProc.setReversed(reverseMode)
        crc = crcMask.dataNum
        poly = 0
        polyMax = crcMask.masterBit
        polyMask = copy.deepcopy(crcMask)
        retList = []
        while poly < polyMax:
#             if self.progress and (poly % 16384) == 16383:
#             if self.progress and (poly % 8192) == 8191:
#                 sys.stdout.write("\r{:b}".format(poly | polyMax))
#                 sys.stdout.flush()

            polyMask.setNumber(poly)
            polyCRC = self.crcProc.calculate3(dataMask, polyMask)
            if polyCRC == crc:
#                 if self.progress:
#                     sys.stdout.write("\r")
#                     print "Found poly: 0b{0:b} 0x{0:X}".format(poly)
                retList.append( PolyKey(poly|polyMax, reverseMode, 0, dataMask.dataSize) )
                
            poly += 1
                        
#         if self.progress:
#             sys.stdout.write("\r")
#             sys.stdout.flush()
            
        return retList
    
    #TODO: try to achieve compatibility without reversing 
    ## check reversed input and poly (crcmod compatibility)
    def findBruteForcePolyReverse(self, dataMask, crcMask, searchRange = 0):
        dataMask.reverseBytes()
        self.crcProc.setReversed(True)
        crc = crcMask.dataNum
        poly = 0
        polyMax = crcMask.masterBit
        polyMask = copy.deepcopy(crcMask)
        retList = []
        while poly < polyMax:
#             if self.progress and (poly % 16384) == 16383:
#             if self.progress and (poly % 8192) == 8191:
#                 sys.stdout.write("\r{:b}".format(poly | polyMax))
#                 sys.stdout.flush()

            polyMask.setNumber(poly)
            polyCRC = self.crcProc.calculate3(dataMask, polyMask)
            if polyCRC == crc:
#                 if self.progress:
#                     sys.stdout.write("\r")
#                     print "Found poly: 0b{0:b} 0x{0:X}".format(poly)
                revPoly = polyMask.reversedData() | polyMax
                retList.append( PolyKey(revPoly, True, 0, dataMask.dataSize) )
                
            poly += 1

#         if self.progress:
#             sys.stdout.write("\r")
#             sys.stdout.flush()
        return retList

    
    ##============================================================
    
    
    def verify(self, inputData, poly, initReg, xorVal):
        if inputData.empty():
            return True
        if inputData.ready() == False:
            return True
        
        numbersList = inputData.numbersList
        dataSize = inputData.dataSize
        crcSize  = inputData.crcSize
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format( len(numbersList), dataSize, crcSize )
        
        polyMask = NumberMask( poly, crcSize )
        
        for num in numbersList:
            data = num[0]
            crc  = num[1]
            if self.progress:
                print "Checking {:X} {:X}, {} {}".format( data, crc, dataSize, crcSize )

            dataMask = NumberMask( data, dataSize )
            crcMask  = NumberMask( crc, crcSize )
            
            self.crcProc.setRegisterInitValue( initReg )
            self.crcProc.setXorOutValue( xorVal )
                
            crc = crcMask.dataNum
            polyCRC = self.crcProc.calculate3( dataMask, polyMask )
            if polyCRC != crc:
                print "CRC mismatch: ", polyCRC, crc
                return False
            
        return True
                
    
    
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

    
