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
from crc.numbermask import reverseBits, NumberMask


class PolyKey:
    def __init__(self, poly=-1, rev=False, dataPos=-1, dataLen=-1):
        self.poly = poly
        self.rev = rev
        self.dataPos = dataPos
        self.dataLen = dataLen

    def __repr__(self):
        return "<PolyKey p:0x{:X} r:{:} dP:{:} dL:{:}>".format(self.poly, self.rev, self.dataPos, self.dataLen)
    
    def __eq__(self, other):
        if self.poly != other.poly:
            return False
        if self.rev != other.rev:
            return False
        if self.dataPos != other.dataPos:
            return False
        if self.dataLen != other.dataLen:
            return False
        return True
    
    def __ne__(self, other):
        return ((self == other) == False)
    
    def __hash__(self):
        return hash(str(self.poly) + str(self.rev))
    
    
class CRCKey:
    def __init__(self, poly=-1, rev=False, init=-1, xor=-1, dataPos=-1, dataLen=-1):
        self.poly = poly
        self.rev = rev
        self.init = init
        self.xor = xor
        self.dataPos = dataPos
        self.dataLen = dataLen

    def __repr__(self):
        return "<CRCKey p:0x{:X} r:{:} i:0x{:X} x:0x{:X} dP:{:} dL:{:}>".format(self.poly, self.rev, self.init, self.xor, self.dataPos, self.dataLen)
    
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
    


class CRCProc(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.reset()
        
    def reset(self):
        self.registerInit = 0x0
        self.xorOut = 0x0
        self.reversed = False

    def setRegisterInitValue(self, value):
        self.registerInit = value
        
    def setXorOutValue(self, value):
        self.xorOut = value
        
    def setInitCRC(self, value, crcSize):
        self.registerInit = value ^ self.xorOut
        if self.reversed == True:
            self.registerInit = reverseBits(self.registerInit, crcSize)
    
    def setReversed(self, value = True):
        self.reversed = value  

    def setValues(self, crcKey):
        self.setReversed( crcKey.rev )
        self.setXorOutValue( crcKey.xor )
        self.setRegisterInitValue( crcKey.init )
    
    ## 'poly' with leading '1'
    def calculate(self, data, poly):
        return self.calculate2(data, data.bit_length(), poly, poly.bit_length()-1)
    
    def calculate2(self, data, dataSize, poly, crcSize):
        dataMask = NumberMask(data, dataSize)
        polyMask = NumberMask(poly, crcSize)
        return self.calculate3(dataMask, polyMask)
        
    def calculate3(self, dataMask, polyMask):
        raise NotImplementedError
    