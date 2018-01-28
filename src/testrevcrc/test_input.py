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

from revcrc.input import DataParser, InputData
 
 
__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)



class InputDataTest(unittest.TestCase):
    def setUp(self):
        # Called before testfunction is executed
        pass
 
    def tearDown(self):
        # Called after testfunction was executed
        pass

    def test_convert(self):
        data = [("E21EAB43EA0B478F52AF6E034D310D819DBC3F", "A2B0A")]
        
        parser = InputData()
        parser.convert( data )

        self.assertEqual( parser.dataSize, 152 )
        self.assertEqual( parser.crcSize, 20 )
        self.assertIn( (5042640062004119076411731879610313259117034559L, 666378), parser.numbersList )


 
class DataParserTest(unittest.TestCase):
    def setUp(self):
        # Called before testfunction is executed
        pass
 
    def tearDown(self):
        # Called after testfunction was executed
        pass

    def test_parse_regular(self):
        parser = DataParser()
        msg = "E21EAB43EA0B478F52AF6E034D310D819DBC3F A2B0A"
        parser.parse(msg)
        self.assertEqual( len(parser.data), 1 )
        self.assertEqual( parser.data[0], ("E21EAB43EA0B478F52AF6E034D310D819DBC3F", "A2B0A") )
        
    def test_parse_trim(self):
        parser = DataParser()
        msg = "  E21EAB43EA0B478F52AF6E034D310D819DBC3F A2B0A  "
        parser.parse(msg)
        self.assertEqual( len(parser.data), 1 )
        self.assertEqual( parser.data[0], ("E21EAB43EA0B478F52AF6E034D310D819DBC3F", "A2B0A") )
        
    def test_parse_full_comment(self):
        parser = DataParser()
        msg = "  #  E21EAB43EA0B478F52AF6E034D310D819DBC3F A2B0A  "
        parser.parse(msg)
        self.assertEqual( len(parser.data), 0 )
        
    def test_parse_full_comment2(self):
        parser = DataParser()
        msg = "  //  E21EAB43EA0B478F52AF6E034D310D819DBC3F A2B0A  "
        parser.parse(msg)
        self.assertEqual( len(parser.data), 0 )
        
    def test_parse_end_comment(self):
        parser = DataParser()
        msg = "   E21EAB43EA0B478F52AF6E034D310D819DBC3F A2B0A  #xxx "
        parser.parse(msg)
        self.assertEqual( len(parser.data), 1 )
        self.assertEqual( parser.data[0], ("E21EAB43EA0B478F52AF6E034D310D819DBC3F", "A2B0A") )


if __name__ == "__main__":
    unittest.main()
