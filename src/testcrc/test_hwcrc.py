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

from crc.hwcrc import HwCRC
import crcmod
import random
from crc.numbermask import NumberMask, reverseBits



__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)



class HwCRCTest(unittest.TestCase):
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
        proc = HwCRC()
        
        crc = proc.calculateCRC( 0x0D00C0F0FFFFFF, dataSize, inputPoly, crcSize, init=regInit, xorout=xorOut )
        self.assertEqual( crc, 0x90 )

        crc = proc.calculateCRC( 0x0000C0F0FFFFFF, dataSize, inputPoly, crcSize, init=regInit, xorout=xorOut )
        self.assertEqual( crc, 0x76 )

        crc = proc.calculateCRC( 0x0E00C0F0FFFFFF, dataSize, inputPoly, crcSize, init=regInit, xorout=xorOut )
        self.assertEqual( crc, 0x77 )

    def test_calculate_1(self):
        crcProc = HwCRC()
        crc = crcProc.calculate2(0b1, 1, 0b1, 1)
        self.assertEqual( crc, 0b1 )

        crc = crcProc.calculate2(0b0, 1, 0b1, 1)
        self.assertEqual( crc, 0b0 )

        crc = crcProc.calculate2(0b10, 2, 0b1, 1)
        self.assertEqual( crc, 0b1 )

        crc = crcProc.calculate2(0b01, 2, 0b1, 1)
        self.assertEqual( crc, 0b1 )

    def test_calculate_1rev(self):
        crcProc = HwCRC()
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
        crcProc = HwCRC()
        crc = crcProc.calculate2(0b00, 2, 0b11, 2)
        self.assertEqual( crc, 0b00 )

        crc = crcProc.calculate2(0b01, 2, 0b11, 2)
        self.assertEqual( crc, 0b11 )

        crc = crcProc.calculate2(0b10, 2, 0b11, 2)
        self.assertEqual( crc, 0b01 )

        crc = crcProc.calculate2(0b11, 2, 0b11, 2)
        self.assertEqual( crc, 0b10 )

    def test_calculate_2rev(self):
        crcProc = HwCRC()
        crcProc.setReversed()

        crc = crcProc.calculate2(0b00, 2, 0b11, 2)
        self.assertEqual( crc, 0b00 )

        crc = crcProc.calculate2(0b01, 2, 0b11, 2)
        self.assertEqual( crc, 0b10 )

        crc = crcProc.calculate2(0b10, 2, 0b11, 2)
        self.assertEqual( crc, 0b11 )

        crc = crcProc.calculate2(0b11, 2, 0b11, 2)
        self.assertEqual( crc, 0b01 )

    def test_calculate_3(self):
        ## taken from https://en.wikipedia.org/wiki/Cyclic_redundancy_check
        crcProc = HwCRC()
        crc = crcProc.calculate2(0b11010011101100, 16, 0b011, 3) ## 0x34EC 0xB
        self.assertEqual( crc, 0b100 )
        crc = crcProc.calculate2(0b11010011101101, 16, 0b011, 3) ## 0x34ED 0xB
        self.assertEqual( crc, 0b111 )
        crc = crcProc.calculate2(0b11010011101110, 16, 0b011, 3) ## 0x34EE 0xB
        self.assertEqual( crc, 0b010 )
        crc = crcProc.calculate2(0b11010011101111, 16, 0b011, 3) ## 0x34EF 0xB
        self.assertEqual( crc, 0b001 )

        crc = crcProc.calculate2(0b11010011101111, 16, 0b011, 3) ## 0x34EF 0xB
        self.assertEqual( crc, 0b001 )
        crc = crcProc.calculate2(0b11010111101111, 16, 0b011, 3) ## 0x35EF 0xB
        self.assertEqual( crc, 0b111 )
        crc = crcProc.calculate2(0b11011011101111, 16, 0b011, 3) ## 0x36EF 0xB
        self.assertEqual( crc, 0b110 )
        crc = crcProc.calculate2(0b11011111101111, 16, 0b011, 3) ## 0x37EF 0xB
        self.assertEqual( crc, 0b000 )

    def test_calculate_leading(self):
        crcProc = HwCRC()
        crc1 = crcProc.calculate(     0b11010011101100, 0b1011)
        crc2 = crcProc.calculate(0b0000011010011101100, 0b1011)
        self.assertEqual( crc1, crc2 )

    def test_calculate_8(self):
        ## taken from http://www.sunshine2k.de/articles/coding/crc/understanding_crc.html#ch3
        crcProc = HwCRC()
        crc = crcProc.calculate(0x112233, 0x107)
        self.assertEqual( crc, 0xD4 )

        crc = crcProc.calculate(0b11000010, 0b100011101)    ## 0xC2 0x11D
        self.assertEqual( crc, 0x0F )

        crc = crcProc.calculate(0xA53937C7, 0b100011101)    ## 0x011D
        self.assertEqual( crc, 0b01011001 )
        crc = crcProc.calculate(0xA53937CF, 0b100011101)    ## 0x011D
        self.assertEqual( crc, 0xB1 )
        crc = crcProc.calculate(0xA53937CB, 0b100011101)    ## 0x011D
        self.assertEqual( crc, 0b11000101 )
        crc = crcProc.calculate(0xA53937CE, 0b100011101)    ## 0x011D
        self.assertEqual( crc, 0b10101100 )                 ## 0xAC

    def test_calculate_8_regInit(self):
        crcProc = HwCRC()
        crcProc.setRegisterInitValue(0xA5)                  ## 0b10100101

        crc = crcProc.calculate(0xA53937CF, 0x11D)
        self.assertEqual( crc, 0x1D )

    def test_calculate_8_xorOut(self):
        crcProc = HwCRC()
        crcProc.setXorOutValue(0xA5)
        crc = crcProc.calculate(0xA53937CF, 0x11D)
        self.assertEqual( crc, 0x14 )
        self.assertEqual( crc ^ 0xA5, 0xB1 )

    def test_calculate2_8rev_check(self):
        ## input data generated from other tests
        crcProc = HwCRC()
        crcProc.setReversed()
        crc = crcProc.calculate2(0x000300, 24, 0x1BF, 8)
        self.assertEqual( crc, 80 )

    def test_calculate3_8rev(self):
        data = 0xF0
        dataSize = 8
        inputPoly = 0x107
        crcSize = 8
        regInit = 0x00
        xorOut = 0x00

        crcProc = HwCRC()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        crcProc.setReversed()
        crc = crcProc.calculate2(data, dataSize, inputPoly, crcSize)
        self.assertEqual( crc, 0 )

    def test_calculate3_8revB(self):
        data = 0xF0FF
        dataSize = 16
        inputPoly = 0x107
        crcSize = 8
        regInit = 0x00
        xorOut = 0x00

        crcProc = HwCRC()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        crcProc.setReversed()
        crc = crcProc.calculate2(data, dataSize, inputPoly, crcSize)
        self.assertEqual( crc, 0 )

    def test_calculate3_8rev_init_xor(self):
        data = 0xF0
        dataSize = 8
        inputPoly = 0x107
        crcSize = 8
        regInit = 0x0F
        xorOut = 0xF0

        crcProc = HwCRC()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        crcProc.setReversed()
        crc = crcProc.calculate2(data, dataSize, inputPoly, crcSize)
        self.assertEqual( crc, 240 )

    def test_MSB_LSB(self):
        data = NumberMask(random.randint(1, 0xFF), 8)
        crcSize = 8
        crcMax = 2**crcSize-1
        inputPoly = NumberMask(random.randint(1, crcMax), crcSize)
        regInit = random.randint(0, crcMax)
        xorOut = random.randint(0, crcMax)

        crcProc = HwCRC()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        crc = crcProc.calculateMSB(data, inputPoly)

        revData = data.reversed()
        revPoly = inputPoly.reversed()
        revRegInit = reverseBits(regInit, crcSize)
        revXorOut = reverseBits(xorOut, crcSize)

        revCrcProc = HwCRC()
        revCrcProc.setReversed()
        revCrcProc.setRegisterInitValue( revRegInit )
        revCrcProc.setXorOutValue( revXorOut )
        crc2 = revCrcProc.calculateLSB(revData, revPoly)

        revCrc = reverseBits(crc2, crcSize)

#         print "values: data:{} poly:{:X} init:{:X} xorOut:{:08b} crc:{:08b} revcrc:{:08b}".format( data, inputPoly, regInit, xorOut, crc, revCrc )
        self.assertEqual( crc, revCrc )

    def test_calculate3_001(self):
        data = NumberMask(0x0001, 16)
        crcSize = 16
        inputPoly = NumberMask(0x10001, crcSize)
        regInit = 0x0
        xorOut  = 0x0
        reverse = False

        crcProc = HwCRC()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )
        crcProc.setInitCRC(regInit, crcSize)

        crc = crcProc.calculate3(data, inputPoly)

#         print "values: {} poly:{:X} init:{:X} xorOut:{:08b} rev:{} crc:{:08b} crcmod:{:08b} crcxor:{:08b}".format( data, inputPoly, regInit, xorOut, reverse, crc, crcLib, crc^crcLib )
        self.assertEqual( crc, 0x0001 )

    def test_calculate3_002(self):
        data = NumberMask(0x0010, 16)
        crcSize = 16
        inputPoly = NumberMask(0x10001, crcSize)
        regInit = 0x0
        xorOut  = 0x0
        reverse = False

        crcProc = HwCRC()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )
        crcProc.setInitCRC(regInit, crcSize)

        crc = crcProc.calculate3(data, inputPoly)

#         print "values: {} poly:{:X} init:{:X} xorOut:{:08b} rev:{} crc:{:08b} crcmod:{:08b} crcxor:{:08b}".format( data, inputPoly, regInit, xorOut, reverse, crc, crcLib, crc^crcLib )
        self.assertEqual( crc, 0x0010 )

    def test_calculate3_003(self):
        data = NumberMask(0x0100, 16)
        crcSize = 16
        inputPoly = NumberMask(0x10001, crcSize)
        regInit = 0x0
        xorOut  = 0x0
        reverse = False

        crcProc = HwCRC()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )
        crcProc.setInitCRC(regInit, crcSize)

        crc = crcProc.calculate3(data, inputPoly)

#         print "values: {} poly:{:X} init:{:X} xorOut:{:08b} rev:{} crc:{:08b} crcmod:{:08b} crcxor:{:08b}".format( data, inputPoly, regInit, xorOut, reverse, crc, crcLib, crc^crcLib )
        self.assertEqual( crc, 0x0100 )

    def test_calculate3_004(self):
        data = NumberMask(0x1000, 16)
        crcSize = 16
        inputPoly = NumberMask(0x10001, crcSize)
        regInit = 0x0
        xorOut  = 0x0
        reverse = False

        crcProc = HwCRC()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )
        crcProc.setInitCRC(regInit, crcSize)

        crc = crcProc.calculate3(data, inputPoly)

#         print "values: {} poly:{:X} init:{:X} xorOut:{:08b} rev:{} crc:{:08b} crcmod:{:08b} crcxor:{:08b}".format( data, inputPoly, regInit, xorOut, reverse, crc, crcLib, crc^crcLib )
        self.assertEqual( crc, 0x1000 )

    def test_calculate3_c16_d80(self):
        data = NumberMask(0x8E843664A9CB222CE7EC, 80)
        crcSize = 16
        inputPoly = NumberMask(0x1ABCD, crcSize)
        regInit = 0x0
        xorOut  = 0x0
        reverse = False

#         masterPoly = inputPoly.masterData()
#         crc_func = crcmod.mkCrcFun(masterPoly, rev=reverse, initCrc=regInit, xorOut=xorOut)
#         crcLib  = crc_func( data.toASCII() )
# #         print "crc: {:X}".format( crcLib )

        crcProc = HwCRC()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )
        crcProc.setInitCRC(regInit, crcSize)

        crc = crcProc.calculate3(data, inputPoly)

#         print "values: {} poly:{:X} init:{:X} xorOut:{:08b} rev:{} crc:{:08b} crcmod:{:08b} crcxor:{:08b}".format( data, inputPoly, regInit, xorOut, reverse, crc, crcLib, crc^crcLib )
#         self.assertEqual( crc, crcLib )
        self.assertEqual( crc, 0xD36F )

    def test_crcmod_c8d64_random(self):
        data = NumberMask(random.randint(1, 0xFFFFFFFFFFFFFFFF), 64)
        crcSize = 8
        crcMax = 2**crcSize-1
        inputPoly = NumberMask((0x1 << crcSize) | random.randint(1, crcMax), crcSize)
#         regInit = random.randint(0, crcMax)
#         xorOut = random.randint(0, crcMax)
        regInit = 0x0
        xorOut = 0x0
        reverse = bool(random.randint(0, 1))

        crc_func = crcmod.mkCrcFun(inputPoly.masterData(), rev=reverse, initCrc=regInit, xorOut=xorOut)
        crcLib  = crc_func( data.toASCII() )
#         print "crc: {:X} {:X}".format( crc, crc2 )

        crcProc = HwCRC()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )

        if reverse:
            data.reverseBytes()
            inputPoly.reverse()
            crcInit = reverseBits(regInit^xorOut, crcSize)
            crcProc.setRegisterInitValue( crcInit )
        else:
            crcInit = regInit^xorOut
            crcProc.setRegisterInitValue( crcInit )

        crc = crcProc.calculate3(data, inputPoly)

#         print "values: {} poly:{:X} init:{:X} xorOut:{:08b} rev:{} crc:{:08b} crcmod:{:08b} crcxor:{:08b}".format( data, inputPoly, regInit, xorOut, reverse, crc, crcLib, crc^crcLib )
        self.assertEqual( crc, crcLib )


    def test_crcmod_c16d64_random(self):
        data = NumberMask(random.randint(1, 0xFFFFFFFFFFFFFFFF), 64)
        crcSize = 16
        crcMax = 2**crcSize-1
        inputPoly = NumberMask((0x1 << crcSize) | random.randint(1, crcMax), crcSize)
#         regInit = random.randint(0, crcMax)
#         xorOut = random.randint(0, crcMax)
        regInit = 0x0
        xorOut  = 0x0
        reverse = bool(random.randint(0, 1))

        crc_func = crcmod.mkCrcFun(inputPoly.masterData(), rev=reverse, initCrc=regInit, xorOut=xorOut)
        crcLib  = crc_func( data.toASCII() )
#         print "crc: {:X} {:X}".format( crc, crc2 )

        crcProc = HwCRC()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )

        if reverse:
            data.reverseBytes()
            inputPoly.reverse()
            crcInit = reverseBits(regInit^xorOut, crcSize)
            crcProc.setRegisterInitValue( crcInit )
        else:
            crcInit = regInit^xorOut
            crcProc.setRegisterInitValue( crcInit )

        crc = crcProc.calculate3(data, inputPoly)

#         print "values: {} poly:{:X} init:{:X} xorOut:{:08b} rev:{} crc:{:08b} crcmod:{:08b} crcxor:{:08b}".format( data, inputPoly, regInit, xorOut, reverse, crc, crcLib, crc^crcLib )
        self.assertEqual( crc, crcLib )


if __name__ == "__main__":
    unittest.main()
