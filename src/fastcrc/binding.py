##
##
##

import os


## cffi is fastest implementation
binding_type = os.getenv( "FASTCRC_BINDING", "auto" )


# print "trying binding:", binding_type
from .utils import convert_to_msb_list, convert_to_lsb_list, convert_to_list, reflect_bits_list


BINDING_FOUND = False


if BINDING_FOUND is False and binding_type in ["auto", "cffi"]:
    ###
    ### cffi implementation
    ###

    try:
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
        from .ctypes.fastcrc8 import hw_crc8_calculate, hw_crc8_calculate_param, hw_crc8_calculate_range
        from .ctypes.fastcrc16 import hw_crc16_calculate, hw_crc16_calculate_param, hw_crc16_calculate_range
        from .ctypes.fastcrc16 import hw_crc16_invert, hw_crc16_invert_range
          
        BINDING_FOUND = True
          
#         print "using binding ctypes"
        
    except ImportError:
        if binding_type != "auto":
            raise
        

if BINDING_FOUND is False and binding_type in ["auto", "swig"]:
    ###
    ### swig implementation
    ###
    
#     print "importing swig"

    try:
        from .swig.fastcrc8 import hw_crc8_calculate, hw_crc8_calculate_param, hw_crc8_calculate_range
        from .swig.fastcrc16 import hw_crc16_calculate, hw_crc16_calculate_param, hw_crc16_calculate_range
        from .swig.fastcrc16 import hw_crc16_invert, hw_crc16_invert_range
        
        BINDING_FOUND = True
        
#         print "using binding swig"
        
    except ImportError:
        if binding_type != "auto":
            raise


if BINDING_FOUND is False:
    raise ImportError( "unable to find binding for: " + binding_type )
