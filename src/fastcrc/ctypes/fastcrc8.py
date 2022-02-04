##
##
##

import ctypes


from ..paths import FASTCRC_CLIB_LIB_PATH

try:
    c_fastcrc = ctypes.CDLL( FASTCRC_CLIB_LIB_PATH )

except OSError as ex:
    ## could not load module
    raise ImportError( ex )


## ========================================================================


# ## old implementation
# class CTypesData8Operator( object ):
#
#     ## dataBytes: bytes list
#     ## dataCRC: int
#     def __init__(self, dataBytes, dataCRC):
#         self.dataBytes = dataBytes
#         self.dataCRC = dataCRC
#
#     def calculate(self, poly, intReg, xorVal):
#         return hw_crc8_calculate( self.dataBytes, poly & 0xFF, intReg, xorVal )
#
#     def calculateParam(self, poly, intReg, xorVal, reverseOrder, reflectBits):
#         return hw_crc8_calculate_param( self.dataBytes, poly & 0xFF, intReg, xorVal, reverseOrder, reflectBits )
#
#     def calculateRange(self, poly, intRegStart, intRegEnd, xorStart, xorEnd):
#         return hw_crc8_calculate_range( self.dataBytes, self.dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )


##
class CTypesData8Operator( object ):

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
        return c_fastcrc.hw_crc8_calculate( self.rawData, self.dataLen, poly, intReg, xorVal )

    def calculateParam(self, poly, intReg, xorVal, reverseOrder, reflectBits):
        return c_fastcrc.hw_crc8_calculate_param( self.rawData, self.dataLen, poly, intReg, xorVal, reverseOrder, reflectBits )

    def calculateRange(self, poly, intRegStart, intRegEnd, xorStart, xorEnd):
        ret_array = c_fastcrc.hw_crc8_calculate_range( self.rawData, self.dataLen, self.dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
        return convert_CRC8ResultArray_to_list( ret_array )


## ========================================================================


def convert_CRC8ResultArray_to_list( result_array ):
    data_content = result_array.contents
    data_size = len( data_content )
    retList = []
    for i in xrange(0, data_size):
        item = data_content[ i ]
        retList.append( ( item.reginit, item.xorout ) )
    c_fastcrc.CRC8ResultArray_free( result_array )
    return retList


## ========================================================================


class CRC8Result(ctypes.Structure):

    _fields_ = [('reginit', ctypes.c_uint8),
                ('xorout', ctypes.c_uint8)]

    def __str__(self):
        return "<CRC8Result 0x%x - init:0x%X, xor:0x%X, crc:0x%X>" % ( id(self), self.reginit, self.xorout, self.crc )


class CRC8ResultArray(ctypes.Structure):

    _fields_ = [('size', ctypes.c_size_t),
                ('capacity', ctypes.c_size_t),
                ('data', ctypes.POINTER( CRC8Result ))]

    def __len__(self):
        return self.size

    def __getitem__(self, index):
        return self.data[ index ]

    def __str__(self):
        return "<CRC8ResultArray 0x%x: %s, %s, 0x%x>" % ( id(self), self.size, self.capacity, id(self.data.contents) )

#     def release(self):
#         c_fastcrc.CRC8ResultArray_free( self )


c_fastcrc.CRC8ResultArray_free.argtypes = [ ctypes.POINTER( CRC8ResultArray ) ]


## ========================================================================


c_fastcrc.hw_crc8_calculate.restype = ctypes.c_uint8


def hw_crc8_calculate( bytesList, poly, intReg, xorVal ):
    arr_len  = len(bytesList)
    arr_type = ctypes.c_uint8 * arr_len
    arr      = arr_type( *bytesList )
    return c_fastcrc.hw_crc8_calculate( arr, arr_len, poly, intReg, xorVal )


c_fastcrc.hw_crc8_calculate_param.restype = ctypes.c_uint8


def hw_crc8_calculate_param( bytesList, poly, intReg, xorVal, reverseOrder, reflectBits ):
    arr_len  = len(bytesList)
    arr_type = ctypes.c_uint8 * arr_len
    arr      = arr_type( *bytesList )
    return c_fastcrc.hw_crc8_calculate_param( arr, arr_len, poly, intReg, xorVal, reverseOrder, reflectBits )


c_fastcrc.hw_crc8_calculate_range.argtypes = [ ctypes.POINTER( ctypes.c_uint8 ), ctypes.c_size_t, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8 ]
c_fastcrc.hw_crc8_calculate_range.restype = ctypes.POINTER( CRC8ResultArray )


def hw_crc8_calculate_range( bytes_list, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd ):
#     print "verify input: 0x%X 0x%X 0x%X 0x%X 0x%X" % ( poly, intRegStart, intRegEnd, xorStart, xorEnd )

    arr_len  = len(bytes_list)
    arr_type = ctypes.c_uint8 * arr_len
    arr      = arr_type( *bytes_list )
    data_array = c_fastcrc.hw_crc8_calculate_range( arr, arr_len, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )

    return convert_CRC8ResultArray_to_list( data_array )
