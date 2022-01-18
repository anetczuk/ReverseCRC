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
from revcrc.solver.reverse import Reverse,\
    InputMaskList
from crc.flush import flush_percent, flush_string


# class VerifyCRCCollector( CRCCollector ):
#     
#     def __init__(self):
#         CRCCollector.__init__(self)
# 
#     def collect(self, poly, initReg, xorVal):
#         flush_string( "Found CRC - poly: 0x{:X} initVal: 0x{:X} xorVal: 0x{:X}\n".format( poly, initReg, xorVal ) )


class VerifySolver(Reverse):

    def __init__(self, crcProcessor, printProgress = None):
        Reverse.__init__(self, crcProcessor, printProgress)

    ## data -- InputData
    def execute( self, data, outputFile ):
        print "input args, poly: %s init: %s, xor: %s crcsize: %s" % ( self.poly, self.initVal, self.xorVal, self.crcSize )

        ## CRC size is determined in following order:
        ## 1. from 'self.crcSize' field set directly
        ## 2. from 'self.poly' passed directly
        ## 3. from data CRC set in input file
        crcSize = None
        if crcSize is None:
            crcSize = self.crcSize
        if crcSize is None and self.poly is not None:
            polyKey = PolyKey( self.poly )
            crcSize = polyKey.size()
        if crcSize is None:
            crcSize = data.crcSize

        if crcSize is None:
            print "\nUnable to determine CRC size: pass poly or crcsize as cmd argument"
            return
        
        if data.crcSize != crcSize:
            ## deduced CRC size differs from input crc
            raise ValueError( "inconsistent crc size [%s] with input data crc[%s]" % ( crcSize, data.crcSize ) )

        inputMasks = InputMaskList( data )
        if inputMasks.empty():
            print "invalid case -- no data"
            return False
        
        reverseOrder = False if self.reverseOrder is None else self.reverseOrder
        if reverseOrder:
            inputMasks.reverseOrder()
          
        reflectBits = False if self.reflectBits is None else self.reflectBits
        if reflectBits:
            inputMasks.reflectBits()
            
        ## List[ (NumberMask, NumberMask) ]
        inputList = inputMasks.getInputMasks()

        rangeSize = 2 ** crcSize
        
        polyListStart = 0
        polyListStop  = rangeSize
        if self.poly is not None:
            polyListStart = self.poly
            polyListStop  = polyListStart + 1
        polyListSize  = polyListStop - polyListStart
        
        initListStart = 0
        initListStop  = rangeSize - 1
        if self.initVal is not None:
            initListStart = self.initVal
            initListStop  = initListStart
        initListSize  = initListStop - initListStart + 1
        
        xorListStart = 0
        xorListStop  = rangeSize - 1
        if self.xorVal is not None:
            xorListStart = self.xorVal
            xorListStop  = xorListStart
        xorListSize  = xorListStop - xorListStart + 1

        subSpaceSize = initListSize * xorListSize
        spaceSize = polyListSize * subSpaceSize
        print "search space size:", spaceSize, polyListSize, initListSize, xorListSize
        
        print "poly search range: %s %s" % ( polyListStart, polyListStop-1 )
        print "init search range: %s %s" % ( initListStart, initListStop )
        print " xor search range: %s %s" % ( xorListStart, xorListStop )
        
        spaceCounter = 0

        crc_operator = self.crcProc.createOperator( crcSize, inputList )

        matchesAll = False
        polyMask   = NumberMask( 0, crcSize )
        
        for polyNum in xrange(polyListStart, polyListStop):
            polyMask.setNumber( polyNum )

            spaceCounter += subSpaceSize
            if self.progress:
                value = spaceCounter * 100.0 / spaceSize
                flush_percent( value, 4 )
            
            crc_found = crc_operator.verifyRange( polyMask, initListStart, initListStop, xorListStart, xorListStop )
            
            if crc_found:
                matchesAll = True
                for item in crc_found:
                    initReg = item[0]
                    xorVal  = item[1]
                    flush_string( "Found CRC - poly: 0x{:X} initVal: 0x{:X} xorVal: 0x{:X}\n".format( polyMask.dataNum, initReg, xorVal ) )
        
        if matchesAll:
            print "\nFound poly matching all data"
        else:
            print "\nNo matching polys found"

#     def createCRCProcessor(self):
#         raise NotImplementedError
#
# #     def createBackwardCRCProcessor(self, dataMask, crc):
# #         return HwCRCBackward( dataMask, crc )

