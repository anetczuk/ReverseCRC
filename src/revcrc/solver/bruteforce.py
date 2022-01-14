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

from collections import Counter

from crc.numbermask import NumberMask
from revcrc.solver.reverse import Reverse, print_results, write_results,\
    flush_number


class BruteForceSolver(Reverse):

    def __init__(self, crcProcessor, printProgress = None):
        Reverse.__init__(self, crcProcessor, printProgress)

    def execute( self, data, outputFile ):
        retList = self.bruteForceStandardInput( data, self.minSearchData )
        if len(retList) < 1:
            print "\nNo keys discovered"
            return

        dataSize = data.size()

        print_results( retList, dataSize )

        print "\nFound results: ", len(retList)
        write_results( retList, dataSize, outputFile )

    def bruteForceStandardInput(self, inputData, searchRange = 0):
        if inputData.empty():
            return []
        if inputData.ready() == False:
            return []

        numbersList = inputData.numbersList
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(numbersList), inputData.dataSize, inputData.crcSize)

        retList = Counter()

        for num in numbersList:
            ## num -- pair of data and crc
            keys = self.findBruteForceStandard( num, inputData.dataSize, inputData.crcSize, searchRange )

            if (self.progress):
                print "\nFound keys:", len( keys )

            retList.update( keys )

        return retList

    def findBruteForceStandard(self, dataCrcPair, dataSize, crcSize, searchRange = 0):
        data1 = dataCrcPair[0]
        crc1  = dataCrcPair[1]

        if self.progress:
            print "Checking {:X} {:X}, {} {}".format(data1, crc1, dataSize, crcSize)

        dataMask = NumberMask(data1, dataSize)
        crcMask  = NumberMask(crc1, crcSize)

        polyList = []

        paramMax = (0x1 << crcSize) - 1

        if self.initVal is not None:
            ## use init value passed by argument
            if self.progress:
                flush_number( self.initVal, crcSize )
            polyList += self._checkXORA( dataMask, crcMask, self.initVal, paramMax )
        else:
            ## search for init value
            initVal = -1
            while initVal < paramMax:
                initVal += 1
                if self.progress:
                    flush_number( initVal, crcSize )
                polyList += self._checkXORA( dataMask, crcMask, initVal, paramMax )

        for key in polyList:
            key.dataPos = 0
            key.dataLen = dataSize

        return polyList

    def _checkXORA(self, dataMask, crcMask, initVal, paramMax ):
        polyList = []

        self.crcProc.setRegisterInitValue( initVal )

        crcSize = crcMask.dataSize

        xorVal = -1
        while xorVal < paramMax:
            xorVal += 1
            if self.initVal is not None and self.progress:
                flush_number( xorVal, crcSize )
            self.crcProc.setXorOutValue( xorVal )

#                 if self.progress:
#                     sys.stdout.write("\r{:b}".format( xorVal ))
#                     sys.stdout.flush()

            polyList += self.findBruteForcePoly(dataMask, crcMask, False)
#                 polyList += self.findBruteForcePoly(dataMask, crcMask, True)
#                 polyList += self.findBruteForcePolyReverse(dataMask, crcMask)

        return polyList
