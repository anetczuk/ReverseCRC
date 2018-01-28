#!/usr/bin/python
#
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


import sys
import argparse 
import logging

import crcmod
import random
from crc.numbermask import NumberMask



def randomHexString(length):
    retString = ""
    for _ in xrange(length):
        retString += random.choice('0123456789ABCDEF')
    return retString
    


## ============================= main section ===================================


if __name__ != '__main__':
    sys.exit(0)


parser = argparse.ArgumentParser(description='Generate message and CRC data')
parser.add_argument('--samples', action='store', required=False, default=10, help='Number of samples' )
parser.add_argument('--datasize', action='store', required=True, help='Size of message (chars)' )
parser.add_argument('--preamblesize', action='store', required=False, default=0, help='Size of preamble' )
parser.add_argument('--poly', action='store', required=True, help='Polynomial with leading \'1\'(in hex)' )
parser.add_argument('--xor', action='store', required=False, default="0", help='Xor value (in hex)' )
parser.add_argument('--reversed', action='store', required=False, default=False, help='Reversed algorithm' )
 
 
args = parser.parse_args()
 

logging.basicConfig(level=logging.DEBUG)


try:
    samples = int(args.samples)
    preSize = int(args.preamblesize)
    dataSize = int(args.datasize)
    poly = int(args.poly, 16)
    polySize = poly.bit_length()
    initCrc = 0x0
    xor = int(args.xor, 16)
    rev = args.reversed
    
    print "## pres:{} ds:{} poly:0x{:X} rev:{} initcrc:0x{:X} xor:0x{:X}".format( preSize, dataSize, poly, rev, initCrc, xor )
    crc_func = crcmod.mkCrcFun(poly, rev=rev, initCrc=initCrc, xorOut=xor)
    
    dataFullSize = preSize+dataSize
    dataFormat = "{:0" + str(dataFullSize/4) + "X}"
    polyFormat = "{:0" + str(polySize/4) + "X}"
    messageFormat = dataFormat + " " + polyFormat
    
    for _ in xrange(0, samples):
        preamble = randomHexString(preSize)
        data = randomHexString(dataSize)
        messageNum = int(preamble + data, 16)
        messageMask = NumberMask( messageNum, dataFullSize*4 )
        polyCRC  = crc_func( messageMask.toASCII() )
        print messageFormat.format(messageMask.dataNum, polyCRC)
    
finally:
    pass
    
    