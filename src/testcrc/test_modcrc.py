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
from crc.modcrc import ModCRC
import crcmod
import random
from crc.numbermask import intToASCII, NumberMask



__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)



class ModCRCTest(unittest.TestCase):

    def setUp(self):
        # Called before testfunction is executed
        pass

    def tearDown(self):
        # Called after testfunction was executed
        pass

    def test_calculateCRC_8_a(self):
        ## http://www.sunshine2k.de/coding/javascript/crc/crc_js.html
        dataSize = 4*8
        inputPoly = 0x1D
        crcSize = 8

        crc = ModCRC().calculateCRC( 0x31323334, dataSize, inputPoly, crcSize, reverse=False )
        self.assertEqual( crc, 0xF2 )

        crc = ModCRC().calculateCRC( 0x31323334, dataSize, inputPoly, crcSize, reverse=True )
        self.assertEqual( crc, 0x43 )

    def test_calculateCRC_8_b(self):
        dataSize = 56
        inputPoly = 0x11D
        crcSize = 8
        regInit = 0x00
        xorOut  = 0x8F

        crc = ModCRC().calculateCRC( 0x0D00C0F0FFFFFF, dataSize, inputPoly, crcSize, init=regInit, xorout=xorOut )
        self.assertEqual( crc, 0x90 )

        crc = ModCRC().calculateCRC( 0x0000C0F0FFFFFF, dataSize, inputPoly, crcSize, init=regInit, xorout=xorOut )
        self.assertEqual( crc, 0x76 )

        crc = ModCRC().calculateCRC( 0x0E00C0F0FFFFFF, dataSize, inputPoly, crcSize, init=regInit, xorout=xorOut )
        self.assertEqual( crc, 0x77 )

    def test_crcmod_8_data(self):
        data = 0xF0FF
        dataSize = 16
        inputPoly = 0x181   ## leave symmetric
        crcSize = 8
        regInit = 0x0
        xorOut = 0x0

        crc_func = crcmod.mkCrcFun(inputPoly, initCrc=regInit, rev=False, xorOut=xorOut)
        crcLib = crc_func( intToASCII(data) )

        crcProc = ModCRC()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        crc = crcProc.calculate2(data, dataSize, inputPoly, crcSize)

#         print "crc: {:b} {:b}".format( crcLib, crc )

        self.assertEqual( crc, crcLib )

    def test_crcmod_8_init(self):
        data =  0xFF
        dataSize = 8
        inputPoly = 0x10F
        crcSize = 8
        regInit = 0x0F
        xorOut = 0x00

        crc_func = crcmod.mkCrcFun(inputPoly, initCrc=regInit, rev=False, xorOut=xorOut)
        crcLib = crc_func( intToASCII(data) )

        crcProc = ModCRC()
        crcProc.setXorOutValue( xorOut )
        crcProc.setInitCRC( regInit, crcSize )

        crc = crcProc.calculate2(data, dataSize, inputPoly, crcSize)
        ##print "crc: 0x{0:X}[0b{0:b}] 0x{1:X}[0b{1:b}]".format( crc, crcLib )
        self.assertEqual( crc, crcLib )

    def test_crcmod_8_xorOut(self):
        data =  0xF0
        dataSize = 8
        inputPoly = 0x100
        crcSize = 8
        regInit = 0x0F
        xorOut = 0xF0

        crc_func = crcmod.mkCrcFun(inputPoly, initCrc=regInit, rev=False, xorOut=xorOut)
        crcLib = crc_func( intToASCII(data) )

        crcProc = ModCRC()
        crcProc.setXorOutValue( xorOut )
        crcProc.setInitCRC( regInit, crcSize )

        crc = crcProc.calculate2(data, dataSize, inputPoly, crcSize)
#         print "crc: 0x{0:X}[0b{0:b}] 0x{1:X}[0b{1:b}]".format( crc, crcLib )
        self.assertEqual( crc, crcLib )

    def test_crcmod_8rev_symm(self):
        data = NumberMask(0xFF, 8)
        inputPoly = NumberMask(0x181, 8)               ## leave symmetric
        regInit = 0x0
        xorOut = 0x0

        crc_func = crcmod.mkCrcFun(inputPoly.masterData(), initCrc=regInit, rev=True, xorOut=xorOut)
        crcLib = crc_func( data.toASCII() )

        crcProc = ModCRC()
        crcProc.setReversed()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )

        revData = data.reversedBytes()
        revPoly = inputPoly.reversed()

        crc = crcProc.calculate3( revData, revPoly)
#         print "crcx: {:b} {:b}".format( crc, crcLib )
        self.assertEqual( crc, crcLib )

    def test_crcmod_8rev_data(self):
        data = NumberMask(0xEF00ABCD, 32)
        inputPoly = NumberMask(0x181, 8)                       ## leave symmetric
        regInit = 0x0
        xorOut = 0x0

        crc_func = crcmod.mkCrcFun(inputPoly.masterData(), initCrc=regInit, rev=True, xorOut=xorOut)
        crcLib = crc_func( data.toASCII() )

        crcProc = ModCRC()
        crcProc.setReversed()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )

        crc = crcProc.calculate3( data, inputPoly)
#         print "crcx: {:b} {:b}".format( crc, crcLib )
        self.assertEqual( crc, crcLib )

    def test_crcmod_8rev_poly(self):
        data = NumberMask(0x81, 16)       ## leave symmetric
        inputPoly = NumberMask(0x1F0, 8)
        regInit = 0x0
        xorOut = 0x0

        crc_func = crcmod.mkCrcFun(inputPoly.masterData(), initCrc=regInit, rev=True, xorOut=xorOut)
        crcLib = crc_func( data.toASCII() )

        crcProc = ModCRC()
        crcProc.setReversed()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )

        crc = crcProc.calculate3( data, inputPoly)
#         print "crcx: {:b} {:b}".format( crc, crcLib )
        self.assertEqual( crc, crcLib )

    def test_crcmod_8rev_init(self):
        data = NumberMask(0xFF0F, 16)
        inputPoly = NumberMask(0x181, 8)
        regInit = 0x0F
        xorOut = 0x0

        crc_func = crcmod.mkCrcFun(inputPoly.masterData(), initCrc=regInit, rev=True, xorOut=xorOut)
        crcLib = crc_func( data.toASCII() )

        crcProc = ModCRC()
        crcProc.setReversed()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )

        crc = crcProc.calculate3( data, inputPoly)
#         print "crcx: {:b} {:b}".format( crc, crcLib )
        self.assertEqual( crc, crcLib )

    def test_crcmod_8rev_xorOut(self):
        data = NumberMask(0xFF, 8)
        inputPoly = NumberMask(0x181, 8)
        regInit = 0x0F
        xorOut = 0x0F
        reverse = True

        crc_func = crcmod.mkCrcFun(inputPoly.masterData(), initCrc=regInit ^ xorOut, rev=reverse, xorOut=xorOut)
        crcLib = crc_func( data.toASCII() )

        crcProc = ModCRC()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )
        crcProc.setRegisterInitValue( regInit )

        crc = crcProc.calculate3( data, inputPoly)
#         print "crcx: {:b} {:b}".format( crc, crcLib )
        self.assertEqual( crc, crcLib )

    def test_crcmod_8darc(self):
        data = NumberMask(0x01, 8)
        inputPoly = NumberMask(0x139, 8)
        regInit = 0x0
        xorOut = 0x0

        crc_func = crcmod.predefined.mkCrcFun('crc-8-darc')
        crcLib = crc_func( data.toASCII() )

        crcProc = ModCRC()
        crcProc.setReversed()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )

        revData = data.reversedBytes()

        crc = crcProc.calculate3( revData, inputPoly)

#         print "crcx: {:b} {:b}".format( crc, crcLib )

        self.assertEqual( crc, crcLib )

    def test_crcmod_8rohc(self):
        data = NumberMask(0xF00F, 16)
        inputPoly = NumberMask(0x107, 8)
        regInit = 0xFF
        xorOut = 0x0

        crc_func = crcmod.predefined.mkCrcFun('crc-8-rohc')     ## rev
        crcLib = crc_func( data.toASCII() )

        crcProc = ModCRC()
        crcProc.setReversed()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )

        crc = crcProc.calculate3( data, inputPoly)

#         print "crcx: {:b} {:b}".format( crcLib, crc )

        self.assertEqual( crc, crcLib )

    def test_crcmod_32(self):
        data =  0x414243
        dataSize = 24
        inputPoly = 0x104c11db7
        regInit = 0x0
        xorOut = 0x00
        crcSize = 32

#         print "XXX {:X} {:X}".format( data, data2)

#         barray1 = bytearray.fromhex('{:x}'.format(data))
#         barray2 = bytearray.fromhex('{:x}'.format(data2))

#         crc32_func = crcmod.mkCrcFun(0x104c11db7, initCrc=regInit, xorOut=xorOut)
        crc32_func = crcmod.mkCrcFun(0x104c11db7, rev=False, initCrc=regInit, xorOut=xorOut)
        crcLib = crc32_func( intToASCII(data) )

        crcProc = ModCRC()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        crc = crcProc.calculate2(data, dataSize, inputPoly, crcSize)

#         print "crc: {:X} {:X}".format( crcLib, crc )
        self.assertEqual( crc, crcLib )

    def test_crcmod_8_random(self):
        data = NumberMask(random.randint(1, 0xFFFFFFFFFFFFFFFF), 64)
        crcSize = 8
        crcMax = 2**crcSize-1
        inputPoly = NumberMask( (0x1 << crcSize) | random.randint(1, crcMax), crcSize)
#         regInit = random.randint(0, crcMax)
#         xorOut = random.randint(0, crcMax)
        regInit = 0x0
        xorOut = 0x0
        reverse = bool(random.randint(0, 1))

        crc_func = crcmod.mkCrcFun(inputPoly.masterData(), rev=reverse, initCrc=regInit, xorOut=xorOut)
        crcLib  = crc_func( data.toASCII() )
#         print "crc: {:X} {:X}".format( crc, crc2 )

        crcProc = ModCRC()
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )
        crcProc.setInitCRC( regInit, crcSize )

        crc = crcProc.calculate3(data, inputPoly)

        self.assertEqual( crc, crcLib )



if __name__ == "__main__":
    unittest.main()
