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
from revcrc.backwardreverse import RevDivisionCRC, RevModCRC
from crc.numbermask import intToASCII
from crc.crcproc import CRCKey, PolyKey
from crc.divisioncrc import DivisionCRC

  
  
__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)



class RevDivisionCRCTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
  
    def tearDown(self):
        # Called after the last testfunction was executed
        pass
    
    def test_findPolysXOR_c8d24_rev(self):
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
        polyList = finder.findPolysXOR( data, crc, data2, crc2, 24, crcSize)
        
#         print "polys:", "[{}]".format( ", ".join("0x{:X}".format(x) for x in polyList) )
        self.assertTrue( PolyKey(inputPoly, True, 0, 24) in polyList )

        
    def test_findSolution_c16d16(self):
        dataList = []
        crcSize = 16
        dataSize = 16
        inputPoly = 0x18005             ## 0x18005 = 98309
        regInit = 0x0
        xorOut = 0x0
        reverse = False
        
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
        self.assertIn( CRCKey(inputPoly, reverse, regInit, -1, 0, dataSize ), foundCRC )
        
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
        self.assertIn( CRCKey(inputPoly, reverse, regInit, -1, 0, dataSize ), foundCRC )


class RevModCRCTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
  
    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_findSolution_empty(self):
        dataList = []
        finder = RevModCRC()
        foundCRC = finder.findSolution(dataList, 8, 8, 0)
        self.assertEqual( foundCRC, set() )
        
    def test_findSolution_one(self):
        dataList = [(1,1)]
        finder = RevModCRC()
        foundCRC = finder.findSolution(dataList, 8, 8, 0)
        self.assertEqual( foundCRC, set() )
        
    def test_findSolution_crc8(self):
        dataList = []
         
        crcFun = crcmod.predefined.mkCrcFun("crc-8")        ## init: 0x0, xor: 0x0, poly: 0x107
         
        data = 0xABCD
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        data = data ^ 0x0040
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        finder = RevModCRC()
        finder.setReturnOnFirst()
        foundCRC = finder.findSolution(dataList, 16, 8, 0)
         
#         print "found:", foundCRC
#         self.assertEqual( len(foundCRC), 1 )
#         crcKey = foundCRC[0]
#         self.assertEqual( crcKey.poly, 0x107 )
#         self.assertEqual( crcKey.init, 0x0 )
#         self.assertEqual( crcKey.xor, 0x0 )
#         self.assertEqual( crcKey.dataPos, 0 )
#         self.assertEqual( crcKey.dataLen, 16 )
        self.assertIn( CRCKey(0x107, False, 0x0, 0x0, 0, 16 ), foundCRC )

    def test_findPolysXOR_crcmod_8Arev(self):
        data =  0xF90AD5FF
        data2 = 0xF90AD5FD
        dataSize = 32
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
        polyList = finder.findPolysXOR(data, crc, data2, crc2, dataSize, crcSize)
        
#         revPoly = reverseBits(inputPoly, crcSize)
#         print "polys: {:X}".format(inputPoly), "[{}]".format( ", ".join("(0x{:X} {})".format(pair[0], pair[1]) for pair in polyList) )
        self.assertIn( PolyKey(inputPoly, True, 0, dataSize), polyList )
    
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
    
    ## test case takes too long
    def xxxtest_findSolution_crcmod16buypass(self):
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
        
        finder = RevModCRC(True)
        foundCRC = finder.findSolution(dataList, dataSize, crcSize, 0)
        
#         print "found:", foundCRC
        self.assertIn( CRCKey(0x18005, False, 0x0, -1, -1, dataSize ), foundCRC )
     
        
 
if __name__ == "__main__":
    unittest.main()
