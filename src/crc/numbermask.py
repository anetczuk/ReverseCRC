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


import math
import copy



def intToASCII(number, dataSize = -1):
    if dataSize < 0:
        dataSize = number.bit_length()
    ret = ""
    value = number
    while( dataSize > 0 ):
        char = value & 0xFF
        ret = chr(char) + ret
        value >>= 8
        dataSize -= 8
    return ret

def asciiToInt(dataString):
    ret = 0
    length = len(dataString)
    for i in xrange(length):                ## start
        ret <<= 8
        val = ord(dataString[i])
        ret |= val & 0xFF
    return ret

def reverseBits(num, sizeBits = -1):
    if sizeBits < 0:
        sizeBits = num.bit_length()
    ret = 0
    val = num
    for _ in range(0, sizeBits):
        ret <<= 1
        ret |= (val & 1)
        val >>= 1
    return ret
#     b = '{:0{width}b}'.format(num, width=sizeBits)
#     return int(b[::-1], 2)

def reverseBytes(num, sizeBytes = -1):
    if sizeBytes < 0:
        sizeBytes = int(math.ceil( float(num.bit_length())/8 ))
    ret = 0
    val = num
    for _ in range(0, sizeBytes):
        ret <<= 8
        ret |= (val & 0xFF)
        val >>= 8
    return ret


class SubNumber(object):
    def __init__(self, data, dataSize, pos):
        self.data = data
        self.size = dataSize
        self.pos = pos                              ## informative, do not affect data
    
    def toASCII(self):
        return intToASCII(self.data, self.size)
    
    def toNumberMask(self):
        return NumberMask(self.data, self.size)
    
    def __repr__(self):
        digits = int(math.ceil( float(self.size)/4 ))
        return ("<SubNumber 0x{0:0" + str(digits) + "X}/{0} {1} {2}>").format(self.data, self.size, self.pos)
    
    def __eq__(self, other):
        if self.data != other.data:
            return False
        if self.size != other.size:
            return False
        if self.pos != other.pos:
            return False
        return True
    
    def __ne__(self, other):
        return ((self == other) == False)
    
    def __hash__(self):
        return hash( (self.data, self.size, self.pos) )
    

def generateSubstrings(dataString, maxPos = -1):
    valSet = set()
    retSet = set()
    length = len(dataString)
    if maxPos < 0:
        maxPos = length-1
    for x in xrange(maxPos+1):
        for y in xrange(x,length):
            substr = dataString[x:y+1]
            if (substr in valSet) == False:
                valSet.add(substr)
                retSet.add( SubNumber(substr, len(substr), x) )
    return retSet

def generateSubstringsReverse(dataString, maxPos = -1):
    valSet = set()
    retSet = set()
    length = len(dataString)
    if maxPos < 0:
        maxPos = length-1
    for x in xrange(length):
        ypos = max(x, length-maxPos-1)
        for y in xrange(ypos,length):
            substr = dataString[x:y+1]
            if (substr in valSet) == False:
                valSet.add(substr)
                subLen = len(substr)
                retSet.add( SubNumber(substr, subLen, length-subLen-x) )
    return retSet



# class RawNumber(object):
#     def __init__(self, data, dataSize):
#         self.dataSize = dataSize
#         self.setNumber(data)
#         
#     def setNumber(self, newValue):
#         self.dataNum = (newValue & ((0b1 << self.dataSize)-1) )
#         
#     def __repr__(self):
#         digits = int(math.ceil( float(self.dataSize)/4 ))
#         return ("<RawNumber 0x{:0" + str(digits) + "X} {}>").format(self.dataNum, self.dataSize)
# 
#     def __eq__(self, other):
#         if self.dataNum != other.dataNum:
#             return False
#         if self.dataSize != other.dataSize:
#             return False
#         return True
#     
#     def __ne__(self, other):
#         return ((self == other) == False)
#     
#     def __hash__(self):
#         return hash( (self.dataSize, self.dataNum) )


    
class NumberMask:
    def __init__(self, data, dataSize):
        self.dataSize = dataSize
        self.calculateCache()
        self.setNumber(data)
    
    def setNumber(self, newValue):
        self.dataNum = (newValue & (self.dataMask))
    
    def calculateCache(self):
        self.masterBit = 0b1 << self.dataSize
        self.dataMask = self.masterBit-1        
    
    def masterData(self):
        return self.dataNum | self.masterBit
    
    def pushMSB(self, bit):
        if bit > 0:
            self.dataNum |= self.masterBit
        self.dataSize += 1
        self.calculateCache()
        
    def pushLSB(self, bit):
        self.dataNum <<= 1
        if bit > 0:
            self.dataNum |= 1
        self.dataSize += 1
        self.calculateCache()
        
    def pushLSZeros(self, num):
        self.dataNum <<= num
        self.dataSize += num
        self.calculateCache()
        
    def popLSZeros(self, num):
        self.dataNum >>= num
        self.dataSize -= num
        self.calculateCache()
        
    def pushMSZeros(self, num):
        self.dataSize += num
        self.calculateCache()
         
    def popMSZeros(self, num):
        self.dataSize -= num
        self.calculateCache()
    
    def containsMSB(self, dataMask):
        sizeDiff = self.dataSize - dataMask.dataSize
        if sizeDiff < 0:
            return False
        cmpMask = (dataMask.dataMask << sizeDiff) 
        data1 = self.dataNum & cmpMask
        data2 = (dataMask.dataNum << sizeDiff)
        return (data1 == data2)
    
    def containsLSB(self, dataMask):
        if self.dataSize < dataMask.dataSize:
            return False
        cmpMask = dataMask.dataMask
        data1 = self.dataNum & cmpMask
        data2 = dataMask.dataNum & cmpMask
        return (data1 == data2)
    
    def reverse(self):
        self.dataNum = reverseBits(self.dataNum, self.dataSize)
        
    def reverseBytes(self):
        bytesNum = int(math.ceil( float(self.dataSize)/8 ))
        self.dataNum = reverseBytes(self.dataNum, bytesNum)

    def reversed(self):
        revData = copy.deepcopy(self)
        revData.reverse()
        return revData
    
    def reversedBytes(self):
        revData = copy.deepcopy(self)
        revData.reverseBytes()
        return revData
    
    def getMSB(self, length):
        retVal = 0
        retBit = 1 << (length-1)
        dataBit = (self.masterBit >> 1)
        for _ in xrange(0, length):
            if (self.dataNum & dataBit) > 0:
                retVal |= retBit
            retBit >>= 1
            dataBit >>= 1
        return retVal    
    
    def getLSB(self, length):
        bitsMask = (1 << length) -1 
        return (self.dataNum & bitsMask)

    def toASCII(self):
        return intToASCII(self.dataNum)
    
    def generateSubnumbers(self, maxPos = -1, minLen = -1):
        valSet = set()
        retSet = set()
        if maxPos < 0:
            maxPos = self.dataSize-1
        if minLen < 1:
            minLen = 1
        lenMask = (1 << minLen) - 1 
        for valLen in xrange(minLen, self.dataSize+1):
            xpos = min(self.dataSize-valLen, maxPos)
            for x in xrange(xpos+1):
                val = (self.dataNum >> x) & lenMask
                t = (val, valLen)
                if (t in valSet) == False:
                    valSet.add( t )
                    retSet.add( SubNumber(val, valLen, x) )
            lenMask = (lenMask << 1) | 0x1
                
        return retSet
    
    def __repr__(self):
        digits = int(math.ceil( float(self.dataSize)/4 ))
        return ("<NumberMask 0x{0:0" + str(digits) + "X}/{0} {1}>").format(self.dataNum, self.dataSize)

    def __eq__(self, other):
        if self.dataNum != other.dataNum:
            return False
        if self.dataSize != other.dataSize:
            return False
        return True
    
    def __ne__(self, other):
        return ((self == other) == False)
    
    def __hash__(self):
        return hash( (self.dataSize, self.dataNum) )
    