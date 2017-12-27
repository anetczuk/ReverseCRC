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
from crc.divisioncrc import DivisionCRC
from crc.hwcrc import HwCRC
from revcrc.backwardreverse import RevHwCRC, CRCKey, RevDivisionCRC, RevModCRC, MessageCRC,\
    RightSubstringChain, LeftSubstringChain, SideSubstringChain
from crc.numbermask import intToASCII
  
  
__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)

  
class RevHwCRCTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
  
    def tearDown(self):
        # Called after the last testfunction was executed
        pass
 
    def test_bruteForce_4_fail(self):
        finder = RevHwCRC()
        poly = finder.bruteForce(0b11000010, 0x06, crcSize = 4)
        self.assertEqual( poly, [] )
        
    def test_bruteForce_8(self):
        finder = RevHwCRC()
        poly = finder.bruteForce(0b11000010, 0x0F, crcSize = 8)
        self.assertTrue( (0b100011101, False) in poly )
        
    def test_bruteForcePair(self):
        finder = RevHwCRC()
        poly = finder.bruteForcePair(["C2","0F"])
        self.assertTrue( (0b100011101, False) in poly )
        
    def test_findXOR_8_1bit(self):
        finder = RevHwCRC()
        polyList = finder.findXOR(0x34EC, 0b100, 0x34ED, 0b111, crcSize = 8)
        self.assertTrue( (0x103, False) in polyList )
        
        polyList = finder.findXOR(0x34EE, 0b010, 0x34EF, 0b001, crcSize = 8)
        self.assertTrue( (0x103, False) in polyList )
        
    def test_findXOR_8_2bit(self):
        finder = RevHwCRC()
        
        polyList = finder.findXOR(0xA53937C7, 0b01011001, 0xA53937CF, 0b10110001, crcSize = 8)
        self.assertTrue( (0x11D, False) in polyList )
        
        polyList = finder.findXOR(0x0000A53937CB, 0b11000101, 0x0000A53937CF, 0b10110001, crcSize = 8)
        self.assertTrue( (0x11D, False) in polyList )
        
        polyList = finder.findXOR(0x1234A53937CB, 0b11000101, 0x1234A53937CF, 0b10110001, crcSize = 8)
        self.assertTrue( (0x11D, False) in polyList )
        
        polyList = finder.findXOR(0xA53937CF, 0x8C, 0xA53937CE, 0x91, crcSize = 8)
        self.assertTrue( (0x11D, False) in polyList )
        
        polyList = finder.findXOR(0xA53937CF, 0x8C, 0xA53937C7, 0x64, crcSize = 8)
        self.assertTrue( (0x11D, False) in polyList )
        
    def test_findXOR_8_3bit(self):
        finder = RevHwCRC()
        polyList = finder.findXOR(0x1234, 0xF1, 0x1235, 0xF6, crcSize = 8)
        self.assertTrue( (0x107, False) in polyList )
    
    def test_findXOR_leading(self):        
        finder = RevHwCRC()
        polyList = finder.findXOR(0x001234, 0xF1, 0x001235, 0xF6, crcSize = 8)
        self.assertTrue( (0x107, False) in polyList )
    
    def test_findXOR_xorout(self):        
        finder = RevHwCRC()
        xorOut = 0xAB
        polyList = finder.findXOR(0x1234, 0xF1^xorOut, 0x1235, 0xF6^xorOut, crcSize = 8)
        self.assertTrue( (0x107, False) in polyList )
    
    def test_findXOR_8_init_xorOut(self):
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
        poly = finder.findXOR(inputVal, crc, inputVal2, crc2, crcSize = 8)
        self.assertTrue( (inputPoly, False) in poly )

    def test_findXOR_crcmod_8A(self):
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
        polyList = finder.findXOR(data, crc, data2, crc2, crcSize = crcSize)
         
#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( (inputPoly, False) in polyList )
        
    def test_findXOR_crcmod_8_random(self):
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
        polyList = finder.findXOR(data, crc, data2, crc2, crcSize = crcSize)
         
#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( (inputPoly, False) in polyList )
        
    def test_findXOR_crcmod_8_random2(self):
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
        polyList = finder.findXOR(data, crc, data2, crc2, crcSize = crcSize)
         
#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( (inputPoly, False) in polyList )

    def test_findXOR_crcmod_8_random3(self):
        data =  int(random.random()*0xFFFFFFFFFFFFFFFF + 1)
        data2 = int(random.random()*0xFFFFFFFFFFFFFFFF + 1)
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
        polyList = finder.findXOR(data, crc, data2, crc2, crcSize = crcSize)
          
#         print "data: 0x{:X} 0x{:X} 0x{:X} 0x{:X} 0x{:X}".format( data, data2, inputPoly, regInit, xorOut )
#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( (inputPoly, False) in polyList )
        
    def test_findSolution_empty(self):
        dataList = []
        finder = RevHwCRC()
        foundCRC = finder.findSolution(dataList, 16, 16, 0)
        self.assertEqual( foundCRC, [] )
        
    def test_findSolution_one(self):
        dataList = [(1,1)]
        finder = RevHwCRC()
        foundCRC = finder.findSolution(dataList, 16, 16, 0)
        self.assertEqual( foundCRC, [] )
        
    def test_findSubstring_found(self):
        finder = RevHwCRC()
        sumMessage = finder.findSubstring(0x3210A53937C7, 0b01011001, 0x1D, 8)
        self.assertEqual( sumMessage, 0xA53937C7 )

    def test_findCRCKey_8(self):
        data =  0xC2
        data2 = data ^ 0b00010000
        dataSize = 8
        inputPoly = 0x11D
        regInit = 0x52
        crcSize = 8
         
#         print "XXX {:X} {:X}".format( data, data2)
         
        crcProc = HwCRC()
        crcProc.setRegisterInitValue(regInit)
        crc = crcProc.calculate2(data, dataSize, inputPoly, crcSize)
        crc2 = crcProc.calculate2(data2, dataSize, inputPoly, crcSize)
         
#         print "crc {:X} {:X}".format( crc, crc2)
         
        finder = RevHwCRC()
        foundCRC = finder.findCRCKey(data, crc, data2, crc2, dataSize, crcSize)
         
#         print "crc:", crcKeyList
        self.assertIn( CRCKey(inputPoly, False, regInit, -1, -1, dataSize ), foundCRC )
         
    def test_findCRCKey_8_long(self):
        dataSize = 32                           ## data size does not matter
        inputPoly = 0x11D
        crcSize = 8
        data =  0xA53937CF
        data2 = data ^ 0b00001000      ## data diff does not matter
        regInit = 0xA5
           
        crcProc = HwCRC()
        crcProc.setRegisterInitValue(regInit)
        crc = crcProc.calculate2(data, dataSize, inputPoly, crcSize)
        crc2 = crcProc.calculate2(data2, dataSize, inputPoly, crcSize)
           
        finder = RevHwCRC()
        foundCRC = finder.findCRCKey(data, crc, data2, crc2, dataSize, crcSize)
 
#         print "crc:", crcKeyList
        self.assertIn( CRCKey(inputPoly, False, regInit, -1, -1, dataSize ), foundCRC )
         
    def test_findCRCKey_8_long2(self):
        dataSize = 32                           ## data size does not matter
        inputPoly = 0x11D
        crcSize = 8
        inputVal =  0xA53937CF
        inputVal2 = inputVal ^ 0b01001000      ## data diff does not matter
        regInit = 0xA5
           
        crcProc = HwCRC()
        crcProc.setRegisterInitValue(regInit)
        crc = crcProc.calculate2(inputVal, dataSize, inputPoly, crcSize)
        crc2 = crcProc.calculate2(inputVal2, dataSize, inputPoly, crcSize)
           
        finder = RevHwCRC()
        foundCRC = finder.findCRCKey(inputVal, crc, inputVal2, crc2, dataSize, crcSize)
  
        self.assertIn( CRCKey(inputPoly, False, regInit, -1, -1, dataSize ), foundCRC )
         
    def test_findCRCKey_8_long3(self):
        dataSize = 32                           ## data size does not matter
        inputPoly = 0x1F51D
        crcSize = 16
        inputVal =  0xE2DCA53937CF
        inputVal2 = inputVal ^ 0x7000      ## data diff does not matter
        regInit = 0xF7A5
        mask = (1 << dataSize) -1
           
        crcProc = HwCRC()
        crcProc.setRegisterInitValue(regInit)
        crc = crcProc.calculate2(inputVal&mask, dataSize, inputPoly, crcSize)
        crc2 = crcProc.calculate2(inputVal2&mask, dataSize, inputPoly, crcSize)
           
        finder = RevHwCRC()
        foundCRC = finder.findCRCKey(inputVal, crc, inputVal2, crc2, dataSize, crcSize)
 
#         print "crc:", crcKeyList
        self.assertIn( CRCKey(inputPoly, False, regInit, -1, -1, dataSize ), foundCRC )
        
    def test_findSolution_c16d16_rev(self):
        dataList = []
        crcSize = 16
        dataSize = 16
        inputPoly = 0x18005             ## 0x18005 = 98309
        regInit = 0x0
        xorOut = 0x0
        reverse = True
        
        ## init: 0, xor: 0, rev, poly: 0x18005
        crcFun = HwCRC()
        crcFun.setReversed(reverse)
        crcFun.setRegisterInitValue(regInit)
        crcFun.setXorOutValue(xorOut)

        data1 = 0xABCD
        crc1  = crcFun.calculate2(data1, dataSize, inputPoly, crcSize)
        dataList.append( (data1, crc1) )
          
        data2 = data1 ^ 0x0010
        crc2  = crcFun.calculate2(data2, dataSize, inputPoly, crcSize)
        dataList.append( (data2, crc2) )
          
        finder = RevHwCRC()
        foundCRC = finder.findSolution(dataList, dataSize, crcSize, 0)
          
#         print "found data:", foundCRC
        self.assertIn( CRCKey(inputPoly, reverse, regInit, -1, -1, dataSize ), foundCRC )


class RevDivisionCRCTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
  
    def tearDown(self):
        # Called after the last testfunction was executed
        pass
    
    def test_findXOR_c8d24_rev(self):
        data  = 0xFD50D7
        data2 = 0xFD53D7
        inputPoly = 0x1BF
        regInit = 0x0
        xorOut = 0x0
        crcSize = 8

        crcProc = DivisionCRC()
        crcProc.setReversed()
        crcProc.setRegisterInitValue(regInit)
        crcProc.setXorOutValue(xorOut)
        
        crc = crcProc.calculate(data, inputPoly)
        crc2 = crcProc.calculate(data2, inputPoly)
#         print "crc: {:X} {:X}".format( crc, crc2 )
         
        finder = RevDivisionCRC()
        polyList = finder.findXOR(data, crc, data2, crc2, crcSize = crcSize)
        
#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( (inputPoly, True) in polyList )

        
    def test_findSolution_c16d16_rev(self):
        dataList = []
        crcSize = 16
        dataSize = 16
        inputPoly = 0x18005             ## 0x18005 = 98309
        regInit = 0x0
        xorOut = 0x0
        reverse = True
        
        ## init: 0, xor: 0, rev, poly: 0x18005
        crcFun = DivisionCRC()
        crcFun.setReversed(reverse)
        crcFun.setRegisterInitValue(regInit)
        crcFun.setXorOutValue(xorOut)

        data1 = 0xABCD
        crc1  = crcFun.calculate2(data1, dataSize, inputPoly, crcSize)
        dataList.append( (data1, crc1) )
          
        data2 = data1 ^ 0x0010
        crc2  = crcFun.calculate2(data2, dataSize, inputPoly, crcSize)
        dataList.append( (data2, crc2) )
          
        finder = RevDivisionCRC()
        foundCRC = finder.findSolution(dataList, dataSize, crcSize, 0)
          
#         print "found data:", foundCRC
        self.assertIn( CRCKey(inputPoly, reverse, regInit, -1, -1, dataSize ), foundCRC )


class RevModCRCTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
  
    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_findXOR_crcmod_8Arev(self):
        data =  0xF90AD5FF
        data2 = 0xF90AD5FD
#         dataSize = 32
        inputPoly = 0x10A
        regInit = 0x00
        xorOut = 0x00
        crcSize = 8
 
        crc_func = crcmod.mkCrcFun(inputPoly, rev=True, initCrc=regInit, xorOut=xorOut)
        crc  = crc_func( intToASCII(data) )
        crc2 = crc_func( intToASCII(data2) )
#         print "crc: {:X} {:X}".format( crc, crc2 )
#         print "data: {:X}/{:X} {:X}/{:X}".format( data, revData1, data2, revData2 )
        
        finder = RevModCRC()
        polyList = finder.findXOR(data, crc, data2, crc2, crcSize = crcSize)
#         polyList = finder.findXOR(data, crc, data2, crc2)
        
#         revPoly = reverseBits(inputPoly, crcSize)
#         print "polys: {:X}".format(inputPoly), "[{}]".format( ", ".join("(0x{:X} {})".format(pair[0], pair[1]) for pair in polyList) )
        self.assertIn( (inputPoly, True), polyList )
    
    #TODO: try fixing
    def xxxtest_findSolution_crcmod16(self):
        dataList = []
        dataSize = 16
        crcSize = 16
          
        crcFun = crcmod.predefined.mkCrcFun("crc-16")        ## init: 0, xor: 0, rev, poly: 0x18005
          
        data1 = 0xABCD
        crc1  = crcFun( intToASCII(data1) )
#         revData1 = reverseBytes(data1)
#         dataList.append( (revData1, crc1) )
        dataList.append( (data1, crc1) )
          
        data2 = data1 ^ 0x0010
        crc2  = crcFun( intToASCII(data2) )
#         revData2 = reverseBytes(data2)
#         dataList.append( (revData2, crc2) )
        dataList.append( (data2, crc2) )
          
        finder = RevModCRC()
        foundCRC = finder.findSolution(dataList, dataSize, crcSize, 0)
          
#         print "found:", foundCRC
        self.assertIn( CRCKey(0x18005, False, 0x0, -1, -1, dataSize ), foundCRC )
    
    def test_findSolution_crcmod16buypass(self):
        dataList = []
        dataSize = 16
        crcSize = 16
        
        crcFun = crcmod.predefined.mkCrcFun("crc-16-buypass")        ## init: 0, xor: 0, poly: 0x18005
        
        data = 0xABCD
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
        
        data = data ^ 0x0010
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
        
        finder = RevModCRC()
        foundCRC = finder.findSolution(dataList, dataSize, crcSize, 0)
        
#         print "found:", foundCRC
        self.assertIn( CRCKey(0x18005, False, 0x0, -1, -1, dataSize ), foundCRC )
    
    
## ===================================================================


class ChainMock:
    def __init__(self):
        self.input = []
    
    def calculate(self, dataCrc):
        self.input.append(dataCrc)
        
    
class RightSubstringChainTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
  
    def tearDown(self):
        # Called after the last testfunction was executed
        pass
 
    def test_calculate(self):
        output = ChainMock()
        inputData = MessageCRC(0b1101, 4, 0b1111, 4)
        processor = RightSubstringChain(output)
        processor.calculate(inputData)
#         print output.input
        self.assertEqual( len(output.input), 4 )
        self.assertEqual( output.input[2].dataNum, 0b101 )
        self.assertEqual( output.input[2].dataSize, 3 )
        self.assertEqual( output.input[3].dataNum, 0b1101 )
        self.assertEqual( output.input[3].dataSize, 4 )
        
        
        
class LeftSubstringChainTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
  
    def tearDown(self):
        # Called after the last testfunction was executed
        pass
 
    def test_calculate(self):
        output = ChainMock()
        inputData = MessageCRC(0b1101, 4, 0b1111, 4)
        processor = LeftSubstringChain(output)
        processor.calculate(inputData)
#         print output.input
        self.assertEqual( len(output.input), 4 )
        self.assertEqual( output.input[2].dataNum, 0b110 )
        self.assertEqual( output.input[2].dataSize, 3 )
        self.assertEqual( output.input[3].dataNum, 0b1101 )
        self.assertEqual( output.input[3].dataSize, 4 )
 


class SideSubstringChainTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
  
    def tearDown(self):
        # Called after the last testfunction was executed
        pass
 
    def test_calculate(self):
        output = ChainMock()
        inputData = MessageCRC(0b1101, 4, 0b1111, 4)
        processor = SideSubstringChain(output)
        processor.calculate(inputData)
#         print output.input
        self.assertEqual( len(output.input), 10 )
 
        
 
if __name__ == "__main__":
    unittest.main()
