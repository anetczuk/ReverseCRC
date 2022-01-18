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

from crc.hwcrc import HwCRC
from crc.divisioncrc import DivisionCRC
from crc.crcproc import CRCKey
from revcrc.input import InputData
from revcrc.solver.bruteforcepairs import BruteForcePairsSolver


__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)


class BruteForcePairsSolverBaseTest(object):

    def test_bruteForceInput_poly(self):
        dataList = []
        dataSize = 16
        crcSize = 8
        inputPoly = 0x185
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

        dInput = InputData(dataList, dataSize, crcSize)
        foundCRC = self.crcFinder.bruteForcePairs(dInput, 0)

#         print "found data:", foundCRC
        self.assertIn( CRCKey(inputPoly, regInit, xorOut, 0, dataSize, rev=reverse ), foundCRC )

    def test_bruteForceInput_poly2(self):
        dataList = []
        dataSize = 80
        crcSize = 8
        inputPoly = 0x185
        regInit = 0x0
        xorOut = 0x0
        reverse = False

        ## init: 0, xor: 0, rev, poly: 0x18005
        self.crcProc.setReversed(reverse)
        self.crcProc.setXorOutValue(xorOut)
        self.crcProc.setRegisterInitValue(regInit)

        data1 = 0xAEA1B0094016BA9CC507
        crc1  = self.crcProc.calculate2(data1, dataSize, inputPoly, crcSize)
        dataList.append( (data1, crc1) )

        data2 = 0xBE4BA4F97059B3C61486
        crc2  = self.crcProc.calculate2(data2, dataSize, inputPoly, crcSize)
        dataList.append( (data2, crc2) )

        dInput = InputData(dataList, dataSize, crcSize)
        foundCRC = self.crcFinder.bruteForcePairs(dInput, 0)

#         print "found data:", foundCRC
        self.assertIn( CRCKey(inputPoly, regInit, xorOut, 0, dataSize, rev=reverse ), foundCRC )

    def test_bruteForceInput_xor(self):
        dataList = []
        dataSize = 16
        crcSize = 8
        inputPoly = 0x185
        regInit = 0x0
        xorOut = 0x0A
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

        dInput = InputData(dataList, dataSize, crcSize)
        foundCRC = self.crcFinder.bruteForcePairs(dInput, 0)

#         print "found data:", foundCRC
        self.assertIn( CRCKey( inputPoly, regInit, xorOut, 0, dataSize, rev=reverse ), foundCRC )

    def test_bruteForceInput_init(self):
        dataList = []
        dataSize = 16
        crcSize = 8
        inputPoly = 0x185
        regInit = 0x0A
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

        dInput = InputData(dataList, dataSize, crcSize)
        foundCRC = self.crcFinder.bruteForcePairs(dInput, 0)

#         print "found data:", foundCRC
        self.assertIn( CRCKey(inputPoly, regInit, xorOut, 0, dataSize, rev=reverse ), foundCRC )


## ===========================================================================


class HwCRC_BruteForcePairsSolver_Test(unittest.TestCase, BruteForcePairsSolverBaseTest):
    def setUp(self):
        # Called before testfunction is executed
        self.crcProc = HwCRC()
        self.crcFinder = BruteForcePairsSolver( HwCRC() )
    def tearDown(self):
        # Called after testfunction was executed
        pass


class DivisionCRC_BruteForcePairsSolver_Test(unittest.TestCase, BruteForcePairsSolverBaseTest):
    def setUp(self):
        # Called before testfunction is executed
        self.crcProc = DivisionCRC()
        self.crcFinder = BruteForcePairsSolver( DivisionCRC() )
    def tearDown(self):
        # Called after testfunction was executed
        pass


if __name__ == "__main__":
    unittest.main()
