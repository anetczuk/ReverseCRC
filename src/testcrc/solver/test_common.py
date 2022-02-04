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

from crc.numbermask import intToASCII
from crc.hwcrc import HwCRC, HwCRCProcessorFactory
from crc.divisioncrc import DivisionCRC, DivisionCRCProcessorFactory
from crc.crcproc import CRCKey
from crc.input import InputData
from crc.solver.common import CommonSolver


__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)


class CommonSolverBaseTest(object):

    def test_findCommon_c8d8_empty(self):
        dataList = []
        foundCRC = self.crcFinder.findCommon(dataList, 8, 8)
        self.assertEqual( len(foundCRC), 0 )

    def test_findCommon_c8d16_empty(self):
        dataList = []
        foundCRC = self.crcFinder.findCommon(dataList, 16, 16, 0)
        self.assertEqual( len(foundCRC), 0 )

    def test_findCommon_c8d16_one(self):
        dataList = [(2, 1)]
        foundCRC = self.crcFinder.findCommon(dataList, 16, 16, 0)
        self.assertEqual( len(foundCRC), 0 )

    def test_findCommon_c16d16(self):
        dataList = []
        crcSize = 16
        dataSize = 16
        inputPoly = 0x18005             ## 0x18005 = 98309
        regInit = 0x0
        xorOut = 0x0
        reverse = False

        ## init: 0, xor: 0, rev, poly: 0x18005
        self.crcProc.setReversed(reverse)
        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)

        data1 = 0xABCD
        crc1  = self.crcProc.calculate2(data1, dataSize, inputPoly, crcSize)
        dataList.append( (data1, crc1) )

        data2 = data1 ^ 0x0010
        crc2  = self.crcProc.calculate2(data2, dataSize, inputPoly, crcSize)
        dataList.append( (data2, crc2) )

        foundCRC = self.crcFinder.findCommon(dataList, dataSize, crcSize, 0)

#         print "found data:", foundCRC
        self.assertIn( CRCKey(inputPoly, regInit, 0, 0, dataSize, rev=reverse ), foundCRC )

    def test_findCommon_c16d16_prefix12(self):
        dataList = []
        crcSize = 16
        dataSize = 16
        inputPoly = 0x18005             ## 0x18005 = 98309
        regInit = 0x0
        xorOut = 0x0
        reverse = False

        preSize = 12
        preamble = (0xFFF << dataSize)

        ## init: 0, xor: 0, rev, poly: 0x18005
        self.crcProc.setReversed(reverse)
        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)

        data1 = 0xABCD
        crc1  = self.crcProc.calculate2(data1, dataSize, inputPoly, crcSize)
        dataList.append( (preamble | data1, crc1) )

        data2 = data1 ^ 0x0010
        crc2  = self.crcProc.calculate2(data2, dataSize, inputPoly, crcSize)
        dataList.append( (preamble | data2, crc2) )

        foundCRC = self.crcFinder.findCommon(dataList, preSize + dataSize, crcSize, 12)

#         print "found data:", foundCRC
        self.assertIn( CRCKey(inputPoly, regInit, 0, 0, dataSize, rev=reverse ), foundCRC )

    def test_findCommon_c16d16_rev(self):
        dataList = []
        crcSize = 16
        dataSize = 16
        inputPoly = 0x18005             ## 0x18005 = 98309
        regInit = 0x0
        xorOut = 0x0
        reverse = True

        ## init: 0, xor: 0, rev, poly: 0x18005
        self.crcProc.setReversed(reverse)
        self.crcProc.setRegisterInitValue(regInit)
        self.crcProc.setXorOutValue(xorOut)

        data1 = 0xABCD
        crc1  = self.crcProc.calculate2(data1, dataSize, inputPoly, crcSize)
        dataList.append( (data1, crc1) )

        data2 = data1 ^ 0x0010
        crc2  = self.crcProc.calculate2(data2, dataSize, inputPoly, crcSize)
        dataList.append( (data2, crc2) )

        foundCRC = self.crcFinder.findCommon(dataList, dataSize, crcSize, 0)

#         print "found data:", foundCRC
        self.assertIn( CRCKey(inputPoly, regInit, 0, 0, dataSize, rev=reverse ), foundCRC )

    def test_findCommonInput_crc8a(self):
        dataList = []

        crcFun = crcmod.predefined.mkCrcFun("crc-8")        ## init: 0x0, xor: 0x0, poly: 0x107

        data = 0xAB
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )

        foundCRC = self.crcFinder.findCommonInput( InputData(dataList, 8, 8) )
        foundCRC = list( foundCRC )

#         print "found:", foundCRC
        self.assertIn( CRCKey(0x107, 0x0, 0x0, 0, 8, rev=False), foundCRC )

    def test_findCommon_crc8b(self):
        dataList = []

        crcFun = crcmod.predefined.mkCrcFun("crc-8")        ## init: 0x0, xor: 0x0, poly: 0x107

        data = 0xABCD
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )

        foundCRC = self.crcFinder.findCommon(dataList, 16, 8)
        foundCRC = list( foundCRC )

#         print "found:", foundCRC
        self.assertIn( CRCKey(0x107, 0x0, 0x0, 0, 16, rev=False), foundCRC )

    def test_findCommon_crc8c(self):
        dataList = []

        crcFun = crcmod.predefined.mkCrcFun("crc-8")        ## init: 0x0, xor: 0x0, poly: 0x107

        data = 0xABCD
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )

        data = data ^ 0x0040
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )

        foundCRC = self.crcFinder.findCommon(dataList, 16, 8, 0)

        self.assertIn( CRCKey(0x107, 0x0, 0x0, 0, 16, rev=False ), foundCRC )

    def test_findCommon_crc16buypass_d32(self):
        dataList = []

        crcFun = crcmod.predefined.mkCrcFun("crc-16-buypass")       ## p:0x18005 r:False i:0x0000 x:0x0000

        data = 0xDCBA4321
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )

        data = data ^ 0x0010
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )

        foundCRC = self.crcFinder.findCommon(dataList, 32, 16)
        foundCRC = list( foundCRC )

#         print "found:", foundCRC
        self.assertIn( CRCKey(0x18005, 0x0, 0x0, 0, 32, rev=False), foundCRC )

    def test_findCommon_crc16_d32(self):
        dataList = []

        crcFun = crcmod.predefined.mkCrcFun("crc-16")       ## p:0x18005 r:True i:0x0000 x:0x0000

        data1 = 0x1234ABCD
        crc1  = crcFun( intToASCII(data1) )
        dataList.append( (data1, crc1) )

        data2 = data1 ^ 0x0010
        crc2  = crcFun( intToASCII(data2) )
        dataList.append( (data2, crc2) )

        foundCRC = self.crcFinder.findCommon(dataList, 32, 16)
        foundCRC = list( foundCRC )

#         print "found:", foundCRC
        self.assertIn( CRCKey(0x18005, 0x0, 0x0, 0, 32, rev=True), foundCRC )

    def test_findCommon_crc16_d32_subdata(self):
        dataList = []

        crcFun = crcmod.predefined.mkCrcFun("crc-16")       ## p:0x18005 r:True i:0x0000 x:0x0000

        data = 0x4B4D
        crc  = crcFun( intToASCII(data) )
        dataList.append( (0x42440000 | data, crc) )

        data = data ^ 0x0010
        crc  = crcFun( intToASCII(data) )
        dataList.append( (0x47440000 | data, crc) )

        foundCRC = self.crcFinder.findCommon(dataList, 32, 16, 16)
        foundCRC = list( foundCRC )

#         print "found:", foundCRC
        self.assertIn( CRCKey(0x18005, 0x0, 0x0, 0, 16, rev=True), foundCRC )

    def test_findCommon_crc16dnp(self):
        dataList = []

        crcFun = crcmod.predefined.mkCrcFun("crc-16-dnp")        ## poly: 0x13D65, rev, init: 0xFFFF, xor: 0xFFFF

        data = 0xABCD
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )

        data = data ^ 0x0010
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )

        foundCRC = self.crcFinder.findCommon(dataList, 16, 16)
        foundCRC = list( foundCRC )

#         print "found:", foundCRC
        self.assertIn( CRCKey(0x13D65, 0xFFFF, 0xFFFF, 0, 16, rev=True), foundCRC )


class HwCRC_CommonSolver_Test(unittest.TestCase, CommonSolverBaseTest):
    def setUp(self):
        # Called before testfunction is executed
        factory = HwCRCProcessorFactory()
        self.crcProc = factory.createForwardProcessor()
        self.crcFinder = CommonSolver()
        self.crcFinder.setProcessorFactory( factory )

    def tearDown(self):
        # Called after testfunction was executed
        pass


class DivisionCRC_CommonSolver_Test(unittest.TestCase, CommonSolverBaseTest):
    def setUp(self):
        # Called before testfunction is executed
        factory = DivisionCRCProcessorFactory()
        self.crcProc = factory.createForwardProcessor()
        self.crcFinder = CommonSolver()
        self.crcFinder.setProcessorFactory( factory )

    def tearDown(self):
        # Called after testfunction was executed
        pass


if __name__ == "__main__":
    unittest.main()
