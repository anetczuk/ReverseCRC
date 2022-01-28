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

import os
import copy
import imp

from crc.crcproc import CRCBackwardProc

from fastcrc.binding import convert_to_list

from fastcrc.paths import FASTCRC_CLIB_SRC_DIR


## import code from directory that is not a package
base_dir = os.path.dirname( __file__ )

generate_lookup8_path = os.path.join( FASTCRC_CLIB_SRC_DIR, "crchw", "generate_lookup8.py" )
generate_lookup8 = imp.load_source( 'fastcrc.generate_lookup8', generate_lookup8_path )

# generate_lookup16_path = os.path.join( base_dir, os.pardir, "fastcrc", "src", "crchw", "generate_lookup16.py" )
# generate_lookup16 = imp.load_source( 'fastcrc.generate_lookup16', generate_lookup16_path )


## ============================================


##
## reg_next =  LT[ poly ][ reg ^ data ]
## ILT[ poly ][ reg_next ] -- returns list of potential "reg" values
##
class InvertLookupTable8():

    def __init__(self):
        self.data = None

    def getPolyDict(self, poly):
        if self.data is None:
            self.data = self._generate()
        return self.data[ poly ]

    def _generate(self):
        data = list()
        for poly in xrange(0, 0x100):
            polyDict = dict()
            data.append( polyDict )
            lookup_table = generate_lookup8.generate_subtable( poly )
            lookupSize = len( lookup_table )
            for key in xrange(0, lookupSize):
                value = lookup_table[ key ]
                regList = polyDict.get( value )
                if regList is None:
                    regList = set()
                    polyDict[ value ] = regList
                regList.add( key )
        return data


##
## poly      -- 16 bit
## reg       -- 16 bit
## reg_next  -- 16 bit
## data      --  8 bit
##
## reg_next = (reg << 8) ^ LT[ poly ][ (reg >> 8) ^ data ]
## ILT[ poly ][ data ][ reg_next ] -- returns list of potential "reg" values
##
class InvertLookupTable16():
    
    def __init__(self):
        pass

    def generate(self):
        ## to be implemented, but it seems that declaring 
        ## static structure of 65536 * 256 * 65536 ~= 1 100 000 000 000
        ## is too much
        pass


class InvertCache():
    
    def __init__(self, polySpaceSize, subSpaceSize=None):
        self.data = list()
        if subSpaceSize is None:
            for _ in xrange(0, polySpaceSize):
                self.data.append( dict() )
        else:
            for _ in xrange(0, polySpaceSize):
                data_dict = list()
                self.data.append( data_dict )
                for _2 in xrange(0, subSpaceSize):
                    data_dict.append( dict() )

    def getPolyDict(self, poly):
        return self.data[ poly ]


INVERSE_TABLE8  = InvertLookupTable8()
INVERSE_CACHE8  = InvertCache( 0x100 )

INVERSE_CACHE16 = InvertCache( 0x10000 )


## ============================================


class HwCRCBackwardState:

    def __init__(self, reg = 0x0):
        self.register = reg

    def copy(self):
        return copy.copy(self)

    def shiftBit(self, regBit, dataBit, revMode = False):
        if revMode == False:
            self.shiftMSB(regBit, dataBit)
        else:
            self.shiftLSB(regBit, dataBit)

#     ## 'regBit' says what bit add to register
#     def shiftMSB(self, regBit, dataBit, polyMask):
#         ## reversing MSB mode
#         if regBit == True:
#             self.register ^= polyMask.dataNum
#             ## valid if last bit is '0'
#             ## it's not allowed to pop 1 from register
#             if (self.register & 1) != 0:
#                 return False
#             self.register |= polyMask.masterBit        ## add master bit to MSB
#         else:
#             ## valid if last bit is '0'
#             ## it's not allowed to pop 1 from register
#             if (self.register & 1) != 0:
#                 return False
#         if dataBit > 0:
#             self.register ^= polyMask.masterBit
#         self.register >>= 1
#         return True

    def shiftMSB_1(self, dataBit, polyMask):
        ## reversing MSB mode

        self.register ^= polyMask.dataNum
        
        ## valid if last bit is '0'
        ## it's not allowed to pop 1 from register
        if (self.register & 1) != 0:
            return False
        
        if dataBit == 0:
            self.register |= polyMask.masterBit        ## add master bit to MSB
        self.register >>= 1
        return True

    def shiftMSB_0(self, dataBit, polyMask):
        ## reversing MSB mode
        
        ## valid if last bit is '0'
        ## it's not allowed to pop 1 from register
        if (self.register & 1) != 0:
            return False
            
        if dataBit > 0:
            self.register ^= polyMask.masterBit
        self.register >>= 1
        return True

    ## shift both 0 and 1 at once
    def shiftMSB_Both(self, dataBit, polyMask):
        ## valid if last bit is '0'
        ## it's not allowed to pop 1 from register
        if (self.register & 1) != 0:
            ## shifting zero is invalid -- shift 1
            if self.shiftMSB_1( dataBit, polyMask ):
#                 print "p pushing 1: 0x%X" % self.register
                return [self]
            return []
 
        ## zero or one
        reg_one = self.register ^ polyMask.dataNum
 
        ## treat self as 0
        if dataBit > 0:
            self.register ^= polyMask.masterBit
        self.register >>= 1
          
        ## valid if last bit is '0'
        ## it's not allowed to pop 1 from register
        if (reg_one & 1) != 0:
            ## shifting one is invalid -- shift 0
#             print "p pushing 0: 0x%X" % self.register
            return [self]

        ## for one    
        if dataBit == 0:
            reg_one |= polyMask.masterBit        ## add master bit to MSB
        reg_one >>= 1

#         print "p pushing 0: 0x%X" % self.register
#         print "p pushing 1: 0x%X" % reg_one
        return [ self, HwCRCBackwardState(reg_one) ]

    ## 'regBit' says what bit add to register
    def shiftLSB(self, regBit, dataBit, polyMask):
        ## reversing LSB mode
        if regBit == True:
            self.register ^= polyMask.dataNum
            self.register <<= 1
            self.register |= 1
        else:
            self.register <<= 1
        ## valid if last bit is '0'
        ## it's not allowed to pop 1 from register
        if (self.register & polyMask.masterBit) != 0:
            return False
        if dataBit > 0:
            self.register ^= 1
        return True


    def __repr__(self):
        return "<HwCRCBState cs:{} r:0x{:X}>".format( self.crcSize, self.register )

    def __eq__(self, other):
        if self.register != other.register:
            return False
        return True

    def __ne__(self, other):
        return ((self == other) == False)

    def __hash__(self):
        return hash( self.register )


## ==========================================================


class HwCRCBackward( CRCBackwardProc ):
    
    def __init__(self):
        CRCBackwardProc.__init__(self)
        self._reverseMode = False
        self.setReversed( False )

    def setReversed(self, value = True):
        self._reverseMode = value
        
        ## optimize execution time by reducing one level of function call
        if value is False:
            self.calculateInitRegBase = self.calculateTabularMSB
        else:
            self.calculateInitRegBase = self.calculateInitRegBaseLSB

    ## polyMask -- NumberMask
    ## dataMask -- NumberMask
    def calculateTabularMSB(self, dataMask, polyMask, crc_raw):
        if polyMask.dataSize == 8:
            regList = self._calculateLookup8MSB(dataMask, polyMask.dataNum, crc_raw)
#             regList = self._calculateCachedMSB(dataMask, polyMask, crc_raw, INVERSE_CACHE8)
            if not regList:
                return []
            if dataMask.dataSize % 8 == 0:
                return regList
            full_bytes = int( dataMask.dataSize / 8 )
            bitStart = full_bytes * 8
            return self._calculateBitsMSB( dataMask.dataNum, bitStart, dataMask.dataSize, polyMask, regList )
        
        elif polyMask.dataSize == 16:
            regList = self._calculateCachedMSB(dataMask, polyMask, crc_raw, INVERSE_CACHE16)
            if not regList:
                return []
            if dataMask.dataSize % 8 == 0:
                return regList
            full_bytes = int( dataMask.dataSize / 8 )
            bitStart = full_bytes * 8
            return self._calculateBitsMSB( dataMask.dataNum, bitStart, dataMask.dataSize, polyMask, regList )

        return self._calculateBitsMSB( dataMask.dataNum, 0, dataMask.dataSize, polyMask, [ crc_raw ] )

    def _calculateLookup8MSB(self, dataMask, poly, crc_raw):
        regList = [crc_raw]

        dataNum = dataMask.dataNum
        poly_lookup = INVERSE_TABLE8.getPolyDict( poly )
        
        full_bytes = int( dataMask.dataSize / 8 )
        for _ in range(0, full_bytes):
            dataByte = dataNum & 0xFF
            newList = []
            for regVal in regList:
                nextRegList = poly_lookup.get( regVal )
                if nextRegList is None:
                    ## no registry value -- invalid case
                    continue
                for nextReg in nextRegList:
                    nextReg ^= dataByte
                    newList.append( nextReg )
            if not newList:
                return []
            regList = newList
            dataNum >>= 8
        
        return regList

    def _calculateCachedMSB(self, dataMask, polyMask, crc_raw, cache_map):
        regList = [crc_raw]

        dataNum = dataMask.dataNum
        poly_lookup = cache_map.getPolyDict( polyMask.dataNum )
        
        full_bytes = int( dataMask.dataSize / 8 )
        for _ in range(0, full_bytes):
            dataByte = dataNum & 0xFF
            
            data_lookup = poly_lookup.get( dataByte )       # dict
            if data_lookup is None:
                data_lookup = dict()
                poly_lookup[ dataByte ] = data_lookup
            
            newList = []
            for regVal in regList:
                
                nextRegList = data_lookup.get( regVal )
                if nextRegList is None:
                    nextRegList = self._calculateBitsMSB( dataByte, 0, 8, polyMask, [regVal] )
                    data_lookup[ regVal ] = nextRegList
                
                if not nextRegList:
                    ## no registry value -- invalid case
                    continue
                newList.extend( nextRegList )

            if not newList:
                return []
            
            regList = newList
            dataNum >>= 8
        
        return regList
    
    def _calculateBitsMSB(self, dataNum, bitStart, bitEnd, polyMask, regList):
        collector = []
        for reg in regList:
            collector.append( HwCRCBackwardState( reg ) )

        dataBit = 1 << bitStart
        for _ in range(bitStart, bitEnd):
            currBit = dataNum & dataBit
            receiver = []
            for c in collector:
#                 byteNum = bitStart / 8
#                 currNum = dataNum >> (byteNum*8)
#                 print "p data: 0x%X %s %s" % ( currNum & 0xFF, currBit, c.register )
                receiver.extend( c.shiftMSB_Both(currBit, polyMask) )

            if len(receiver) < 1:
                return []
            dataBit <<= 1
            collector = receiver

        retList = []
        for item in collector:
            retList.append( item.register )
        return retList
    
    ## ===================================

    def calculateInitRegBaseLSB(self, dataMask, polyMask, crc_raw):
        collector = []
        collector.append( HwCRCBackwardState( crc_raw ) )

        dataNum = dataMask.dataNum
        dataBit = (dataMask.masterBit >> 1)

        for _ in range(0, dataMask.dataSize):
            currBit = dataNum & dataBit
            receiver = []

            for c in collector:
                c1 = c
                c2 = c.copy()
 
                c1_valid = c1.shiftLSB(False, currBit, polyMask)
                if c1_valid:
                    receiver.append(c1)
                c2_valid = c2.shiftLSB(True, currBit, polyMask)
                if c2_valid:
                    receiver.append(c2)

            if len(receiver) < 1:
                return []
            dataBit >>= 1
            collector = receiver

        retList = []
        for item in collector:
            retList.append( item.register )
        return retList


## ==========================================================


def create_backward_processor(crcSize):
    if crcSize != 16:
        return HwCRCBackward()

#     return HwCRCBackward()
    
    
    try:
        from fastcrc.binding import hw_crc16_invert, hw_crc16_invert_range
#     except ImportError as ex:
    except ImportError:
        ## disable fastcrc -- there were problem with importing fastcrc
#         print "unable to import fastcrc:", ex
#         print "WARNING: fast CRC is disabled!!!"
        return HwCRCBackward()


    ## assuming that CRC is 16 bit
    class Fast16HwCRCBackward( HwCRCBackward ):
        
        def __init__(self):
            HwCRCBackward.__init__(self)
            self.fast16Data = dict()
    
        def calculateInitRegRange(self, dataMask, crcNum, polyMask, xorStart, xorEnd):
            if self._reverseMode is False:
                ## use fast implementation
                if dataMask.dataSize % 8 == 0:
                    full_bytes = int( dataMask.dataSize / 8 )
                    dataNum = dataMask.dataNum
                    bytes_list = self.fast16Data.get( dataNum )
                    if bytes_list is None:
                        bytes_list = convert_to_list( dataNum, full_bytes  )
                        self.fast16Data[ dataNum ] = bytes_list 
                    return hw_crc16_invert_range( bytes_list, crcNum, polyMask.dataNum, xorStart, xorEnd )
    
            ## use standard implementation
            return HwCRCBackward.calculateInitRegRange(self, dataMask, crcNum, polyMask, xorStart, xorEnd)
    
        ## polyMask -- NumberMask
        ## dataMask -- NumberMask
        def calculateTabularMSB(self, dataMask, polyMask, crc_raw):
            regList = self._calculateFast16MSB(dataMask, polyMask.dataNum, crc_raw)
            if not regList:
                return []
            if dataMask.dataSize % 8 == 0:
                return regList
            full_bytes = int( dataMask.dataSize / 8 )
            bitStart = full_bytes * 8
            return self._calculateBitsMSB( dataMask.dataNum, bitStart, dataMask.dataSize, polyMask, regList )
    
        ### implementation of "self._calculateBitsMSB()" method using C
        def _calculateFast16MSB(self, dataMask, poly, crc_raw):
            full_bytes = int( dataMask.dataSize / 8 )
            dataNum = dataMask.dataNum
            bytes_list = self.fast16Data.get( dataNum )
            if bytes_list is None:
                bytes_list = convert_to_list( dataNum, full_bytes  )
                self.fast16Data[ dataNum ] = bytes_list 
            return hw_crc16_invert( bytes_list, poly, crc_raw )

    return Fast16HwCRCBackward()
