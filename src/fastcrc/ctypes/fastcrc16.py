##
##
##

import os
import ctypes


base_dir = os.path.dirname( __file__ )

fastcrc_path = os.path.join( base_dir, os.pardir, "build", "install", "libfastcrc.so" )

c_fastcrc = ctypes.CDLL( fastcrc_path )


## ========================================================================


class CRC16Result(ctypes.Structure):
    """ creates a struct """

    _fields_ = [('reg', ctypes.c_uint16 ),
                ('xor', ctypes.c_uint16)]

    def __str__(self):
        return "<CRC16Result 0x%x - init:0x%X, xor:0x%X, crc:0x%X>" % ( id(self), self.reg, self.xor, self.crc )


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
    data_content = data_array.contents
    data_size = len( data_content )
    retList = []
    for i in xrange(0, data_size):
        item = data_content[ i ]
        retList.append( ( item.reg, item.xor ) )
    c_fastcrc.CRC16ResultArray_free( data_array )
    return retList
