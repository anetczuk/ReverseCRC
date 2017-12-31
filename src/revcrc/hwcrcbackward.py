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

    def __init__(self, polyMask, reg = 0x0):
        self.polyMask = polyMask
        self.crcMSB = self.polyMask.masterBit >> 1
        self.register = reg
        self.valid = True

    def copy(self):
        return copy.copy(self)

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
            self.register ^= self.polyMask.dataNum
            self.register |= self.polyMask.masterBit
        self.valid = ((self.register & 1) == 0)     ## valid if last bit is '0'
        self.register >>= 1
        if dataBit > 0:
            self.register ^= self.crcMSB

    ## 'one' says what bit add to register
    def shiftLSB(self, regBit, dataBit):
        ## reversing LSB mode
        if regBit == True:
            self.register ^= self.polyMask.dataNum
            self.register <<= 1
            self.register |= 1
        else:
            self.register <<= 1
        self.valid = ((self.register & self.polyMask.masterBit) == 0)     ## valid if last bit is '0'
        if dataBit > 0:
            self.register ^= 1
        
    def __repr__(self):
        regSize4 = int(math.ceil( float(self.polyMask.dataSize)/4 ))
        messageFormat = "<CRCBState pm:{} r:0x{:0" + str(regSize4) + "X} v:{}>"
        return messageFormat.format(self.polyMask, self.register, self.valid)
    
    def __eq__(self, other):
        if self.polyMask != other.polyMask:
            return False
        if self.register != other.register:
            return False
        if self.valid != other.valid:
            return False
        return True
     
    def __ne__(self, other):
        return ((self == other) == False)
     
    def __hash__(self):
        return hash(str(self.polyMask) + str(self.register) + str(self.valid))

 
 
class HwCRCBackward:
    def __init__(self, dataMask, crc):
        self.dataMask = dataMask
        self.crc = crc
        self.reversedMode = False
 
    def setReversed(self, value = True):
        self.reversedMode = value
 
    def calculate(self, polyMask, xorOut = 0):
        collector = []
        collector.append( HwCRCBackwardState( polyMask, self.crc^xorOut) )
        
        dataNum = self.dataMask.dataNum
        dataBit = 1
        if self.reversedMode:
            dataBit = (self.dataMask.masterBit >> 1)
            
        for _ in range(0, self.dataMask.dataSize):
            currBit = dataNum & dataBit
            receiver = []
            for c in collector:
                c1 = c
                c2 = c.copy()
                
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
            collector = receiver
#             print "collector:", collector
            if len(receiver) < 1:
                return []
            
        return collector

