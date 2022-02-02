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

from crc.crcproc import PolyKey, CRCKey
from crc.numbermask import NumberMask
import random


class PolyKeyTest(unittest.TestCase):
    def setUp(self):
        # Called before testfunction is executed
        pass

    def tearDown(self):
        # Called after testfunction was executed
        pass

    def test_equality(self):
        key1 = PolyKey()
        self.assertEqual( key1, key1 )

        key2 = PolyKey()
        self.assertEqual( key1, key2 )

    def test_equality_diff(self):
        key1 = PolyKey()
        key2 = PolyKey(-1, rev=True)

        self.assertNotEqual( key1.revOrd, key2.revOrd )
        self.assertNotEqual( key1.refBits, key2.refBits )
        self.assertNotEqual( key1, key2 )


class CRCKeyTest(unittest.TestCase):
    def setUp(self):
        # Called before testfunction is executed
        pass

    def tearDown(self):
        # Called after testfunction was executed
        pass

    def test_size_0x00(self):
        key1 = CRCKey( 0x00 )
        crcsize = key1.size()
        self.assertEqual( crcsize, 0 )

    def test_size_0x01(self):
        key1 = CRCKey( 0x01 )
        crcsize = key1.size()
        self.assertEqual( crcsize, 0 )

    def test_size_0x123(self):
        key1 = CRCKey( 0x123 )
        crcsize = key1.size()
        self.assertEqual( crcsize, 8 )


## =============================================================



class CRCBackwardTestParametrized(object):
    def setUp(self):
        # Called before testfunction is executed
        pass

    def tearDown(self):
        # Called after testfunction was executed
        pass

    def test_calculateInitReg_check(self):
        dataSize = 8
        data = NumberMask(0xC2, dataSize)
        crcSize = 8
        inputPoly = NumberMask(0b100011101, crcSize)
        crc = 0x0F
        regInit = 0x0
        xorOut = 0x0

        retList = self.crcBackward.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_calculateInitReg_2(self):
        dataSize = 2
        data =  NumberMask(0x01, dataSize)
        crcSize = 2
        inputPoly = NumberMask(0b101, crcSize)
        regInit = 0x00
        xorOut = 0x00

        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)
        crc = self.crcProc.calculate3(data, inputPoly)

        retList = self.crcBackward.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_calculateInitReg_2rev(self):
        dataSize = 2
        data =  NumberMask(0x02, dataSize)
        crcSize = 2
        inputPoly = NumberMask(0b101, crcSize)
        regInit = 0x00
        xorOut = 0x00
        reverse = True

        self.crcProc.setReversed(reverse)
        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)
        crc = self.crcProc.calculate3(data, inputPoly)

        self.crcBackward.setReversed(reverse)
        retList = self.crcBackward.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_calculateInitReg_4rev(self):
        dataSize = 4
        data =  NumberMask(0x08, dataSize)
        crcSize = 4
        inputPoly = NumberMask(0x12, crcSize)
        regInit = 0x00
        xorOut = 0x00
        reverse = True

        self.crcProc.setReversed(reverse)
        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)
        crc = self.crcProc.calculate3(data, inputPoly)

        self.crcBackward.setReversed(reverse)
        retList = self.crcBackward.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_calculateInitReg_8_001(self):
        dataSize = 8
        data = NumberMask(0x01, dataSize)
        crcSize = 8
        inputPoly = NumberMask(0b100000001, crcSize)
        regInit = 0x01
        xorOut  = 0x00

        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)
        crc = self.crcProc.calculate3(data, inputPoly)

#         print "zzzz: 0x%X 0x%X 0x%X" % ( data.dataNum, inputPoly.dataNum, crc )

        retList = self.crcBackward.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_calculateInitReg_8_002(self):
        dataSize = 8
        data =  NumberMask(0xC6, dataSize)
        crcSize = 8
        inputPoly = NumberMask(0b100011101, crcSize)
        regInit = 0x00
        xorOut = 0x00

        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)
        crc = self.crcProc.calculate3(data, inputPoly)

        retList = self.crcBackward.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_calculateInitReg_round_c8d8_init_random(self):
        dataSize = 8
        crcSize = 8
        data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
        crcMax = 2**crcSize-1
        inputPoly = NumberMask(random.randint(1, crcMax), crcSize)
        regInit = random.randint(1, crcMax)
        xorOut = 0x0
        reverse = random.randint(1, crcMax)

        self.crcProc.setReversed(reverse)
        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)
        crc = self.crcProc.calculate3(data, inputPoly)

        self.crcBackward.setReversed(reverse)
        retList = self.crcBackward.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_calculateInitReg_round_xor_random(self):
        dataPower = random.randint(1, 8)
        dataSize = dataPower*8
        data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
        crcSize = random.randint(1, dataPower)*8
        crcMax = 2**crcSize-1
        inputPoly = NumberMask(random.randint(1, crcMax), crcSize)

        regInit = 0x0
        xorOut = random.randint(1, crcMax)
        reverse = random.randint(1, crcMax)

        self.crcProc.setReversed(reverse)
        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)
        crc = self.crcProc.calculate3(data, inputPoly)

        self.crcBackward.setReversed(reverse)
        retList = self.crcBackward.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList)

    def test_calculateInitRe_ground_init_random(self):
        dataPower = random.randint(1, 8)
        dataSize = dataPower*8
        data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
        crcSize = random.randint(1, dataPower)*8
        crcMax = 2**crcSize-1
        inputPoly = NumberMask(random.randint(1, crcMax), crcSize)

        regInit = random.randint(1, crcMax)
        xorOut = 0x0
        reverse = random.randint(1, crcMax)

        self.crcProc.setReversed(reverse)
        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)
        crc = self.crcProc.calculate3(data, inputPoly)

        self.crcBackward.setReversed(reverse)
        retList = self.crcBackward.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_calculateInitReg_round_DCRC_init_random(self):
        dataPower = random.randint(1, 8)
        dataSize = dataPower*8
        data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
        crcSize = random.randint(1, dataPower)*8
        crcMax = 2**crcSize-1
        inputPoly = NumberMask(random.randint(1, crcMax), crcSize)

        regInit = random.randint(1, crcMax)
        xorOut = 0x0
        reverse = random.randint(1, crcMax)

        self.crcProc.setReversed(reverse)
        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)
        crc = self.crcProc.calculate3(data, inputPoly)

        self.crcBackward.setReversed(reverse)
        retList = self.crcBackward.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList)

    def test_calculateInitReg_c16d16_random(self):
        dataSize = 16
        crcSize = 16
        data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
        crcMax = 2**crcSize-1
        inputPoly = NumberMask(random.randint(1, crcMax), crcSize)
        regInit = random.randint(1, crcMax)
        xorOut = 0x0

        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)
        crc = self.crcProc.calculate3(data, inputPoly)

        retList = self.crcBackward.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
