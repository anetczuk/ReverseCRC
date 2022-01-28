#!/usr/bin/env python2

##
##
##

import os
import sys


BASE_DIR = os.path.dirname( __file__ )


out_path = os.path.join( BASE_DIR, "crc16lookup.h" )


##
## Implementation based on http://www.sunshine2k.de/articles/coding/crc/understanding_crc.html#ch44
##
def generate_subtable( poly ):
    table = dict()
    for div in xrange(0, 0x100):
        reg = div << 8
        for _ in xrange(0, 8):
            if reg & 0x8000 != 0:
                reg <<= 1
                reg ^= poly
            else:
                reg <<= 1
        table[ div ] = reg & 0xFFFF
    return table


def write_row( outfile, poly ):
    subtable = generate_subtable( poly )
    
    for sub in xrange(0, 0xFF):
        item = subtable[sub]
        outfile.write( str(item) + ", " )

    ## last item
    item = subtable[0xFF]
    outfile.write( str(item) + " " )


def main():
    ## write output
    header = """///

#ifndef CRC16_LOOKUPTABLE_H_
#define CRC16_LOOKUPTABLE_H_

#include <stdint.h>                             /// int types


///
/// table indexed in following way: [ polynomial ][ registry ]
/// 2D representation is slightly faster in use than 1D version
///
static const uint16_t CRC16_LookupTable[65536][256] = { 
"""

    footer = """};

#endif /* CRC16_LOOKUPTABLE_H_ */
"""

    with open(out_path, 'w') as outfile:
        outfile.write( header )
        
        for poly in xrange(0, 0xFFFF):
            outfile.write( "\t{" )
            write_row( outfile, poly )
            outfile.write( "},\n" )
            
        ## last poly
        outfile.write( "\t{" )
        write_row( outfile, 0xFFFF )
        outfile.write( "}\n" )
        
        outfile.write( footer )
        
    print "table written to:", out_path
    
    return 0


if __name__ == '__main__':
    ret = main()
    sys.exit( ret )
