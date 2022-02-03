##
##
##

from fastcrc8 import swigraw_fastcrc, convert_to_uint8array


## ========================================================================


# ## old implementation
# class SwigRawData16Operator( object ):
# 
#     ## dataBytes: bytes list
#     ## dataCRC: int
#     def __init__(self, dataBytes, dataCRC):
#         self.dataBytes = dataBytes
#         self.dataCRC = dataCRC
# 
#     def calculate(self, poly, intReg, xorVal):
#         return hw_crc16_calculate( self.dataBytes, poly & 0xFF, intReg, xorVal )
# 
#     def calculateParam(self, poly, intReg, xorVal, reverseOrder, reflectBits):
#         return hw_crc16_calculate_param( self.dataBytes, poly & 0xFF, intReg, xorVal, reverseOrder, reflectBits )
# 
#     def calculateRange(self, poly, intRegStart, intRegEnd, xorStart, xorEnd):
#         return hw_crc16_calculate_range( self.dataBytes, self.dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
#     
#     def invert(self, poly, regVal):
#         return hw_crc16_invert( self.dataBytes, poly, regVal )
# 
#     def invertRange(self, crcNum, poly, xorStart, xorEnd):
#         return hw_crc16_invert_range( self.dataBytes, poly, xorStart, xorEnd )


##
class SwigRawData16Operator( object ):
 
    ## dataBytes: bytes list
    ## dataCRC: int
    def __init__(self, dataBytes, dataCRC):
        self.rawData = convert_to_uint8array( dataBytes )
        self.dataLen = len( dataBytes )
        self.dataCRC = dataCRC
 
    def __del__(self):
        swigraw_fastcrc.delete_Uint8Array( self.rawData )
 
    def calculate(self, poly, intReg, xorVal):
        return swigraw_fastcrc.hw_crc16_calculate( self.rawData, self.dataLen, poly, intReg, xorVal )
 
    def calculateParam(self, poly, intReg, xorVal, reverseOrder, reflectBits):
        return swigraw_fastcrc.hw_crc16_calculate_param( self.rawData, self.dataLen, poly, intReg, xorVal, reverseOrder, reflectBits )
 
    def calculateRange(self, poly, intRegStart, intRegEnd, xorStart, xorEnd):
        ret_array = swigraw_fastcrc.hw_crc16_calculate_range( self.rawData, self.dataLen, self.dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
        return convert_CRC16ResultArray_to_list( ret_array )
 
    def invert(self, poly, regVal):
        ret_array = swigraw_fastcrc.hw_crc16_invert( self.rawData, self.dataLen, poly, regVal )
        return convert_uint16_array_to_list( ret_array )
 
    def invertRange(self, crcNum, poly, xorStart, xorEnd):
        ret_array = swigraw_fastcrc.hw_crc16_invert_range( self.rawData, self.dataLen, crcNum, poly, xorStart, xorEnd )
        xorList = convert_CRC16ResultArray_to_dict( ret_array )
        return xorList.items()                                          ## return list of pairs


## ========================================================================


def convert_CRC16ResultArray_to_list( result_array ):
    data_size = result_array.size
    retList = []
    for i in xrange(0, data_size):
        item = swigraw_fastcrc.CRC16ResultArray_getptr( result_array, i )
        retList.append( ( item.reginit, item.xorout ) )
    swigraw_fastcrc.CRC16ResultArray_free( result_array )
    return retList


def convert_CRC16ResultArray_to_dict( result_array ):
    data_size = result_array.size
    xorList = dict()
    for i in xrange(0, data_size):
        item = swigraw_fastcrc.CRC16ResultArray_getptr( result_array, i )
        regList = xorList.get( item.xorout, None )
        if regList is None:
            regList = list()
            xorList[ item.xorout ] = regList
        regList.append( item.reginit )
    swigraw_fastcrc.CRC16ResultArray_free( result_array )
    return xorList


def convert_uint16_array_to_list( result_array ):
    ret_size = result_array.size
    retList = []
    for i in xrange(0, ret_size):
        item = swigraw_fastcrc.uint16_array_getvalue( result_array, i )
        retList.append( item )
#     retList = list( data_content )
    swigraw_fastcrc.uint16_array_free( result_array )
    return retList


## ========================================================================


def hw_crc16_calculate( bytesList, poly, intReg, xorVal ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret = swigraw_fastcrc.hw_crc16_calculate( data_array, arr_len, poly, intReg, xorVal )
    swigraw_fastcrc.delete_Uint8Array( data_array )

    return ret
#    return swigraw_fastcrc.hw_crc16_calculate( data_array.cast(), arr_len, poly, intReg, xorVal )


def hw_crc16_calculate_param( bytesList, poly, intReg, xorVal, reverseOrder, reflectBits ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret = swigraw_fastcrc.hw_crc16_calculate_param( data_array, arr_len, poly, intReg, xorVal, reverseOrder, reflectBits )
    swigraw_fastcrc.delete_Uint8Array( data_array )

    return ret
#    return swigraw_fastcrc.hw_crc16_calculate_param( data_array.cast(), arr_len, poly, intReg, xorVal, reverseOrder, reflectBits )


def hw_crc16_calculate_range( bytesList, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret_array = swigraw_fastcrc.hw_crc16_calculate_range( data_array, arr_len, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )
    swigraw_fastcrc.delete_Uint8Array( data_array )

#    ret_array = swigraw_fastcrc.hw_crc16_calculate_range( data_array.cast(), arr_len, dataCRC, poly, intRegStart, intRegEnd, xorStart, xorEnd )

    return convert_CRC16ResultArray_to_list( ret_array )


def hw_crc16_invert( bytesList, poly, regVal ):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret_array = swigraw_fastcrc.hw_crc16_invert( data_array, arr_len, poly, regVal )
    swigraw_fastcrc.delete_Uint8Array( data_array )

#    ret_array = swigraw_fastcrc.hw_crc16_invert( data_array.cast(), arr_len, poly, regVal )
    return convert_uint16_array_to_list( ret_array )


def hw_crc16_invert_range( bytesList, crcNum, poly, xorStart, xorEnd):
    arr_len  = len(bytesList)
    data_array = convert_to_uint8array( bytesList )

    ret_array = swigraw_fastcrc.hw_crc16_invert_range( data_array, arr_len, crcNum, poly, xorStart, xorEnd )
    swigraw_fastcrc.delete_Uint8Array( data_array )
#    ret_array = swigraw_fastcrc.hw_crc16_invert_range( data_array.cast(), arr_len, crcNum, poly, xorStart, xorEnd )

    xorList = convert_CRC16ResultArray_to_dict( ret_array )
    return xorList.items()                                          ## return list of pairs
