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
import time
import argparse 
import logging

from revcrc.input import InputData
import itertools
from revcrc.revcommon import RevCRCCommon
from revcrc.reversecrc import RevHwCRC, BruteForceChain



def brutePoly(inputPair):
    ##inputPair[1] = inputPair[1][::-1]    ## reverse
    
    print "Finding poly for data: {} {}".format(inputPair[0], inputPair[1])
    crcPoly = RevHwCRC.bruteForcePair(inputPair, True)
    if len(crcPoly) > 0:
        print "Found poly: {}".format(crcPoly)

        
def findXOR(inputPair1, inputPair2):
    data1String = inputPair1[0]
    crc1String = inputPair1[1]
    crc1String = crc1String[:4]         ## substring
    
    crc1Size = len(crc1String) * 4
        
    data1 = int(data1String, 16)
    crc1 = int(crc1String, 16)
    
    data2String = inputPair2[0]
    crc2String = inputPair2[1]
    crc2String = crc2String[:4]         ## substring
    
    print "Finding poly for data: {} {} {} {}".format(data1String, crc1String, data2String, crc2String )
    
    data2 = int(data2String, 16)
    crc2 = int(crc2String, 16)

    reverse = RevHwCRC(crc1Size, False)
#     reverse.findXOR2(data1, crc1, data2, crc2)
#     retList = reverse.findCRCKey(data1, crc1, data2, crc2)
    retList = reverse.findXOR2(data1, crc1, data2, crc2)
#     if len(retList) > 0:
#         print "Found polys:", retList

    for ret in retList:
        print "Found data: 0x{:X}".format(ret)
        
        
def combinations( dataList, subListLen ):
    return list(itertools.combinations(dataList, subListLen))


def findKey(inputPair1, inputPair2):
    print "Finding poly for data: {} {} {} {}".format(inputPair1[0], inputPair1[1], inputPair2[0], inputPair2[1], )

    data1String = inputPair1[0]
    crc1String = inputPair1[1]
    
    crc1Size = len(crc1String) * 4
        
    data1 = int(data1String, 16)
    crc1 = int(crc1String, 16)
    
    data2String = inputPair2[0]
    crc2String = inputPair2[1]
    data2 = int(data2String, 16)
    crc2 = int(crc2String, 16)

    reverse = RevHwCRC(crc1Size, False)
#     reverse.findXOR2(data1, crc1, data2, crc2)
    retList = reverse.findCRCKey(data1, crc1, data2, crc2)
#     if len(retList) > 0:
#         print "Found polys:", retList

    for ret in retList:
        print "Found data: {}".format(ret)

    
    

## ============================= main section ===================================


if __name__ != '__main__':
    sys.exit(0)


parser = argparse.ArgumentParser(description='Finding CRC algorithm from data')
parser.add_argument('--mode', action='store', required=True, choices=["FS", "XOR", "SS", "BF", "COMMON"], help='Mode' )
parser.add_argument('--file', action='store', required=True, help='File with data' )
 
 
args = parser.parse_args()
 

logging.basicConfig(level=logging.DEBUG)

print "Starting"

starttime = time.time()

try:
    
    dataParser = InputData()
    data = dataParser.parseFile(args.file)

#     dataSet = set(data)
#     for i in dataSet:
#         inputPair = i
#         dataString = inputPair[0]
#         crcString = inputPair[1]
#         print dataString, crcString
#     sys.exit( 1 )
    
    
    if   args.mode == "FS":
        for i in range(0, len(data)):
            inputPair = data[i]
            brutePoly(inputPair)
    elif args.mode == "XOR":
        comb = combinations( data, 2 )
        cLen = len(comb)
        for i in range(0, cLen):
            sys.stdout.write( str(i) + "/" + str(cLen) + " "  )
            combPair = comb[i]
            findXOR(combPair[0], combPair[1])
        
#         for i in range(0, len(data)-1):
#             findXOR(data[i], data[i+1])
            
#         for i in range(0, len(data)-1, 2):
#             findXOR(data[i], data[i+1])
    elif args.mode == "KEY":
        for i in range(0, len(data)-1, 2):
            findKey(data[i], data[i+1])
    elif args.mode == "SS":
        for i in range(0, len(data)):
            inputPair = data[i]
            dataNum = int(inputPair[0], 16)
            crcNum = int(inputPair[1], 16)
            polyUnderTest = 0x101231
    #         polyUnderTest = 0x123273
    #         polyUnderTest = 0x110210
    #         polyUnderTest = 0x154294
    #         polyUnderTest = 0x10CE3C
            print "Finding substring for data: {:X} {:X} 0x{:X}".format(dataNum, crcNum, polyUnderTest)
            subMessage = RevHwCRC.findSubstring(dataNum, crcNum, polyUnderTest)
            if subMessage != -1:
                print "Found substring: 0x{:X}".format(subMessage)
    elif args.mode == "BF":
        chain = BruteForceChain()
        for i in range(0, len(data)):
            inputPair = data[i]
            print "Finding poly for data: {} {}".format(inputPair[0], inputPair[1])
            dataNum = int(inputPair[0], 16)
            dataSize = len(inputPair[0]) * 4
            crcNum = int(inputPair[1], 16)
            crcSize = len(inputPair[1]) * 4
            dataCrc = DataCRC(dataNum, dataSize, crcNum, crcSize)
            chain.calculate(dataCrc)
    elif args.mode == "COMMON":
        finder = RevCRCCommon(16)
        foundCRC = finder.findSolutionStrings(data)
    else:
        print "Invalid mode:", args.mode
        sys.exit(1)

finally:
    timeDiff = (time.time()-starttime)*1000.0
    print "Calculation time: {:13.8f}ms".format(timeDiff)
    