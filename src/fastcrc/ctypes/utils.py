##
##
##

from crc.numbermask import reverse_number


## least significant byte goes first in list
def convert_to_list( number, numberBytesSize ):
    retList = []
    for _ in range(numberBytesSize):
        byte = number & 0xFF
        retList.append( byte )
        number = number >> 8
    return retList


def reflect_bits_list( number_list ):
    for i in xrange(0, len(number_list)):
        number_list[ i ] = reverse_number( number_list[ i ], 8 )


## does bytes reorder and bits reflection
## least significant byte goes first in list
def convert_to_lsb_list( number, numberBytesSize ):
    number_list = convert_to_list( number, numberBytesSize )
    reflect_bits_list( number_list )
    return number_list


## does bytes reorder
## most significant byte goes first in list
def convert_to_msb_list( number, numberBytesSize ):
    number_list = convert_to_list( number, numberBytesSize )
    number_list.reverse()
    return number_list
