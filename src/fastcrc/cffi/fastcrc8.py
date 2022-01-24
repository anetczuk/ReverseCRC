##
##
##

import os
import sys

import cffi


BASE_DIR = os.path.dirname( __file__ )

sys.path.append( os.path.join( BASE_DIR, 'build') )


import cffi_fastcrc.lib as cffi_fastcrc


ffi = cffi.FFI()


## ========================================================================


# class CFFIArrayWrapper():
#     
#     def __init__(self, pointer):
#         self.ptr = pointer
#     
#     def __len__(self):
#         return self.ptr.size
#     
#     def __getitem__(self, index):
#         return self.ptr.data[ index ]
#     
#     def __nonzero__(self):
#         return self.ptr.size > 0


## ========================================================================
 
 
def hw_crc8_calculate( bytesList, poly, intReg, xorVal ):
    arr_len  = len(bytesList)
    return cffi_fastcrc.hw_crc8_calculate( bytesList, arr_len, poly & 0xFF, intReg, xorVal )
 
 
def hw_crc8_calculate_param( bytesList, poly, intReg, xorVal, reverseOrder, reflectBits ):
    arr_len  = len(bytesList)
#     print "hw_crc8_calculate_param:", bytesList, arr_len, poly & 0xFF, intReg, xorVal, reverseOrder, reflectBits
    return cffi_fastcrc.hw_crc8_calculate_param( bytesList, arr_len, poly & 0xFF, intReg, xorVal, reverseOrder, reflectBits )
 
 
def hw_crc8_calculate_range( bytesList, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd ):
#     print "verify input: 0x%X 0x%X 0x%X 0x%X 0x%X" % ( poly, intRegStart, intRegEnd, xorStart, xorEnd )
     
    arr_len  = len(bytesList)
    data_array = cffi_fastcrc.hw_crc8_calculate_range( bytesList, arr_len, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
    
#     data_array = ffi.gc(data_array, cffi_fastcrc.CRC8ResultArray_free)
#     return CFFIArrayWrapper( data_array )

    data_size = data_array.size
    retList = []
    for i in xrange(0, data_size):
        item = data_array.data[ i ]
        retList.append( ( item.reginit, item.xorout ) )
 
    cffi_fastcrc.CRC8ResultArray_free( data_array )
    return retList
