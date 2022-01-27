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

from crc.numbermask import reverse_number


try:
    from fastcrc.utils import convert_to_msb_list, convert_to_lsb_list, reflect_bits_list
    from fastcrc.swig.fastcrc16 import hw_crc16_calculate, hw_crc16_calculate_param, hw_crc16_calculate_range,\
        hw_crc16_invert, hw_crc16_invert_range
    USE_FAST_CRC = True
except ImportError as ex:
    ## disable fastcrc -- there were problem with importing fastcrc
#     print "unable to import fastcrc:", ex
    USE_FAST_CRC = False


##
if USE_FAST_CRC:

    class FastCRC16Test(unittest.TestCase):
        def setUp(self):
            # Called before testfunction is executed
            pass
    
        def tearDown(self):
            # Called after testfunction was executed
            pass
    
        def test_hw_crc16_calculate(self):
            bytes_list = [ 0xFF, 0xFF, 0xFF, 0xFF ]
            crc = hw_crc16_calculate( bytes_list, 0xFF, 0x00, 0x00 )
            self.assertEqual( crc, 3915 )
    
        def test_hw_crc16_calculate_msb(self):
            data     = 0x0D00C0F0FFFFFF
            dataSize = 56
            poly     = 0x1D
            xorOut   = 0x00
    
            ## 0x0D -- 0b 0000 1101
            ## 0xB0 -- 0b 1011 0000
            bytes_list = convert_to_msb_list( data, dataSize / 8 )
            self.assertEqual( bytes_list[0], 0x0D )
            
            calc_crc = hw_crc16_calculate( bytes_list, poly, 0x00, xorOut )
            
            self.assertEqual( calc_crc, 52847 )
    
        def test_hw_crc16_calculate_msb_xor(self):
            data     = 0x0D00C0F0FFFFFF
            dataSize = 56
            poly     = 0x1D
            xorOut   = 0x8F
            
            bytes_list = convert_to_msb_list( data, dataSize / 8 )
            calc_crc = hw_crc16_calculate( bytes_list, poly, 0x00, xorOut )
            
            self.assertEqual( calc_crc, 52960 )
    
        def test_hw_crc16_calculate_1_reverse(self):
            data     = 0x12
            dataSize = 8
            poly     = 0xBF
            
            poly = reverse_number( poly, 8 )
            bytes_list = convert_to_lsb_list( data, dataSize / 8 )
            calc_crc = hw_crc16_calculate( bytes_list, poly, 0x00, 0x00 )
            calc_crc = reverse_number( calc_crc, 8 )
            
            self.assertEqual( calc_crc, 21 )
    
        def test_hw_crc16_calculate_3_reverse(self):
            data     = 0x000300
            dataSize = 24
            poly     = 0x1BF
            
            poly = reverse_number( poly, 8 )
            bytes_list = convert_to_lsb_list( data, dataSize / 8 )
            calc_crc = hw_crc16_calculate( bytes_list, poly, 0x00, 0x00 )
            calc_crc = reverse_number( calc_crc, 8 )
            
            self.assertEqual( calc_crc, 189 )                         ## 80
    
        def test_hw_crc16_calculate_param_reverse(self):
            data     = 0x030201
            dataSize = 24
            poly     = 0x1BF
            
            msb_bytes_list = convert_to_msb_list( data, dataSize / 8 )
            param_crc = hw_crc16_calculate_param( msb_bytes_list, poly, 0x00, 0x00, True, False )
            self.assertEqual( param_crc, 15082 )
            
            ## check relation
            msb_bytes_list.reverse()
            calc_crc = hw_crc16_calculate( msb_bytes_list, poly, 0x00, 0x00 )
            self.assertEqual( param_crc, calc_crc )
    
        def test_hw_crc16_calculate_param_reflect(self):
            data     = 0x030201
            dataSize = 24
            poly     = 0x1BF
            
            msb_bytes_list = convert_to_msb_list( data, dataSize / 8 )
            param_crc = hw_crc16_calculate_param( msb_bytes_list, poly, 0x00, 0x00, False, True )
            self.assertEqual( param_crc, 12084 )
            
            ## check relation
            reflect_bits_list( msb_bytes_list )
            calc_crc = hw_crc16_calculate( msb_bytes_list, poly, 0x00, 0x00 )
            self.assertEqual( param_crc, calc_crc )
    
        def test_hw_crc16_calculate_param_rr(self):
            data     = 0x030201
            dataSize = 24
            poly     = 0x1BF
            
            msb_bytes_list = convert_to_msb_list( data, dataSize / 8 )
            param_crc = hw_crc16_calculate_param( msb_bytes_list, poly, 0x00, 0x00, True, True )
            self.assertEqual( param_crc, 24635 )
            
            ## check relation
            msb_bytes_list.reverse()
            reflect_bits_list( msb_bytes_list )
            calc_crc = hw_crc16_calculate( msb_bytes_list, poly, 0x00, 0x00 )
            self.assertEqual( param_crc, calc_crc )
    
        def test_hw_crc16_calculate_range(self):
            bytes_list = [ 0xFF, 0xFF, 0xFF, 0xFF ]
            data_crc = 0xFE
            results = hw_crc16_calculate_range( bytes_list, data_crc, 0x11, 0x00, 0x00, 0x00, 0xFFFF )
            self.assertEqual( len(results), 1 )
            self.assertEqual( results[0], (0, 4094) )
    
        def test_hw_crc16_invert(self):
            bytes_list = [ 0xFF, 0xFF, 0xFF, 0xFF ]
            results = hw_crc16_invert( bytes_list, 0x11, 0x00 )
            self.assertEqual( len(results), 1 )
            self.assertEqual( results[0], 61680 )
    
        def test_hw_crc16_invert_range(self):
            bytes_list = [ 0xFF, 0xFF, 0x00, 0xFF ]
            results = hw_crc16_invert_range( bytes_list, 0x1111, 0x11, 0x00, 0x00 )
            self.assertEqual( len(results), 1 )
            self.assertEqual( results[0], (0, [61470]) )
    

if __name__ == "__main__":
    unittest.main()
