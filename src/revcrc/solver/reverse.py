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
import copy
from collections import Counter

from crc.numbermask import NumberMask
from crc.crcproc import CRCKey, PolyKey


## ======================================================================


def get_popular( mostCommon, limit ):
    retList = []
    for poly in mostCommon:
        if poly[1] < limit:
            break
        retList.append( poly )
    return retList


def print_keys_to( stream, commonList ):
    stream.write( "Discovered keys[{:}]:\n".format( len(commonList) ) )
    for poly in commonList:
        stream.write( str(poly) + "\n" )

    keysList = []
    for poly, _ in commonList:
        key = poly.getPolyKey()
        keysList.append( key )
    polyKeys = Counter()
    polyKeys.update( keysList )

    polysList = polyKeys.most_common()
    stream.write( "\nDiscovered polys[{:}]:\n".format( len(polysList) ) )
    for poly in polysList:
        stream.write( str(poly) + "\n" )


# input: Counter[ CRCKey ]
def print_results_to( stream, retList, inputSize ):
    mostCommon = retList.most_common()
    print_keys_to( stream, mostCommon )

    popular = get_popular( mostCommon, inputSize )
    if len(popular) < 1:
        return

    stream.write( "\n\nFOUND MATCHING KEYS[{:}]:\n\n".format( len(popular) ) )
    print_keys_to( stream, popular )


def print_results( retList, inputSize ):
    sys.stdout.write( "\n" )
    print_results_to( sys.stdout, retList, inputSize )


def write_results( retList, inputSize, outpath ):
    with open(outpath, "w") as text_file:
        print_results_to( text_file, retList, inputSize )


## ======================================================================


class MessageCRC:
    def __init__(self, data, dataSize, crc, crcSize):
        self.dataNum = data
        self.dataSize = dataSize
        self.crcNum = crc
        self.crcSize = crcSize

    def dataMask(self):
        return NumberMask(self.dataNum, self.dataSize)

    def crcMask(self):
        return NumberMask(self.crcNum, self.crcSize)

    def __repr__(self):
        return "<MessageCRC {:X} {} {:X} {}>".format(self.dataNum, self.dataSize, self.crcNum, self.crcSize)


## ======================================================================


## convert list of raw int to list of NumberMask
class InputMaskList():

    def __init__(self, inputData):
        self.inputData = inputData
        self.items = list()             ## List[ (NumberMask, NumberMask) ]
        
        inputList = inputData.numbersList
        dataSize  = inputData.dataSize
        crcSize   = inputData.crcSize
                
        for num in inputList:
            data = num[0]
            crc  = num[1]
            dataMask = NumberMask( data, dataSize )
            crcMask  = NumberMask( crc, crcSize )
            
            self.items.append( (dataMask, crcMask) )

    def empty(self):
        return len( self.items ) < 1 

    def getInputMasks(self):
        return self.items
    
    ## reverse order of bytes
    def reverseOrder(self):
        for dataMask, crcMask in self.items:
            dataMask.reorderBytes()
            crcMask.reorderBytes()
    
    def reflectBits(self):
        for dataMask, crcMask in self.items:
            dataMask.reflectBits()
            crcMask.reflectBits()


## ======================================================================


class InputParams(object):
    
    def __init__(self):
        self.data = None        # InputData
        self.crcSize = None     # int, number of bits
        self.poly = None        # int
        self.initReg = None        # int
        self.xorVal  = None        # int
        self.reverseOrder = None        # bool
        self.reflectBits  = None        # bool

    def getCRCSize(self):
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
            crcSize = self.data.crcSize
        
        return crcSize

    def getPolySearchRange(self):
        return self._getSearchRange( self.poly )

    def getInitRegSearchRange(self):
        return self._getSearchRange( self.initReg )

    def getXorValSearchRange(self):
        return self._getSearchRange( self.xorVal )

    def _getSearchRange(self, value):
        if value is None:
            crc_size   = self.getCRCSize()
            range_size = 2 ** crc_size
            valListStart = 0
            valListStop  = range_size - 1
            return ( valListStart, valListStop )
        else:
            valListStart = value
            valListStop  = valListStart
            return ( valListStart, valListStop )

    def getReverseOrder(self):
        return False if self.reverseOrder is None else self.reverseOrder

    def getReflectBits(self):
        return False if self.reflectBits is None else self.reflectBits


## ======================================================================


class Reverse(object):
    '''
    Base class for reverse algorithms
    '''

    def __init__(self, crcProcessor, printProgress = None):
        self.poly    = None
        self.initVal = None
        self.xorVal  = None
        self.crcSize = None
        self.minSearchData = None

        self.returnFirst = False
        if printProgress == None:
            self.progress = False
        else:
            self.progress = printProgress
        self.crcProc = crcProcessor
        
        self.reverseOrder = None        ## bool, should bytes be read in reverse?
        self.reflectBits  = None        ## bool, should reflect bits in each input byte?

    def setReturnOnFirst(self):
        self.returnFirst = True

    def setPoly(self, value):
        self.poly = value

    ## set registry initial value
    def setInitValue(self, value):
        self.initVal = value

    def setXorValue(self, value):
        self.xorVal = value

    def setCRCSize(self, value):
        self.crcSize = value

    def setReverseMode(self, bytesORder, bitsReflect):
        self.reverseOrder = bytesORder
        self.reflectBits  = bitsReflect

    def setMinSearchData(self, value):
        self.minSearchData = value

    ## abstract method
    ## inputParams -- InputParams
    def execute( self, inputParams, outputFile ):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )

    # ========================================================

    # return List[ PolyKey ]
    def findPolysXOR(self, data1, crc1, data2, crc2, dataSize, crcSize, searchRange = 0):
        xorData = data1 ^ data2
        xorCRC = crc1 ^ crc2
        if self.progress:
            print "Checking {:X} {:X} xor {:X} {:X} = {:X} {:X}, {} {}".format(data1, crc1, data2, crc2, xorData, xorCRC, dataSize, crcSize)
        xorMask = NumberMask(xorData, dataSize)
        crcMask = NumberMask(xorCRC, crcSize)

        retList = []

        subList = xorMask.generateSubnumbers(xorMask.dataSize - searchRange, 0)
        listLen = len(subList)
        ind = 0
        for sub in subList:
            ind += 1
#             print "Checking subnumber {}".format(sub)
            if self.progress:
                #print "Checking substring {:X}".format(sub.dataNum)
                sys.stdout.write( "\r{}/{} checking substring {}\n".format(ind, listLen, sub) )
                sys.stdout.flush()

            dataMask = sub.toNumberMask()

            crcList = []
            crcList += self.findBruteForcePoly(dataMask, crcMask, False)
            crcList += self.findBruteForcePoly(dataMask, crcMask, True)

            polyList = []
            for item in crcList:
                polyList.append( item.getPolyKey() )

            polyList += self.findBruteForcePolyReverse(dataMask, crcMask)

            if len(polyList) < 1:
                continue
            for key in polyList:
                key.dataPos = sub.pos
                key.dataLen = sub.size
            retList += polyList
#             print "Found sub:", subRet, sub

#         if self.progress:
#             sys.stdout.write("\r")
#             sys.stdout.flush()

        return retList


    # return List[ PolyKey ]
    def findBruteForcePoly(self, dataMask, crcMask, reverseMode):
        self.crcProc.setReversed(reverseMode)
        crc = crcMask.dataNum
        poly = 0
        polyMax = crcMask.masterBit
        polyMask = copy.deepcopy(crcMask)
        retList = []
        while poly < polyMax:
#             if self.progress and (poly % 16384) == 16383:
#             if self.progress and (poly % 8192) == 8191:
#                 sys.stdout.write("\r{:b}".format(poly | polyMax))
#                 sys.stdout.flush()

            polyMask.setNumber(poly)
            polyCRC = self.crcProc.calculate3(dataMask, polyMask)
            if polyCRC == crc:
#                 if self.progress:
#                     sys.stdout.write("\r")
#                     print "Found poly: 0b{0:b} 0x{0:X}".format(poly)

                polyValue = poly | polyMax
                polyInit = self.crcProc.registerInit
                polyXor = self.crcProc.xorOut
                retList.append( CRCKey(polyValue, polyInit, polyXor, 0, dataMask.dataSize, rev=reverseMode) )
#                 retList.append( PolyKey(polyValue, 0, dataMask.dataSize, rev=reverseMode) )

            poly += 1

#         if self.progress:
#             sys.stdout.write("\r")
#             sys.stdout.flush()

        return retList

    #TODO: try to achieve compatibility without reversing
    ## check reversed input and poly (crcmod compatibility)
    def findBruteForcePolyReverse(self, dataMask, crcMask, searchRange = 0):
        dataMask.reorderBytes()
        self.crcProc.setReversed(True)
        crc = crcMask.dataNum
        poly = 0
        polyMax = crcMask.masterBit
        polyMask = copy.deepcopy(crcMask)
        retList = []
        while poly < polyMax:
#             if self.progress and (poly % 16384) == 16383:
#             if self.progress and (poly % 8192) == 8191:
#                 sys.stdout.write("\r{:b}".format(poly | polyMax))
#                 sys.stdout.flush()

            polyMask.setNumber(poly)
            polyCRC = self.crcProc.calculate3(dataMask, polyMask)
            if polyCRC == crc:
#                 if self.progress:
#                     sys.stdout.write("\r")
#                     print "Found poly: 0b{0:b} 0x{0:X}".format(poly)
                revPoly = polyMask.reversedData() | polyMax
#                 polyInit = self.crcProc.registerInit
#                 polyXor = self.crcProc.xorOut
#                 retList.append( CRCKey(revPoly, polyInit, polyXor, 0, dataMask.dataSize, rev=True) )
                retList.append( PolyKey(revPoly, 0, dataMask.dataSize, rev=True) )

            poly += 1

#         if self.progress:
#             sys.stdout.write("\r")
#             sys.stdout.flush()
        return retList
