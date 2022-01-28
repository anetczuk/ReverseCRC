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
import crcmod
import random

from crc.numbermask import intToASCII
from crc.hwcrc import HwCRC
from crc.divisioncrc import DivisionCRC
from crc.crcproc import PolyKey
from crc.input import InputData
from crc.solver.polys import PolysSolver


__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)


class PolysSolverBaseTest(object):

    def test_findPolysXOR_c8d24_rev(self):
        data  = 0xFD50D7
        data2 = 0xFD53D7
        inputPoly = 0x1BF
        regInit = 0x0
        xorOut = 0x0
        crcSize = 8

        self.crcProc.setReversed()
        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)

        crc = self.crcProc.calculate(data, inputPoly)
        crc2 = self.crcProc.calculate(data2, inputPoly)
#         print "crc: {:X} {:X}".format( crc, crc2 )

        polyList = self.crcFinder.findPolysXOR( data, crc, data2, crc2, 24, crcSize)

#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( PolyKey(inputPoly, 0, 24, rev=True) in polyList )

    def test_findPolysXOR_8_1bit(self):
        polyList = self.crcFinder.findPolysXOR(0x34EC, 0b100, 0x34ED, 0b111, 16, 8)
        self.assertTrue( PolyKey(0x103, 0, 16, rev=False) in polyList )

        polyList = self.crcFinder.findPolysXOR(0x34EE, 0b010, 0x34EF, 0b001, 16, 8)
        self.assertTrue( PolyKey(0x103, 0, 16, rev=False) in polyList )

    def test_findPolysXOR_8_2bit(self):
        polyList = self.crcFinder.findPolysXOR(0xA53937C7, 0b01011001, 0xA53937CF, 0b10110001, 32, 8)
        self.assertTrue( PolyKey(0x11D, 0, 32, rev=False) in polyList )

        polyList = self.crcFinder.findPolysXOR(0x0000A53937CB, 0b11000101, 0x0000A53937CF, 0b10110001, 32, 8)
        self.assertTrue( PolyKey(0x11D, 0, 32, rev=False) in polyList )

        polyList = self.crcFinder.findPolysXOR(0x1234A53937CB, 0b11000101, 0x1234A53937CF, 0b10110001, 48, 8)
        self.assertTrue( PolyKey(0x11D, 0, 48, rev=False) in polyList )

        polyList = self.crcFinder.findPolysXOR(0xA53937CF, 0x8C, 0xA53937CE, 0x91, 32, 8)
        self.assertTrue( PolyKey(0x11D, 0, 32, rev=False) in polyList )

        polyList = self.crcFinder.findPolysXOR(0xA53937CF, 0x8C, 0xA53937C7, 0x64, 32, 8)
        self.assertTrue( PolyKey(0x11D, 0, 32, rev=False) in polyList )

    def test_findPolysXOR_8_3bit(self):
        polyList = self.crcFinder.findPolysXOR(0x1234, 0xF1, 0x1235, 0xF6, 16, 8)
        self.assertTrue( PolyKey(0x107, 0, 16, rev=False) in polyList )

    def test_findPolysXOR_leading(self):
        polyList = self.crcFinder.findPolysXOR(0x001234, 0xF1, 0x001235, 0xF6, 16, 8)
        self.assertTrue( PolyKey(0x107, 0, 16, rev=False) in polyList )

    def test_findPolysXOR_xorout(self):
        xorOut = 0xAB
        polyList = self.crcFinder.findPolysXOR(0x1234, 0xF1^xorOut, 0x1235, 0xF6^xorOut, 16, 8)
        self.assertTrue( PolyKey(0x107, 0, 16, rev=False) in polyList )

    def test_findPolysXOR_c8_init_xorOut(self):
        dataSize = 42                           ## data size does not matter
        inputPoly = 0x1D5
        inputVal =  0xA53937CF
        inputVal2 = inputVal ^ 0b100101000      ## data diff does not matter

        self.crcProc.setRegisterInitValue(0xA5)
        self.crcProc.setXorOutValue(0x7C)
        crc = self.crcProc.calculate2(inputVal, dataSize, inputPoly, 8)
        crc2 = self.crcProc.calculate2(inputVal2, dataSize, inputPoly, 8)

        poly = self.crcFinder.findPolysXOR(inputVal, crc, inputVal2, crc2, dataSize, 8)
        self.assertTrue( PolyKey(inputPoly, 0, dataSize, rev=False) in poly )

    def test_findPolysXOR_crcmod_8A(self):
        data =  0xF90AD50F
        data2 = 0xF90AD50D
        inputPoly = 0x10A
        regInit = 0x00
        xorOut = 0x00
        crcSize = 8

        crc_func = crcmod.mkCrcFun(inputPoly, rev=False, initCrc=regInit, xorOut=xorOut)
        crc  = crc_func( intToASCII(data) )
        crc2 = crc_func( intToASCII(data2) )
#         print "crc: {:X} {:X}".format( crc, crc2 )

        polyList = self.crcFinder.findPolysXOR(data, crc, data2, crc2, 32, crcSize)

#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( PolyKey(inputPoly, 0, 32, rev=False) in polyList )

    def test_findPolysXOR_crcmod_8Arev_d32(self):
        data  = 0xF90AD5FD
        data2 =  data | 0xF
        dataSize = 32
        inputPoly = 0x10A
        regInit = 0x00
        xorOut = 0x00
        crcSize = 8

        crc_func = crcmod.mkCrcFun(inputPoly, rev=True, initCrc=regInit, xorOut=xorOut)
        crc  = crc_func( intToASCII(data, dataSize) )
        crc2 = crc_func( intToASCII(data2, dataSize) )
#         print "crc: {:X} {:X}".format( crc, crc2 )
#         print "data: {:X}/{:X} {:X}/{:X}".format( data, revData1, data2, revData2 )

        polyList = self.crcFinder.findPolysXOR(data, crc, data2, crc2, dataSize, crcSize)

#         revPoly = reverse_number(inputPoly, crcSize)
#         print "polys: {:X}".format(inputPoly), "[{}]".format( ", ".join("(0x{:X} {})".format(pair[0], pair[1]) for pair in polyList) )
        self.assertIn( PolyKey(inputPoly, 0, dataSize, rev=True), polyList )

    def test_findPolysXOR_crcmod_8_random(self):
        data =  0xF90AD50D769553D3110A4535D37
        data2 = 0xF90AD50D769553D311024535537
#         inputPoly = 0x1B7
        inputPoly = 0x100 | int(random.random()*0xFF + 1)
        regInit = int(random.random()*0xFF + 1)
        xorOut = 0x0
        crcSize = 8

        crc_func = crcmod.mkCrcFun(inputPoly, rev=False, initCrc=regInit, xorOut=xorOut)
        crc  = crc_func( intToASCII(data) )
        crc2 = crc_func( intToASCII(data2) )
#         print "crc: {:X} {:X}".format( crc, crc2 )

        polyList = self.crcFinder.findPolysXOR(data, crc, data2, crc2, 108, crcSize)

#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( PolyKey(inputPoly, 0, 108, rev=False) in polyList )

    def test_findPolysXOR_crcmod_8_random2(self):
        data =  0xF90AD50D769553D31102453553F
        data2 = 0xF90AD50D769553D313624535537
#         inputPoly = 0x1B7
        inputPoly = 0x100 | int(random.random()*0xFF + 1)
        regInit = int(random.random()*0xFF + 1)
        xorOut = int(random.random()*0xFF + 1)
        crcSize = 8

        crc_func = crcmod.mkCrcFun(inputPoly, rev=False, initCrc=regInit, xorOut=xorOut)
        crc  = crc_func( intToASCII(data) )
        crc2 = crc_func( intToASCII(data2) )
#         print "crc: {:X} {:X}".format( crc, crc2 )

        polyList = self.crcFinder.findPolysXOR(data, crc, data2, crc2, 108, crcSize)

#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( PolyKey(inputPoly, 0, 108, rev=False) in polyList )

    def test_findPolysXOR_crcmod_8_random3(self):
        dataSize = 64
        data =  int(random.random()*0xFFFFFFFFFFFFFFFF + 1)
        data2 = int(random.random()*0xFFFFFFFFFFFFFFFF + 1)
#         inputPoly = 0x1B7
        inputPoly = 0x100 | int(random.random()*0xFF + 1)
        regInit = int(random.random()*0xFF + 1)
        xorOut = int(random.random()*0xFF + 1)
        crcSize = 8

        crc_func = crcmod.mkCrcFun(inputPoly, rev=False, initCrc=regInit, xorOut=xorOut)
        crc  = crc_func( intToASCII(data, dataSize) )
        crc2 = crc_func( intToASCII(data2, dataSize) )
#         print "crc: {:X} {:X}".format( crc, crc2 )

        polyList = self.crcFinder.findPolysXOR(data, crc, data2, crc2, dataSize, crcSize)

#         print "data: 0x{:X} 0x{:X} 0x{:X} 0x{:X} 0x{:X}".format( data, data2, inputPoly, regInit, xorOut )
#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( PolyKey(inputPoly, 0, dataSize, rev=False) in polyList )

    def test_findPolys_poly(self):
        dataList = []
        dataSize = 16
        crcSize = 16
        inputPoly = 0x18005
        regInit = 0x0
        xorOut = 0x0
        reverse = False

        ## init: 0, xor: 0, rev, poly: 0x18005
        self.crcProc.setReversed(reverse)
        self.crcProc.setXorOutValue(xorOut)
        self.crcProc.setRegisterInitValue(regInit)

        data1 = 0xABCD
        crc1  = self.crcProc.calculate2(data1, dataSize, inputPoly, crcSize)
        dataList.append( (data1, crc1) )

        data2 = data1 ^ 0x0010
        crc2  = self.crcProc.calculate2(data2, dataSize, inputPoly, crcSize)
        dataList.append( (data2, crc2) )

        inputData = InputData(dataList, dataSize, crcSize)
        foundCRC = self.crcFinder.findPolys(inputData, 0)

#         print "found data:", foundCRC
        self.assertIn( PolyKey(inputPoly, 0, dataSize, rev=reverse ), foundCRC )

    def test_findPolys(self):
        dataList = []
        dataList.append( ("71FB2EE1", "BE0D") )
        dataList.append( ("D5C0A73B", "D9B4") )

        inputData = InputData()
        inputData.convert( dataList )
        foundCRC = self.crcFinder.findPolys(inputData, 0)

#         print "found data:", foundCRC
        self.assertIn( PolyKey(0x18005, 0, 32, rev=False ), foundCRC )

    def test_findPolys_preamble(self):
        dataList = []
        dataList.append( ("CC71FB2EE1", "BE0D") )
        dataList.append( ("FFD5C0A73B", "D9B4") )

        inputData = InputData()
        inputData.convert( dataList )
        foundCRC = self.crcFinder.findPolys(inputData, 8)

#         print "found data:", foundCRC
        self.assertIn( PolyKey(0x18005, 0, 32, rev=False ), foundCRC )


class HwCRC_PolysSolver_Test(unittest.TestCase, PolysSolverBaseTest):
    def setUp(self):
        # Called before testfunction is executed
        self.crcProc = HwCRC()
        self.crcFinder = PolysSolver()
        self.crcFinder.setProcessor( HwCRC() )
    def tearDown(self):
        # Called after testfunction was executed
        pass


class DivisionCRC_PolysSolver_Test(unittest.TestCase, PolysSolverBaseTest):
    def setUp(self):
        # Called before testfunction is executed
        self.crcProc = DivisionCRC()
        self.crcFinder = PolysSolver()
        self.crcFinder.setProcessor( DivisionCRC() )
    def tearDown(self):
        # Called after testfunction was executed
        pass


if __name__ == "__main__":
    unittest.main()
