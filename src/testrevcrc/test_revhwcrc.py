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
 
import crcmod
import random
from revcrc.backwardreverse import RevHwCRC
from crc.hwcrc import HwCRC
from crc.numbermask import intToASCII
from crc.crcproc import CRCKey, PolyKey
from revcrc.input import InputData

  
  
__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)

  
class RevHwCRCTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
  
    def tearDown(self):
        # Called after the last testfunction was executed
        pass
 
    def test_findPolysXOR_8_1bit(self):
        finder = RevHwCRC()
        polyList = finder.findPolysXOR(0x34EC, 0b100, 0x34ED, 0b111, 16, 8)
        self.assertTrue( PolyKey(0x103, False, 0, 16) in polyList )
        
        polyList = finder.findPolysXOR(0x34EE, 0b010, 0x34EF, 0b001, 16, 8)
        self.assertTrue( PolyKey(0x103, False, 0, 16) in polyList )
        
    def test_findPolysXOR_8_2bit(self):
        finder = RevHwCRC()
        
        polyList = finder.findPolysXOR(0xA53937C7, 0b01011001, 0xA53937CF, 0b10110001, 32, 8)
        self.assertTrue( PolyKey(0x11D, False, 0, 32) in polyList )
        
        polyList = finder.findPolysXOR(0x0000A53937CB, 0b11000101, 0x0000A53937CF, 0b10110001, 32, 8)
        self.assertTrue( PolyKey(0x11D, False, 0, 32) in polyList )
        
        polyList = finder.findPolysXOR(0x1234A53937CB, 0b11000101, 0x1234A53937CF, 0b10110001, 48, 8)
        self.assertTrue( PolyKey(0x11D, False, 0, 48) in polyList )
        
        polyList = finder.findPolysXOR(0xA53937CF, 0x8C, 0xA53937CE, 0x91, 32, 8)
        self.assertTrue( PolyKey(0x11D, False, 0, 32) in polyList )
        
        polyList = finder.findPolysXOR(0xA53937CF, 0x8C, 0xA53937C7, 0x64, 32, 8)
        self.assertTrue( PolyKey(0x11D, False, 0, 32) in polyList )
        
    def test_findPolysXOR_8_3bit(self):
        finder = RevHwCRC()
        polyList = finder.findPolysXOR(0x1234, 0xF1, 0x1235, 0xF6, 16, 8)
        self.assertTrue( PolyKey(0x107, False, 0, 16) in polyList )
    
    def test_findPolysXOR_leading(self):        
        finder = RevHwCRC()
        polyList = finder.findPolysXOR(0x001234, 0xF1, 0x001235, 0xF6, 16, 8)
        self.assertTrue( PolyKey(0x107, False, 0, 16) in polyList )
    
    def test_findPolysXOR_xorout(self):        
        finder = RevHwCRC()
        xorOut = 0xAB
        polyList = finder.findPolysXOR(0x1234, 0xF1^xorOut, 0x1235, 0xF6^xorOut, 16, 8)
        self.assertTrue( PolyKey(0x107, False, 0, 16) in polyList )
    
    def test_findPolysXOR_8_init_xorOut(self):
        dataSize = 42                           ## data size does not matter
        inputPoly = 0x1D5
        inputVal =  0xA53937CF
        inputVal2 = inputVal ^ 0b100101000      ## data diff does not matter
        
        crcProc = HwCRC()
        crcProc.setRegisterInitValue(0xA5)
        crcProc.setXorOutValue(0x7C)
        crc = crcProc.calculate2(inputVal, dataSize, inputPoly, 8)
        crc2 = crcProc.calculate2(inputVal2, dataSize, inputPoly, 8)
        
        finder = RevHwCRC()
        poly = finder.findPolysXOR(inputVal, crc, inputVal2, crc2, dataSize, 8)
        self.assertTrue( PolyKey(inputPoly, False, 0, dataSize) in poly )

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
         
        finder = RevHwCRC()
        polyList = finder.findPolysXOR(data, crc, data2, crc2, 32, crcSize)
         
#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( PolyKey(inputPoly, False, 0, 32) in polyList )
        
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
         
        finder = RevHwCRC()
        polyList = finder.findPolysXOR(data, crc, data2, crc2, 108, crcSize)
         
#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( PolyKey(inputPoly, False, 0, 108) in polyList )
        
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
         
        finder = RevHwCRC()
        polyList = finder.findPolysXOR(data, crc, data2, crc2, 108, crcSize)
         
#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( PolyKey(inputPoly, False, 0, 108) in polyList )

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
          
        finder = RevHwCRC()
        polyList = finder.findPolysXOR(data, crc, data2, crc2, dataSize, crcSize)
          
#         print "data: 0x{:X} 0x{:X} 0x{:X} 0x{:X} 0x{:X}".format( data, data2, inputPoly, regInit, xorOut )
#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( PolyKey(inputPoly, False, 0, dataSize) in polyList )

    def test_findCommon8_empty(self):
        dataList = []
        finder = RevHwCRC()
        foundCRC = finder.findCommon(dataList, 8, 8)
        foundCRC = list( foundCRC )
        self.assertEqual( foundCRC, [] )

    def test_findCommon16_empty(self):
        dataList = []
        finder = RevHwCRC()
        foundCRC = finder.findCommon(dataList, 16, 16, 0)
        self.assertEqual( foundCRC, set() )
        
    def test_findCommon_one(self):
        dataList = [(2,1)]
        finder = RevHwCRC()
        foundCRC = finder.findCommon(dataList, 16, 16, 0)
        self.assertEqual( foundCRC, set() )

    def test_findCommon_c16d16_rev(self):
        dataList = []
        dataSize = 16
        crcSize = 16
        inputPoly = 0x18005
        regInit = 0x0
        xorOut = 0x0
        reverse = True
        
        ## init: 0, xor: 0, rev, poly: 0x18005
        crcFun = HwCRC()
        crcFun.setReversed(reverse)
        crcFun.setXorOutValue(xorOut)
        crcFun.setRegisterInitValue(regInit)

        data1 = 0xABCD
        crc1  = crcFun.calculate2(data1, dataSize, inputPoly, crcSize)
        dataList.append( (data1, crc1) )
          
        data2 = data1 ^ 0x0010
        crc2  = crcFun.calculate2(data2, dataSize, inputPoly, crcSize)
        dataList.append( (data2, crc2) )
          
        finder = RevHwCRC()
        foundCRC = finder.findCommon(dataList, dataSize, crcSize, 0)
          
#         print "found data:", foundCRC
        self.assertIn( CRCKey(inputPoly, reverse, regInit, xorOut, 0, dataSize ), foundCRC )
        
    def test_findCommonInput_8a(self):
        dataList = []
        
        crcFun = crcmod.predefined.mkCrcFun("crc-8")        ## init: 0x0, xor: 0x0, poly: 0x107
        
        data = 0xAB
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
        
        finder = RevHwCRC()
        foundCRC = finder.findCommonInput( InputData(dataList, 8, 8) )
        foundCRC = list( foundCRC )

#         print "found:", foundCRC
        self.assertIn( CRCKey(0x107, False, 0x0, 0x0, 0, 8), foundCRC )
        
    def test_findCommon_8b(self):
        dataList = []
        
        crcFun = crcmod.predefined.mkCrcFun("crc-8")        ## init: 0x0, xor: 0x0, poly: 0x107
        
        data = 0xABCD
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
        
        finder = RevHwCRC()
        foundCRC = finder.findCommon(dataList, 16, 8)
        foundCRC = list( foundCRC )

#         print "found:", foundCRC
        self.assertIn( CRCKey(0x107, False, 0x0, 0x0, 0, 16), foundCRC )

    def test_findCommon_crc16buypass(self):
        dataList = []
         
        crcFun = crcmod.predefined.mkCrcFun("crc-16-buypass")       ## p:0x18005 r:False i:0x0000 x:0x0000
         
        data = 0xDCBA4321
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        data = data ^ 0x0010
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        finder = RevHwCRC()
        foundCRC = finder.findCommon(dataList, 32, 16)
        foundCRC = list( foundCRC )
         
#         print "found:", foundCRC
        self.assertIn( CRCKey(0x18005, False, 0x0, 0x0, 0, 32), foundCRC )
        
    #TODO: try to fix test
    def xxxtest_findCommon_crc16(self):
        dataList = []
         
        crcFun = crcmod.predefined.mkCrcFun("crc-16")       ## p:0x18005 r:True i:0x0000 x:0x0000
         
        data = 0x4B4D
        crc  = crcFun( intToASCII(data) )
        dataList.append( (0x42440000 | data, crc) )
         
        data = data ^ 0x0010
        crc  = crcFun( intToASCII(data) )
        dataList.append( (0x47440000 | data, crc) )
         
        finder = RevHwCRC()
        foundCRC = finder.findCommon(dataList, 32, 16)
        foundCRC = list( foundCRC )
         
#         print "found:", foundCRC
        self.assertIn( CRCKey(0x18005, True, 0x0, 0x0, 0, 16), foundCRC )
        
    #TODO: try to fix test
    def xxxtest_findCommon_crc16_d32(self):
        dataList = []
         
        crcFun = crcmod.predefined.mkCrcFun("crc-16")       ## p:0x18005 r:True i:0x0000 x:0x0000
         
        data1 = 0x1234ABCD
        crc1  = crcFun( intToASCII(data1) )
        dataList.append( (data1, crc1) )
         
        data2 = data1 ^ 0x0010
        crc2  = crcFun( intToASCII(data2) )
        dataList.append( (data2, crc2) )
         
        finder = RevHwCRC()
        foundCRC = finder.findCommon(dataList, 32, 16)
        foundCRC = list( foundCRC )
         
#         print "found:", foundCRC
        self.assertIn( CRCKey(0x18005, True, 0x0, 0x0, 0, 32), foundCRC )
        
    #TODO: try to fix test
    def xxxtest_findCommon_crc16dnp(self):
        dataList = []
         
        crcFun = crcmod.predefined.mkCrcFun("crc-16-dnp")        ## poly: 0x13D65, rev, init: 0xFFFF, xor: 0xFFFF 
         
        data = 0xABCD
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        data = data ^ 0x0010
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        finder = RevHwCRC()
        foundCRC = finder.findCommon(dataList, 16, 16)
        foundCRC = list( foundCRC )
         
#         print "found:", foundCRC
        self.assertIn( CRCKey(0x13D65, True, 0xFFFF, 0xFFFF, 0, 16), foundCRC )

    def test_findPolysInput_poly(self):
        dataList = []
        dataSize = 16
        crcSize = 8
        inputPoly = 0x185
        regInit = 0x0
        xorOut = 0x0
        reverse = False
        
        ## init: 0, xor: 0, rev, poly: 0x18005
        crcFun = HwCRC()
        crcFun.setReversed(reverse)
        crcFun.setXorOutValue(xorOut)
        crcFun.setRegisterInitValue(regInit)

        data1 = 0xABCD
        crc1  = crcFun.calculate2(data1, dataSize, inputPoly, crcSize)
        dataList.append( (data1, crc1) )
          
        data2 = data1 ^ 0x0010
        crc2  = crcFun.calculate2(data2, dataSize, inputPoly, crcSize)
        dataList.append( (data2, crc2) )
          
        finder = RevHwCRC()
        inputData = InputData(dataList, dataSize, crcSize)
        foundCRC = finder.findPolysInput(inputData, 0)
          
#         print "found data:", foundCRC
        self.assertIn( PolyKey(inputPoly, reverse, 0, dataSize ), foundCRC )
        
    def test_bruteForceNumbers_poly(self):
        dataList = []
        dataSize = 16
        crcSize = 8
        inputPoly = 0x185
        regInit = 0x0
        xorOut = 0x0
        reverse = False
        
        ## init: 0, xor: 0, rev, poly: 0x18005
        crcFun = HwCRC()
        crcFun.setReversed(reverse)
        crcFun.setXorOutValue(xorOut)
        crcFun.setRegisterInitValue(regInit)

        data1 = 0xABCD
        crc1  = crcFun.calculate2(data1, dataSize, inputPoly, crcSize)
        dataList.append( (data1, crc1) )
          
        data2 = data1 ^ 0x0010
        crc2  = crcFun.calculate2(data2, dataSize, inputPoly, crcSize)
        dataList.append( (data2, crc2) )
          
        finder = RevHwCRC()
        dInput = InputData(dataList, dataSize, crcSize)
        foundCRC = finder.bruteForceInput(dInput, 0)
          
#         print "found data:", foundCRC
        self.assertIn( CRCKey(inputPoly, reverse, regInit, xorOut, 0, dataSize ), foundCRC )

    def test_bruteForceNumbers_poly2(self):
        dataList = []
        dataSize = 80
        crcSize = 8
        inputPoly = 0x185
        regInit = 0x0
        xorOut = 0x0
        reverse = False

        ## init: 0, xor: 0, rev, poly: 0x18005
        crcFun = HwCRC()
        crcFun.setReversed(reverse)
        crcFun.setXorOutValue(xorOut)
        crcFun.setRegisterInitValue(regInit)

        data1 = 0xAEA1B0094016BA9CC507
        crc1  = crcFun.calculate2(data1, dataSize, inputPoly, crcSize)
        dataList.append( (data1, crc1) )
          
        data2 = 0xBE4BA4F97059B3C61486
        crc2  = crcFun.calculate2(data2, dataSize, inputPoly, crcSize)
        dataList.append( (data2, crc2) )
          
        finder = RevHwCRC()
        dInput = InputData(dataList, dataSize, crcSize)
        foundCRC = finder.bruteForceInput(dInput, 0)
          
#         print "found data:", foundCRC
        self.assertIn( CRCKey(inputPoly, reverse, regInit, xorOut, 0, dataSize ), foundCRC )
        
    def test_bruteForceNumbers_xor(self):
        dataList = []
        dataSize = 16
        crcSize = 8
        inputPoly = 0x185
        regInit = 0x0
        xorOut = 0x0A
        reverse = False
        
        ## init: 0, xor: 0, rev, poly: 0x18005
        crcFun = HwCRC()
        crcFun.setReversed(reverse)
        crcFun.setXorOutValue(xorOut)
        crcFun.setRegisterInitValue(regInit)

        data1 = 0xABCD
        crc1  = crcFun.calculate2(data1, dataSize, inputPoly, crcSize)
        dataList.append( (data1, crc1) )
          
        data2 = data1 ^ 0x0010
        crc2  = crcFun.calculate2(data2, dataSize, inputPoly, crcSize)
        dataList.append( (data2, crc2) )
          
        finder = RevHwCRC()
        dInput = InputData(dataList, dataSize, crcSize)
        foundCRC = finder.bruteForceInput(dInput, 0)
          
#         print "found data:", foundCRC
        self.assertIn( CRCKey(inputPoly, reverse, regInit, xorOut, 0, dataSize ), foundCRC )
        
    def test_bruteForceNumbers_init(self):
        dataList = []
        dataSize = 16
        crcSize = 8
        inputPoly = 0x185
        regInit = 0x0A
        xorOut = 0x0
        reverse = False
        
        ## init: 0, xor: 0, rev, poly: 0x18005
        crcFun = HwCRC()
        crcFun.setReversed(reverse)
        crcFun.setXorOutValue(xorOut)
        crcFun.setRegisterInitValue(regInit)

        data1 = 0xABCD
        crc1  = crcFun.calculate2(data1, dataSize, inputPoly, crcSize)
        dataList.append( (data1, crc1) )
          
        data2 = data1 ^ 0x0010
        crc2  = crcFun.calculate2(data2, dataSize, inputPoly, crcSize)
        dataList.append( (data2, crc2) )
          
        finder = RevHwCRC()
        dInput = InputData(dataList, dataSize, crcSize)
        foundCRC = finder.bruteForceInput(dInput, 0)
          
#         print "found data:", foundCRC
        self.assertIn( CRCKey(inputPoly, reverse, regInit, xorOut, 0, dataSize ), foundCRC )
     
        
 
if __name__ == "__main__":
    unittest.main()
