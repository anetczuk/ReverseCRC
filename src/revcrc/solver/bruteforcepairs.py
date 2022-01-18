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

import sys
import itertools
from collections import Counter

from crc.numbermask import NumberMask
from crc.flush import flush_number, flush_string
from crc.crcproc import CRCKey
from revcrc.solver.reverse import Reverse, print_results, write_results,\
    MessageCRC


class BruteForcePairsSolver(Reverse):

    def __init__(self, crcProcessor, printProgress = None):
        Reverse.__init__(self, crcProcessor, printProgress)

    ## inputParams -- InputParams
    def execute( self, inputParams, outputFile ):
        data = inputParams.data
        
        retList = self.bruteForcePairs( data, self.minSearchData )
        if len(retList) < 1:
            print "\nNo keys discovered"
            return

        dataSize = data.size() * ( data.size() - 1 ) / 2

        print_results( retList, dataSize )

        print "\nFound results: ", len(retList)
        write_results( retList, dataSize, outputFile )

    # return Counter[ CRCKey ]
    def bruteForcePairs(self, inputData, searchRange = 0):
        if inputData.empty():
            return []
        if inputData.ready() == False:
            return []

        numbersList = inputData.numbersList
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(numbersList), inputData.dataSize, inputData.crcSize)

        retList = []
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
            
            dataSize = inputData.dataSize
            crcSize  = inputData.crcSize
    
            self.crcProc.setXorOutValue( 0x0 )          ## it OK, XOR method eliminates ('xor value' set to 0x0)
    
            # List[ PolyKey ]
#             print "looking for potential polys:", data1, crc1, data2, crc2, dataSize, crcSize, self.crcProc.registerInit, self.crcProc.xorOut 
            keyList = self.findPolysXOR(data1, crc1, data2, crc2, dataSize, crcSize, searchRange)
    
            if (self.progress):
                print "Found {} potential polynomials to check".format( len(keyList) )
    
            ## finding xor value
    
            dataCrc1 = MessageCRC(data1, dataSize, crc1, crcSize)
            dataCrc2 = MessageCRC(data2, dataSize, crc2, crcSize)
    
            keys = []
            for item in keyList:
#                 if self.progress:
#                     flush_string( "checking key: {}".format( item ) )

                paramsList = self.findBruteForceParams( dataCrc1, dataCrc2, item )
                
                if len(paramsList) < 1:
                    continue
                keys += paramsList

            if (self.progress):
                print "Found keys:", len( keys )

            retList += keys
            
            #TODO: what is initReg and xorVal for self.crcProc???
            self.crcProc.setRegisterInitValue( 0xFF )


        return Counter( retList )

    # dataCrc1 -- MessageCRC
    # dataCrc2 -- MessageCRC
    # polyKey -- PolyKey
    # return List[ CRCKey ]
    def findBruteForceParams(self, dataCrc1, dataCrc2, polyKey):
        self.crcProc.setReversed( polyKey.isReversedFully() )     # PolyKey

        crcSize = dataCrc1.crcSize
              
        polyMask = NumberMask(polyKey.poly, crcSize)
        
        dataMask1 = dataCrc1.dataMask()
        dataMask2 = dataCrc2.dataMask()
        
        paramMax = (0x1 << crcSize) - 1         # 0xFFFF

        polyList = []
  
        initValStart = 0
        initValEnd   = paramMax
        if self.initVal is not None:
            initValStart = self.initVal
            initValEnd   = initValStart
 
        crcMask1  = dataCrc1.crcMask()
        crcMask2  = dataCrc2.crcMask()
 
        inputData = [ (dataMask1, crcMask1), (dataMask2, crcMask2) ]
        crc_operator = self.crcProc.createOperator( crcSize, inputData )
            
        crc_found = crc_operator.verifyRange( polyMask, initValStart, initValEnd, 0, paramMax )
        
        for item in crc_found:
            initReg = item[0]
            xorVal  = item[1]
#             print  "Found CRC - poly: 0x{:X} initVal: 0x{:X} xorVal: 0x{:X}\n".format( polyMask.dataNum, initReg, xorVal )
            newKey = CRCKey( polyKey.poly, initReg, xorVal, polyKey.dataPos, polyKey.dataLen, revOrd=polyKey.revOrd, refBits=polyKey.refBits )
            polyList.append( newKey )

        if self.progress:
            sys.stdout.write("\r")
            sys.stdout.flush()

        return polyList

