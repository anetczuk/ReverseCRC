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
        return "<DCRCBState dm:{} pm{} r:0x{:X}>".format( self.dataMask, self.polyMask, self.register )
#         regSize4 = int(math.ceil( float(self.crcSize)/4 ))
#         messageFormat = "<DCRCBState dm:{} pm{} r:0x{:0" + str(regSize4) + "X}>"
#         return messageFormat.format(self.dataMask, self.polyMask, self.register)
    
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
    def __init__(self, dataMask, crc):
        self.dataMask = copy.deepcopy(dataMask)
        self.crc = crc
        self.reversedMode = False

    def setReversed(self, value = True):
        self.reversedMode = value

    def calculate(self, polyMask, xorOut = 0):
        crcSize = polyMask.dataSize
        collector = []
        collector.append( DivisionCRCBackwardState( polyMask, self.crc^xorOut) )
        
        ### shift crc zeros        
        collector = self._roundZeros(collector, crcSize)
            
        initShift = min(crcSize, self.dataMask.dataSize)
        
        ## divide
        divideShifts = self.dataMask.dataSize - crcSize
        collector = self._round(collector, divideShifts)
        
        if len(collector) < 1:
            return []
        
        ## init shift register
        self._initShift(collector, initShift)
            
        return collector
    
    def _roundZeros(self, collector, crcSize):
        retList = []
        if self.reversedMode == False:
            self.dataMask.pushLSZeros(crcSize)
            retList = self._round(collector, crcSize)
            self.dataMask.popLSZeros(crcSize)
            for c in retList:
                c.popLSZeros(crcSize)
        else:
            self.dataMask.pushMSZeros(crcSize)
            retList = self._round(collector, crcSize)
            self.dataMask.popMSZeros(crcSize)
            for c in retList:
                c.popMSZeros(crcSize)
#         print "collector:", retList
        return retList
        
    def _round(self, collector, num=1):
        for _ in range(0, num):
            receiver = []
            for c in collector:
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
            collector = receiver
#             print "collector:", collector
            if len(receiver) < 1:
                return []
        return collector
            
    def _initShift(self, collector, shiftLength):
#         initBits = self.dataMask.getMSB(shiftLength)
#         for c in collector:
#             c.initXor(initBits, shiftLength)
            
        if self.reversedMode == False:
            initBits = self.dataMask.getMSB(shiftLength)
            for c in collector:
                c.initXorMSB(initBits, shiftLength)
        else:
            initBits = self.dataMask.getLSB(shiftLength)
            for c in collector:
                c.initXorLSB(initBits, shiftLength)

    
    def isProper(self, crcBack):
        if self.reversedMode == False:
            return self.dataMask.containsLSB( crcBack.dataMask )
        else:
            return self.dataMask.containsMSB( crcBack.dataMask )
    
