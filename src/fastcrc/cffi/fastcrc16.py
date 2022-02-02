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


##
class Data16Operator( object ):

    ## dataBytes: bytes list
    ## dataCRC: int
    def __init__(self, dataBytes, dataCRC):
        self.rawData = dataBytes                    ## no need to convert data
        self.dataLen = len( dataBytes )
        self.dataCRC = dataCRC

#     def __del__(self):
#         ## do nothing -- data will be released automatically
#         pass

    def calculate(self, poly, intReg, xorVal):
        return cffi_fastcrc.hw_crc16_calculate( self.rawData, self.dataLen, poly, intReg, xorVal )

    def calculateParam(self, poly, intReg, xorVal, reverseOrder, reflectBits):
        return cffi_fastcrc.hw_crc16_calculate_param( self.rawData, self.dataLen, poly, intReg, xorVal, reverseOrder, reflectBits )

    def calculateRange(self, poly, intRegStart, intRegEnd, xorStart, xorEnd):
        ret_array = cffi_fastcrc.hw_crc16_calculate_range( self.rawData, self.dataLen, self.dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
        return convert_CRC16ResultArray_to_list( ret_array )

    def invert(self, poly, regVal):
        ret_array = cffi_fastcrc.hw_crc16_invert( self.rawData, self.dataLen, poly, regVal )
        return convert_uint16_array_to_list( ret_array )

    def invertRange(self, crcNum, poly, xorStart, xorEnd):
        ret_array = cffi_fastcrc.hw_crc16_invert_range( self.rawData, self.dataLen, crcNum, poly, xorStart, xorEnd )
        xorList = convert_CRC16ResultArray_to_dict( ret_array )
        return xorList.items()                                          ## return list of pairs


## ========================================================================


def convert_CRC16ResultArray_to_list( result_array ):
    data_size = result_array.size
    retList = []
    for i in xrange(0, data_size):
        item = result_array.data[ i ]
        retList.append( ( item.reginit, item.xorout ) )

    cffi_fastcrc.CRC16ResultArray_free( result_array )
    return retList


def convert_CRC16ResultArray_to_dict( result_array ):
    data_size = result_array.size
    xorList = dict()
    for i in xrange(0, data_size):
        item = result_array.data[ i ]
        regList = xorList.get( item.xorout, None )
        if regList is None:
            regList = list()
            xorList[ item.xorout ] = regList
        regList.append( item.reginit )

    cffi_fastcrc.CRC16ResultArray_free( result_array )
    return xorList


def convert_uint16_array_to_list( result_array ):
    data_size = result_array.size
    retList = []
    for i in xrange(0, data_size):
        item = result_array.data[ i ]
        retList.append( item )
#     retList = list( data_content )

    cffi_fastcrc.uint16_array_free( result_array )
    return retList


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
    return convert_CRC16ResultArray_to_list( data_array )


def hw_crc16_invert( bytesList, poly, regVal ):
    arr_len  = len(bytesList)
    data_array = cffi_fastcrc.hw_crc16_invert( bytesList, arr_len, poly, regVal )

#     data_array = ffi.gc(data_array, cffi_fastcrc.uint16_array_free)
#     return CFFIArrayWrapper( data_array )

    return convert_uint16_array_to_list( data_array )


def hw_crc16_invert_range( bytesList, crcNum, poly, xorStart, xorEnd):
    arr_len  = len(bytesList)
    data_array = cffi_fastcrc.hw_crc16_invert_range( bytesList, arr_len, crcNum, poly, xorStart, xorEnd )

#     data_array = ffi.gc(data_array, cffi_fastcrc.CRC16ResultArray_free)
#     return CFFIArrayWrapper( data_array )

    xorList = convert_CRC16ResultArray_to_dict( data_array )
    return xorList.items()                                          ## return list of pairs
