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


from crc.crcproc import CRCProc


##
##
class HwCRC(CRCProc):
    def __init__(self):
        CRCProc.__init__(self)
  
    def calculate3(self, dataMask, polyMask):
        if self.reversed == False:
            return self.calculateMSB(dataMask, polyMask)
        else:
            return self.calculateLSB(dataMask, polyMask)
        
    ## 'poly' without leading '1'
    def calculateMSB(self, dataMask, polyMask):         
        register = self.registerInit
 
        dataNum = dataMask.dataNum
        dataBit = (dataMask.masterBit >> 1)

        crcMSB = (polyMask.masterBit >> 1)
        crcMask = polyMask.masterBit-1
 
        ##for _ in range(0, dataMask.dataSize):
        while(dataBit > 0):
            if (dataNum & dataBit) > 0:
                register ^= crcMSB
            dataBit >>= 1
            register <<= 1
            if (register & polyMask.masterBit) > 0:
                register ^= polyMask.dataNum
                register &= crcMask
                  
        if self.xorOut != 0:
            register ^= self.xorOut
            
        return register

    ## 'poly' without leading '1'
    def calculateLSB(self, dataMask, polyMask):         
        register = self.registerInit
  
        dataNum = dataMask.dataNum
        dataBit = 1
  
        for _ in range(0, dataMask.dataSize):
            if (dataNum & dataBit) > 0:
                register ^= 1
            if (register & 1) > 0:
                register >>= 1
                register ^= polyMask.dataNum
            else:
                register >>= 1
            dataBit <<= 1
  
        if self.xorOut != 0:
            register ^= self.xorOut
          
        return register


    #TODO: remove method
    @staticmethod
    def reverseBits(num, size):
        b = '{:0{width}b}'.format(num, width=size)
        return int(b[::-1], 2)

    #TODO: remove method
    @staticmethod
    def calcCRC(data, poly):
        crcProc = HwCRC()
        return crcProc.calculate(data, poly)

