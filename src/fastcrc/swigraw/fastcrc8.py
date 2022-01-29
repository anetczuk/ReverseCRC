##
##
##

import os
import sys

import imp


BASE_DIR = os.path.dirname( __file__ )

BUILD_DIR = os.path.join( BASE_DIR, 'build' )


sys.path.append( BUILD_DIR )


swig_fastcrc_path = os.path.join( BUILD_DIR, 'swigraw_fastcrc.py' )

try:
    swigraw_fastcrc = imp.load_source( 'fastcrc.swigraw_fastcrc', swig_fastcrc_path )

except IOError as ex:
    ## could not load module
    raise ImportError( ex )


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
    
    ret_size = ret_array.size
    retList = []
    for i in xrange(0, ret_size):
        item = swigraw_fastcrc.CRC8ResultArray_getptr( ret_array, i )
        retList.append( ( item.reginit, item.xorout ) )
  
    swigraw_fastcrc.CRC8ResultArray_free( ret_array )
    return retList
