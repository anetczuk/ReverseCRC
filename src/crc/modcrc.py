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


from crc.hwcrc import HwCRC
from crc.numbermask import reverseBits


##
## Compatible with crcmod library
##
class ModCRC(HwCRC):
    def __init__(self, crcSize):
        HwCRC.__init__(self, crcSize)
        
    def setInitCRC(self, value):
        self.registerInit = value
        self.registerInit ^= self.xorOut
        if self.reversed == True:
            self.registerInit = reverseBits(self.registerInit, self.crcSize)
        
    def calculate3(self, dataMask, poly):
        if self.reversed == False:
            return self.calculateMSB(dataMask, poly)
        else:
            revData = dataMask.reversedBytes()
            revPoly = reverseBits(poly, self.crcSize)
            return self.calculateLSB(revData, revPoly)
#             return self.calculateLSB(dataMask, poly)