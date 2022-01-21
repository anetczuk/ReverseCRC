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
# import logging

import random
from crc.hwcrc import HwCRC
from revcrc.hwcrcbackward import HwCRCBackward
from crc.numbermask import NumberMask


# logging.basicConfig(level=logging.INFO)


class HwCRCBackwardTest(unittest.TestCase):
    def setUp(self):
        # Called before testfunction is executed
        pass

    def tearDown(self):
        # Called after testfunction was executed
        pass

    def test_calculate_check(self):
        dataSize = 8
        data = NumberMask(0xC2, dataSize)
        crcSize = 8
        inputPoly = NumberMask(0b100011101, crcSize)
        crc = 0x0F
        regInit = 0x0
        xorOut = 0x0

        cb = HwCRCBackward()
        retList = cb.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_calculate_2(self):
        dataSize = 2
        data =  NumberMask(0x01, dataSize)
        crcSize = 2
        inputPoly = NumberMask(0b101, crcSize)
        regInit = 0x00
        xorOut = 0x00

        crcProc = HwCRC()
        crcProc.setRegisterInitValue(regInit)
        crcProc.setXorOutValue(xorOut)
        crc = crcProc.calculate3(data, inputPoly)

        cb = HwCRCBackward()
        retList = cb.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_calculate_2rev(self):
        dataSize = 2
        data =  NumberMask(0x02, dataSize)
        crcSize = 2
        inputPoly = NumberMask(0b101, crcSize)
        regInit = 0x00
        xorOut = 0x00
        reverse = True

        crcProc = HwCRC()
        crcProc.setReversed(reverse)
        crcProc.setRegisterInitValue(regInit)
        crcProc.setXorOutValue(xorOut)
        crc = crcProc.calculate3(data, inputPoly)

        cb = HwCRCBackward()
        cb.setReversed(reverse)
        retList = cb.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_calculate_4rev(self):
        dataSize = 4
        data =  NumberMask(0x08, dataSize)
        crcSize = 4
        inputPoly = NumberMask(0x12, crcSize)
        regInit = 0x00
        xorOut = 0x00
        reverse = True

        crcProc = HwCRC()
        crcProc.setReversed(reverse)
        crcProc.setRegisterInitValue(regInit)
        crcProc.setXorOutValue(xorOut)
        crc = crcProc.calculate3(data, inputPoly)

        cb = HwCRCBackward()
        cb.setReversed(reverse)
        retList = cb.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_calculate_8_001(self):
        dataSize = 8
        data = NumberMask(0x01, dataSize)
        crcSize = 8
        inputPoly = NumberMask(0b100000001, crcSize)
        regInit = 0x01
        xorOut  = 0x00

        crcProc = HwCRC()
        crcProc.setRegisterInitValue(regInit)
        crcProc.setXorOutValue(xorOut)
        crc = crcProc.calculate3(data, inputPoly)

        cb = HwCRCBackward()

#         print "zzzz: 0x%X 0x%X 0x%X" % ( data.dataNum, inputPoly.dataNum, crc )

        retList = cb.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_calculate_8_002(self):
        dataSize = 8
        data =  NumberMask(0xC6, dataSize)
        crcSize = 8
        inputPoly = NumberMask(0b100011101, crcSize)
        regInit = 0x00
        xorOut = 0x00

        crcProc = HwCRC()
        crcProc.setRegisterInitValue(regInit)
        crcProc.setXorOutValue(xorOut)
        crc = crcProc.calculate3(data, inputPoly)

        cb = HwCRCBackward()
        retList = cb.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_round_c8d8_init_random(self):
        dataSize = 8
        crcSize = 8
        data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
        crcMax = 2**crcSize-1
        inputPoly = NumberMask(random.randint(1, crcMax), crcSize)
        regInit = random.randint(1, crcMax)
        xorOut = 0x0
        reverse = random.randint(1, crcMax)

        crcFun = HwCRC()
        crcFun.setReversed(reverse)
        crcFun.setRegisterInitValue(regInit)
        crcFun.setXorOutValue(xorOut)
        crc = crcFun.calculate3(data, inputPoly)

        cb = HwCRCBackward()
        cb.setReversed(reverse)
        retList = cb.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_round_xor_random(self):
        dataPower = random.randint(1, 8)
        dataSize = dataPower*8
        data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
        crcSize = random.randint(1, dataPower)*8
        crcMax = 2**crcSize-1
        inputPoly = NumberMask(random.randint(1, crcMax), crcSize)

        regInit = 0x0
        xorOut = random.randint(1, crcMax)
        reverse = random.randint(1, crcMax)

        crcFun = HwCRC()
        crcFun.setReversed(reverse)
        crcFun.setRegisterInitValue(regInit)
        crcFun.setXorOutValue(xorOut)
        crc = crcFun.calculate3(data, inputPoly)

        cb = HwCRCBackward()
        cb.setReversed(reverse)
        retList = cb.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList)

    def test_round_init_random(self):
        dataPower = random.randint(1, 8)
        dataSize = dataPower*8
        data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
        crcSize = random.randint(1, dataPower)*8
        crcMax = 2**crcSize-1
        inputPoly = NumberMask(random.randint(1, crcMax), crcSize)

        regInit = random.randint(1, crcMax)
        xorOut = 0x0
        reverse = random.randint(1, crcMax)

        crcFun = HwCRC()
        crcFun.setReversed(reverse)
        crcFun.setRegisterInitValue(regInit)
        crcFun.setXorOutValue(xorOut)
        crc = crcFun.calculate3(data, inputPoly)

        cb = HwCRCBackward()
        cb.setReversed(reverse)
        retList = cb.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )

    def test_round_DCRC_init_random(self):
        dataPower = random.randint(1, 8)
        dataSize = dataPower*8
        data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
        crcSize = random.randint(1, dataPower)*8
        crcMax = 2**crcSize-1
        inputPoly = NumberMask(random.randint(1, crcMax), crcSize)

        regInit = random.randint(1, crcMax)
        xorOut = 0x0
        reverse = random.randint(1, crcMax)

        crcFun = HwCRC()
        crcFun.setReversed(reverse)
        crcFun.setRegisterInitValue(regInit)
        crcFun.setXorOutValue(xorOut)
        crc = crcFun.calculate3(data, inputPoly)

        cb = HwCRCBackward()
        cb.setReversed(reverse)
        retList = cb.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList)

    def test_calc_c16d16_random(self):
        dataSize = 16
        crcSize = 16
        data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
        crcMax = 2**crcSize-1
        inputPoly = NumberMask(random.randint(1, crcMax), crcSize)
        regInit = random.randint(1, crcMax)
        xorOut = 0x0

        crcFun = HwCRC()
        crcFun.setRegisterInitValue(regInit)
        crcFun.setXorOutValue(xorOut)
        crc = crcFun.calculate3(data, inputPoly)

        cb = HwCRCBackward()
        retList = cb.calculateInitReg( data, crc, inputPoly, xorOut)
        self.assertIn( regInit, retList )


if __name__ == "__main__":
    unittest.main()
