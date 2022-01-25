##
##
##

import os
import sys

import imp


BASE_DIR = os.path.dirname( __file__ )

BUILD_DIR = os.path.join( BASE_DIR, 'build' )


sys.path.append( BUILD_DIR )


swig_fastcrc_path = os.path.join( BUILD_DIR, 'swig_fastcrc.py' )

swig_fastcrc = imp.load_source( 'fastcrc.swig_fastcrc', swig_fastcrc_path )


def convert_to_uint8array( bytesList ):
    arr_len  = len(bytesList)
    data_array = swig_fastcrc.new_Uint8Array( arr_len )
    for i in xrange( 0, arr_len ):
        swig_fastcrc.Uint8Array_setitem( data_array, i, bytesList[i] )
    return data_array


## ========================================================================


def hw_crc16_calculate( bytesList, poly, intReg, xorVal ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )
        
    ret = swig_fastcrc.hw_crc16_calculate( data_array, arr_len, poly, intReg, xorVal )
    swig_fastcrc.delete_Uint8Array( data_array )
    
    return ret


def hw_crc16_calculate_param( bytesList, poly, intReg, xorVal, reverseOrder, reflectBits ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )
    
    ret = swig_fastcrc.hw_crc16_calculate_param( data_array, arr_len, poly, intReg, xorVal, reverseOrder, reflectBits )
    swig_fastcrc.delete_Uint8Array( data_array )
    
    return ret


def hw_crc16_calculate_range( bytesList, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )
        
    ret_array = swig_fastcrc.hw_crc16_calculate_range( bytesList, arr_len, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
    swig_fastcrc.delete_Uint8Array( data_array )
    
    data_size = ret_array.size
    retList = []
    for i in xrange(0, data_size):
        item = ret_array.data[ i ]
        retList.append( ( item.reginit, item.xorout ) )
 
    swig_fastcrc.CRC16ResultArray_free( ret_array )
    return retList


def hw_crc16_invert( bytesList, poly, regVal ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret_array = swig_fastcrc.hw_crc16_invert( data_array, arr_len, poly, regVal )
    swig_fastcrc.delete_Uint8Array( data_array )
    
    ret_size = ret_array.size
    retList = []
    for i in xrange(0, ret_size):
        item = swig_fastcrc.uint16_array_getvalue( ret_array, i )
        retList.append( item )
#     retList = list( data_content )
 
    swig_fastcrc.uint16_array_free( ret_array )
    return retList

def hw_crc16_invert_range( bytesList, crcNum, poly, xorStart, xorEnd):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )
        
    ret_array = swig_fastcrc.hw_crc16_invert_range( data_array, arr_len, crcNum, poly, xorStart, xorEnd )
    swig_fastcrc.delete_Uint8Array( data_array )
    
    data_size = ret_array.size
    xorList = dict()
    for i in xrange(0, data_size):
        item = swig_fastcrc.CRC16ResultArray_getptr( ret_array, i )
        regList = xorList.get( item.xorout, None )
        if regList is None:
            regList = list()
            xorList[ item.xorout ] = regList
        regList.append( item.reginit )
 
    swig_fastcrc.CRC16ResultArray_free( ret_array )
    return xorList.items()
