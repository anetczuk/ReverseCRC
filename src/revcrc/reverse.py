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


def flush_number( num, bitSize ):
    formatStr = "\r{:0%sb}" % bitSize
    sys.stdout.write( formatStr.format(num) )
    sys.stdout.flush()


def flush_float( value, places ):
    formatStr = "\r{:.%sf}" % places
    sys.stdout.write( formatStr.format(value) )
    sys.stdout.flush()


def flush_string( value ):
    sys.stdout.write( "\r{}".format(value) )
    sys.stdout.flush()


def flush_percent( value, places ):
    formatStr = "\r{:.%sf}%%" % places
    sys.stdout.write( formatStr.format(value) )
    sys.stdout.flush()


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

    def setMinSearchData(self, value):
        self.minSearchData = value

    def dataSize( self, data ):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )

    ## abstract method
    def execute( self, data, outputFile ):
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
                retList.append( CRCKey(polyValue, reverseMode, polyInit, polyXor, 0, dataMask.dataSize) )
#                 retList.append( PolyKey(polyValue, reverseMode, 0, dataMask.dataSize) )

            poly += 1

#         if self.progress:
#             sys.stdout.write("\r")
#             sys.stdout.flush()

        return retList

    #TODO: try to achieve compatibility without reversing
    ## check reversed input and poly (crcmod compatibility)
    def findBruteForcePolyReverse(self, dataMask, crcMask, searchRange = 0):
        dataMask.reverseBytes()
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
#                 retList.append( CRCKey(revPoly, True, polyInit, polyXor, 0, dataMask.dataSize) )
                retList.append( PolyKey(revPoly, True, 0, dataMask.dataSize) )

            poly += 1

#         if self.progress:
#             sys.stdout.write("\r")
#             sys.stdout.flush()
        return retList


## ==========================================================


class BruteForceSolver(Reverse):

    def __init__(self, crcProcessor, printProgress = None):
        Reverse.__init__(self, crcProcessor, printProgress)

    def dataSize( self, data ):
        return data.size()

    def execute( self, data, outputFile ):
        retList = self.bruteForceStandardInput( data, self.minSearchData )
        if len(retList) < 1:
            print "\nNo keys discovered"
            return

        dataSize = self.dataSize( data )

        print_results( retList, dataSize )

        print "\nFound results: ", len(retList)
        write_results( retList, dataSize, outputFile )

    def bruteForceStandardInput(self, inputData, searchRange = 0):
        if inputData.empty():
            return []
        if inputData.ready() == False:
            return []

        numbersList = inputData.numbersList
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(numbersList), inputData.dataSize, inputData.crcSize)

        retList = Counter()

        for num in numbersList:
            ## num -- pair of data and crc
            keys = self.findBruteForceStandard( num, inputData.dataSize, inputData.crcSize, searchRange )

            if (self.progress):
                print "\nFound keys:", len( keys )

            retList.update( keys )

        return retList

    def findBruteForceStandard(self, dataCrcPair, dataSize, crcSize, searchRange = 0):
        data1 = dataCrcPair[0]
        crc1  = dataCrcPair[1]

        if self.progress:
            print "Checking {:X} {:X}, {} {}".format(data1, crc1, dataSize, crcSize)

        dataMask = NumberMask(data1, dataSize)
        crcMask  = NumberMask(crc1, crcSize)

        polyList = []

        paramMax = (0x1 << crcSize) - 1

        if self.initVal is not None:
            ## use init value passed by argument
            if self.progress:
                flush_number( self.initVal, crcSize )
            polyList += self._checkXORA( dataMask, crcMask, self.initVal, paramMax )
        else:
            ## search for init value
            initVal = -1
            while initVal < paramMax:
                initVal += 1
                if self.progress:
                    flush_number( initVal, crcSize )
                polyList += self._checkXORA( dataMask, crcMask, initVal, paramMax )

        for key in polyList:
            key.dataPos = 0
            key.dataLen = dataSize

        return polyList

    def _checkXORA(self, dataMask, crcMask, initVal, paramMax ):
        polyList = []

        self.crcProc.setRegisterInitValue( initVal )

        crcSize = crcMask.dataSize

        xorVal = -1
        while xorVal < paramMax:
            xorVal += 1
            if self.initVal is not None and self.progress:
                flush_number( xorVal, crcSize )
            self.crcProc.setXorOutValue( xorVal )

#                 if self.progress:
#                     sys.stdout.write("\r{:b}".format( xorVal ))
#                     sys.stdout.flush()

            polyList += self.findBruteForcePoly(dataMask, crcMask, False)
#                 polyList += self.findBruteForcePoly(dataMask, crcMask, True)
#                 polyList += self.findBruteForcePolyReverse(dataMask, crcMask)

        return polyList


## ==========================================================


class BruteForcePairsSolver(Reverse):

    def __init__(self, crcProcessor, printProgress = None):
        Reverse.__init__(self, crcProcessor, printProgress)

    def dataSize( self, data ):
        return data.size() * ( data.size() - 1 ) / 2

    def execute( self, data, outputFile ):
        retList = self.bruteForcePairsInput( data, self.minSearchData )
        if len(retList) < 1:
            print "\nNo keys discovered"
            return

        dataSize = self.dataSize( data )

        print_results( retList, dataSize )

        print "\nFound results: ", len(retList)
        write_results( retList, dataSize, outputFile )

    # return Counter[ CRCKey ]
    def bruteForcePairsInput(self, inputData, searchRange = 0):
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

            keys = self.findBruteForcePairs(numberPair1, numberPair2, inputData.dataSize, inputData.crcSize, searchRange)

            if (self.progress):
                print "Found keys:", len( keys )

            retList += keys

        return Counter( retList )

    # return List[ CRCKey ]
    def findBruteForcePairs(self, dataCrcPair1, dataCrcPair2, dataSize, crcSize, searchRange = 0):
        data1 = dataCrcPair1[0]
        crc1  = dataCrcPair1[1]
        data2 = dataCrcPair2[0]
        crc2  = dataCrcPair2[1]

        keyList = self.findPolysXOR(data1, crc1, data2, crc2, dataSize, crcSize, searchRange)

        if (self.progress):
            print "Found {} potential polynomials to check".format( len(keyList) )

        ## finding xor value

        dataCrc1 = MessageCRC(data1, dataSize, crc1, crcSize)
        dataCrc2 = MessageCRC(data2, dataSize, crc2, crcSize)

        retList = []
        for key in keyList:
            paramsList = self.findBruteForceParams(dataCrc1, dataCrc2, key)
            if len(paramsList) < 1:
                continue
            #if self.progress:
            #    sys.stdout.write("\r")
            #    print "Found keys: {}".format( paramsList )
            retList += paramsList
        return retList

    # return List[ CRCKey ]
    def findBruteForceParams(self, dataCrc1, dataCrc2, polyKey):
        self.crcProc.setReversed( polyKey.rev )

        crcSize = dataCrc1.crcSize

        paramMax = (0x1 << crcSize) - 1

        polyList = []

        if self.initVal is not None:
            ## use init value passed by argument
            if self.progress:
                flush_number( self.initVal, crcSize )
            polyList += self._checkXORB( dataCrc1, dataCrc2, polyKey, crcSize, self.initVal, paramMax )
        else:
            ## search for init value
            initVal = -1
            while initVal < paramMax:
                initVal += 1
                if self.progress:
                    flush_number( initVal, crcSize )
                keysList = self._checkXORB( dataCrc1, dataCrc2, polyKey, crcSize, initVal, paramMax )
                polyList.extend( keysList )

        if self.progress:
            sys.stdout.write("\r")
            sys.stdout.flush()
        return polyList

    # return List[ CRCKey ]
    def _checkXORB(self, dataCrc1, dataCrc2, polyKey, crcSize, initVal, paramMax ):
        polyList = []

        polyMask = NumberMask(polyKey.poly, crcSize)

        dataMask1 = dataCrc1.dataMask()
        dataMask2 = dataCrc2.dataMask()
        crc1 = dataCrc1.crcNum
        crc2 = dataCrc2.crcNum

        self.crcProc.setRegisterInitValue( initVal )

        xorVal = -1
        while xorVal < paramMax:
            xorVal += 1

            self.crcProc.setXorOutValue( xorVal )

            polyCRC = self.crcProc.calculate3(dataMask1, polyMask)
            if polyCRC != crc1:
                continue
            polyCRC = self.crcProc.calculate3(dataMask2, polyMask)
            if polyCRC != crc2:
                continue

            newKey = CRCKey(polyKey.poly, polyKey.rev, initVal, xorVal, polyKey.dataPos, polyKey.dataLen)

            #if self.progress:
            #    sys.stdout.write("\r")
            #    print "Found key: {}".format(newKey)

            polyList.append( newKey )

        return polyList


## =============================================================


class PolysSolver(Reverse):

    def __init__(self, crcProcessor, printProgress = None):
        Reverse.__init__(self, crcProcessor, printProgress)

    def dataSize( self, data ):
        return data.size() * ( data.size() - 1 ) / 2

    def execute( self, data, outputFile ):
        retList = self.findPolysInput( data, self.minSearchData )
        if len(retList) < 1:
            print "\nNo keys discovered"
            return

        dataSize = self.dataSize( data )

        print_results( retList, dataSize )

        print "\nFound results: ", len(retList)
        write_results( retList, dataSize, outputFile )

    # return Counter[ PolyKey ]
    def findPolysInput(self, inputData, searchRange = 0):
        if inputData.empty():
            return []
        if inputData.ready() == False:
            return []

        numbersList = inputData.numbersList
        if (self.progress):
            print "List size: {} Data size: {} CRC size: {}".format(len(numbersList), inputData.dataSize, inputData.crcSize)

        ##retList = set()
        retList = Counter()
        comb = list( itertools.combinations( numbersList, 2 ) )
        cLen = len(comb)

        if (self.progress):
            print "Combinations number:", cLen

        for i in range(0, cLen):
            combPair = comb[i]
            numberPair1 = combPair[0]
            numberPair2 = combPair[1]

            data1 = numberPair1[0]
            crc1 = numberPair1[1]
            data2 = numberPair2[0]
            crc2 = numberPair2[1]

            keys = self.findPolysXOR(data1, crc1, data2, crc2, inputData.dataSize, inputData.crcSize, searchRange)

#             if (self.progress):
#                 keysSet = set(keys)
#                 print "Found polys:", keysSet

            retList.update( keys )

        return retList


## ============================================


class CommonSolver(Reverse):

    def __init__(self, crcProcessor, printProgress = None):
        Reverse.__init__(self, crcProcessor, printProgress)

    def dataSize( self, data ):
        return data.size()

    def execute( self, data, outputFile ):
        retList = self.findCommonInput( data, self.minSearchData )
        if len(retList) < 1:
            print "\nNo keys discovered"
            return

        dataSize = self.dataSize( data )

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
        revDataMask = dataMask.reversedBytes()
        polyMask.reverse()

        polyCRC = self.crcProc.calculate3(revDataMask, polyMask)
        if polyCRC == crcMask.dataNum:
            retList.add( crcKey )


## ============================================


class VerifySolver(Reverse):

    def __init__(self, crcProcessor, printProgress = None):
        Reverse.__init__(self, crcProcessor, printProgress)

    def dataSize( self, data ):
        return data.size()

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

