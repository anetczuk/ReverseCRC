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
import itertools
from collections import Counter

from crc.numbermask import NumberMask
from crc.crcproc import CRCKey
from revcrc.solver.reverse import Reverse, print_results, write_results,\
    flush_number, MessageCRC


class BruteForcePairsSolver(Reverse):

    def __init__(self, crcProcessor, printProgress = None):
        Reverse.__init__(self, crcProcessor, printProgress)

    def dataSize( self, data ):
        return data.size() * ( data.size() - 1 ) / 2

    def execute( self, data, outputFile ):
        retList = self.bruteForcePairsInput( data, self.minSearchData )
        if len(retList) < 1:
            print "\nNo keys discovered"
            return

        dataSize = self.dataSize( data )

        print_results( retList, dataSize )

        print "\nFound results: ", len(retList)
        write_results( retList, dataSize, outputFile )

    # return Counter[ CRCKey ]
    def bruteForcePairsInput(self, inputData, searchRange = 0):
        if inputData.empty():
            return []
        if inputData.ready() == False:
            return []

        numbersList = inputData.numbersList
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(numbersList), inputData.dataSize, inputData.crcSize)

        retList = []
        comb = list( itertools.combinations( numbersList, 2 ) )
        cLen = len(comb)

        if (self.progress):
            print "Combinations number:", cLen

        for i in range(0, cLen):
            combPair = comb[i]
            numberPair1 = combPair[0]
            numberPair2 = combPair[1]

            keys = self.findBruteForcePairs(numberPair1, numberPair2, inputData.dataSize, inputData.crcSize, searchRange)

            if (self.progress):
                print "Found keys:", len( keys )

            retList += keys

        return Counter( retList )

    # return List[ CRCKey ]
    def findBruteForcePairs(self, dataCrcPair1, dataCrcPair2, dataSize, crcSize, searchRange = 0):
        data1 = dataCrcPair1[0]
        crc1  = dataCrcPair1[1]
        data2 = dataCrcPair2[0]
        crc2  = dataCrcPair2[1]

        keyList = self.findPolysXOR(data1, crc1, data2, crc2, dataSize, crcSize, searchRange)

        if (self.progress):
            print "Found {} potential polynomials to check".format( len(keyList) )

        ## finding xor value

        dataCrc1 = MessageCRC(data1, dataSize, crc1, crcSize)
        dataCrc2 = MessageCRC(data2, dataSize, crc2, crcSize)

        retList = []
        for key in keyList:
            paramsList = self.findBruteForceParams(dataCrc1, dataCrc2, key)
            if len(paramsList) < 1:
                continue
            #if self.progress:
            #    sys.stdout.write("\r")
            #    print "Found keys: {}".format( paramsList )
            retList += paramsList
        return retList

    # return List[ CRCKey ]
    def findBruteForceParams(self, dataCrc1, dataCrc2, polyKey):
        self.crcProc.setReversed( polyKey.rev )

        crcSize = dataCrc1.crcSize

        paramMax = (0x1 << crcSize) - 1

        polyList = []

        if self.initVal is not None:
            ## use init value passed by argument
            if self.progress:
                flush_number( self.initVal, crcSize )
            polyList += self._checkXORB( dataCrc1, dataCrc2, polyKey, crcSize, self.initVal, paramMax )
        else:
            ## search for init value
            initVal = -1
            while initVal < paramMax:
                initVal += 1
                if self.progress:
                    flush_number( initVal, crcSize )
                keysList = self._checkXORB( dataCrc1, dataCrc2, polyKey, crcSize, initVal, paramMax )
                polyList.extend( keysList )

        if self.progress:
            sys.stdout.write("\r")
            sys.stdout.flush()
        return polyList

    # return List[ CRCKey ]
    def _checkXORB(self, dataCrc1, dataCrc2, polyKey, crcSize, initVal, paramMax ):
        polyList = []

        polyMask = NumberMask(polyKey.poly, crcSize)

        dataMask1 = dataCrc1.dataMask()
        dataMask2 = dataCrc2.dataMask()
        crc1 = dataCrc1.crcNum
        crc2 = dataCrc2.crcNum

        self.crcProc.setRegisterInitValue( initVal )

        xorVal = -1
        while xorVal < paramMax:
            xorVal += 1

            self.crcProc.setXorOutValue( xorVal )

            polyCRC = self.crcProc.calculate3(dataMask1, polyMask)
            if polyCRC != crc1:
                continue
            polyCRC = self.crcProc.calculate3(dataMask2, polyMask)
            if polyCRC != crc2:
                continue

            newKey = CRCKey(polyKey.poly, polyKey.rev, initVal, xorVal, polyKey.dataPos, polyKey.dataLen)

            #if self.progress:
            #    sys.stdout.write("\r")
            #    print "Found key: {}".format(newKey)

            polyList.append( newKey )

        return polyList
