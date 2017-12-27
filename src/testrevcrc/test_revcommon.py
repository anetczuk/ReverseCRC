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
from revcrc.revcommon import RevCRCCommon
from crc.numbermask import intToASCII
from revcrc.reverse import CRCKey

  
  
__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)

  
class RevCRCCommonTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
  
    def tearDown(self):
        # Called after the last testfunction was executed
        pass
 
    def test_findSolution_empty(self):
        dataList = []
        finder = RevCRCCommon()
        foundCRC = finder.findSolution(dataList, 8, 8)
        foundCRC = list( foundCRC )
        self.assertEqual( foundCRC, [] )
        
    def test_findSolution_8a(self):
        dataList = []
        
        crcFun = crcmod.predefined.mkCrcFun("crc-8")        ## init: 0x0, xor: 0x0, poly: 0x107
        
        data = 0xAB
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
        
        finder = RevCRCCommon()
        foundCRC = finder.findSolution(dataList, 8, 8)
        foundCRC = list( foundCRC )

#         print "found:", foundCRC
        self.assertIn( CRCKey(0x107, False, 0x0, 0x0, 0, 8), foundCRC )
        
    def test_findSolution_8b(self):
        dataList = []
        
        crcFun = crcmod.predefined.mkCrcFun("crc-8")        ## init: 0x0, xor: 0x0, poly: 0x107
        
        data = 0xABCD
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
        
        finder = RevCRCCommon()
        foundCRC = finder.findSolution(dataList, 16, 8)
        foundCRC = list( foundCRC )

#         print "found:", foundCRC
        self.assertIn( CRCKey(0x107, False, 0x0, 0x0, 0, 16), foundCRC )

    def test_findSolution_crc16(self):
        dataList = []
         
        crcFun = crcmod.predefined.mkCrcFun("crc-16")
         
        data = 0x1234ABCD
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        data = data ^ 0x0010
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        finder = RevCRCCommon()
        foundCRC = finder.findSolution(dataList, 32, 16)
        foundCRC = list( foundCRC )
         
#         print "found:", foundCRC
        self.assertIn( CRCKey(0x18005, True, 0x0, 0x0, 0, 32), foundCRC )
        
    def test_findSolution_crc16buypass(self):
        dataList = []
         
        crcFun = crcmod.predefined.mkCrcFun("crc-16-buypass")
         
        data = 0xDCBA4321
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        data = data ^ 0x0010
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        finder = RevCRCCommon()
        foundCRC = finder.findSolution(dataList, 32, 16)
        foundCRC = list( foundCRC )
         
#         print "found:", foundCRC
        self.assertIn( CRCKey(0x18005, False, 0x0, 0x0, 0, 32), foundCRC )
        
    def test_findSolution_crc16dnp(self):
        dataList = []
         
        crcFun = crcmod.predefined.mkCrcFun("crc-16-dnp")        ## init: 0xFFFF, xor: 0xFFFF, rev, poly: 0x13D65
         
        data = 0xABCD
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        data = data ^ 0x0010
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        finder = RevCRCCommon()
        foundCRC = finder.findSolution(dataList, 16, 16)
        foundCRC = list( foundCRC )
         
#         print "found:", foundCRC
        self.assertIn( CRCKey(0x13D65, True, 0xFFFF, 0xFFFF, 0, 16), foundCRC )

    def test_findSolutionSubstring_crc16(self):
        dataList = []
         
        crcFun = crcmod.predefined.mkCrcFun("crc-16")
         
        data = 0x4B4D
        crc  = crcFun( intToASCII(data) )
        dataList.append( (0x42440000 | data, crc) )
         
        data = data ^ 0x0010
        crc  = crcFun( intToASCII(data) )
        dataList.append( (0x47440000 | data, crc) )
         
        finder = RevCRCCommon()
        foundCRC = finder.findSolution(dataList, 32, 16)
        foundCRC = list( foundCRC )
         
#         print "found:", foundCRC
        self.assertIn( CRCKey(0x18005, True, 0x0, 0x0, 0, 16), foundCRC )

 
if __name__ == "__main__":
    unittest.main()
