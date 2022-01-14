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
from revcrc.solver.reverse import Reverse, flush_percent, flush_string,\
    InputMaskList


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

        rangeSize = 2 ** crcSize
        
        polyListStart = 0
        polyListStop  = rangeSize
        if self.poly is not None:
            polyListStart = self.poly
            polyListStop  = polyListStart + 1
        polyListSize  = polyListStop - polyListStart
        
        initListStart = 0
        initListStop  = rangeSize
        if self.initVal is not None:
            initListStart = self.initVal
            initListStop  = initListStart + 1
        initListSize  = initListStop - initListStart
        
        xorListStart = 0
        xorListStop  = rangeSize
        if self.poly is not None:
            xorListStart = self.xorVal
            xorListStop  = xorListStart + 1
        xorListSize  = xorListStop - xorListStart

        spaceSize = polyListSize * initListSize * xorListSize
        print "search space size:", spaceSize, polyListSize, initListSize, xorListSize

        inputMasks = InputMaskList( data )
        if inputMasks.empty():
            print "invalid case -- no data"
            return False
        inputList = inputMasks.getInputMasks()
        
        spaceCounter = 0

        matchesAll = False
        polyMask   = NumberMask( 0, crcSize )
        
        for polyNum in xrange(polyListStart, polyListStop):
            polyMask.setNumber( polyNum )

            for self.crcProc.registerInit in xrange(initListStart, initListStop):
#             for initNum in xrange(initListStart, initListStop):
#                 self.crcProc.setRegisterInitValue( initNum )
                
                spaceCounter += xorListSize
                if self.progress:
                    value = spaceCounter * 100.0 / spaceSize
                    flush_percent( value, 4 )
                
                for self.crcProc.xorOut in xrange(xorListStart, xorListStop):
#                 for xorNum in xrange(xorListStart, xorListStop):
#                     self.crcProc.setXorOutValue( xorNum )
                    
                    ret = self._verify_input( inputList, polyMask )
                    if ret is True:
                        flush_string( "Found CRC - poly: 0x{:X} initVal: 0x{:X} xorVal: 0x{:X}\n".format( polyNum, self.crcProc.registerInit, self.crcProc.xorOut ) )
                        matchesAll = True
                        continue

        if matchesAll:
            print "\nFound poly matching all data"
        else:
            print "\nNo matching polys found"

    ## 
    def _verify_input(self, inputList, polyMask):
        for num in inputList:
            dataMask = num[0]
            crcMask  = num[1]

            polyCRC = self.crcProc.calculate3( dataMask, polyMask )
            if polyCRC != crcMask.dataNum:
                return False

        return True

#     def createCRCProcessor(self):
#         raise NotImplementedError
#
# #     def createBackwardCRCProcessor(self, dataMask, crc):
# #         return HwCRCBackward( dataMask, crc )

