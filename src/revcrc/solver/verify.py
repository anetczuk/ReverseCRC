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

from crc.numbermask import NumberMask
from crc.crcproc import PolyKey
from revcrc.solver.reverse import Reverse, flush_percent, flush_string


class VerifySolver(Reverse):

    def __init__(self, crcProcessor, printProgress = None):
        Reverse.__init__(self, crcProcessor, printProgress)

    ## data -- InputData
    def execute( self, data, outputFile ):
        print "input:", self.poly, self.initVal, self.xorVal, self.crcSize

        if self.poly is None and self.crcSize is None:
            print "\nAt least one data need to be passed: poly or crcsize"
            return

        crcSize = None
        if self.poly is not None:
            polyKey = PolyKey( self.poly )
            crcSize = polyKey.size()
        else:
            crcSize = self.crcSize

        if crcSize is None:
            print "\nUnable to determine CRC size"
            return

        polyList = list()
        if self.poly is not None:
            polyList.append( self.poly )
        else:
            polyList = range(0, 2 ** crcSize)

        initList = list()
        if self.initVal is not None:
            initList.append( self.initVal )
        else:
            initList = range(0, 2 ** crcSize)

        xorList = list()
        if self.xorVal is not None:
            xorList.append( self.xorVal )
        else:
            xorList = range(0, 2 ** crcSize)

        spaceSize = len( polyList ) * len( initList ) * len( xorList )
        print "search space size:", spaceSize, len( polyList ), len( initList ), len( xorList )

        spaceCounter = 1

        matchesAll = False
        for polyNum in polyList:
            polyMask = NumberMask( polyNum, crcSize )

            for initNum in initList:
                currCounter = spaceCounter
                for xorNum in xorList:
                    if self.progress:
                        value = currCounter * 100.0 / spaceSize
                        flush_percent( value, 6 )
                    ret = self.verify_input( data, polyMask, initNum, xorNum )
                    if ret is True:
                        flush_string( "Found CRC - poly: 0x{:X} initVal: 0x{:X} xorVal: 0x{:X}\n".format( polyNum, initNum, xorNum ) )
                        matchesAll = True
                        continue
                    currCounter += 1
                spaceCounter += len( xorList )
        if matchesAll:
            print "\nFound poly matching all data"
        else:
            print "\nNo matching polys found"

    def verify_input(self, inputData, polyMask, initReg, xorVal):
        if inputData.empty():
            return True
        if inputData.ready() == False:
            return True

        inputList = inputData.numbersList
        dataSize  = inputData.dataSize
        crcSize   = inputData.crcSize

        for num in inputList:
            data = num[0]
            crc  = num[1]
#             if self.progress:
#                 print "Checking {:X} {:X}, {} {}".format( data, crc, dataSize, crcSize )

            dataMask = NumberMask( data, dataSize )
            crcMask  = NumberMask( crc, crcSize )

            self.crcProc.setRegisterInitValue( initReg )
            self.crcProc.setXorOutValue( xorVal )

            crc = crcMask.dataNum
            polyCRC = self.crcProc.calculate3( dataMask, polyMask )
            if polyCRC != crc:
#                 print "CRC mismatch: ", polyCRC, crc
                return False

        return True

#     def createCRCProcessor(self):
#         raise NotImplementedError
#
# #     def createBackwardCRCProcessor(self, dataMask, crc):
# #         return HwCRCBackward( dataMask, crc )

