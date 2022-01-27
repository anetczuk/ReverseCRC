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

try:
    swig_fastcrc = imp.load_source( 'swig_fastcrc', swig_fastcrc_path )
    # swig_fastcrc = imp.load_source( 'fastcrc.swig_fastcrc', swig_fastcrc_path )

except IOError as ex:
    ## could not load module
    raise ImportError( ex )


# def convert_to_uint8array( bytesList ):
#     arr_len  = len(bytesList)
#     data_array = swig_fastcrc.Uint8Array( arr_len )
#     for i in xrange( 0, arr_len ):
#         data_array[i] = bytesList[i]
#     return data_array

def convert_to_uint8array( bytesList ):
    arr_len  = len(bytesList)
    data_array = swig_fastcrc.new_Uint8Array( arr_len )
    for i in xrange( 0, arr_len ):
        swig_fastcrc.Uint8Array_setitem( data_array, i, bytesList[i] )
    return data_array


## ========================================================================
  
  
def hw_crc8_calculate( bytesList, poly, intReg, xorVal ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )
    
    ret = swig_fastcrc.hw_crc8_calculate( data_array, arr_len, poly & 0xFF, intReg, xorVal )

    swig_fastcrc.delete_Uint8Array( data_array )
    return ret
#     return swig_fastcrc.hw_crc8_calculate( data_array.cast(), arr_len, poly & 0xFF, intReg, xorVal )
  
  
def hw_crc8_calculate_param( bytesList, poly, intReg, xorVal, reverseOrder, reflectBits ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret = swig_fastcrc.hw_crc8_calculate_param( data_array, arr_len, poly & 0xFF, intReg, xorVal, reverseOrder, reflectBits )

    swig_fastcrc.delete_Uint8Array( data_array )
    return ret
#     return swig_fastcrc.hw_crc8_calculate_param( data_array.cast(), arr_len, poly & 0xFF, intReg, xorVal, reverseOrder, reflectBits )
  
  
def hw_crc8_calculate_range( bytesList, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd ):
#     print "verify input: 0x%X 0x%X 0x%X 0x%X 0x%X" % ( poly, intRegStart, intRegEnd, xorStart, xorEnd )
    
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret_array = swig_fastcrc.hw_crc8_calculate_range( data_array, arr_len, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
    swig_fastcrc.delete_Uint8Array( data_array )

#    ret_array = swig_fastcrc.hw_crc8_calculate_range( data_array.cast(), arr_len, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
    
    ret_size = ret_array.size
    retList = []
    for i in xrange(0, ret_size):
        item = swig_fastcrc.CRC8ResultArray_getptr( ret_array, i )
        retList.append( ( item.reginit, item.xorout ) )
  
    swig_fastcrc.CRC8ResultArray_free( ret_array )
    return retList
