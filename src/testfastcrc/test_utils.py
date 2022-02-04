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

from fastcrc.utils import convert_to_lsb_list, convert_to_msb_list


class BytesTest(unittest.TestCase):
    def setUp(self):
        # Called before testfunction is executed
        pass

    def tearDown(self):
        # Called after testfunction was executed
        pass

    def test_convert_to_lsb_list(self):
        bytes_list = convert_to_lsb_list( 0x04030201, 4 )
        self.assertEqual( len(bytes_list), 4 )
        self.assertEqual( bytes_list[0], 0x80 )     ## 0b 1000 0000
        self.assertEqual( bytes_list[1], 0x40 )     ## 0b 0100 0000
        self.assertEqual( bytes_list[2], 0xC0 )     ## 0b 1100 0000
        self.assertEqual( bytes_list[3], 0x20 )     ## 0b 0010 0000

    def test_convert_to_msb_list(self):
        bytes_list = convert_to_msb_list( 0x04030201, 4 )
        self.assertEqual( len(bytes_list), 4 )
        self.assertEqual( bytes_list[0], 0x04 )
        self.assertEqual( bytes_list[1], 0x03 )
        self.assertEqual( bytes_list[2], 0x02 )
        self.assertEqual( bytes_list[3], 0x01 )


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
