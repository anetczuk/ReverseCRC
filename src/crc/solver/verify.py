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

from crc.numbermask import NumberMask
from crc.crcproc import PolyKey, CRCKey
from crc.solver.reverse import Reverse,\
    InputMaskList, print_results, write_results
from crc.flush import flush_percent, flush_string
from collections import Counter


_LOGGER = logging.getLogger(__name__)


# class VerifyCRCCollector( CRCCollector ):
#
#     def __init__(self):
#         CRCCollector.__init__(self)
#
#     def collect(self, poly, initReg, xorVal):
#         flush_string( "Found CRC - poly: 0x{:X} initVal: 0x{:X} xorVal: 0x{:X}\n".format( poly, initReg, xorVal ) )


class VerifySolver(Reverse):

    def __init__(self, printProgress = None):
        Reverse.__init__(self, printProgress)

    ## inputParams -- InputParams
    def execute( self, inputParams, outputFile ):
        inputData = inputParams.data

        crcSize = inputParams.getCRCSize()
        if crcSize is None:
            _LOGGER.error( "Unable to determine CRC size: pass poly or crcsize as cmd argument" )
            return

        if inputData.crcSize != crcSize:
            ## deduced CRC size differs from input crc
            raise ValueError( "inconsistent crc size [%s] with input data crc[%s]" % ( crcSize, inputData.crcSize ) )

        inputMasks = InputMaskList( inputData )
        if inputMasks.empty():
            _LOGGER.error( "invalid case -- no data" )
            return False

        _LOGGER.info( "crc size: %s" % crcSize )

        revOrd = inputParams.isReverseOrder()
        if revOrd:
            inputMasks.reverseOrder()
        refBits = inputParams.isReflectBits()
        if refBits:
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

        spaceCounter = 0

        crc_forward  = self.procFactory.createForwardProcessor( crcSize )
        crc_operator = crc_forward.createOperator( crcSize, inputList )

        polyMask     = NumberMask( 0, crcSize )

        results = Counter()

        for polyNum in xrange(polyListStart, polyListStop + 1):
            polyMask.setNumber( polyNum )

            spaceCounter += subSpaceSize
            if self.progress:
                value = spaceCounter * 100.0 / spaceSize
                flush_percent( value, 4 )

            crc_found = crc_operator.verifyRange( polyMask, initListStart, initListStop, xorListStart, xorListStop )

            for item in crc_found:
                initReg = item[0]
                xorVal  = item[1]
#                     flush_string( "Found CRC - poly: 0x{:X} initVal: 0x{:X} xorVal: 0x{:X}\n".format( polyMask.dataNum, initReg, xorVal ) )
                key = CRCKey( polyMask.dataNum, initReg, xorVal, 0, inputData.dataSize, revOrd=revOrd, refBits=refBits )
                results[ key ] += 1

        _LOGGER.info( "\n\nFound total results: %s", len(results) )
        if self.progress:
            print_results( results, 1 )

        if outputFile is not None:
            write_results( results, 1, outputFile )

        return results
