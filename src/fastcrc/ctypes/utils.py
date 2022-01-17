##
##
##

from crc.numbermask import reverse_number


## least significant byte goes first in list
def convert_to_lsb_list( number, numberBytesSize ):
    retList = []
    for _ in range(numberBytesSize):
        byte = reverse_number( number, 8 )
#         byte = number & 0xFF
        retList.append( byte )
        number = number >> 8
    return retList


## most significant byte goes first in list
def convert_to_msb_list( number, numberBytesSize ):
    retList = []
    for _ in range(numberBytesSize):
#         byte = reverse_number( number, 8 )
        byte = number & 0xFF
        retList.append( byte )
        number = number >> 8
    ## appending and list reverse is faster than inserting at front of list
    retList.reverse()
    return retList
