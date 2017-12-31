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



class MessageCRC:
    def __init__(self, data, dataSize, crc, crcSize):
        self.dataNum = data
        self.dataSize = dataSize
        self.crcNum = crc
        self.crcSize = crcSize
        
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
        dInput = InputData(dataList)
        self.findSolutionNumbers(dInput, searchRange)
        
    def findSolutionNumbers(self, inputData, searchRange = 0):
        if inputData.empty():
            return
        
        if inputData.ready() == False:
            inputData.convert()
            
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

#     def bruteForceList(self, dataList, searchRange = 0):
#         dInput = InputData(dataList)
#         self.findSolutionNumbers(dInput, searchRange)
#         
#     def bruteForceNumbers(self, inputData, searchRange = 0):
#         if inputData.empty():
#             return
#         
#         if inputData.ready() == False:
#             inputData.convert()
#             
#         if (self.progress):
#             print "List size: {} Data size: {} CRC size: {}".format(len(inputData.numbersList), inputData.dataSize, inputData.crcSize)
#             
#         self.numbersList = []
#         self.dataSize = 0
#         self.crcSize = 0
#         for dn in inputData.numbersList:
#             dataCrc = MessageCRC(dn[0], inputData.dataSize, dn[1], inputData.crcSize)
#             if self.progress:
#                 print "Checking {:X} {:X}, {} {}".format(dataCrc.dataNum, dataCrc.crcNum, dataCrc.dataSize, dataCrc.crcSize)
#             retList = []
#             retList += self.bruteForce(dataCrc, False, searchRange)
#             retList += self.bruteForce(dataCrc, True, searchRange)
#             ##retList
#     
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
                
    #TODO: remove
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

    