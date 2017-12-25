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



def intToASCII(number):
    ret = ""
    value = number
    while( value > 0 ):
        char = value & 0xFF
        ret = chr(char) + ret
        value >>= 8
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


class NumberMask:
    def __init__(self, data, dataSize):
        self.msbMask = 0b1 << dataSize      ## cached value
        self.dataNum = (data & (self.msbMask-1))
        self.dataSize = dataSize
    
    def pushMSB(self, bit):
        if bit > 0:
            self.dataNum |= self.msbMask
        self.dataSize += 1
        self.msbMask <<= 1
        
    def pushLSB(self, bit):
        self.dataNum <<= 1
        if bit > 0:
            self.dataNum |= 1
        self.dataSize += 1
        self.msbMask <<= 1
        
    def pushLSZeros(self, num):
        self.dataNum <<= num
        self.dataSize += num
        self.msbMask <<= num
        
    def popLSZeros(self, num):
        self.dataNum >>= num
        self.dataSize -= num
        self.msbMask >>= num
        
    def pushMSZeros(self, num):
        self.dataSize += num
        self.msbMask <<= num
         
    def popMSZeros(self, num):
        self.dataSize -= num
        self.msbMask >>= num
    
    def containsMSB(self, dataMask):
        sizeDiff = self.dataSize - dataMask.dataSize
        if sizeDiff < 0:
            return False
        cmpMask = ((dataMask.msbMask-1) << sizeDiff) 
        data1 = self.dataNum & cmpMask
        data2 = (dataMask.dataNum << sizeDiff)
        return (data1 == data2)
    
    def containsLSB(self, dataMask):
        if self.dataSize < dataMask.dataSize:
            return False
        cmpMask = dataMask.msbMask-1
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
        retBits = 0
        dataBit = (self.msbMask >> 1)
        for _ in range(0, length):
            retBits <<= 1
            if (self.dataNum & dataBit) > 0:
                retBits |= 1
            dataBit >>= 1
        return retBits
    
    def getLSB(self, length):
        bitsMask = (1 << length) -1 
        return (self.dataNum & bitsMask)

    def toASCII(self):
        return intToASCII(self.dataNum)
    
    def __repr__(self):
        digits = int(math.ceil( float(self.dataSize)/4 ))
        return ("<NumberMask 0x{:0" + str(digits) + "X} {}>").format(self.dataNum, self.dataSize)

    def __eq__(self, other):
        if self.dataNum != other.dataNum:
            return False
        if self.dataSize != other.dataSize:
            return False
        return True
    
    def __ne__(self, other):
        return ((self == other) == False)
    
#     def __hash__(self):
#         return hash(str(self.dataNum) + str(self.dataSize))
