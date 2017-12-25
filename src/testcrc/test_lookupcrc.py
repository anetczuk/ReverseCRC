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
from crc.lookupcrc import LookupCRC



class LookupCRCTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
 
    def tearDown(self):
        # Called after the last testfunction was executed
        pass
      
    def test_calculate_2(self):
        data = 0b1011
        poly = 0b111
        ##crcCalc = CRC(2)
        ##crc = crcCalc.calculate(data, poly)
        crc = 1
        
        crcProc = LookupCRC(2, 1)
        lookupCrc = crcProc.calculate2(data, 4, poly)
        self.assertEqual( lookupCrc, crc )
        
    def test_calculate_4(self):
        data = 0b00001001
        poly = 0b11001
        ##crcCalc = CRC(4)
        ##crc = crcCalc.calculate(data, poly)
        crc = 14
        
        crcProc = LookupCRC(4, 2)
        lookupCrc = crcProc.calculate2(data, 8, poly)
        self.assertEqual( lookupCrc, crc )
        
    def test_calculate_4_half(self):
        data = 0b00001001
        poly = 0b11001
#         crcCalc = CRC(4)
#         crc = crcCalc.calculate2(data, 6, poly)
        crc = 14
        
        crcProc = LookupCRC(4, 4)
        with self.assertRaises(AssertionError):
            lookupCrc = crcProc.calculate2(data, 6, poly)
            self.assertEqual( lookupCrc, crc )
    
    def test_calculate_8(self):
        data = 0xA53937C7
        poly = 0x11D
        ##crcCalc = CRC(8)
        ##crc = crcCalc.calculate(data, poly)
        crc = 89
        
        crcProc = LookupCRC(8, 4)
        lookupCrc = crcProc.calculate(data, poly)
        self.assertEqual( lookupCrc, crc )



if __name__ == "__main__":
    unittest.main()
