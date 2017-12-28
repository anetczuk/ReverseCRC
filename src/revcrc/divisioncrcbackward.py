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


import copy
import math
from crc.numbermask import NumberMask



class DivisionCRCBackwardState:

    def __init__(self, polyMask, reg = 0x0, dataMask = NumberMask(0, 0)):
        self.dataMask = copy.deepcopy(dataMask)
        self.polyMask = copy.deepcopy(polyMask)
        self.register = reg

    def shiftBit(self, one, revMode = False):
        if revMode == False:
            self.shiftMSB(one)
        else:
            self.shiftLSB(one)
        
    ## 'one' says what bit add to register
    def shiftMSB(self, one):
        ## reversing MSB mode
        if one:
            self.register ^= self.polyMask.dataNum
            self.register |= self.polyMask.masterBit             ## set one
        self.dataMask.pushMSB( self.register & 1 )
        self.register >>= 1
        
    ## 'one' says what bit add to register
    def shiftLSB(self, one):
        ## reversing MSB mode
        if one:
            self.register ^= self.polyMask.dataNum
            self.register <<= 1
            self.register |= 1
        else:
            self.register <<= 1
        self.dataMask.pushLSB( self.register & self.polyMask.masterBit )
        self.register &= self.polyMask.dataMask

    def initXorMSB(self, data, dataSize):
        self.dataMask.dataNum |= (data << self.dataMask.dataSize)
        self.dataMask.dataSize += dataSize
        self.register ^= data
        
    def initXorLSB(self, data, dataSize):
        self.dataMask.dataNum <<= dataSize
        self.dataMask.dataNum |= data
        self.dataMask.dataSize += dataSize
        self.register ^= data

    def popLSZeros(self, num):
        self.dataMask.popLSZeros(num)
        
    def popMSZeros(self, num):
        self.dataMask.popMSZeros(num)
        
    def __repr__(self):
        regSize4 = int(math.ceil( float(self.crcSize)/4 ))
        messageFormat = "<DCRCBState dm:{} pm{} r:0x{:0" + str(regSize4) + "X}>"
        return messageFormat.format(self.dataMask, self.polyMask, self.register)
    
    def __eq__(self, other):
        if self.dataMask != other.dataMask:
            return False
        if self.polyMask != other.polyMask:
            return False
        if self.register != other.register:
            return False
        return True
     
    def __ne__(self, other):
        return ((self == other) == False)
     
    def __hash__(self):
        return hash(str(self.dataMask) + str(self.polyMask) + str(self.register))


##
## Finds registry init value
##
class DivisionCRCBackward:
    def __init__(self, dataMask, crc, polyMask, xorOut = 0):
        self.dataMask = copy.deepcopy(dataMask)
        self.crcSize = polyMask.dataSize
        self.reversedMode = False
        self.collector = []
        self.collector.append( DivisionCRCBackwardState( polyMask, crc^xorOut) )

    def setReversed(self, value = True):
        self.reversedMode = value

    def calculate(self):
        ### shift crc zeros        
        self._roundZeros()
            
        initShift = min(self.crcSize, self.dataMask.dataSize)
        
        ## divide
        divideShifts = self.dataMask.dataSize - self.crcSize
        self._round(divideShifts)
        
        if len(self.collector) < 1:
            return []
        
        ## init shift register
        self._initShift(initShift)
            
        return self.collector
    
    def _roundZeros(self):
        if self.reversedMode == False:
            self.dataMask.pushLSZeros(self.crcSize)
            self._round(self.crcSize)
            self.dataMask.popLSZeros(self.crcSize)
            for c in self.collector:
                c.popLSZeros(self.crcSize)
        else:
            self.dataMask.pushMSZeros(self.crcSize)
            self._round(self.crcSize)
            self.dataMask.popMSZeros(self.crcSize)
            for c in self.collector:
                c.popMSZeros(self.crcSize)            
#         print "collector:", self.collector
        
    def _round(self, num=1):
        for _ in range(0, num):
            receiver = []
            for c in self.collector:
                ##c1 = copy.deepcopy(c)
                c1 = c
                c2 = copy.deepcopy(c)
                
                c1.shiftBit(False, self.reversedMode)
                if self.isProper(c1):
                    receiver.append(c1)
                c2.shiftBit(True, self.reversedMode)
                if self.isProper(c2):
                    receiver.append(c2)
    #             print "collection:", receiver
            self.collector = receiver
#             print "collector:", self.collector
            if len(receiver) < 1:
                return
            
    def _initShift(self, shiftLength):
#         initBits = self.dataMask.getMSB(shiftLength)
#         for c in self.collector:
#             c.initXor(initBits, shiftLength)
            
        if self.reversedMode == False:
            initBits = self.dataMask.getMSB(shiftLength)
            for c in self.collector:
                c.initXorMSB(initBits, shiftLength)
        else:
            initBits = self.dataMask.getLSB(shiftLength)
            for c in self.collector:
                c.initXorLSB(initBits, shiftLength)

    
    def isProper(self, crcBack):
        if self.reversedMode == False:
            return self.dataMask.containsLSB( crcBack.dataMask )
        else:
            return self.dataMask.containsMSB( crcBack.dataMask )
    
