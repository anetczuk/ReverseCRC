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


class DivisionCRC:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.registerInit = 0x0
        self.xorOut = 0x0
        self.reversed = False
    
#     def setCRCSize(self, crcSize):
#         self.crcSize = crcSize
#         self.masterBit = 0b1 << self.crcSize
#         self.crcMask = self.masterBit - 1
    
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
    
    ## 'poly' with leading '1'
    def calculate(self, data, poly):
        return self.calculate2(data, data.bit_length(), poly, poly.bit_length()-1)
    
    def calculate2(self, data, dataSize, poly, crcSize):
        dataMask = NumberMask(data, dataSize)
        polyMask = NumberMask(poly, crcSize)
        return self.calculate3(dataMask, polyMask)
  
    def calculate3(self, dataMask, polyMask):
        if self.reversed == False:
            return self.calculateMSB(dataMask, polyMask)
        else:
            return self.calculateLSB(dataMask, polyMask)
    
    ## old implementation is very helpful when defining backward algorithm
    ## 'poly' without leading '1'
    def calculateMSB(self, dataMask, polyMask):
        ## MSB first
        
        ## with leading '1' to xor out bit on shifting
        genPoly = polyMask.dataNum | polyMask.masterBit
        
        dataNum = dataMask.dataNum
  
        ## init shift register
        initShift = min(polyMask.dataSize, dataMask.dataSize)
        register = dataMask.getMSB(initShift) ^ self.registerInit
        dataBit = (dataMask.masterBit >> (initShift+1))
        ## old version
#         register = 0
#         dataBit = (dataMask.masterBit >> 1)
#         initShift = min(self.crcSize, dataMask.dataSize)
#         ### copy first 'initShift' from input
#         for _ in range(0, initShift):
#             register <<= 1
#             if (dataNum & dataBit) > 0:
#                 register |= 1
#             dataBit >>= 1
#         register ^= self.registerInit
          
        ## divide
        for _ in range(initShift, dataMask.dataSize):
            register <<= 1
            if (dataNum & dataBit) > 0:
                register |= 1
            if (register & polyMask.masterBit) > 0:
                register ^= genPoly
            dataBit >>= 1
              
#         if register == 0:
#             return register
#         if self.xorOut != 0:
#             register ^= self.xorOut
            
        ### shift crc zeros
        for _ in range(0, polyMask.dataSize):
            register <<= 1
            if (register & polyMask.masterBit) > 0:
                register ^= genPoly
                 
        if self.xorOut != 0:
            register ^= self.xorOut
            
        return register
    
    ## old implementation is very helpful when defining backward algorithm
    ## 'poly' without leading '1'
    def calculateLSB(self, dataMask, polyMask):
        ## LSB first
        
        dataNum = dataMask.dataNum
 
        ## init shift register
        initShift = min(polyMask.dataSize, dataMask.dataSize)
        register = dataMask.getLSB(initShift) ^ self.registerInit
        dataBit = (1 << initShift)
        ## old version
#         register = 0
#         dataBit = 1
#         msbPoly = (self.masterBit >> 1)
#         
#         initShift = min(self.crcSize, dataMask.dataSize)
#         for _ in range(0, initShift):
#             register >>= 1
#             if (dataNum & dataBit) > 0:
#                 register |= msbPoly
#             dataBit <<= 1
# #         register ^= reverseBits(self.registerInit, self.crcSize)
#         register ^= self.registerInit
         
        ## divide
        for _ in range(initShift, dataMask.dataSize):
            if (dataNum & dataBit) > 0:
                register |= polyMask.masterBit
            if (register & 1) > 0:
                register >>= 1
                register ^= polyMask.dataNum
            else:
                register >>= 1
            dataBit <<= 1

#         if register == 0:
#             return register
#         if self.xorOut != 0:
#             register ^= self.xorOut
             
        ### shift crc zeros
        for _ in range(0, polyMask.dataSize):
            if (register & 1) > 0:
                register >>= 1
                register ^= polyMask.dataNum
            else:
                register >>= 1

        if self.xorOut != 0:
            register ^= self.xorOut
            
        return register
    
    