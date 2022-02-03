##
##
##

import os


## cffi is fastest implementation
binding_type = os.getenv( "FASTCRC_BINDING", "auto" )


# print "trying binding:", binding_type
# from .utils import convert_to_msb_list, convert_to_lsb_list, convert_to_list, reflect_bits_list


BINDING_FOUND = False


if BINDING_FOUND is False and binding_type in ["auto", "cffi"]:
    ###
    ### cffi implementation
    ###

    try:
        from .cffi.fastcrc8  import CffiData8Operator  as Data8Operator
        from .cffi.fastcrc16 import CffiData16Operator as Data16Operator

        from .cffi.fastcrc8 import hw_crc8_calculate, hw_crc8_calculate_param, hw_crc8_calculate_range
        from .cffi.fastcrc16 import hw_crc16_calculate, hw_crc16_calculate_param, hw_crc16_calculate_range
        from .cffi.fastcrc16 import hw_crc16_invert, hw_crc16_invert_range

        BINDING_FOUND = True

#         print "using binding cffi"

    except ImportError:
        if binding_type != "auto":
            raise


if BINDING_FOUND is False and binding_type in ["auto", "ctypes"]:
    ###
    ### ctypes implementation
    ###

    try:
        from .ctypes.fastcrc8  import CTypesData8Operator  as Data8Operator
        from .ctypes.fastcrc16 import CTypesData16Operator as Data16Operator

        from .ctypes.fastcrc8 import hw_crc8_calculate, hw_crc8_calculate_param, hw_crc8_calculate_range
        from .ctypes.fastcrc16 import hw_crc16_calculate, hw_crc16_calculate_param, hw_crc16_calculate_range
        from .ctypes.fastcrc16 import hw_crc16_invert, hw_crc16_invert_range

        BINDING_FOUND = True

#         print "using binding ctypes"

    except ImportError:
        if binding_type != "auto":
            raise


if BINDING_FOUND is False and binding_type in ["auto", "swigraw"]:
    ###
    ### swig implementation
    ###

#     print "importing swig"

    try:
        from .swigraw.fastcrc8  import SwigRawData8Operator  as Data8Operator
        from .swigraw.fastcrc16 import SwigRawData16Operator as Data16Operator

        from .swigraw.fastcrc8 import hw_crc8_calculate, hw_crc8_calculate_param, hw_crc8_calculate_range
        from .swigraw.fastcrc16 import hw_crc16_calculate, hw_crc16_calculate_param, hw_crc16_calculate_range
        from .swigraw.fastcrc16 import hw_crc16_invert, hw_crc16_invert_range

        BINDING_FOUND = True

#         print "using binding swig"

    except ImportError:
        if binding_type != "auto":
            raise


if BINDING_FOUND is False and binding_type in ["auto", "swigoo"]:
    ###
    ### swig implementation
    ###

#     print "importing swig"

    try:
        from .swigoo.fastcrc8  import SwigOOData8Operator  as Data8Operator
        from .swigoo.fastcrc16 import SwigOOData16Operator as Data16Operator

        from .swigoo.fastcrc8 import hw_crc8_calculate, hw_crc8_calculate_param, hw_crc8_calculate_range
        from .swigoo.fastcrc16 import hw_crc16_calculate, hw_crc16_calculate_param, hw_crc16_calculate_range
        from .swigoo.fastcrc16 import hw_crc16_invert, hw_crc16_invert_range

        BINDING_FOUND = True

#         print "using binding swig"

    except ImportError:
        if binding_type != "auto":
            raise


if BINDING_FOUND is False:
    raise ImportError( "unable to find binding for: " + binding_type )
