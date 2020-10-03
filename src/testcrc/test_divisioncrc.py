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
from crc.hwcrc import HwCRC
from crc.divisioncrc import DivisionCRC
import random
import crcmod
from crc.numbermask import NumberMask, reverseBits

# import logging

 
 
__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)

        
        
class DivisionCRCTest(unittest.TestCase):
    def setUp(self):
        # Called before testfunction is executed
        pass
 
    def tearDown(self):
        # Called after testfunction was executed
        pass
      
    def test_calculateCRC_8_b(self):
        dataSize = 56
        inputPoly = 0x11D
        crcSize = 8
        regInit = 0x00
        xorOut  = 0x8F

        crc = DivisionCRC().calculateCRC( 0x0D00C0F0FFFFFF, dataSize, inputPoly, crcSize, init=regInit, xorout=xorOut )
        self.assertEqual( crc, 0x90 )
        
        crc = DivisionCRC().calculateCRC( 0x0000C0F0FFFFFF, dataSize, inputPoly, crcSize, init=regInit, xorout=xorOut )
        self.assertEqual( crc, 0x76 )
        
        crc = DivisionCRC().calculateCRC( 0x0E00C0F0FFFFFF, dataSize, inputPoly, crcSize, init=regInit, xorout=xorOut )
        self.assertEqual( crc, 0x77 )

    def test_calculate_1(self):
        crcProc = DivisionCRC()
        crc = crcProc.calculate2(0b1, 1, 0b1, 1)
        self.assertEqual( crc, 0b1 )
        
        crc = crcProc.calculate2(0b0, 1, 0b1, 1)
        self.assertEqual( crc, 0b0 )
        
        crc = crcProc.calculate2(0b10, 2, 0b1, 1)
        self.assertEqual( crc, 0b1 )
        
        crc = crcProc.calculate2(0b01, 2, 0b1, 1)
        self.assertEqual( crc, 0b1 )
        
    def test_calculate_1rev(self):
        crcProc = DivisionCRC()
        crcProc.setReversed()
        
        crc = crcProc.calculate2(0b1, 1, 0b1, 1)
        self.assertEqual( crc, 0b1 )
        
        crc = crcProc.calculate2(0b0, 1, 0b1, 1)
        self.assertEqual( crc, 0b0 )
        
        crc = crcProc.calculate2(0b10, 2, 0b1, 1)
        self.assertEqual( crc, 0b1 )
        
        crc = crcProc.calculate2(0b01, 2, 0b1, 1)
        self.assertEqual( crc, 0b1 )
        
    def test_calculate_2(self):
        crcProc = DivisionCRC()
        crc = crcProc.calculate2(0b00, 2, 0b11, 2)
        self.assertEqual( crc, 0b00 )
        
        crc = crcProc.calculate2(0b01, 2, 0b11, 2)
        self.assertEqual( crc, 0b11 )
        
        crc = crcProc.calculate2(0b10, 2, 0b11, 2)
        self.assertEqual( crc, 0b01 )
        
        crc = crcProc.calculate2(0b11, 2, 0b11, 2)
        self.assertEqual( crc, 0b10 )
        
    def test_calculate_2rev(self):
        crcProc = DivisionCRC()
        crcProc.setReversed()
        
        crc = crcProc.calculate2(0b00, 2, 0b11, 2)
        self.assertEqual( crc, 0b00 )
        
        crc = crcProc.calculate2(0b01, 2, 0b11, 2)
        self.assertEqual( crc, 0b10 )
        
        crc = crcProc.calculate2(0b10, 2, 0b11, 2)
        self.assertEqual( crc, 0b11 )
        
        crc = crcProc.calculate2(0b11, 2, 0b11, 2)
        self.assertEqual( crc, 0b01 )
    
    def test_calculate_2_repeated(self):    
        data = 0xABCD
        crcSize = 16
        dataSize = 16
        inputPoly = 0x18005             ## 0x18005 = 98309
        regInit = 0x0
        xorOut = 0x0
        reverse = True
        
        ## init: 0, xor: 0, rev, poly: 0x18005
        crcFun = DivisionCRC()
        crcFun.setReversed(reverse)
        crcFun.setRegisterInitValue(regInit)
        crcFun.setXorOutValue(xorOut)

        crc = crcFun.calculate2(data, dataSize, inputPoly, crcSize)
        
        for _ in xrange(0, 10):
            crc2 = crcFun.calculate2(data, dataSize, inputPoly, crcSize)
            self.assertEqual( crc, crc2 )
        
    def test_MSB_LSB(self):
        data = NumberMask(random.randint(1, 0xFF), 8)
        crcSize = 8
        crcMax = 2**crcSize-1
        inputPoly = NumberMask(random.randint(1, crcMax), crcSize)
        regInit = random.randint(0, crcMax)
        xorOut = random.randint(0, crcMax)
                
        crcProc = DivisionCRC()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        crc = crcProc.calculateMSB(data, inputPoly)
        
        revData = data.reversed()
        revPoly = inputPoly.reversed()
        revRegInit = reverseBits(regInit, crcSize)
        revXorOut = reverseBits(xorOut, crcSize)
        
        revCrcProc = DivisionCRC()
        revCrcProc.setReversed()
        revCrcProc.setRegisterInitValue( revRegInit )
        revCrcProc.setXorOutValue( revXorOut )
        crc2 = revCrcProc.calculateLSB(revData, revPoly)
        
        revCrc = reverseBits(crc2, crcSize)
        
#         print "values: data:{} poly:{:X} init:{:X} xorOut:{:08b} crc:{:08b} revcrc:{:08b}".format( data, inputPoly, regInit, xorOut, crc, revCrc )
        self.assertEqual( crc, revCrc )

    def test_CRC(self):
        data = NumberMask(0xBF, 8)
        inputPoly = NumberMask(0x130, 8)
        regInit = 0x0
        xorOut = 0x0
        reverse = True
 
        crcProc = HwCRC()
        crcProc.setReversed(reverse)
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )        
        crc  = crcProc.calculate3(data, inputPoly)
        
        dcrcProc = DivisionCRC()
        dcrcProc.setReversed(reverse)
        dcrcProc.setRegisterInitValue( regInit )
        dcrcProc.setXorOutValue( xorOut )
        dcrc = dcrcProc.calculate3(data, inputPoly)
          
#         crc_func = crcmod.mkCrcFun(inputPoly, rev=reverse, initCrc=regInit, xorOut=xorOut)
#         crcLib  = crc_func( data.toASCII() )          
#         print "crc: {:X} {:X} {:X} {:X}".format( dcrc, crc, crcLib, inputPoly )
        
        self.assertEqual( dcrc, crc )
        
    def test_CRC_random(self):
        data = NumberMask(random.randint(1, 0xFFFFFFFFFFFFFFFF), 64)
        crcSize = 8
        crcMax = 2**8-1
        inputPoly = NumberMask(0x100 | random.randint(1, crcMax), crcSize)
        regInit = random.randint(0, crcMax)
        xorOut = random.randint(0, crcMax)
        reverse = bool(random.randint(0, 1))
 
        crc_func = HwCRC()
        crc_func.setReversed(reverse)
        crc_func.setRegisterInitValue( regInit )
        crc_func.setXorOutValue( xorOut )
        crcLib  = crc_func.calculate3(data, inputPoly)
        
        crcProc = DivisionCRC()
        crcProc.setReversed(reverse)
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        crc = crcProc.calculate3(data, inputPoly)
          
#         print "values: {} poly:{:X} init:{:X} xorOut:{:08b} rev:{} crc:{:08b} crcmod:{:08b} crcxor:{:08b}".format( data, inputPoly, regInit, xorOut, reverse, crc, crcLib, crc^crcLib )
#         self.assertEqual( crc, crcLib, "Data: {} 0x{:X} 0x{:X} 0x{:X} {}".format(data, inputPoly, regInit, xorOut, reverse ) )
        self.assertEqual( crc, crcLib )

    def test_crcmod_c8d16_rev(self):
        data = NumberMask(0xE3F2, 16)
        inputPoly = NumberMask(0x1F0, 8)
        regInit = 0x0
        xorOut = 0x0
        reverse = True
 
        crc_func = crcmod.mkCrcFun(inputPoly.masterData(), rev=reverse, initCrc=regInit, xorOut=xorOut)
        crcLib  = crc_func( data.toASCII() )
#         print "crc: {:X} {:X}".format( crc, crc2 )
        
        crcProc = DivisionCRC()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )
        crcProc.setRegisterInitValue( regInit )
        
        data.reverseBytes()
        inputPoly.reverse()
        
        crc = crcProc.calculate3(data, inputPoly)
          
#         print "values: {} poly:{:X} init:{:X} xorOut:{:08b} rev:{} crc:{:08b} crcmod:{:08b} crcxor:{:08b}".format( data, inputPoly, regInit, xorOut, reverse, crc, crcLib, crc^crcLib )
        self.assertEqual( crc, crcLib )
        
    def test_crcmod_c8d16_revB(self):
        data = NumberMask(0xE3F2, 16)
        inputPoly = NumberMask(0x1F0, 8)
        regInit = 0x0
        xorOut = 0x0
        reverse = True
 
        revInputPoly = inputPoly.reversed()
        revData = data.reversedBytes()
 
        crc_func = crcmod.mkCrcFun(revInputPoly.masterData(), rev=reverse, initCrc=regInit, xorOut=xorOut)
        crcLib  = crc_func( revData.toASCII() )
#         print "crc: {:X} {:X}".format( crc, crc2 )
        
        crcProc = DivisionCRC()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )
        crcProc.setRegisterInitValue( regInit )
#         crcProc.setInitCRC( regInit )
        
        crc = crcProc.calculate3(data, inputPoly)
          
#         print "values: {} poly:{:X} init:{:X} xorOut:{:08b} rev:{} crc:{:08b} crcmod:{:08b} crcxor:{:08b}".format( data, inputPoly, regInit, xorOut, reverse, crc, crcLib, crc^crcLib )
        self.assertEqual( crc, crcLib )
        
    def test_crcmod_c8d64_zero(self):
        data = NumberMask(0x00, 8*random.randint(1, 8))
        crcSize = 8
        crcMax = 2**8-1
        inputPoly = NumberMask(0x100 | random.randint(1, crcMax), crcSize)
        reverse = bool(random.randint(0, 1))
        regInit = 0x0
        xorOut = 0x0
 
        crc_func = crcmod.mkCrcFun(inputPoly.masterData(), rev=reverse, initCrc=regInit, xorOut=xorOut)
        crcLib  = crc_func( data.toASCII() )
#         print "crc: {:X} {:X}".format( crc, crc2 )
        
        crcProc = DivisionCRC()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )
        crcProc.setInitCRC( regInit, crcSize )
        
        if reverse:
            data.reverseBytes()
        
        crc = crcProc.calculate3(data, inputPoly)
          
#         print "values: {} poly:{:X} init:{:X} xorOut:{:08b} rev:{} crc:{:08b} crcmod:{:08b} crcxor:{:08b}".format( data, inputPoly, regInit, xorOut, reverse, crc, crcLib, crc^crcLib )
        self.assertEqual( crc, crcLib )
        
    def test_crcmod_c8d64_random(self):
        data = NumberMask(random.randint(1, 0xFFFFFFFFFFFFFFFF), 64)
        crcSize = 8
        crcMax = 2**8-1
        inputPoly = NumberMask(0x100 | random.randint(1, crcMax), crcSize)
        ## 'regInit' and 'xorOut' are not incompatible
        regInit = 0x0
        xorOut = 0x0
        reverse = bool(random.randint(0, 1))
 
        crc_func = crcmod.mkCrcFun(inputPoly.masterData(), rev=reverse, initCrc=regInit, xorOut=xorOut)
        crcLib  = crc_func( data.toASCII() )
#         print "crc: {:X} {:X}".format( crc, crc2 )
        
        crcProc = DivisionCRC()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )
        crcProc.setRegisterInitValue( regInit )
#         crcProc.setInitCRC( regInit )
        
        if reverse:
            data.reverseBytes()
            inputPoly.reverse()
        
        crc = crcProc.calculate3(data, inputPoly)
          
#         print "values: {} poly:{:X} init:{:X} xorOut:{:08b} rev:{} crc:{:08b} crcmod:{:08b} crcxor:{:08b}".format( data, inputPoly, regInit, xorOut, reverse, crc, crcLib, crc^crcLib )
        self.assertEqual( crc, crcLib )
        
        
        
if __name__ == "__main__":
    unittest.main()
