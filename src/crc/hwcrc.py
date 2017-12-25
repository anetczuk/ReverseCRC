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


##
##
class HwCRC:
    def __init__(self, crcSize):
        self.setCRCSize(crcSize)
        self.reset()
    
    def reset(self):
        self.registerInit = 0x0
        self.xorOut = 0x0
        self.reversed = False
    
    def setCRCSize(self, crcSize):
        self.crcSize = crcSize
        self.masterBit = 0b1 << self.crcSize
        self.crcMask = self.masterBit - 1
    
    def setRegisterInitValue(self, value):
        self.registerInit = value
        
    def setXorOutValue(self, value):
        self.xorOut = value
    
    def setReversed(self, value = True):
        self.reversed = value
        
    def calculate(self, data, poly):
        return self.calculate2(data, data.bit_length(), poly)
    
    def calculate2(self, data, dataSize, poly):
        dataMask = NumberMask(data, dataSize)
        return self.calculate3(dataMask, poly)
  
    def calculate3(self, dataMask, poly):
        if self.reversed == False:
            return self.calculateMSB(dataMask, poly)
        else:
#             revPoly = reverseBits(poly, self.crcSize)
#             return self.calculateLSB(dataMask, revPoly)
            return self.calculateLSB(dataMask, poly)
        
    ## 'poly' without leading '1'
    def calculateMSB(self, dataMask, poly):         
        register = self.registerInit
 
        dataNum = dataMask.dataNum
        dataBit = (dataMask.msbMask >> 1)

        crcMSB = (self.masterBit >> 1)
        genPoly = poly & self.crcMask
 
        ##for _ in range(0, dataMask.dataSize):
        while(dataBit > 0):
            if (dataNum & dataBit) > 0:
                register ^= crcMSB
            dataBit >>= 1
            register <<= 1
            if (register & self.masterBit) > 0:
                register ^= genPoly
                register &= self.crcMask
                  
        if self.xorOut != 0:
            register ^= self.xorOut
            
        return register

    ## 'poly' without leading '1'
    def calculateLSB(self, dataMask, poly):         
        register = self.registerInit
  
        genPoly = poly & self.crcMask
  
        dataNum = dataMask.dataNum
        dataBit = 1
  
        for _ in range(0, dataMask.dataSize):
            if (dataNum & dataBit) > 0:
                register ^= 1
            if (register & 1) > 0:
                register >>= 1
                register ^= genPoly
            else:
                register >>= 1
            dataBit <<= 1
  
        if self.xorOut != 0:
            register ^= self.xorOut
          
        return register


    @staticmethod
    def reverseBits(num, size):
        b = '{:0{width}b}'.format(num, width=size)
        return int(b[::-1], 2)

    @staticmethod
    def calcCRC(data, poly):
        crcProc = HwCRC(poly.bit_length())
        return crcProc.calculate(data, poly)

