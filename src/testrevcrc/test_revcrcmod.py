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
from revcrc.revcrcmod import RevCRCMod
from crc.numbermask import intToASCII
# import logging
 
  
  
__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)

  
class RevCRCModTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
  
    def tearDown(self):
        # Called after the last testfunction was executed
        pass
 
    def test_findSolution_empty(self):
        dataList = []
        finder = RevCRCMod()
        foundCRC = finder.findSolution(dataList, 8, 8, 0)
        self.assertEqual( foundCRC, [] )
        
    def test_findSolution_one(self):
        dataList = [(1,1)]
        finder = RevCRCMod()
        foundCRC = finder.findSolution(dataList, 8, 8, 0)
        self.assertEqual( foundCRC, [] )
        
    def test_findSolution_crc8(self):
        dataList = []
         
        crcFun = crcmod.predefined.mkCrcFun("crc-8")        ## init: 0x0, xor: 0x0, poly: 0x107
         
        data = 0xABCD
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        data = data ^ 0x0040
        crc  = crcFun( intToASCII(data) )
        dataList.append( (data, crc) )
         
        finder = RevCRCMod()
        finder.setReturnOnFirst()
        foundCRC = finder.findSolution(dataList, 8, 8, 0)
         
#         print "found:", foundCRC
        self.assertEqual( len(foundCRC), 1 )
        crcKey = foundCRC[0]
        self.assertEqual( crcKey.poly, 0x107 )
        self.assertEqual( crcKey.init, 0x0 )
        self.assertEqual( crcKey.xor, 0x0 )
        self.assertEqual( crcKey.dataPos, 0 )
        self.assertEqual( crcKey.dataLen, 16 )

 
if __name__ == "__main__":
    unittest.main()
