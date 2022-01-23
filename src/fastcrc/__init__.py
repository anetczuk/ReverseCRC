##
##
##

###
### ctypes implementation
###

# from .ctypes.fastcrc8 import hw_crc8_calculate, hw_crc8_calculate_param, hw_crc8_calculate_range
#  
# from .ctypes.fastcrc16 import hw_crc16_calculate, hw_crc16_calculate_param, hw_crc16_calculate_range
# from .ctypes.fastcrc16 import hw_crc16_invert, hw_crc16_invert_range
#  
# from .ctypes.utils import convert_to_msb_list, convert_to_lsb_list, convert_to_list, reflect_bits_list


###
### cffi implementation
###

from .cffi.fastcrc8 import hw_crc8_calculate, hw_crc8_calculate_param, hw_crc8_calculate_range

from .cffi.fastcrc16 import hw_crc16_calculate, hw_crc16_calculate_param, hw_crc16_calculate_range
from .cffi.fastcrc16 import hw_crc16_invert, hw_crc16_invert_range

from .ctypes.utils import convert_to_msb_list, convert_to_lsb_list, convert_to_list, reflect_bits_list
