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
 


class HwCRCBackwardState:

    def __init__(self, crcSize, poly, reg = 0x0):
        self.crcSize = crcSize
        self.masterBit = 0b1 << self.crcSize     ## cached value
#         self.crcMask = self.masterBit - 1
        crcMask = self.masterBit - 1
        self.crcMSB = (self.masterBit >> 1)
        self.poly = poly & crcMask
        self.register = reg
        self.valid = True

    def isValid(self):
        return self.valid

    def shiftBit(self, regBit, dataBit, revMode = False):
        if revMode == False:
            self.shiftMSB(regBit, dataBit)
        else:
            self.shiftLSB(regBit, dataBit)
        
    ## 'one' says what bit add to register
    def shiftMSB(self, regBit, dataBit):
        ## reversing MSB mode
        if regBit == True:
            self.register ^= self.poly
            self.register |= self.masterBit
        self.valid = ((self.register & 1) == 0)     ## valid if last bit is '0'
        self.register >>= 1
        if dataBit > 0:
            self.register ^= self.crcMSB

    ## 'one' says what bit add to register
    def shiftLSB(self, regBit, dataBit):
        ## reversing LSB mode
        if regBit == True:
            self.register ^= self.poly
            self.register <<= 1
            self.register |= 1
        else:
            self.register <<= 1
        self.valid = ((self.register & self.masterBit) == 0)     ## valid if last bit is '0'
        if dataBit > 0:
            self.register ^= 1
        
    def __repr__(self):
        regSize4 = int(math.ceil( float(self.crcSize)/4 ))
        messageFormat = "<CRCBState p:0x{:X} cs:{} r:0x{:0" + str(regSize4) + "X}>"
        return messageFormat.format(self.poly, self.crcSize, self.register)
    
    def __eq__(self, other):
        if self.crcSize != other.crcSize:
            return False
        if self.poly != other.poly:
            return False
        if self.register != other.register:
            return False
        return True
     
    def __ne__(self, other):
        return ((self == other) == False)
     
    def __hash__(self):
        return hash(str(self.poly) + str(self.crcSize) + str(self.register))

 
 
class HwCRCBackward:
    def __init__(self, dataMask, crc, crcSize, poly, xorOut = 0):
        self.dataMask = copy.deepcopy(dataMask)
        self.reversedMode = False
        self.collector = []
        self.collector.append( HwCRCBackwardState( crcSize, poly, crc^xorOut) )
 
    def setReversed(self, value = True):
        self.reversedMode = value
 
    def calculate(self):
        dataNum = self.dataMask.dataNum
        dataBit = 1
        if self.reversedMode:
            dataBit = (self.dataMask.msbMask >> 1)
            
        for _ in range(0, self.dataMask.dataSize):
            currBit = dataNum & dataBit
            receiver = []
            for c in self.collector:
                c1 = copy.deepcopy(c)
                c2 = copy.deepcopy(c)
                c1.shiftBit(False, currBit, self.reversedMode)
                if c1.isValid():
                    receiver.append(c1)
                c2.shiftBit(True, currBit, self.reversedMode)
                if c2.isValid():
                    receiver.append(c2)
            if self.reversedMode == False:
                dataBit <<= 1
            else:
                dataBit >>= 1
    #             print "collection:", receiver
            self.collector = receiver
#             print "collector:", self.collector
            if len(receiver) < 1:
                return []
            
        return self.collector

