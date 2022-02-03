##
##
##

import ctypes

from fastcrc8 import c_fastcrc


## ========================================================================


##
class CTypesData16Operator( object ):

    ## dataBytes: bytes list
    ## dataCRC: int
    def __init__(self, dataBytes, dataCRC):
        arr_len  = len(dataBytes)
        arr_type = ctypes.c_uint8 * arr_len
        self.rawData = arr_type( *dataBytes )
        self.dataLen = arr_len
        self.dataCRC = dataCRC

#     def __del__(self):
#         ## do nothing -- data will be released automatically
#         pass

    def calculate(self, poly, intReg, xorVal):
        return c_fastcrc.hw_crc16_calculate( self.rawData, self.dataLen, poly, intReg, xorVal )

    def calculateParam(self, poly, intReg, xorVal, reverseOrder, reflectBits):
        return c_fastcrc.hw_crc16_calculate_param( self.rawData, self.dataLen, poly, intReg, xorVal, reverseOrder, reflectBits )

    def calculateRange(self, poly, intRegStart, intRegEnd, xorStart, xorEnd):
        ret_array = c_fastcrc.hw_crc16_calculate_range( self.rawData, self.dataLen, self.dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
        return convert_CRC16ResultArray_to_list( ret_array )

    def invert(self, poly, regVal):
        ret_array = c_fastcrc.hw_crc16_invert( self.rawData, self.dataLen, poly, regVal )
        return convert_uint16_array_to_list( ret_array )

    def invertRange(self, crcNum, poly, xorStart, xorEnd):
        ret_array = c_fastcrc.hw_crc16_invert_range( self.rawData, self.dataLen, crcNum, poly, xorStart, xorEnd )
        xorList = convert_CRC16ResultArray_to_dict( ret_array )
        return xorList.items()                                          ## return list of pairs


## ========================================================================


def convert_CRC16ResultArray_to_list( result_array ):
    data_content = result_array.contents
    data_size = len( data_content )
    retList = []
    for i in xrange(0, data_size):
        item = data_content[ i ]
        retList.append( ( item.reginit, item.xorout ) )

    c_fastcrc.CRC16ResultArray_free( result_array )
    return retList


def convert_CRC16ResultArray_to_dict( result_array ):
    data_content = result_array.contents
    data_size = len( data_content )
    xorList = dict()
    for i in xrange(0, data_size):
        item = data_content[ i ]
        regList = xorList.get( item.xorout, None )
        if regList is None:
            regList = list()
            xorList[ item.xorout ] = regList
        regList.append( item.reginit )
    c_fastcrc.CRC16ResultArray_free( result_array )
    return xorList


def convert_uint16_array_to_list( result_array ):
    data_content = result_array.contents
    retList = []
    data_size = len( data_content )
    for i in xrange(0, data_size):
        item = data_content[ i ]
        retList.append( item )
#     retList = list( data_content )
    c_fastcrc.uint16_array_free( result_array )
    return retList


## ========================================================================


class CRC16Result(ctypes.Structure):
    """ creates a struct """

    _fields_ = [('reginit', ctypes.c_uint16 ),
                ('xorout', ctypes.c_uint16)]

    def __str__(self):
        return "<CRC16Result 0x%x - init:0x%X, xor:0x%X, crc:0x%X>" % ( id(self), self.reginit, self.xorout, self.crc )


class CRC16ResultArray(ctypes.Structure):
    """ creates a struct """

    _fields_ = [('size', ctypes.c_size_t),
                ('capacity', ctypes.c_size_t),
                ('data', ctypes.POINTER( CRC16Result ))]

    def __len__(self):
        return self.size

    def __getitem__(self, index):
        return self.data[ index ]

    def __str__(self):
        return "<CRC16ResultArray 0x%x: %s, %s, 0x%x>" % ( id(self), self.size, self.capacity, id(self.data.contents) )

#     def release(self):
#         c_fastcrc.CRC16ResultArray_free( self )


c_fastcrc.CRC16ResultArray_free.argtypes = [ ctypes.POINTER( CRC16ResultArray ) ]


class uint16_array(ctypes.Structure):
    """ creates a struct """

    _fields_ = [('size', ctypes.c_size_t),
                ('capacity', ctypes.c_size_t),
                ('data', ctypes.POINTER( ctypes.c_uint16 ))]

    def __len__(self):
        return self.size

    def __getitem__(self, index):
        return self.data[ index ]

    def __str__(self):
        return "<uint16_array 0x%x: %s, %s, 0x%x>" % ( id(self), self.size, self.capacity, id(self.data.contents) )

#     def release(self):
#         c_fastcrc.CRC16ResultArray_free( self )


c_fastcrc.uint16_array_free.argtypes = [ ctypes.POINTER( uint16_array ) ]


## ========================================================================


c_fastcrc.hw_crc16_calculate.restype = ctypes.c_uint16
def hw_crc16_calculate( bytesList, poly, intReg, xorVal ):
    arr_len  = len(bytesList)
    arr_type = ctypes.c_uint8 * arr_len
    arr      = arr_type( *bytesList )
    return c_fastcrc.hw_crc16_calculate( arr, arr_len, poly, intReg, xorVal )


c_fastcrc.hw_crc16_calculate_param.restype = ctypes.c_uint16
def hw_crc16_calculate_param( bytesList, poly, intReg, xorVal, reverseOrder, reflectBits ):
    arr_len  = len(bytesList)
    arr_type = ctypes.c_uint8 * arr_len
    arr      = arr_type( *bytesList )
    return c_fastcrc.hw_crc16_calculate_param( arr, arr_len, poly, intReg, xorVal, reverseOrder, reflectBits )


c_fastcrc.hw_crc16_calculate_range.argtypes = [ ctypes.POINTER( ctypes.c_uint8 ), ctypes.c_size_t, ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint16 ]
c_fastcrc.hw_crc16_calculate_range.restype = ctypes.POINTER( CRC16ResultArray )
def hw_crc16_calculate_range( bytes_list, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd ):
    arr_len  = len(bytes_list)
    arr_type = ctypes.c_uint8 * arr_len
    arr      = arr_type( *bytes_list )
    data_array = c_fastcrc.hw_crc16_calculate_range( arr, arr_len, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )

    return convert_CRC16ResultArray_to_list( data_array )


c_fastcrc.hw_crc16_invert.argtypes = [ ctypes.POINTER( ctypes.c_uint8 ), ctypes.c_size_t, ctypes.c_uint16, ctypes.c_uint16 ]
c_fastcrc.hw_crc16_invert.restype = ctypes.POINTER( uint16_array )
def hw_crc16_invert( bytes_list, poly, regVal ):
    arr_len  = len(bytes_list)
    arr_type = ctypes.c_uint8 * arr_len
    arr      = arr_type( *bytes_list )
    data_array = c_fastcrc.hw_crc16_invert( arr, arr_len, poly, regVal )

    return convert_uint16_array_to_list( data_array )

c_fastcrc.hw_crc16_invert_range.argtypes = [ ctypes.POINTER( ctypes.c_uint8 ), ctypes.c_size_t, ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint16 ]
c_fastcrc.hw_crc16_invert_range.restype = ctypes.POINTER( CRC16ResultArray )
def hw_crc16_invert_range( bytes_list, crcNum, poly, xorStart, xorEnd):
    arr_len  = len(bytes_list)
    arr_type = ctypes.c_uint8 * arr_len
    arr      = arr_type( *bytes_list )

    data_array = c_fastcrc.hw_crc16_invert_range( arr, arr_len, crcNum, poly, xorStart, xorEnd )

    xorList = convert_CRC16ResultArray_to_dict( data_array )
    return xorList.items()                                          ## return list of pairs
