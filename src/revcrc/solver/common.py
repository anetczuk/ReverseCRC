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
from crc.crcproc import CRCKey
from revcrc.solver.reverse import Reverse, print_results, write_results


class CommonSolver(Reverse):

    def __init__(self, crcProcessor, printProgress = None):
        Reverse.__init__(self, crcProcessor, printProgress)

    def execute( self, data, outputFile ):
        retList = self.findCommonInput( data, self.minSearchData )
        if len(retList) < 1:
            print "\nNo keys discovered"
            return

        dataSize = data.size()

        print_results( retList, dataSize )

        print "\nFound results: ", len(retList)
        write_results( retList, dataSize, outputFile )

    def findCommonInput(self, inputData, searchRange = -1):
        if inputData.empty():
            return []
        if inputData.ready() == False:
            return []
        if searchRange < 0:
            searchRange = inputData.dataSize-1

        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(inputData.numbersList), inputData.dataSize, inputData.crcSize)

        return self.findCommon(inputData.numbersList, inputData.dataSize, inputData.crcSize, searchRange)

    ## searchRange=0 means exact length (no subvalues)
    def findCommon(self, dataList, dataSize, crcSize, searchRange = 0):
        retList = Counter()

        if len(dataList) < 1:
            return retList

        for i in xrange(0, len(dataList)):
            dataPair = dataList[i]
            dataMask = NumberMask(dataPair[0], dataSize)
            keys = self.findCRCKeyBits( dataMask, dataPair[1], crcSize, searchRange)
            retList.update( keys )

        return retList

    def findCRCKeyBits(self, dataMask, crcNum, crcSize, searchRange):
        if self.progress:
            print "Checking {:X} {:X}".format(dataMask.dataNum, crcNum)

        crcMask = NumberMask(crcNum, crcSize)

        retList = set()

        subList = dataMask.generateSubnumbers(dataMask.dataSize - searchRange, 0)
        for sub in subList:
#             print "Checking subnumber {}".format(sub)
#             if self.progress:
#                 print "Checking substring {:X}".format(sub.dataNum)
            subRet = self.findCRC(sub, crcMask)
            if len(subRet) < 1:
                continue
            for key in subRet:
                key.dataPos = sub.pos
                key.dataLen = sub.size
            retList |= subRet
#             print "Found sub:", subRet, sub

        #if self.progress and len(retList)>0:
        #    print "Found keys:", retList

        return retList

    def findCRC(self, subNum, crcMask):
        dataMask = subNum.toNumberMask()
        retList = set()
        if crcMask.dataSize == 8:
            self.checkCRC(dataMask, crcMask, CRCKey(0x107, False, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x139, True, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11D, False, 0xFD, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x107, False, 0x55, 0x55), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x131, True, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x107, True, 0xFF, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x19B, True, 0x0, 0x0), retList)
        elif crcMask.dataSize == 16:
            self.checkCRC(dataMask, crcMask, CRCKey(0x18005, True, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x18005, False, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x18005, False, 0x800D, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x10589, False, 0x0001, 0x0001), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x13D65, True, 0xFFFF, 0xFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x13D65, False, 0xFFFF, 0xFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, False, 0x0, 0xFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x18005, True, 0xFFFF, 0xFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, True, 0xFFFF, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, True, 0x554D, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x18BB7, False, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x1A097, False, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x18005, True, 0x0, 0xFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, True, 0x0, 0xFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, False, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x18005, True, 0xFFFF, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, True, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, False, 0xFFFF, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11021, False, 0x1D0F, 0x0), retList)
        elif crcMask.dataSize == 24:
            self.checkCRC(dataMask, crcMask, CRCKey(0x1864CFB, False, 0xB704CE, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x15D6DCB, False, 0xFEDCBA, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x15D6DCB, False, 0xABCDEF, 0x0), retList)
        elif crcMask.dataSize == 32:
            self.checkCRC(dataMask, crcMask, CRCKey(0x104C11DB7, True, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x104C11DB7, False, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x11EDC6F41, True, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x1A833982B, True, 0x0, 0xFFFFFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x104C11DB7, False, 0xFFFFFFFF, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x104C11DB7, False, 0xFFFFFFFF, 0xFFFFFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x1814141AB, False, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x104C11DB7, True, 0xFFFFFFFF, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x1000000AF, False, 0x0, 0x0), retList)
        elif crcMask.dataSize == 64:
            self.checkCRC(dataMask, crcMask, CRCKey(0x1000000000000001B, True, 0x0, 0x0), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x142F0E1EBA9EA3693, False, 0x0, 0xFFFFFFFFFFFFFFFF), retList)
            self.checkCRC(dataMask, crcMask, CRCKey(0x1AD93D23594C935A9, True, 0xFFFFFFFFFFFFFFFF, 0x0), retList)
        return retList

    def checkCRC(self, dataMask, crcMask, crcKey, retList):
        ## dataMask: NumberMask
        ## crcMask: NumberMask
        ## crcKey: CRCKey

        ##print "Checking data:", dataMask, crc, crcMaskKey

        self.crcProc.setValues(crcKey)

        polyMask = NumberMask(crcKey.poly, crcMask.dataSize)

        polyCRC = self.crcProc.calculate3(dataMask, polyMask)
        if polyCRC == crcMask.dataNum:
            retList.add( crcKey )
            ## we assume that if key was found then testing on reversed input will fail
            return

        if crcKey.rev == False:
            return

        #TODO: try to achieve compatibility without reversing
        ## check reversed input (crcmod compatibility)
        self.crcProc.setInitCRC( crcKey.init, crcMask.dataSize )
        revDataMask = dataMask.reorderedBytes()
        polyMask.reverse()

        polyCRC = self.crcProc.calculate3(revDataMask, polyMask)
        if polyCRC == crcMask.dataNum:
            retList.add( crcKey )
