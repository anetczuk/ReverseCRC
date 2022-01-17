##
##
##



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
#         byte = reverse_byte( number, 8 )
        byte = number & 0xFF
        retList.append( byte )
        number = number >> 8
    ## appending and list reverse is faster than inserting at front of list
    retList.reverse()
    return retList


def reverse_byte( number, bitsNum ):
    result = 0
    for _ in xrange( bitsNum ):
        result = (result << 1) + (number & 1)
        number >>= 1
    return result
