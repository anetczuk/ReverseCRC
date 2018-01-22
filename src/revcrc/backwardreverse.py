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
from crc.hwcrc import HwCRC
from crc.divisioncrc import DivisionCRC
from crc.modcrc import ModCRC, CRCModCacheMap
from revcrc.hwcrcbackward import HwCRCBackward
from revcrc.divisioncrcbackward import DivisionCRCBackward
from revcrc.reverse import Reverse
from crc.numbermask import NumberMask, intToASCII
import itertools
import sys
from crc.crcproc import CRCKey


    

##
##
class BackwardReverse(Reverse):
    
    ## crcSize  -- size of crc in bits
#     def __init__(self, crcSize, printProgress = None):
    def __init__(self, printProgress = None):
        Reverse.__init__(self, printProgress)
        
    def findSolution(self, dataList, dataSize, crcSize, searchRange = 0):
        if len(dataList) < 2:
            return []
        
        retList = []
        comb = list( itertools.combinations( dataList, 2 ) )
        cLen = len(comb)
        
        if (self.progress):
            print "Combinations number:", cLen
        
        for i in range(0, cLen):
            combPair = comb[i]
            dataPair1 = combPair[0]
            dataPair2 = combPair[1]
            
            data1 = dataPair1[0]
            crc1 = dataPair1[1]
            data2 = dataPair2[0]
            crc2 = dataPair2[1]
            keys = self.findCRCKeyBackward(data1, crc1, data2, crc2, dataSize, crcSize, searchRange)
            
            retList += keys
            
        return retList
      
    def findCRCKeyBackward(self, data1, crc1, data2, crc2, dataSize, crcSize, searchRange=0):
        if self.progress:
            print "Checking {:X} {:X} xor {:X} {:X}, {} {}".format(data1, crc1, data2, crc2, dataSize, crcSize)
        
        foundList = self.findPolysXOR( data1, crc1, data2, crc2, dataSize, crcSize, 0 )
        polyList = []
        for item in foundList:
            polyList.append( (item.poly, item.rev) )
        
        if self.progress:
            sys.stdout.write("\r")
#             print "Found polys:", polyList
            joinString = ", ".join( "(0x{:X}, {})".format(x[0], x[1]) for x in polyList )
            print "Found polys:", "[{}]".format( joinString )
        
        searchStart = max(0, dataSize-searchRange)
        
        retList = []
        for polyPair in polyList:
            poly = polyPair[0]
            polyMask = NumberMask(poly, crcSize)
            reversedMode = polyPair[1]
            polyAdded = False
            for ds in range(searchStart, dataSize+1):
                ##print "Shifting:", data1, ds, searchStart, (dataSize+1), searchRange
                d1 = NumberMask(data1, ds)
                cb1 = self.createBackwardCRCProcessor(d1, crc1)
                cb1.setReversed(reversedMode)
                backList1 = cb1.calculate(polyMask)
                if len(backList1) < 1:
                    continue
                
                d2 = NumberMask(data2, ds)
                cb2 = self.createBackwardCRCProcessor(d2, crc2)
                cb2.setReversed(reversedMode)
                backList2 = cb2.calculate(polyMask)
                if len(backList2) < 1:
                    continue
# 
                backList = self.intersectBackLists(backList1, backList2)
                if len(backList) < 1:
                    continue 

                for initVal in backList:
                    crcProc = self.createCRCProcessor()
                    crcProc.setReversed(reversedMode)
                    crcProc.setRegisterInitValue(initVal)
                    
                    verifyCrc1 = crcProc.calculate3(d1, polyMask)
                    if (verifyCrc1 != crc1):
                        continue
                    
                    verifyCrc2 = crcProc.calculate3(d2, polyMask)
                    if (verifyCrc2 != crc2):
                        ### rarely the condition happens
                        continue
                    
                    thekey = CRCKey(poly, reversedMode, initVal, -1, 0, ds)
                    if self.progress:
                        sys.stdout.write("\r")
                        print "Found key:", thekey
                    retList.append( thekey )
                    polyAdded = True
            if polyAdded == False:
                ret = CRCKey()
                ret.poly = poly
                retList.append(ret)
                
        return retList
    
    def intersectBackLists(self, list1, list2):
        tmpList1 = set()
        for item in list1:
            tmpList1.add( item.register )
            
        tmpList2 = set()
        for item in list2:
            tmpList2.add( item.register )
            
        return tmpList1.intersection(tmpList2)
    
    def createBackwardCRCProcessor(self, dataMask, crc):
        raise NotImplementedError
    
    
## =========================================================================
    
    
class RevHwCRC(BackwardReverse):
    def __init__(self, printProgress = None):
        BackwardReverse.__init__(self, printProgress)

    def createCRCProcessor(self):
        return HwCRC()
        
    def createBackwardCRCProcessor(self, dataMask, crc):        
        return HwCRCBackward( dataMask, crc )
    
    
class RevDivisionCRC(BackwardReverse):
    def __init__(self, printProgress = None):
        BackwardReverse.__init__(self, printProgress)

    def createCRCProcessor(self):
        return DivisionCRC()
        
    def createBackwardCRCProcessor(self, dataMask, crc):     
        return DivisionCRCBackward( dataMask, crc )
    
    
class RevModCRC(Reverse):
    def __init__(self, printProgress = None):
        Reverse.__init__(self, printProgress)


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
            keys = self.findCRCKeyForward(data1, crc1, data2, crc2, dataSize, crcSize, searchRange)
            
            retList += keys
            
        return retList
    
    def findCRCKeyForward(self, data1, crc1, data2, crc2, dataSize, crcSize, searchRange=0):
        if self.progress:
            print "Checking {:X} {:X} xor {:X} {:X} {} {}".format(data1, crc1, data2, crc2, dataSize, crcSize)
        
        polyList = self.findPolysXOR( data1, crc1, data2, crc2, dataSize, crcSize, 0 )
        
        dataString1 = intToASCII(data1)
        dataString2 = intToASCII(data2)
        regMax = 1 << crcSize
        
        if self.progress:
            print "found polys:", polyList
    
        retList = []
        for item in polyList:
            poly = item.poly
            reverse = item.rev
            polyAdded = False
#             print "checking poly: {:X}".format( poly )
            for initReg in xrange(0, regMax):
#                 print "checking init: {:b}".format( initReg )
                for xorReg in xrange(0, regMax):
                    crcKey = CRCKey(poly, reverse, initReg, xorReg, 0, dataSize)
                    
                    verifyCrc1 = self.calculateStringCRC(crcKey, dataString1 )
                    if (verifyCrc1 != crc1):
                        continue
                        
                    verifyCrc2 = self.calculateStringCRC(crcKey, dataString2 )
                    if (verifyCrc2 != crc2):
                        continue
                    
                    retList.append(crcKey)
                    polyAdded = True
                    if self.returnFirst == True:
                        return retList
                     
            if polyAdded == False:
                ret = CRCKey()
                ret.poly = poly
                retList.append(ret)
                
        return retList
    
    def calculateStringCRC(self, crcKey, data):
        crc_func = CRCModCacheMap.instance.getFunction(crcKey)
#         crc_func = crcmod.mkCrcFun(poly, rev=reverse, initCrc=initReg, xorOut=xorOut)
        return crc_func( data )


    ### =========================================================


    def createCRCProcessor(self):
        return ModCRC()        

    