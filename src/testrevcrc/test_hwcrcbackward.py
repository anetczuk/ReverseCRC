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
 
 
import unittest
import os
# import logging
 
import random
from crc.hwcrc import HwCRC
from revcrc.hwcrcbackward import HwCRCBackward, HwCRCBackwardState
from crc.numbermask import NumberMask
  
  
__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)
 
 
  
class HwCRCBackwardTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
  
    def tearDown(self):
        # Called after the last testfunction was executed
        pass
 
    def test_calculate_check(self):
        data = 0xC2
        dataSize = 8
        inputPoly = 0b100011101
        crc = 0x0F
        crcSize = 8
        regInit = 0x0
        xorOut = 0x0
         
        cb = HwCRCBackward( NumberMask(data, dataSize), crc, crcSize, inputPoly, xorOut )
        retList = cb.calculate()
        self.assertIn( HwCRCBackwardState(crcSize, inputPoly, regInit), retList )
   
    def test_calculate_2(self):
        data =  0x01
        dataSize = 2
        inputPoly = 0b101
        crcSize = 2
        regInit = 0x00
        xorOut = 0x00
          
        crcProc = HwCRC(crcSize)
        crcProc.setRegisterInitValue(regInit)
        crcProc.setXorOutValue(xorOut)
        crc = crcProc.calculate2(data, dataSize, inputPoly)
          
        cb = HwCRCBackward( NumberMask(data, dataSize), crc, crcSize, inputPoly, xorOut )
        retList = cb.calculate()
        self.assertIn( HwCRCBackwardState(crcSize, inputPoly, regInit), retList )
        
    def test_calculate_2rev(self):
        data =  0x02
        dataSize = 2
        inputPoly = 0b101
        crcSize = 2
        regInit = 0x00
        xorOut = 0x00
        reverse = True
          
        crcProc = HwCRC(crcSize)
        crcProc.setReversed(reverse)
        crcProc.setRegisterInitValue(regInit)
        crcProc.setXorOutValue(xorOut)
        crc = crcProc.calculate2(data, dataSize, inputPoly)
          
        cb = HwCRCBackward( NumberMask(data, dataSize), crc, crcSize, inputPoly, xorOut )
        cb.setReversed(reverse)
        retList = cb.calculate()
        self.assertIn( HwCRCBackwardState(crcSize, inputPoly, regInit), retList )
         
    def test_calculate_3(self):
        data =  0xC6
        dataSize = 8
        inputPoly = 0b100011101
        regInit = 0x00
        xorOut = 0x00
        crcSize = 8
          
        crcProc = HwCRC(crcSize)
        crcProc.setRegisterInitValue(regInit)
        crcProc.setXorOutValue(xorOut)
        crc = crcProc.calculate2(data, dataSize, inputPoly)
          
        cb = HwCRCBackward( NumberMask(data, dataSize), crc, crcSize, inputPoly, xorOut )
        retList = cb.calculate()
        self.assertIn( HwCRCBackwardState(crcSize, inputPoly, regInit), retList )
        
    def test_calculate_4rev(self):
        data =  0x08
        dataSize = 4
        inputPoly = 0x12
        regInit = 0x00
        xorOut = 0x00
        crcSize = 4
        reverse = True
          
        crcProc = HwCRC(crcSize)
        crcProc.setReversed(reverse)
        crcProc.setRegisterInitValue(regInit)
        crcProc.setXorOutValue(xorOut)
        crc = crcProc.calculate2(data, dataSize, inputPoly)
          
        cb = HwCRCBackward( NumberMask(data, dataSize), crc, crcSize, inputPoly, xorOut )
        cb.setReversed(reverse)
        retList = cb.calculate()
        self.assertIn( HwCRCBackwardState(crcSize, inputPoly, regInit), retList )
         
    def test_round_c8d8_init_random(self):
        dataSize = 8
        crcSize = 8
        data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
        crcMax = 2**crcSize-1
        inputPoly = random.randint(1, crcMax)
        regInit = random.randint(1, crcMax)
        xorOut = 0x0
        reverse = random.randint(1, crcMax)
 
        crcFun = HwCRC(crcSize)
        crcFun.setReversed(reverse)
        crcFun.setRegisterInitValue(regInit)
        crcFun.setXorOutValue(xorOut)
        crc = crcFun.calculate3(data, inputPoly)
          
        cb = HwCRCBackward( data, crc, crcSize, inputPoly, xorOut )
        cb.setReversed(reverse)
        retList = cb.calculate()
        self.assertIn( HwCRCBackwardState(crcSize, inputPoly, regInit), retList )
        
    def test_round_xor_random(self):
        dataPower = random.randint(1, 8)
        dataSize = dataPower*8
        data = random.randint(1, 2**dataSize-1)
        crcSize = random.randint(1, dataPower)*8
        crcMax = 2**crcSize-1
        inputPoly = random.randint(1, crcMax)
        
        regInit = 0x0
        xorOut = random.randint(1, crcMax)
        reverse = random.randint(1, crcMax)
 
        crcFun = HwCRC(crcSize)
        crcFun.setReversed(reverse)
        crcFun.setRegisterInitValue(regInit)
        crcFun.setXorOutValue(xorOut)
        crc = crcFun.calculate2(data, dataSize, inputPoly)
          
        cb = HwCRCBackward( NumberMask(data, dataSize), crc, crcSize, inputPoly, xorOut )
        cb.setReversed(reverse)
        retList = cb.calculate()
        self.assertIn( HwCRCBackwardState(crcSize, inputPoly, regInit), retList)

    def test_round_init_random(self):
        dataPower = random.randint(1, 8)
        dataSize = dataPower*8
        data = random.randint(1, 2**dataSize-1)
        crcSize = random.randint(1, dataPower)*8
        crcMax = 2**crcSize-1
        inputPoly = random.randint(1, crcMax)
        
        regInit = random.randint(1, crcMax)
        xorOut = 0x0
        reverse = random.randint(1, crcMax)
 
        crcFun = HwCRC(crcSize)
        crcFun.setReversed(reverse)
        crcFun.setRegisterInitValue(regInit)
        crcFun.setXorOutValue(xorOut)
        crc = crcFun.calculate2(data, dataSize, inputPoly)
          
        cb = HwCRCBackward( NumberMask(data, dataSize), crc, crcSize, inputPoly, xorOut )
        cb.setReversed(reverse)
        retList = cb.calculate()
        self.assertIn( HwCRCBackwardState(crcSize, inputPoly, regInit), retList )
        
    def test_round_DCRC_init_random(self):
        dataPower = random.randint(1, 8)
        dataSize = dataPower*8
        data = random.randint(1, 2**dataSize-1)
        crcSize = random.randint(1, dataPower)*8
        crcMax = 2**crcSize-1
        inputPoly = random.randint(1, crcMax)
        
        regInit = random.randint(1, crcMax)
        xorOut = 0x0
        reverse = random.randint(1, crcMax)
 
        crcFun = HwCRC(crcSize)
        crcFun.setReversed(reverse)
        crcFun.setRegisterInitValue(regInit)
        crcFun.setXorOutValue(xorOut)
        crc = crcFun.calculate2(data, dataSize, inputPoly)
          
        cb = HwCRCBackward( NumberMask(data, dataSize), crc, crcSize, inputPoly, xorOut )
        cb.setReversed(reverse)
        retList = cb.calculate()
        self.assertIn( HwCRCBackwardState(crcSize, inputPoly, regInit), retList)

 
 
if __name__ == "__main__":
    unittest.main()
