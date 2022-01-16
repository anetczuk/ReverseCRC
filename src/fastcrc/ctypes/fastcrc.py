##
##
##

import os
import ctypes


base_dir = os.path.dirname( __file__ )

fastcrc_path = os.path.join( base_dir, os.pardir, "build", "install", "libfastcrc.so" )

c_fastcrc = ctypes.CDLL( fastcrc_path )


## least significant byte goes first in list
def convert_to_lsb_list( number, numberBytesSize ):
    retList = []
    for _ in range(numberBytesSize):
        byte = number & 0xFF
        retList.append( byte )
        number = number >> 8
    return retList


## most significant byte goes first in list
def convert_to_msb_list( number, numberBytesSize ):
    retList = []
    for _ in range(numberBytesSize):
        byte = number & 0xFF
        retList.append( byte )
        number = number >> 8
    ## appending and list reverse is faster than inserting at front of list
    retList.reverse()
    return retList


c_fastcrc.hw_crc8_calculate.restype = ctypes.c_ubyte
def hw_crc8_calculate( dataList, poly, intReg, xorVal ):
    arr_len  = len(dataList)
    arr_type = ctypes.c_ubyte * arr_len
    arr      = arr_type( *dataList )
    return c_fastcrc.hw_crc8_calculate( arr, arr_len, poly, intReg, xorVal )
    
