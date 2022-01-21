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


## return ceil integer as result of division
def divide_ceil( number, divider ):
    return int( math.ceil( float( number ) / divider ) )


## reverse whole number
def reverse_number(num, sizeBits = -1):
    if sizeBits < 0:
        sizeBits = num.bit_length()
    ret = 0
    number = num
    for _ in range(0, sizeBits):
        ret <<= 1
        ret |= (number & 1)
        number >>= 1
    return ret
#     b = '{:0{width}b}'.format(num, width=sizeBits)
#     return int(b[::-1], 2)


## change (reverse) order of bytes in number
def reorder_bytes(num, sizeBytes = -1):
    if sizeBytes < 0:
        sizeBytes = divide_ceil( num.bit_length(), 8 )
    ret = 0
    number = num
    for _ in range(0, sizeBytes):
        ret <<= 8
        ret |= (number & 0xFF)
        number >>= 8
    return ret


def reflect_bits(num, sizeBits):
    sizeBytes = divide_ceil( sizeBits, 8 )
    ret = 0
    number = num
    for i in range(0, sizeBytes):
        ret += reverse_number(number & 0xFF, 8) << (i * 8)
        number >>= 8
    return ret


## =================================================


class SubNumber(object):
    def __init__(self, data, dataSize, pos):
        self.data = data
        self.size = dataSize
        self.pos = pos                              ## informative, do not affect data, counts from LSB

    def toASCII(self):
        return intToASCII(self.data, self.size)

    def toNumberMask(self):
        return NumberMask(self.data, self.size)

    def __repr__(self):
        digits = divide_ceil( self.size, 4 )
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


class NumberMask:
    """Container for data and it's size given in bits."""

    ## dataSize -- number of bits
    def __init__(self, data, dataSize):
        self.dataSize  = dataSize                ## number of bits
        self.masterBit = None                    ## equals to 2 ** dataSize 
        self.dataMask  = None
        self.dataNum   = None
        self.revDataBytes = None
        self.calculateCache()
        self.setNumber(data)

    def __repr__(self):
        digits = divide_ceil( self.dataSize, 4 )
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

    def setNumber(self, newValue):
        #self.dataNum = (newValue & (self.dataMask))
        self.dataNum = newValue
        if self.dataNum > self.dataMask:
            self.dataNum &= self.dataMask
        self.revDataBytes = None

    def calculateCache(self):
        self.masterBit = 0b1 << self.dataSize
        self.dataMask = self.masterBit-1

    def masterData(self):
        return self.dataNum | self.masterBit

    ## reverse whole number
    def reverse(self):
        self.dataNum = reverse_number(self.dataNum, self.dataSize)
        self.revDataBytes = None

    ## reverse whole number
    def reversed(self):
        revData = copy.deepcopy(self)
        revData.reverse()
        return revData

    ## reverse whole number
    def reversedData(self):
        return reverse_number(self.dataNum, self.dataSize)

    def reorderBytes(self):
        self._calcReorderBytes()
        tmpData = self.dataNum
        self.dataNum = self.revDataBytes
        self.revDataBytes = tmpData

    def reorderedBytes(self):
        self._calcReorderBytes()
        return NumberMask(self.revDataBytes, self.dataSize)

    def reflectBits(self):
        self.revDataBytes = None
        self.dataNum = reflect_bits( self.dataNum, self.dataSize )

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
    
    def generateSubnumbers(self, minLen = -1, maxPos = -1):
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

    def toASCII(self):
        return intToASCII(self.dataNum)
    
    ## 0b 11  1100 0011  1111 1111 -> 0b 0000 0011  1100 0011  1111 1111 -> 0b 1111 1111  1100 0011  0000 0011
    def _calcReorderBytes(self):
        if self.revDataBytes != None:
            return
#         if self.dataSize % 8 != 0:
#             raise ValueError( "bytes reordering is valid only for bits number be multiple of 8, current size is %s" % self.dataSize )
        bytesNum = divide_ceil( self.dataSize, 8 )
        self.revDataBytes = reorder_bytes( self.dataNum, bytesNum )


class ReverseNumberMask( NumberMask ):
    
    def __init__(self, data = 0, dataSize = 0):
        NumberMask.__init__( self, data, dataSize )

    @classmethod
    def from_NumberMask(cls, data):
        data = ReverseNumberMask( data.dataNum, data.dataSize )
        return data

    def pushMSB(self, bit):
        if bit > 0:
            self.dataNum |= self.masterBit
            self.revDataBytes = None
        self.dataSize += 1
        self.calculateCache()

    def pushLSB(self, bit):
        self.dataNum <<= 1
        self.revDataBytes = None
        if bit > 0:
            self.dataNum |= 1
        self.dataSize += 1
        self.calculateCache()

    def pushLSZeros(self, num):
        self.dataNum <<= num
        self.revDataBytes = None
        self.dataSize += num
        self.calculateCache()

    def popLSZeros(self, num):
        self.dataNum >>= num
        self.revDataBytes = None
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
