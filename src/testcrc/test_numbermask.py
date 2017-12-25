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
from crc.numbermask import intToASCII, reverseBits, NumberMask



class GlobalTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
 
    def tearDown(self):
        # Called after the last testfunction was executed
        pass
      
    def test_intToASCII(self):
        val = intToASCII(0x414243)
        self.assertEqual( val, "ABC" )
        
        val = intToASCII(0x4441)
        self.assertEqual( val, "DA" )
        
    def test_reverseBits(self):
        val = reverseBits( 0b11000001 )
        self.assertEqual( val, 0b10000011 )
        
        val = reverseBits( 0x1021 )
        self.assertEqual( val, 0x1081 )               ## 0x8408
        
        val = reverseBits( 0x11021 ) 
        self.assertEqual( val, 0x10811 )
        
        val = reverseBits( 0x8005 )
        self.assertEqual( val, 0xA001 )
        
    def test_reverseBits_size(self):        
        val = reverseBits( 0x0FA, 12 )
        self.assertEqual( val, 0x5F0 )
        
        val = reverseBits( 0x4441, 16 )
        self.assertEqual( val, 0x8222 )



class NumberMaskTest(unittest.TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_eq_instance(self):
        data = NumberMask(0, 0)
        self.assertEqual(data, data)
        
    def test_eq_value(self):
        data1 = NumberMask(0, 0)
        data2 = NumberMask(0, 0)
        self.assertEqual(data1, data2)
        
    def test_ne_value1(self):
        data1 = NumberMask(0, 1)
        data2 = NumberMask(1, 1)
        self.assertNotEqual(data1, data2)
        
    def test_ne_value2(self):
        data1 = NumberMask(1, 2)
        data2 = NumberMask(1, 3)
        self.assertNotEqual(data1, data2)
        
    def test_in_instance(self):
        data = NumberMask(0, 0)
        self.assertIn(data, [data])
        
    def test_containsMSB_1(self):
        data1 = NumberMask(0xF0, 8)
        data2 = NumberMask(0xF0, 8)
        contains = data1.containsMSB( data2 )
        self.assertTrue(contains)
        
    def test_containsMSB_2(self):
        data1 = NumberMask(0xF0, 8)
        data2 = NumberMask(0xF, 4)
        contains = data1.containsMSB( data2 )
        self.assertTrue(contains)
        
    def test_containsMSB_3(self):
        data1 = NumberMask(0xF0, 8)
        data2 = NumberMask(0xE, 4)
        contains = data1.containsMSB( data2 )
        self.assertFalse(contains)
        
    def test_containsMSB_4(self):
        data1 = NumberMask(0x70, 8)
        data2 = NumberMask(0xE, 4)
        contains = data1.containsMSB( data2 )
        self.assertFalse(contains)
        
    def test_containsLSB_1(self):
        data1 = NumberMask(0x0F, 8)
        data2 = NumberMask(0x0F, 8)
        contains = data1.containsLSB( data2 )
        self.assertTrue(contains)
        
    def test_containsLSB_2(self):
        data1 = NumberMask(0x0F, 8)
        data2 = NumberMask(0x0F, 4)
        contains = data1.containsLSB( data2 )
        self.assertTrue(contains)
        
    def test_containsLSB_3(self):
        data1 = NumberMask(0x0F, 8)
        data2 = NumberMask(0x0E, 4)
        contains = data1.containsLSB( data2 )
        self.assertFalse(contains)
        
    def test_containsLSB_4(self):
        data1 = NumberMask(0x07, 8)
        data2 = NumberMask(0x0E, 4)
        contains = data1.containsLSB( data2 )
        self.assertFalse(contains)




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()