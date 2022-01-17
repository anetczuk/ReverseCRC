##
##
##

import os
import ctypes


base_dir = os.path.dirname( __file__ )

fastcrc_path = os.path.join( base_dir, os.pardir, "build", "install", "libfastcrc.so" )

c_fastcrc = ctypes.CDLL( fastcrc_path )


## ========================================================================


class CRC8Result(ctypes.Structure):
    """ creates a struct """

    _fields_ = [('reg', ctypes.c_uint8),
                ('xor', ctypes.c_uint8),
                ('crc', ctypes.c_uint8)]

    def __str__(self):
        return "<CRC8Result 0x%x - init:0x%X, xor:0x%X, crc:0x%X>" % ( id(self), self.reg, self.xor, self.crc )


class CRC8ResultArray(ctypes.Structure):
    """ creates a struct """

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


c_fastcrc.hw_crc8_calculate.restype = ctypes.c_uint8
def hw_crc8_calculate( bytesList, poly, intReg, xorVal ):
    arr_len  = len(bytesList)
    arr_type = ctypes.c_uint8 * arr_len
    arr      = arr_type( *bytesList )
    return c_fastcrc.hw_crc8_calculate( arr, arr_len, poly, intReg, xorVal )


c_fastcrc.hw_crc8_calculate_range.argtypes = [ ctypes.POINTER( ctypes.c_uint8 ), ctypes.c_size_t, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8 ]
c_fastcrc.hw_crc8_calculate_range.restype = ctypes.POINTER( CRC8ResultArray )
def hw_crc8_calculate_range( bytes_list, dataCRC, poly, intReg, xorStart, xorEnd ):
    arr_len  = len(bytes_list)
    arr_type = ctypes.c_uint8 * arr_len
    arr      = arr_type( *bytes_list )
    data_array = c_fastcrc.hw_crc8_calculate_range( arr, arr_len, dataCRC, poly, intReg, xorStart, xorEnd )
    data_content = data_array.contents
    data_size = len( data_content )
    retList = []
    for i in xrange(0, data_size):
        item = data_content[ i ]
#         retList.append( ( item.reg, item.xor, item.crc ) )
        retList.append( item.xor )
    c_fastcrc.CRC8ResultArray_free( data_array )
    return retList
