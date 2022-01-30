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

import math

from crc.numbermask import reverse_number, NumberMask
from collections import Counter


class PolyKey:
    def __init__(self, poly=-1, dataPos=-1, dataLen=-1, rev=None, revOrd=None, refBits=None ):
        self.poly = poly

        self.revOrd  = False
        self.refBits = False
        if rev is not None:
            self.revOrd  = rev
            self.refBits = rev
        if revOrd is not None:
            self.revOrd = revOrd
        if refBits is not None:
            self.refBits = refBits

        self.dataPos = dataPos
        self.dataLen = dataLen
        self.crcSize = None

    def __repr__(self):
        return "<PolyKey p:0x{:X} ro:{:} rb:{:} dP:{:} dL:{:}>".format(self.poly, self.revOrd, self.refBits, self.dataPos, self.dataLen)

    def __eq__(self, other):
        if self.poly != other.poly:
            return False
        if self.revOrd != other.revOrd:
            return False
        if self.refBits != other.refBits:
            return False
        if self.dataPos != other.dataPos:
            return False
        if self.dataLen != other.dataLen:
            return False
        return True

    def __ne__(self, other):
        return ((self == other) == False)

    def __hash__(self):
        return hash( str(self.poly) + str(self.revOrd) + str(self.refBits) )

    ## for backward compatibility
    def isReversedFully(self):
        return self.revOrd and self.refBits

    def getPolyKey(self):
        return self

    def size(self):
        if self.crcSize is None:
            if self.poly < 1:
                self.crcSize = 0
            else:
                self.crcSize = int( math.log( self.poly, 2 ) )
        return self.crcSize


class CRCKey:
    def __init__( self, poly=-1, init=-1, xor=-1, dataPos=-1, dataLen=-1, rev=None, revOrd=None, refBits=None ):
        self.poly = poly                    ## with leading 1

        self.revOrd  = False
        self.refBits = False
        if rev is not None:
            self.revOrd  = rev
            self.refBits = rev
        if revOrd is not None:
            self.revOrd = revOrd
        if refBits is not None:
            self.refBits = refBits

        self.init = init
        self.xor = xor
        self.dataPos = dataPos              ## counts starting from LSB
        self.dataLen = dataLen
        self.crcSize = None

    def __repr__(self):
        crc_size = str( self.size() / 4 )
        template = "<CRCKey p:0x{:X} i:0x{:0" + crc_size + "X} x:0x{:0" + crc_size + "X} ro:{:} rb:{:} dP:{:} dL:{:}>"
#         print "template:", template
#         print "input:", type(self.poly), type(self.init), type(self.xor), type(self.revOrd), type(self.refBits), type(self.dataPos), type(self.dataLen)
        return template.format(self.poly, self.init, self.xor, self.revOrd, self.refBits, self.dataPos, self.dataLen)

    def __eq__(self, other):
        if self.poly != other.poly:
            return False
        if self.revOrd != other.revOrd:
            return False
        if self.refBits != other.refBits:
            return False
        if self.init != other.init:
            return False
        if self.xor != other.xor:
            return False
        if self.dataPos != other.dataPos:
            return False
        if self.dataLen != other.dataLen:
            return False
        return True

    def __ne__(self, other):
        return ((self == other) == False)

    def __hash__(self):
#         return hash(str(self.poly) + str(self.init) + str(self.xor))
        return hash( (self.poly, self.init, self.xor) )

    def size(self):
        if self.crcSize is None:
            if self.poly < 1:
                self.crcSize = 0
            else:
                self.crcSize = int( math.log( self.poly, 2 ) )
        return self.crcSize

    ## for backward compatibility
    def isReversedFully(self):
        return self.revOrd and self.refBits

    def getPolyKey(self):
        return PolyKey( self.poly, self.dataPos, self.dataLen, self.revOrd, self.refBits )


## ===================================================================


class CRCProcessorFactory(object):

    def __init__(self):
        pass

    # crcSize -- int, number of bits
    # return CRCProc
    def createForwardProcessor(self, crcSize=None):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )

    # crcSize -- int, number of bits
    # return CRCBackwardProc
    def createBackwardProcessor(self, crcSize=None):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )

    # crcSize -- int, number of bits
    # inputData: List[ (NumberMask, NumberMask) ]
    # return CRCOperator
    def createOperator(self, crcSize, inputData):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )


## ===================================================================


class CRCProc(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.reset()

    def reset(self):
        self.registerInit = 0x0
        self.xorOut = 0x0
        self._reversed = False              ## do not set field directly, use setter
        ## controls if input and result should be reflected during calculation
        self.setReversed( False )

    def setInitValue(self, value):
        self.registerInit = value

    def setRegisterInitValue(self, value):
        self.registerInit = value

    def setXorOutValue(self, value):
        self.xorOut = value

    def setInitCRC(self, value, crcSize):
        self.registerInit = value ^ self.xorOut
        if self._reversed == True:
            self.registerInit = reverse_number(self.registerInit, crcSize)

    def setReversed(self, value = True):
        self._reversed = value

    # crcKey -- CRCKey
    def setValues(self, crcKey):
        self.setReversed( crcKey.isReversedFully() )
        self.setXorOutValue( crcKey.xor )
        self.setRegisterInitValue( crcKey.init )

    ## 'poly' with leading '1'
    def calculate(self, data, poly):
        return self.calculate2(data, data.bit_length(), poly, poly.bit_length()-1)

    def calculate2(self, data, dataSize, poly, crcSize):
        dataMask = NumberMask(data, dataSize)
        polyMask = NumberMask(poly, crcSize)
        return self.calculate3(dataMask, polyMask)

    ## returns calculated CRC
    def calculate3(self, dataMask, polyMask):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )

    def calculateCRC( self, data, dataSize, poly, crcSize, init=0, xorout=0, reverse=False ):
        self.setReversed( reverse )
        self.setRegisterInitValue( init )
        self.setXorOutValue( xorout )
        crc = self.calculate2(data, dataSize, poly, crcSize)
        return crc

    ## inputData: List[ (NumberMask, NumberMask) ]
    def createOperator(self, crcSize, inputData):
        return self.createStandardOperator( crcSize, inputData )

    def createStandardOperator(self, crcSize, inputData):
#         print( "creating StandardCRCOperator" )
        return StandardCRCOperator( self, inputData )

    def createBackwardProcessor(self, crcSize):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )


## =================================================================


class CRCBackwardProc( object ):

    def __init__(self):
        pass

    def setReversed(self, value = True):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )

    def calculate(self, polyMask, xorOut):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )

    def calculateInitReg(self, dataMask, crc, polyMask, xorOut):
        crc_raw = crc ^ xorOut
        return self.calculateInitRegBase( dataMask, polyMask, crc_raw )

    def calculateInitRegBase(self, dataMask, polyMask, crc_raw):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )

    def calculateInitRegRange(self, dataMask, crcNum, polyMask, xorStart, xorEnd):
        ## default (standard) implementation
        xorDict = list()
        for xorOut in xrange(xorStart, xorEnd + 1):
            crc_raw = crcNum ^ xorOut
            init_found = self.calculateInitRegBase( dataMask, polyMask, crc_raw )
            if init_found:
                #xorDict[ xorOut ] = init_found
                xorDict.append( (xorOut, init_found) )
        return xorDict


## =================================================================


##
class CRCOperator(object):

    def __init__(self):
        pass

    def calculate(self, polyMask):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )

    ## return CRC if matches any data
    def calculateRange(self, polyMask, intRegStart, intRegEnd, xorStart, xorEnd):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )

    def verify(self, polyMask):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )

    ## return CRC if matches for all data
    def verifyRange(self, polyMask, intRegStart, intRegEnd, xorStart, xorEnd):
        raise NotImplementedError( "%s not implemented abstract method" % type(self) )


class ResultContainer( object ):
    def __init__(self):
        self.data = set()

    def empty(self):
        return len( self.data ) < 1

    def intersect(self, resultList):
        if self.data:
            common = self.data.intersection( resultList )
            if not common:
                return False
            self.data = common
        else:
            ## no results -- init
            self.data.update( resultList )
        return len( self.data ) > 0


class StandardCRCOperator( CRCOperator ):

    def __init__(self, crcProcessor, inputData):
        CRCOperator.__init__(self)
        self.processor = crcProcessor               ## CRCProc
        self.data = inputData                       ## List[ (NumberMask, NumberMask) ]

    def calculate(self, polyMask):
        retList = []
        for num in self.data:
            dataMask = num[0]
            crc = self.processor.calculate3( dataMask, polyMask )
            retList.append( crc )
        return retList

    def verify(self, polyMask):
        for item in self.data:
            dataMask = item[0]
            crcMask  = item[1]
            crc = self.processor.calculate3( dataMask, polyMask )
            if crc != crcMask.dataNum:
                return False

        ## all CRC matches
        return True

    ## return CRC if matches any data
    def calculateRange(self, polyMask, intRegStart, intRegEnd, xorStart, xorEnd):
#         print "verify input: 0x%X 0x%X 0x%X 0x%X 0x%X" % ( polyMask.dataNum, intRegStart, intRegEnd, xorStart, xorEnd )

        results = Counter()

        for item in self.data:
            dataMask = item[0]
            crcMask  = item[1]

            crc_match = []
            for self.processor.registerInit in xrange(intRegStart, intRegEnd + 1):
                for self.processor.xorOut in xrange(xorStart, xorEnd + 1):
                    crc = self.processor.calculate3( dataMask, polyMask )
                    if crc == crcMask.dataNum:
                        crc_match.append( ( self.processor.registerInit, self.processor.xorOut ) )
            results.update( crc_match )

        return results

    ## return CRC if matches for all data
    def verifyRange(self, polyMask, intRegStart, intRegEnd, xorStart, xorEnd):
        if not self.data:
            return []

        ## first item -- standard iteration
        item = self.data[0]
        dataMask = item[0]
        crcMask  = item[1]

        crc_match = []
        for self.processor.registerInit in xrange(intRegStart, intRegEnd + 1):
            for self.processor.xorOut in xrange(xorStart, xorEnd + 1):
                crc = self.processor.calculate3( dataMask, polyMask )
                if crc == crcMask.dataNum:
                    crc_match.append( ( self.processor.registerInit, self.processor.xorOut ) )
        results = crc_match
        if not results:
            ## no common result found -- return
            return []

        ##
        ## iterate over rest elements
        ##
        for item in self.data[1:]:
            dataMask = item[0]
            crcMask  = item[1]

            ## results from previous data item -- reuse
            crc_match = []
            for item in results:
                self.processor.registerInit = item[0]
                self.processor.xorOut       = item[1]
                crc = self.processor.calculate3( dataMask, polyMask )
                if crc == crcMask.dataNum:
                    crc_match.append( ( self.processor.registerInit, self.processor.xorOut ) )

            results = crc_match
            if not results:
                ## no common result found -- return
                return []

        return results
