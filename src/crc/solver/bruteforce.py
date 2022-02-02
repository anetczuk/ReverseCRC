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

import logging

from collections import Counter

from crc.numbermask import NumberMask
from crc.solver.reverse import Reverse, print_results, write_results,\
    InputMaskList
from crc.flush import flush_number, flush_percent
from crc.crcproc import CRCKey


_LOGGER = logging.getLogger(__name__)


class BruteForceSolver(Reverse):

    def __init__(self, printProgress = None):
        Reverse.__init__(self, printProgress)

    ## inputParams -- InputParams
    def execute( self, inputParams, outputFile ):
        retList = self.bruteForce( inputParams, self.minSearchData )
        if len(retList) < 1:
            _LOGGER.info( "\nNo keys discovered" )
            return retList

        data = inputParams.data
        dataSize = data.size()

        _LOGGER.info( "\n\nFound total results: %s", len(retList) )
        if self.progress:
            print_results( retList, dataSize )

        if outputFile is not None:
            write_results( retList, dataSize, outputFile )

        return retList

    ## inputParams -- InputParams
    def bruteForce(self, inputParams, searchRange = 0):
        inputData = inputParams.data    # InputData

        crcSize = inputParams.getCRCSize()
        if crcSize is None:
            print "\nUnable to determine CRC size: pass poly or crcsize as cmd argument"
            return []

        if inputData.crcSize != crcSize:
            ## deduced CRC size differs from input crc
            raise ValueError( "inconsistent crc size [%s] with input data crc[%s]" % ( crcSize, inputData.crcSize ) )

        inputMasks = InputMaskList( inputData )
        if inputMasks.empty():
            print "invalid case -- no data"
            return []

        _LOGGER.info( "crc size: %s" % crcSize )

        if inputParams.isReverseOrder():
            inputMasks.reverseOrder()
        if inputParams.isReflectBits():
            inputMasks.reflectBits()

        ## List[ (NumberMask, NumberMask) ]
        inputList = inputMasks.getInputMasks()

        polyListStart, polyListStop = inputParams.getPolySearchRange()
        polyListSize = polyListStop - polyListStart + 1

        initListStart, initListStop = inputParams.getInitRegSearchRange()
        initListSize  = initListStop - initListStart + 1

        xorListStart, xorListStop = inputParams.getXorValSearchRange()
        xorListSize  = xorListStop - xorListStart + 1

        subSpaceSize = initListSize * xorListSize
        spaceSize    = polyListSize * subSpaceSize
        _LOGGER.info( "search space size: %s %s %s %s", spaceSize, polyListSize, initListSize, xorListSize )

        _LOGGER.info( "poly search range: %s %s" % ( polyListStart, polyListStop ) )
        _LOGGER.info( "init search range: %s %s" % ( initListStart, initListStop ) )
        _LOGGER.info( " xor search range: %s %s" % ( xorListStart, xorListStop ) )


        crc_forward  = self.procFactory.createForwardProcessor( crcSize )
        crc_operator = crc_forward.createOperator( crcSize, inputList )

        retList = Counter()

        spaceCounter = 0
        polyMask     = NumberMask( 0, crcSize )

        for polyNum in xrange(polyListStart, polyListStop + 1):
            polyMask.setNumber( polyNum )

            spaceCounter += subSpaceSize
            if self.progress:
                value = spaceCounter * 100.0 / spaceSize
                flush_percent( value, 4 )

            # Counter
            crc_found = crc_operator.calculateRange( polyMask, initListStart, initListStop, xorListStart, xorListStop )

            for item in crc_found:
                initReg = item[0]
                xorVal  = item[1]
                counted = crc_found[ item ]
#                 flush_string( "Found CRC - poly: 0x{:X} initVal: 0x{:X} xorVal: 0x{:X}\n".format( polyMask.dataNum, initReg, xorVal ) )
                key = CRCKey(polyMask.dataNum, initReg, xorVal, 0, inputData.dataSize, rev=False)
                retList[ key ] += counted

        return retList
