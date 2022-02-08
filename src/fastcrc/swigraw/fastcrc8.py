##
##
##

import os
import sys

import imp

from . import USE_CACHED_OPERATORS


BASE_DIR = os.path.dirname( __file__ )

BUILD_DIR = os.path.join( BASE_DIR, 'build' )


sys.path.append( BUILD_DIR )


swig_fastcrc_path = os.path.join( BUILD_DIR, 'swigraw_fastcrc.py' )

try:
    swigraw_fastcrc = imp.load_source( 'fastcrc.swigraw_fastcrc', swig_fastcrc_path )

except IOError as ex:
    ## could not load module
    raise ImportError( ex )


## ========================================================================


if USE_CACHED_OPERATORS:

    ##
    class SwigRawData8Operator( object ):

        ## dataBytes: bytes list
        ## dataCRC: int
        def __init__(self, dataBytes, dataCRC):
            self.rawData = convert_to_uint8array( dataBytes )
            self.dataLen = len( dataBytes )
            self.dataCRC = dataCRC

        def __del__(self):
            swigraw_fastcrc.delete_Uint8Array( self.rawData )

        def calculate(self, poly, intReg, xorVal):
            return swigraw_fastcrc.hw_crc8_calculate( self.rawData, self.dataLen, poly & 0xFF, intReg, xorVal )

        def calculateParam(self, poly, intReg, xorVal, reverseOrder, reflectBits):
            return swigraw_fastcrc.hw_crc8_calculate_param( self.rawData, self.dataLen, poly & 0xFF, intReg, xorVal, reverseOrder, reflectBits )

        def calculateRange(self, poly, intRegStart, intRegEnd, xorStart, xorEnd):
            ret_array = swigraw_fastcrc.hw_crc8_calculate_range( self.rawData, self.dataLen, self.dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
            return convert_CRC8ResultArray_to_list( ret_array )

else:

    ## old implementation
    class SwigRawData8Operator( object ):

        ## dataBytes: bytes list
        ## dataCRC: int
        def __init__(self, dataBytes, dataCRC):
            self.dataBytes = dataBytes
            self.dataCRC = dataCRC

        def calculate(self, poly, intReg, xorVal):
            return hw_crc8_calculate( self.dataBytes, poly & 0xFF, intReg, xorVal )

        def calculateParam(self, poly, intReg, xorVal, reverseOrder, reflectBits):
            return hw_crc8_calculate_param( self.dataBytes, poly & 0xFF, intReg, xorVal, reverseOrder, reflectBits )

        def calculateRange(self, poly, intRegStart, intRegEnd, xorStart, xorEnd):
            return hw_crc8_calculate_range( self.dataBytes, self.dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )


## ========================================================================


# def convert_to_uint8array( bytesList ):
#     arr_len  = len(bytesList)
#     data_array = swigraw_fastcrc.Uint8Array( arr_len )
#     for i in xrange( 0, arr_len ):
#         data_array[i] = bytesList[i]
#     return data_array

def convert_to_uint8array( bytesList ):
    arr_len  = len(bytesList)
    data_array = swigraw_fastcrc.new_Uint8Array( arr_len )
    for i in xrange( 0, arr_len ):
        swigraw_fastcrc.Uint8Array_setitem( data_array, i, bytesList[i] )
    return data_array


def convert_CRC8ResultArray_to_list( result_array ):
    ret_size = result_array.size
    retList = []
    for i in xrange(0, ret_size):
        item = swigraw_fastcrc.CRC8ResultArray_getptr( result_array, i )
        retList.append( ( item.reginit, item.xorout ) )

    swigraw_fastcrc.CRC8ResultArray_free( result_array )
    return retList


## ========================================================================


def hw_crc8_calculate( bytesList, poly, intReg, xorVal ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret = swigraw_fastcrc.hw_crc8_calculate( data_array, arr_len, poly & 0xFF, intReg, xorVal )

    swigraw_fastcrc.delete_Uint8Array( data_array )
    return ret
#     return swigraw_fastcrc.hw_crc8_calculate( data_array.cast(), arr_len, poly & 0xFF, intReg, xorVal )


def hw_crc8_calculate_param( bytesList, poly, intReg, xorVal, reverseOrder, reflectBits ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret = swigraw_fastcrc.hw_crc8_calculate_param( data_array, arr_len, poly & 0xFF, intReg, xorVal, reverseOrder, reflectBits )

    swigraw_fastcrc.delete_Uint8Array( data_array )
    return ret
#     return swigraw_fastcrc.hw_crc8_calculate_param( data_array.cast(), arr_len, poly & 0xFF, intReg, xorVal, reverseOrder, reflectBits )


def hw_crc8_calculate_range( bytesList, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd ):
#     print "verify input: 0x%X 0x%X 0x%X 0x%X 0x%X" % ( poly, intRegStart, intRegEnd, xorStart, xorEnd )

    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret_array = swigraw_fastcrc.hw_crc8_calculate_range( data_array, arr_len, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
    swigraw_fastcrc.delete_Uint8Array( data_array )

#    ret_array = swigraw_fastcrc.hw_crc8_calculate_range( data_array.cast(), arr_len, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
    return convert_CRC8ResultArray_to_list( ret_array )
