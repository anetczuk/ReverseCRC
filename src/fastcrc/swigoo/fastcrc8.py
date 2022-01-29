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
  
  
def hw_crc8_calculate( bytesList, poly, intReg, xorVal ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )
    
    return swigoo_fastcrc.hw_crc8_calculate( data_array.cast(), arr_len, poly & 0xFF, intReg, xorVal )
  
  
def hw_crc8_calculate_param( bytesList, poly, intReg, xorVal, reverseOrder, reflectBits ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    return swigoo_fastcrc.hw_crc8_calculate_param( data_array.cast(), arr_len, poly & 0xFF, intReg, xorVal, reverseOrder, reflectBits )
  
  
def hw_crc8_calculate_range( bytesList, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd ):
#     print "verify input: 0x%X 0x%X 0x%X 0x%X 0x%X" % ( poly, intRegStart, intRegEnd, xorStart, xorEnd )
    
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret_array = swigoo_fastcrc.hw_crc8_calculate_range( data_array.cast(), arr_len, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
    
    ret_size = ret_array.size
    retList = []
    for i in xrange(0, ret_size):
        item = swigoo_fastcrc.CRC8ResultArray_getptr( ret_array, i )
        retList.append( ( item.reginit, item.xorout ) )
  
    return retList
