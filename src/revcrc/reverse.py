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
from revcrc.input import InputData
import itertools
from crc.crcproc import CRCKey



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

    def findSolutionList(self, dataList, searchRange = 0):
        dInput = InputData()
        dInput.convert(dataList)
        self.findSolutionNumbers(dInput, searchRange)
        
    def findSolutionNumbers(self, inputData, searchRange = 0):
        if inputData.empty():
            return
        if inputData.ready() == False:
            return
            
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(inputData.numbersList), inputData.dataSize, inputData.crcSize)
            
        self.findSolution(inputData.numbersList, inputData.dataSize, inputData.crcSize, searchRange)

    def findXOR(self, data1, crc1, data2, crc2, dataSize = -1, crcSize = -1):
        if dataSize < 0:
            dataSize = max(data1.bit_length(), data2.bit_length())
        if crcSize < 0:
            crcSize = max(crc1.bit_length(), crc2.bit_length())
        return self.findPolyXOR(data1, crc1, data2, crc2, dataSize, crcSize)
    
    def findPolyXOR(self, data1, crc1, data2, crc2, dataSize, crcSize):
        inputData = data1 ^ data2
        inputCRC = crc1 ^ crc2
        
#         if self.progress:
#             messageFormat = "xor-ed input: {:b} {:0" + str(crcSize) + "b}"
#             print messageFormat.format(inputData, inputCRC)

#         messageFormat = "xor-ed input: {:X} {:0" + str(self.crcSize) + "b}"
#         print messageFormat.format(inputData, inputCRC)
        
        dataCrc = MessageCRC(inputData, dataSize, inputCRC, crcSize)
        retList = []
        retList += self.bruteForcePolyMode(dataCrc, False)
        retList += self.bruteForcePolyMode(dataCrc, True)
        return retList
    
    def bruteForcePoly(self, data, crc, dataSize = -1, crcSize = -1):
        if dataSize < 0:
            dataSize = data.bit_length()
        if crcSize < 0:
            crcSize = crc.bit_length()
        dataCrc = MessageCRC(data, dataSize, crc, crcSize)
        retList = []
        retList += self.bruteForcePolyMode(dataCrc, False)
        retList += self.bruteForcePolyMode(dataCrc, True)
        return retList
    
    def bruteForcePolyMode(self, dataCrc, reverseMode):
        crcProc = self.createCRCProcessor()
        crcProc.setReversed(reverseMode)
        crc = dataCrc.crcNum
        dataMask = NumberMask(dataCrc.dataNum, dataCrc.dataSize)
        poly = (0x1 << dataCrc.crcSize)
        polyMax = (poly << 1) 
        polyMask = NumberMask(0x0, dataCrc.crcSize)
        retList = []
        while poly < polyMax:
#             if self.progress and (poly % 16384) == 16383:
            if self.progress and (poly % 8192) == 8191:
                sys.stdout.write("\r{:b}".format(poly))
                sys.stdout.flush()

            polyMask.setNumber(poly)
#             print "calcxxx:", dataMask
            polyCRC = crcProc.calculate3(dataMask, polyMask)
            if polyCRC == crc:
                ##print "Detected poly: {:b}".format(retPoly)
                
#                 if self.progress:
#                     sys.stdout.write("\r")
#                     print "Found poly: 0b{0:b} 0x{0:X}".format(poly)

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

    ## ==========================================================

    def bruteForceList(self, dataList, searchRange = 0):
        dInput = InputData(dataList)
        dInput.convert(dataList)
        self.bruteForceInput(dInput, searchRange)
         
    def bruteForceNumbers(self, numbersList, dataSize, crcSize, searchRange = 0):
        dInput = InputData(numbersList, dataSize, crcSize)
        return self.bruteForceInput(dInput, searchRange)
    
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
            
            data1 = numberPair1[0]
            crc1 = numberPair1[1]
            data2 = numberPair2[0]
            crc2 = numberPair2[1]
            
            keys = self.findBruteForce(data1, crc1, data2, crc2, inputData.dataSize, inputData.crcSize, searchRange)

            if (self.progress):
                print "Found keys:", keys

            retList += keys
            
        return retList

    def findBruteForce(self, data1, crc1, data2, crc2, dataSize, crcSize, searchRange = 0):
        xorData = data1 ^ data2
        xorCRC = crc1 ^ crc2
        xorDataCrc = MessageCRC(xorData, dataSize, xorCRC, crcSize)
        
        if self.progress:
            print "Checking {:X} {:X} xor {:X} {:X}, {} {}".format(data1, crc1, data2, crc2, dataSize, crcSize)
                
        ## finding polys
        keyList = []
        keyList += self.findBruteForcePoly(xorDataCrc, False, searchRange)
        keyList += self.findBruteForcePoly(xorDataCrc, True, searchRange)
        
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
#             print "calcxxx:", dataMask
            polyCRC = crcProc.calculate3(dataMask, polyMask)
            if polyCRC == crc:
                if self.progress:
                    sys.stdout.write("\r")
                    print "Found poly: 0b{0:b} 0x{0:X}".format(poly)
                retList.append( CRCKey(poly, reverseMode, 0x0, 0x0, 0, dataCrc.dataSize) )
            poly += 1
        
        if self.progress:
            sys.stdout.write("\r")
            sys.stdout.flush()
        return retList

    def findBruteForceParams(self, dataCrc1, dataCrc2, crcKey):
        crcProc = self.createCRCProcessor()
        crcProc.setReversed( crcKey.rev )
         
        crcSize = dataCrc1.crcSize
        dataMask1 = dataCrc1.dataMask()
        dataMask2 = dataCrc2.dataMask()
        polyMask = NumberMask(crcKey.poly, crcSize)
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
                
                newKey = CRCKey(crcKey.poly, crcKey.rev, initVal, xorVal, crcKey.dataPos, crcKey.dataLen)
                
                if self.progress:
                    sys.stdout.write("\r")
                    print "Found key: {}".format(newKey)
                    
                retList.append( newKey )
         
        if self.progress:
            sys.stdout.write("\r")
            sys.stdout.flush()
        return retList

#     def bruteForce(self, dataCrc, reverseMode, searchRange = 0):
#         polyList = self.findPolyXOR(data1, crc1, data2, crc2, dataSize, crcSize)
#          
#         if self.progress:
#             sys.stdout.write("\r")
# #             print "Found polys:", polyList
#             joinString = ", ".join( "(0x{:X}, {})".format(x[0], x[1]) for x in polyList )
#             print "Found polys:", "[{}]".format( joinString )
#          
#         searchStart = dataSize-searchRange
#          
#         retList = []
#         for polyPair in polyList:
#             poly = polyPair[0]
#             polyMask = NumberMask(poly, crcSize)
#             reversedMode = polyPair[1]
#             polyAdded = False
#             for ds in range(searchStart, dataSize+1):
#                 d1 = NumberMask(data1, ds)
#                 cb1 = self.createBackwardCRCProcessor(d1, crc1)
#                 cb1.setReversed(reversedMode)
#                 backList1 = cb1.calculate(polyMask)
#                 if len(backList1) < 1:
#                     continue
#                  
#                 d2 = NumberMask(data2, ds)
#                 cb2 = self.createBackwardCRCProcessor(d2, crc2)
#                 cb2.setReversed(reversedMode)
#                 backList2 = cb2.calculate(polyMask)
#                 if len(backList2) < 1:
#                     continue
# # 
#                 backList = self.intersectBackLists(backList1, backList2)
#                 if len(backList) < 1:
#                     continue 
#  
#                 for initVal in backList:
#                     crcProc = self.createCRCProcessor()
#                     crcProc.setReversed(reversedMode)
#                     crcProc.setRegisterInitValue(initVal)
#                      
#                     verifyCrc1 = crcProc.calculate3(d1, polyMask)
#                     if (verifyCrc1 != crc1):
#                         continue
#                      
#                     verifyCrc2 = crcProc.calculate3(d2, polyMask)
#                     if (verifyCrc2 != crc2):
#                         ### rarely the condition happens
#                         continue
#                      
#                     thekey = CRCKey(poly, reversedMode, initVal, -1, 0, ds)
#                     if self.progress:
#                         sys.stdout.write("\r")
#                         print "Found key:", thekey
#                     retList.append( thekey )
#                     polyAdded = True
#             if polyAdded == False:
#                 ret = CRCKey()
#                 ret.poly = poly
#                 retList.append(ret)
#                  
#         return retList
                
    #TODO: remove method
    def findSubstring(self, dataNum, crcNum, polyUnderTest, polySize):
        dataSize = dataNum.bit_length()
           
        testMessage = 0
        bitMask = 1
        polyMask = NumberMask(polyUnderTest, polySize)
        for ds in range(0, dataSize):
            testMessage = testMessage | (bitMask & dataNum)        ## in each iteration adds one bit to variable
            bitMask = bitMask << 1
               
            ## print "Testing: 0x{:X}".format(testMessage)
               
#             crcProc = HwCRC()
#             crc = crcProc.calculate2(testMessage, testMessage.bit_length(), polyUnderTest, polySize)
            ##print "Found: {} {}".format(crc, crcNum)
            dataMask = NumberMask(testMessage, ds)
            crc = self.calculateNumberCRC(polyMask, False, 0x0, 0x0, dataMask)
            if crc == crcNum:
                return testMessage
        return -1
    
    ##============================================================

    def findSolution(self, dataList, dataSize, crcSize, searchRange = 0):
        raise NotImplementedError

    def calculateNumberCRC(self, polyMask, reverse, initReg, xorOut, dataMask):
        raise NotImplementedError

    