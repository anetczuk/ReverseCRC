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
from crc.crcproc import PolyKey, CRCKey
from crc.solver.reverse import Reverse,\
    InputMaskList, print_results, write_results
from crc.flush import flush_percent, flush_string
from collections import Counter


class BackwardSolver(Reverse):

    def __init__(self, printProgress = None):
        Reverse.__init__(self, printProgress)

    ## inputParams -- InputParams
    def execute( self, inputParams, outputFile ):
        inputData = inputParams.data        # InputData
        
        crcSize = inputParams.getCRCSize()
        if crcSize is None:
            print "\nUnable to determine CRC size: pass poly or crcsize as cmd argument"
            return
        
        if inputData.crcSize != crcSize:
            ## deduced CRC size differs from input crc
            raise ValueError( "inconsistent crc size [%s] with input data crc[%s]" % ( crcSize, inputData.crcSize ) )

        inputMasks = InputMaskList( inputData )
        if inputMasks.empty():
            print "invalid case -- no data"
            return False
        
        print "crc size: %s" % crcSize
        
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
        print "search space size:", spaceSize, numbersLen, polyListSize, xorListSize
        
        print "poly search range: %s %s" % ( polyListStart, polyListStop )
        print " xor search range: %s %s" % ( xorListStart, xorListStop )
        
        spaceCounter = 0

        crc_backward = self.crcProc.createBackwardProcessor( crcSize )       # CRCBackwardProc
        
        subInputList = inputList[1:]
        crc_operator = self.crcProc.createOperator( crcSize, subInputList )
#         crc_operator = self.crcProc.createStandardOperator( crcSize, subInputList )

        results = Counter()
        
        dataSize = inputData.dataSize
        
        firstDataItem  = inputList[0]
        firstDataMask = firstDataItem[0]
        firstCrcMask  = firstDataItem[1]
        firstCrc      = firstCrcMask.dataNum
        
#         initSum = 0
        
        polyMask = NumberMask( 0, crcSize )
        for polyNum in xrange(polyListStart, polyListStop + 1):
            if polyNum is 0x0:
                ## value does not make sense and it's heavily computable
                spaceCounter += numbersLen * subSpaceSize
                continue

            polyMask.setNumber( polyNum )
            
            spaceCounter += numbersLen * subSpaceSize
            if self.progress:
                value = spaceCounter * 100.0 / spaceSize
                flush_percent( value, 7 )
            
            xorDict = crc_backward.calculateInitRegRange( firstDataMask, firstCrc, polyMask, xorListStart, xorListStop )

            for xorOutPair in xorDict:
                xorOut      = xorOutPair[0]
                init_found  = xorOutPair[1]
                self.crcProc.setXorOutValue( xorOut )
                
                for init_reg in init_found:
                    self.crcProc.setInitValue( init_reg )
                    
                    valid = crc_operator.verify( polyMask )
                    if valid:
                        key = CRCKey( polyNum, init_reg, xorOut, 0, dataSize, revOrd=False, refBits=False )
                        results[ key ] += 1

        print "\n\nFound total results: ", len(results), "\n"

        print_results( results, 1, True )
 
        write_results( results, 1, outputFile, True )

#         print "inits per item:", initSum, float(initSum) / (polyListSize*xorListSize*numbersLen)
