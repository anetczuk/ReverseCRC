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
from crc.divisioncrc import DivisionCRC
from crc.divisioncrcbackward import DivisionCRCBackwardState,\
    DivisionCRCBackward
from crc.numbermask import NumberMask
from testcrc.test_crcproc import CRCBackwardTestParametrized



__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)



class DivisionCRCBackwardStateTest(unittest.TestCase):
    def setUp(self):
        # Called before testfunction is executed
        pass

    def tearDown(self):
        # Called after testfunction was executed
        pass

    def test_shift(self):
        crcSize = 8
        poly = NumberMask(0b100011101, crcSize)
        crc = 0x0F

        cb = DivisionCRCBackwardState(poly, crc)

        cb.shiftBit(True)
        self.assertEqual( cb.register, 0b10001001 )
        self.assertEqual( cb.dataMask.dataSize, 1 )
        self.assertEqual( cb.dataMask.dataNum, 0 )

        cb.shiftBit(True)
        self.assertEqual( cb.register, 0b11001010 )     ## 202
        self.assertEqual( cb.dataMask.dataSize, 2 )
        self.assertEqual( cb.dataMask.dataNum, 0 )

        cb.shiftBit(False)
        self.assertEqual( cb.register, 0b01100101 )
        self.assertEqual( cb.dataMask.dataSize, 3 )
        self.assertEqual( cb.dataMask.dataNum, 0 )

        cb.shiftBit(True)
        self.assertEqual( cb.register, 0b10111100 )
        self.assertEqual( cb.dataMask.dataSize, 4 )
        self.assertEqual( cb.dataMask.dataNum, 0 )

        cb.shiftBit(False)                              ## 6
        self.assertEqual( cb.register, 0b01011110 )
        self.assertEqual( cb.dataMask.dataSize, 5 )
        self.assertEqual( cb.dataMask.dataNum, 0 )

        cb.shiftBit(False)                              ## 6
        self.assertEqual( cb.register, 0b00101111 )
        self.assertEqual( cb.dataMask.dataSize, 6 )
        self.assertEqual( cb.dataMask.dataNum, 0 )

        cb.shiftBit(True)                               ## 5
        self.assertEqual( cb.register, 0b10011001 )
        self.assertEqual( cb.dataMask.dataSize, 7 )
        self.assertEqual( cb.dataMask.dataNum, 0 )

        cb.shiftBit(True)                               ## 4
        self.assertEqual( cb.register, 0b11000010 )
        self.assertEqual( cb.dataMask.dataSize, 8 )
        self.assertEqual( cb.dataMask.dataNum, 0 )

        for _ in range(0, 8):
            cb.shiftBit(False)

        self.assertEqual( cb.register, 0 )
        self.assertEqual( cb.dataMask.dataSize, 16 )
        self.assertEqual( cb.dataMask.dataNum, 0xC200 )


# # class DivisionCRCBackwardTest(unittest.TestCase, CRCBackwardTestParametrized):
# class DivisionCRCBackwardTest(unittest.TestCase):
#     def setUp(self):
#         # Called before testfunction is executed
#         pass
# 
#     def tearDown(self):
#         # Called after testfunction was executed
#         pass
# 
#     def test_round_cd8(self):
#         dataSize = 8
#         data = NumberMask(0xC2, dataSize)
#         crcSize = 8
#         inputPoly = NumberMask(0b100011101, crcSize)
#         crc = 0x0F
#         regInit = 0x0
#         xorOut = 0
# 
#         cb = DivisionCRCBackward( data, crc )
#         retList = cb.calculate(inputPoly, xorOut)
#         self.assertIn(DivisionCRCBackwardState(inputPoly, regInit, data), retList)
# 
#     def test_round_cd8_2(self):
#         dataSize = 8
#         data =  NumberMask(0xC2, dataSize)
#         crcSize = 8
#         inputPoly = NumberMask(0b100011101, crcSize)
#         regInit = 0x00
#         xorOut = 0x00
# 
#         crcProc = DivisionCRC()
#         crcProc.setRegisterInitValue(regInit)
#         crcProc.setXorOutValue(xorOut)
#         crc = crcProc.calculate3(data, inputPoly)
# 
#         cb = DivisionCRCBackward( data, crc )
#         retList = cb.calculate(inputPoly, xorOut)
#         self.assertIn(DivisionCRCBackwardState(inputPoly, 0x0, data), retList)
# 
#     def test_round_cd8_3(self):
#         dataSize = 8
#         data =  NumberMask(0xC6, dataSize)
#         crcSize = 8
#         inputPoly = NumberMask(0b100011101, crcSize)
#         regInit = 0x00
#         xorOut = 0x00
# 
#         crcProc = DivisionCRC()
#         crcProc.setRegisterInitValue(regInit)
#         crcProc.setXorOutValue(xorOut)
#         crc = crcProc.calculate3(data, inputPoly)
# 
#         cb = DivisionCRCBackward( data, crc )
#         retList = cb.calculate(inputPoly, xorOut)
#         self.assertIn(DivisionCRCBackwardState(inputPoly, 0x0, data), retList)
# 
#     def test_round_cd8_3rev(self):
#         dataSize = 8
#         data =  NumberMask(0xC6, dataSize)
#         crcSize = 8
#         inputPoly = NumberMask(0b100011101, crcSize)
#         regInit = 0x00
#         xorOut = 0x00
#         reverse = True
# 
#         crcProc = DivisionCRC()
#         crcProc.setReversed(reverse)
#         crcProc.setRegisterInitValue(regInit)
#         crcProc.setXorOutValue(xorOut)
#         crc = crcProc.calculate3(data, inputPoly)
# 
#         cb = DivisionCRCBackward( data, crc )
#         cb.setReversed(reverse)
#         retList = cb.calculate(inputPoly, xorOut)
#         self.assertIn(DivisionCRCBackwardState(inputPoly, 0x0, data), retList)
# 
#     def test_round_c8d9_rev(self):
#         dataSize = 9
#         data =  NumberMask(0x100, dataSize)
#         crcSize = 8
#         inputPoly = NumberMask(0b100011101, crcSize)
#         regInit = 0x00
#         xorOut = 0x00
#         reverse = True
# 
#         crcProc = DivisionCRC()
#         crcProc.setReversed(reverse)
#         crcProc.setRegisterInitValue(regInit)
#         crcProc.setXorOutValue(xorOut)
#         crc = crcProc.calculate3(data, inputPoly)
# 
#         cb = DivisionCRCBackward( data, crc )
#         cb.setReversed(reverse)
#         retList = cb.calculate(inputPoly, xorOut)
#         self.assertIn(DivisionCRCBackwardState(inputPoly, 0x0, data), retList)
# 
#     def test_round_c8d16(self):
#         dataSize = 16
#         data =  NumberMask(0x5AC6, dataSize)
#         crcSize = 8
#         inputPoly = NumberMask(0b100011101, crcSize)
#         regInit = 0x00
#         xorOut = 0x00
# 
#         crcProc = DivisionCRC()
#         crcProc.setRegisterInitValue(regInit)
#         crcProc.setXorOutValue(xorOut)
#         crc = crcProc.calculate3(data, inputPoly)
# 
#         cb = DivisionCRCBackward( data, crc )
#         retList = cb.calculate(inputPoly, xorOut)
#         self.assertIn(DivisionCRCBackwardState(inputPoly, 0x0, data), retList)
# 
#     def test_round_c8d16_rev(self):
#         dataSize = 16
#         data =  NumberMask(0x5AC6, dataSize)
#         crcSize = 8
#         inputPoly = NumberMask(0b100011101, crcSize)
#         regInit = 0x00
#         xorOut = 0x00
#         reverse = True
# 
#         crcProc = DivisionCRC()
#         crcProc.setReversed(reverse)
#         crcProc.setRegisterInitValue(regInit)
#         crcProc.setXorOutValue(xorOut)
#         crc = crcProc.calculate3(data, inputPoly)
# 
#         cb = DivisionCRCBackward( data, crc )
#         cb.setReversed(reverse)
#         retList = cb.calculate(inputPoly, xorOut)
#         self.assertIn(DivisionCRCBackwardState(inputPoly, 0x0, data), retList)
# 
#     def test_round_c8d8_init_random(self):
#         dataSize = 8
#         crcSize = 8
#         data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
#         crcMax = 2**crcSize-1
#         inputPoly = NumberMask(random.randint(1, crcMax), crcSize)
#         regInit = random.randint(1, crcMax)
#         xorOut = 0x0
#         reverse = random.randint(1, crcMax)
# 
#         crcFun = DivisionCRC()
#         crcFun.setReversed(reverse)
#         crcFun.setRegisterInitValue(regInit)
#         crcFun.setXorOutValue(xorOut)
#         crc = crcFun.calculate3(data, inputPoly)
# 
#         cb = DivisionCRCBackward( data, crc )
#         cb.setReversed(reverse)
#         retList = cb.calculate(inputPoly, xorOut)
#         self.assertIn(DivisionCRCBackwardState(inputPoly, regInit, data), retList)
# 
#     def test_round_xor_random(self):
#         dataPower = random.randint(1, 8)
#         dataSize = dataPower*8
#         data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
#         crcSize = random.randint(1, dataPower)*8
#         crcMax = 2**crcSize-1
#         inputPoly = NumberMask(random.randint(1, crcMax), crcSize)
# 
#         regInit = 0x0
#         xorOut = random.randint(1, crcMax)
#         reverse = random.randint(1, crcMax)
# 
#         crcFun = DivisionCRC()
#         crcFun.setReversed(reverse)
#         crcFun.setRegisterInitValue(regInit)
#         crcFun.setXorOutValue(xorOut)
#         crc = crcFun.calculate3(data, inputPoly)
# 
#         cb = DivisionCRCBackward( data, crc )
#         cb.setReversed(reverse)
#         retList = cb.calculate(inputPoly, xorOut)
#         self.assertIn(DivisionCRCBackwardState(inputPoly, regInit, data), retList)
# 
#     def test_round_init_random(self):
#         dataPower = random.randint(1, 8)
#         dataSize = dataPower*8
#         data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
#         crcSize = random.randint(1, dataPower)*8
#         crcMax = 2**crcSize-1
#         inputPoly = NumberMask(random.randint(1, crcMax), crcSize)
# 
#         regInit = random.randint(1, crcMax)
#         xorOut = 0x0
#         reverse = random.randint(1, crcMax)
# 
#         crcFun = DivisionCRC()
#         crcFun.setReversed(reverse)
#         crcFun.setRegisterInitValue(regInit)
#         crcFun.setXorOutValue(xorOut)
#         crc = crcFun.calculate3(data, inputPoly)
# 
#         cb = DivisionCRCBackward( data, crc )
#         cb.setReversed(reverse)
#         retList = cb.calculate(inputPoly, xorOut)
#         self.assertIn(DivisionCRCBackwardState(inputPoly, regInit, data), retList)
# 
#     def test_round_DCRC_init_random(self):
#         dataPower = random.randint(1, 8)
#         dataSize = dataPower*8
#         data = NumberMask(random.randint(1, 2**dataSize-1), dataSize)
#         crcSize = random.randint(1, dataPower)*8
#         crcMax = 2**crcSize-1
#         inputPoly = NumberMask(random.randint(1, crcMax), crcSize)
# 
#         regInit = random.randint(1, crcMax)
#         xorOut = 0x0
#         reverse = random.randint(1, crcMax)
# 
#         crcFun = DivisionCRC()
#         crcFun.setReversed(reverse)
#         crcFun.setRegisterInitValue(regInit)
#         crcFun.setXorOutValue(xorOut)
#         crc = crcFun.calculate3(data, inputPoly)
# 
#         cb = DivisionCRCBackward( data, crc )
#         cb.setReversed(reverse)
#         retList = cb.calculate(inputPoly, xorOut)
#         self.assertIn(DivisionCRCBackwardState(inputPoly, regInit, data), retList)


if __name__ == "__main__":
    unittest.main()
