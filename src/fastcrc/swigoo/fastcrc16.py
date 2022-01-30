##
##
##

import os
import sys

import imp


BASE_DIR = os.path.dirname( __file__ )

BUILD_DIR = os.path.join( BASE_DIR, 'build' )


sys.path.append( BUILD_DIR )


swig_fastcrc_path = os.path.join( BUILD_DIR, 'swigoo_fastcrc.py' )

try:
    swigoo_fastcrc = imp.load_source( 'fastcrc.swigoo_fastcrc', swig_fastcrc_path )

except IOError as ex:
    ## could not load module
    raise ImportError( ex )


def convert_to_uint8array( bytesList ):
    arr_len  = len(bytesList)
    data_array = swigoo_fastcrc.Uint8Array( arr_len )
    for i in xrange( 0, arr_len ):
        data_array[i] = bytesList[i]
    return data_array


## ========================================================================


def hw_crc16_calculate( bytesList, poly, intReg, xorVal ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    return swigoo_fastcrc.hw_crc16_calculate( data_array.cast(), arr_len, poly, intReg, xorVal )


def hw_crc16_calculate_param( bytesList, poly, intReg, xorVal, reverseOrder, reflectBits ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    return swigoo_fastcrc.hw_crc16_calculate_param( data_array.cast(), arr_len, poly, intReg, xorVal, reverseOrder, reflectBits )


def hw_crc16_calculate_range( bytesList, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret_array = swigoo_fastcrc.hw_crc16_calculate_range( data_array.cast(), arr_len, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )

    data_size = ret_array.size
    retList = []
    for i in xrange(0, data_size):
        item = swigoo_fastcrc.CRC16ResultArray_getptr( ret_array, i )
        retList.append( ( item.reginit, item.xorout ) )

    return retList


def hw_crc16_invert( bytesList, poly, regVal ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret_array = swigoo_fastcrc.hw_crc16_invert( data_array.cast(), arr_len, poly, regVal )

    ret_size = ret_array.size
    retList = []
    for i in xrange(0, ret_size):
        item = swigoo_fastcrc.uint16_array_getvalue( ret_array, i )
        retList.append( item )
#     retList = list( data_content )

    return retList


def hw_crc16_invert_range( bytesList, crcNum, poly, xorStart, xorEnd):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret_array = swigoo_fastcrc.hw_crc16_invert_range( data_array.cast(), arr_len, crcNum, poly, xorStart, xorEnd )

    data_size = ret_array.size
    xorList = dict()
    for i in xrange(0, data_size):
        item = swigoo_fastcrc.CRC16ResultArray_getptr( ret_array, i )
        regList = xorList.get( item.xorout, None )
        if regList is None:
            regList = list()
            xorList[ item.xorout ] = regList
        regList.append( item.reginit )

    return xorList.items()
