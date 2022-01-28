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

import itertools
from collections import Counter

from crc.solver.reverse import Reverse, print_results, write_results, XORReverse


class PolysSolver( XORReverse ):

    def __init__(self, printProgress = None):
        XORReverse.__init__(self, printProgress)

    ## inputParams -- InputParams
    def execute( self, inputParams, outputFile ):
        data = inputParams.data

        retList = self.findPolys( data, self.minSearchData )
        if len(retList) < 1:
            print "\nNo keys discovered"
            return

        dataSize = data.size() * ( data.size() - 1 ) / 2

        print_results( retList, dataSize )

        print "\nFound results: ", len(retList)
        write_results( retList, dataSize, outputFile )

    # return Counter[ PolyKey ]
    def findPolys(self, inputData, searchRange = 0):
        if inputData.empty():
            return []
        if inputData.ready() == False:
            return []

        numbersList = inputData.numbersList
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(numbersList), inputData.dataSize, inputData.crcSize)

        ##retList = set()
        retList = Counter()
        comb = list( itertools.combinations( numbersList, 2 ) )
        cLen = len(comb)

        if (self.progress):
            print "Combinations number:", cLen

        for i in range(0, cLen):
            combPair = comb[i]
            numberPair1 = combPair[0]
            numberPair2 = combPair[1]

            data1 = numberPair1[0]
            crc1  = numberPair1[1]
            data2 = numberPair2[0]
            crc2  = numberPair2[1]

            keys = self.findPolysXOR(data1, crc1, data2, crc2, inputData.dataSize, inputData.crcSize, searchRange)

#             if (self.progress):
#                 keysSet = set(keys)
#                 print "Found polys:", keysSet

            retList.update( keys )

        return retList
