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


__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)


class XorTest(unittest.TestCase):
    def setUp(self):
        # Called before testfunction is executed
        pass

    def tearDown(self):
        # Called after testfunction was executed
        pass

    def test_xor_8(self):
        crcFun = crcmod.predefined.mkCrcFun("crc-8")        ## poly=0x107 rev=False init:0x0 xor:0x0

        data1 = 0x4B4D
        crc1  = crcFun( intToASCII(data1) )

        data2 = data1 ^ 0x0010
        crc2  = crcFun( intToASCII(data2) )

        xdata = data1 ^ data2
        xcrc  = crcFun( intToASCII(xdata) )

        xorcrc = crc1 ^ crc2

#         print "xor: d1:{:X} {:X} d2:{:X} {:X} xor:{:X} {:X} {:X}".format( data1, crc1, data2, crc2, xdata, xcrc, xorcrc )
        self.assertEquals( xcrc, xorcrc )

    def test_xor_hwcrc16_random(self):
        dataSize = 24
        data1 = random.randint(1, 0xFFFFFF)
        data2 = random.randint(1, 0xFFFFFF)
        crcSize = 16
        inputPoly = 0x10000 | random.randint(1, 0xFFFF)
        regInit = random.randint(1, 0xFFFF)
        xorOut = random.randint(1, 0xFFFF)

        crcFun = HwCRC()
        crcFun.setReversed(False)
        crcFun.setXorOutValue(xorOut)
        crcFun.setRegisterInitValue(regInit)

        crc1 = crcFun.calculate2(data1, dataSize, inputPoly, crcSize)
        crc2 = crcFun.calculate2(data2, dataSize, inputPoly, crcSize)

        xdata = data1 ^ data2
        crcFunXor = HwCRC()
        crcFunXor.setReversed(False)
        xcrc = crcFunXor.calculate2(xdata, dataSize, inputPoly, crcSize)

        xorcrc = crc1 ^ crc2

#         print "xor: d1:{:X} {:X} d2:{:X} {:X} r:{:X} xo:{:X} xor:{:X} {:X} {:X}".format( data1, crc1, data2, crc2, regInit, xorOut, xdata, xcrc, xorcrc )
        self.assertEquals( xcrc, xorcrc )

    def test_xor_crcmod16_random(self):
        dataSize = 24
        data1 = random.randint(1, 0xFFFFFF)
        data2 = random.randint(1, 0xFFFFFF)
        inputPoly = 0x10000 | random.randint(1, 0xFFFF)
        regInit = random.randint(1, 0xFFFF)
        xorOut = random.randint(1, 0xFFFF)

        crcFun = crcmod.mkCrcFun(inputPoly, rev=False, initCrc=regInit, xorOut=xorOut)
        crc1  = crcFun( intToASCII(data1, dataSize) )
        crc2  = crcFun( intToASCII(data2, dataSize) )

        xdata = data1 ^ data2
        crcFunXor = crcmod.mkCrcFun(inputPoly, rev=False, initCrc=0x0, xorOut=0x0)
        xcrc  = crcFunXor( intToASCII(xdata, dataSize) )

        xorcrc = crc1 ^ crc2

        message = "poly:{:X} d1:{:X} c1:{:X} d2:{:X} c2:{:X} ri:{:X} xo:{:X} xor:{:X} {:X} != {:X}".format( inputPoly, data1, crc1, data2, crc2, regInit, xorOut, xdata, xcrc, xorcrc )
        self.assertEquals( xcrc, xorcrc, message )


if __name__ == "__main__":
    unittest.main()
