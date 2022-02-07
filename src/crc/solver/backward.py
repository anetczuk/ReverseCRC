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


class BackwardSolver(Reverse):

    def __init__(self, printProgress=None):
        Reverse.__init__(self, printProgress)

    ## inputParams -- InputParams
    ## returns Counter<CRCKey>
    def execute( self, inputParams, outputFile ):
        inputData = inputParams.data        # InputData

        crcSize = inputParams.getCRCSize()
        if crcSize is None:
            print "\nUnable to determine CRC size: pass poly or crcsize as cmd argument"
            return None

        if inputData.crcSize != crcSize:
            ## deduced CRC size differs from input crc
            raise ValueError( "inconsistent crc size [%s] with input data crc[%s]" % ( crcSize, inputData.crcSize ) )

        if crcSize < 1:
            raise ValueError( "invalid crc size [%s]" % ( crcSize ) )

        inputMasks = InputMaskList( inputData )
        if inputMasks.empty():
            print "invalid case -- no data"
            return None

        _LOGGER.info( "crc size: %s" % crcSize )

#         revOrd = inputParams.isReverseOrder()
#         if revOrd:
#             inputMasks.reverseOrder()
#         refBits = inputParams.isReflectBits()
#         if refBits:
#             inputMasks.reflectBits()

        inputList = inputMasks.getInputMasks()          # List[ (NumberMask, NumberMask) ]
        numbersLen = len(inputList)

        polyListStart, polyListStop = inputParams.getPolySearchRange()
        polyListSize = polyListStop - polyListStart + 1

        xorListStart, xorListStop = inputParams.getXorValSearchRange()
        xorListSize  = xorListStop - xorListStart + 1

        subSpaceSize = xorListSize
        spaceSize    = numbersLen * polyListSize * subSpaceSize
        _LOGGER.info( "search space size: %s %s %s %s", spaceSize, numbersLen, polyListSize, xorListSize )

        _LOGGER.info( "poly search range: %s %s" % ( polyListStart, polyListStop ) )
        _LOGGER.info( " xor search range: %s %s" % ( xorListStart, xorListStop ) )

        spaceCounter = 0

        crc_forward  = self.procFactory.createForwardProcessor( crcSize )      # CRCProcessor
        crc_backward = self.procFactory.createInvertProcessor( crcSize )       # CRCInvertProcessor

        crc_operator = None
        if numbersLen > 1:
            subInputList = inputList[1:]
            ## CRCDataOperator
            crc_operator = crc_forward.createDataOperator( crcSize, subInputList )

        results = Counter()

        dataSize = inputData.dataSize

        firstDataItem  = inputList[0]
        firstDataMask = firstDataItem[0]
        firstCrcMask  = firstDataItem[1]
        firstCrc      = firstCrcMask.dataNum

#         initSum = 0

        polyMask = NumberMask( 0, crcSize )
        for polyNum in xrange(polyListStart, polyListStop + 1):
            if polyNum == 0x0:
                ## value does not make sense and it's heavily computable
                spaceCounter += numbersLen * subSpaceSize
                continue

            polyMask.setNumber( polyNum )

            spaceCounter += numbersLen * subSpaceSize
            if self.progress:
                value = spaceCounter * 100.0 / spaceSize
                flush_percent( value, 7 )

            ## xorDict: List[ (xor, List[init]) ]
            xorDict = crc_backward.calculateInitRegRange( firstDataMask, firstCrc, polyMask, xorListStart, xorListStop )

            if crc_operator is None:
                ## there is only single data row
                for xorOutPair in xorDict:
                    xorOut      = xorOutPair[0]
                    init_found  = xorOutPair[1]
                    for init_reg in init_found:
                        key = CRCKey( polyNum, init_reg, xorOut, 0, dataSize, revOrd=False, refBits=False )
                        results[ key ] += 1
                continue

#             callsCounter = 0

            for xorOutPair in xorDict:
                xorOut      = xorOutPair[0]
                init_found  = xorOutPair[1]
                crc_forward.setXorOutValue( xorOut )

#                 callsCounter += len( init_found )

                for init_reg in init_found:
                    crc_forward.setInitValue( init_reg )

                    valid = crc_operator.verify( polyMask )
                    if valid:
                        key = CRCKey( polyNum, init_reg, xorOut, 0, dataSize, revOrd=False, refBits=False )
                        results[ key ] += 1

#             print "verify call count:", callsCounter

        _LOGGER.info( "\n\nFound total results: %s", len(results) )

        if self.progress:
            print ""
            print_results( results, 1, True )

        if outputFile is not None:
            write_results( results, 1, outputFile, True )

#         print "inits per item:", initSum, float(initSum) / (polyListSize*xorListSize*numbersLen)

        return results
