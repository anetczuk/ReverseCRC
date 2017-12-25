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
from crc.modcrc import ModCRC
import crcmod
import random
from crc.numbermask import intToASCII, NumberMask, reverseBits



__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)

        
        
class ModCRCTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
 
    def tearDown(self):
        # Called after the last testfunction was executed
        pass
        
    def test_crcmod_8_data(self):
        data = 0xF0FF
        dataSize = 16
        inputPoly = 0x181   ## leave symmetric
        crcSize = 8
        regInit = 0x0
        xorOut = 0x0
          
        crc_func = crcmod.mkCrcFun(inputPoly, initCrc=regInit, rev=False, xorOut=xorOut)
        crcLib = crc_func( intToASCII(data) )
        
        crcProc = ModCRC(crcSize)
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        crc = crcProc.calculate2(data, dataSize, inputPoly)

#         print "crc: {:b} {:b}".format( crcLib, crc )

        self.assertEqual( crc, crcLib )
        
    def test_crcmod_8_init(self):
        data =  0xFF
        dataSize = 8
        inputPoly = 0x10F
        crcSize = 8
        regInit = 0x0F
        xorOut = 0x00
            
        crc_func = crcmod.mkCrcFun(inputPoly, initCrc=regInit, rev=False, xorOut=xorOut)
        crcLib = crc_func( intToASCII(data) )
            
        crcProc = ModCRC(crcSize)
        crcProc.setXorOutValue( xorOut )
        crcProc.setInitCRC( regInit )
            
        crc = crcProc.calculate2(data, dataSize, inputPoly)
        ##print "crc: 0x{0:X}[0b{0:b}] 0x{1:X}[0b{1:b}]".format( crc, crcLib )
        self.assertEqual( crc, crcLib )
        
    def test_crcmod_8_xorOut(self):
        data =  0xF0
        dataSize = 8
        inputPoly = 0x100
        crcSize = 8
        regInit = 0x0F
        xorOut = 0xF0
             
        crc_func = crcmod.mkCrcFun(inputPoly, initCrc=regInit, rev=False, xorOut=xorOut)
        crcLib = crc_func( intToASCII(data) )
             
        crcProc = ModCRC(crcSize)
        crcProc.setXorOutValue( xorOut )
        crcProc.setInitCRC( regInit )
             
        crc = crcProc.calculate2(data, dataSize, inputPoly)
#         print "crc: 0x{0:X}[0b{0:b}] 0x{1:X}[0b{1:b}]".format( crc, crcLib )
        self.assertEqual( crc, crcLib )
        
    def test_crcmod_8rev_symm(self):
        data = NumberMask(0xFF, 8)
        inputPoly = 0x181               ## leave symmetric
        crcSize = 8
        regInit = 0x0
        xorOut = 0x0
          
        crc_func = crcmod.mkCrcFun(inputPoly, initCrc=regInit, rev=True, xorOut=xorOut)
        crcLib = crc_func( data.toASCII() )
  
        crcProc = ModCRC(crcSize)
        crcProc.setReversed()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        
        revData = data.reversedBytes()
        revPoly = reverseBits(inputPoly, crcSize)
                
        crc = crcProc.calculate3( revData, revPoly)
#         print "crcx: {:b} {:b}".format( crc, crcLib )
        self.assertEqual( crc, crcLib )
        
    def test_crcmod_8rev_data(self):
        data = NumberMask(0xEF00ABCD, 32)
        inputPoly = 0x181                       ## leave symmetric
        crcSize = 8
        regInit = 0x0
        xorOut = 0x0
          
        crc_func = crcmod.mkCrcFun(inputPoly, initCrc=regInit, rev=True, xorOut=xorOut)
        crcLib = crc_func( data.toASCII() )
  
        crcProc = ModCRC(crcSize)
        crcProc.setReversed()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        
        crc = crcProc.calculate3( data, inputPoly)
#         print "crcx: {:b} {:b}".format( crc, crcLib )
        self.assertEqual( crc, crcLib )
        
    def test_crcmod_8rev_poly(self):
        data = NumberMask(0x81, 16)       ## leave symmetric
        inputPoly = 0x1F0
        crcSize = 8
        regInit = 0x0
        xorOut = 0x0
          
        crc_func = crcmod.mkCrcFun(inputPoly, initCrc=regInit, rev=True, xorOut=xorOut)
        crcLib = crc_func( data.toASCII() )
  
        crcProc = ModCRC(crcSize)
        crcProc.setReversed()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        
        crc = crcProc.calculate3( data, inputPoly)
#         print "crcx: {:b} {:b}".format( crc, crcLib )
        self.assertEqual( crc, crcLib )
        
    def test_crcmod_8rev_init(self):
        data = NumberMask(0xFF0F, 16)
        inputPoly = 0x181
        crcSize = 8
        regInit = 0x0F
        xorOut = 0x0

        crc_func = crcmod.mkCrcFun(inputPoly, initCrc=regInit, rev=True, xorOut=xorOut)
        crcLib = crc_func( data.toASCII() )
   
        crcProc = ModCRC(crcSize)
        crcProc.setReversed()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
         
        crc = crcProc.calculate3( data, inputPoly)
#         print "crcx: {:b} {:b}".format( crc, crcLib )
        self.assertEqual( crc, crcLib )
        
    def test_crcmod_8rev_xorOut(self):
        data = NumberMask(0xFF, 8)
        inputPoly = 0x181
        crcSize = 8
        regInit = 0x0F
        xorOut = 0x0F
          
        crc_func = crcmod.mkCrcFun(inputPoly, initCrc=regInit, rev=True, xorOut=xorOut)
        crcLib = crc_func( data.toASCII() )
    
        crcProc = ModCRC(crcSize)
        crcProc.setReversed()
        crcProc.setXorOutValue( xorOut )
        crcProc.setInitCRC( regInit )
        
        revData = data.reversedBytes()
        revPoly = reverseBits(inputPoly, crcSize)
                  
        crc = crcProc.calculate3( revData, revPoly)
#         print "crcx: {:b} {:b}".format( crc, crcLib )
        self.assertEqual( crc, crcLib )
        
    def test_crcmod_8darc(self):
        data = NumberMask(0x01, 8)
        inputPoly = 0x139
        crcSize = 8
        regInit = 0x0
        xorOut = 0x0
         
        crc_func = crcmod.predefined.mkCrcFun('crc-8-darc')
        crcLib = crc_func( data.toASCII() )
         
        crcProc = ModCRC(crcSize)
        crcProc.setReversed()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        
        revData = data.reversedBytes()
         
        crc = crcProc.calculate3( revData, inputPoly)
 
#         print "crcx: {:b} {:b}".format( crc, crcLib )
 
        self.assertEqual( crc, crcLib )
        
    def test_crcmod_8rohc(self):
        data = NumberMask(0xF00F, 16)
        inputPoly = 0x107
        regInit = 0xFF
        xorOut = 0x0
        crcSize = 8
         
        crc_func = crcmod.predefined.mkCrcFun('crc-8-rohc')     ## rev
        crcLib = crc_func( data.toASCII() )
         
        crcProc = ModCRC(crcSize)
        crcProc.setReversed()
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        
        crc = crcProc.calculate3( data, inputPoly)
 
#         print "crcx: {:b} {:b}".format( crcLib, crc )
 
        self.assertEqual( crc, crcLib )

    def test_crcmod_32(self):
        data =  0x414243
        dataSize = 24
        inputPoly = 0x104c11db7
        regInit = 0x0
        xorOut = 0x00
        crcSize = 32
          
#         print "XXX {:X} {:X}".format( data, data2)
  
#         barray1 = bytearray.fromhex('{:x}'.format(data))
#         barray2 = bytearray.fromhex('{:x}'.format(data2))
  
#         crc32_func = crcmod.mkCrcFun(0x104c11db7, initCrc=regInit, xorOut=xorOut)
        crc32_func = crcmod.mkCrcFun(0x104c11db7, rev=False, initCrc=regInit, xorOut=xorOut)
        crcLib = crc32_func( intToASCII(data) )
  
        crcProc = ModCRC(crcSize)
        crcProc.setRegisterInitValue( regInit )
        crcProc.setXorOutValue( xorOut )
        crc = crcProc.calculate2(data, dataSize, inputPoly)
         
#         print "crc: {:X} {:X}".format( crcLib, crc )
        self.assertEqual( crc, crcLib )
        
    def test_crcmod_8_random(self):
        data = NumberMask(random.randint(1, 0xFFFFFFFFFFFFFFFF), 64)
        crcSize = 8
        crcMax = 2**crcSize-1
        inputPoly = (0x1 << crcSize) | random.randint(1, crcMax)
#         regInit = random.randint(0, crcMax)
#         xorOut = random.randint(0, crcMax)
        regInit = 0x0
        xorOut = 0x0
        reverse = bool(random.randint(0, 1))
 
        crc_func = crcmod.mkCrcFun(inputPoly, rev=reverse, initCrc=regInit, xorOut=xorOut)
        crcLib  = crc_func( data.toASCII() )
#         print "crc: {:X} {:X}".format( crc, crc2 )
        
        crcProc = ModCRC(crcSize)
        crcProc.setReversed(reverse)
        crcProc.setXorOutValue( xorOut )
        crcProc.setInitCRC( regInit )
        
        crc = crcProc.calculate3(data, inputPoly)
          
        self.assertEqual( crc, crcLib )
        


if __name__ == "__main__":
    unittest.main()
