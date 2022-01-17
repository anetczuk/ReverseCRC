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

from fastcrc.ctypes.fastcrc8 import hw_crc8_calculate, hw_crc8_calculate_range


class HwCRC8Test(unittest.TestCase):
    def setUp(self):
        # Called before testfunction is executed
        pass

    def tearDown(self):
        # Called after testfunction was executed
        pass

    def test_hw_crc8_calculate(self):
        bytes_list = [ 0xFF, 0xFF, 0xFF, 0xFF ]
        crc = hw_crc8_calculate( bytes_list, 0xFF, 0x00, 0x00 )
        self.assertEqual( crc, 240 )

    def test_hw_crc8_calculate_range(self):
        bytes_list = [ 0xFF, 0xFF, 0xFF, 0xFF ]
        data_crc = 0xFE
        results = hw_crc8_calculate_range( bytes_list, data_crc, 0x11, 0x00, 0x00, 0xFF )
        self.assertEqual( len(results), 1 )
        self.assertEqual( results[0], 14 )


if __name__ == "__main__":
    unittest.main()
