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
from crc.numbermask import intToASCII, NumberMask
import sys



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

    def bruteForce3(self, dataCrc):
        crcNum = dataCrc.crcNum
        poly = 1 << (dataCrc.crcSize)
        polyMax = poly << 1
        retList = []
        dataString = intToASCII(dataCrc.dataNum)
        
        while poly < polyMax:
#             print "checking poly: {:b}".format( poly )
            ##crc_func = crcmod.mkCrcFun(poly, rev=False, initCrc=0x0, xorOut=0x0)
            ##polyCRC  = crc_func( dataString )

            polyCRC = self.calculateStringCRC(poly, False, 0x0, 0x0, dataString)
            if polyCRC == crcNum:
                retList.append(poly)
            poly += 1
        return retList

    
    
    ##============================================================
    
    
    
    def bruteForcePair(self, inputPair):
        dataString = inputPair[0]
        crcString = inputPair[1]
 
        data = int(dataString, 16)
        crc = int(crcString, 16)
        crcSize = len(crcString) * 4
         
        return self.bruteForce(data, crc, crcSize = crcSize)
    
    def bruteForce(self, data, crc, dataSize = -1, crcSize = -1):
        if dataSize < 0:
            dataSize = data.bit_length()
        if crcSize < 0:
            crcSize = crc.bit_length()
        dataCrc = MessageCRC(data, dataSize, crc, crcSize)
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
        poly = (0x1 << dataCrc.crcSize)
        polyMax = (poly << 1) 
        polyNum = NumberMask(0x0, dataCrc.crcSize)
        retList = []
        while poly < polyMax:
            if self.progress and (poly % 16384) == 16383:
                sys.stdout.write("\r{:b}".format(poly))
                sys.stdout.flush()

            polyNum.setNumber(poly)
            polyCRC = crcProc.calculate3(dataMask, polyNum)
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
    
    def calculateStringCRC(self, poly, reverse, initReg, xorOut, data):
        raise NotImplementedError
    
    def calculateNumberCRC(self, polyMask, reverse, initReg, xorOut, dataMask):
        raise NotImplementedError

    