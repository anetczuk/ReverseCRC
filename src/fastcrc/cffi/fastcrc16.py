##
##
##

import cffi

from fastcrc8 import cffi_fastcrc


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


def hw_crc16_calculate( bytesList, poly, intReg, xorVal ):
    arr_len  = len(bytesList)
    return cffi_fastcrc.hw_crc16_calculate( bytesList, arr_len, poly, intReg, xorVal )


def hw_crc16_calculate_param( bytesList, poly, intReg, xorVal, reverseOrder, reflectBits ):
    arr_len  = len(bytesList)
    return cffi_fastcrc.hw_crc16_calculate_param( bytesList, arr_len, poly, intReg, xorVal, reverseOrder, reflectBits )


def hw_crc16_calculate_range( bytesList, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd ):
    arr_len  = len(bytesList)
    data_array = cffi_fastcrc.hw_crc16_calculate_range( bytesList, arr_len, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )

#     data_array = ffi.gc(data_array, cffi_fastcrc.CRC16ResultArray_free)
#     return CFFIArrayWrapper( data_array )

    data_size = data_array.size
    retList = []
    for i in xrange(0, data_size):
        item = data_array.data[ i ]
        retList.append( ( item.reginit, item.xorout ) )

    cffi_fastcrc.CRC16ResultArray_free( data_array )
    return retList


def hw_crc16_invert( bytesList, poly, regVal ):
    arr_len  = len(bytesList)
    data_array = cffi_fastcrc.hw_crc16_invert( bytesList, arr_len, poly, regVal )

#     data_array = ffi.gc(data_array, cffi_fastcrc.uint16_array_free)
#     return CFFIArrayWrapper( data_array )

    data_size = data_array.size
    retList = []
    for i in xrange(0, data_size):
        item = data_array.data[ i ]
        retList.append( item )
#     retList = list( data_content )

    cffi_fastcrc.uint16_array_free( data_array )
    return retList

def hw_crc16_invert_range( bytesList, crcNum, poly, xorStart, xorEnd):
    arr_len  = len(bytesList)
    data_array = cffi_fastcrc.hw_crc16_invert_range( bytesList, arr_len, crcNum, poly, xorStart, xorEnd )

#     data_array = ffi.gc(data_array, cffi_fastcrc.CRC16ResultArray_free)
#     return CFFIArrayWrapper( data_array )

    data_size = data_array.size
    xorList = dict()
    for i in xrange(0, data_size):
        item = data_array.data[ i ]
        regList = xorList.get( item.xorout, None )
        if regList is None:
            regList = list()
            xorList[ item.xorout ] = regList
        regList.append( item.reginit )

    cffi_fastcrc.CRC16ResultArray_free( data_array )
    return xorList.items()
