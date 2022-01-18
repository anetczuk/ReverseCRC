#!/usr/bin/env python2
#
# MIT License
#
# Copyright (c) 2017 Arkadiusz Netczuk <dev.arnet@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import sys
import time
import argparse
import logging
import cProfile

from revcrc.input import DataParser

from crc.hwcrc import HwCRC
from crc.divisioncrc import DivisionCRC
from crc.modcrc import ModCRC
from revcrc.solver.bruteforce import BruteForceSolver
from revcrc.solver.bruteforcepairs import BruteForcePairsSolver
from revcrc.solver.polys import PolysSolver
from revcrc.solver.common import CommonSolver
from revcrc.solver.verify import VerifySolver


def create_processor( algorithm ):
    if algorithm == "HW":
        return HwCRC()
    elif algorithm == "DIV":
        return DivisionCRC()
    elif algorithm == "MOD":
        return ModCRC()
#     elif args.alg == "COMMON":
#         finder = RevCRCCommon( printProgress )
    return None


## return Reverse
def create_solver( mode, processor, printProgress ):
    if mode == "BF":
        return BruteForceSolver( processor, printProgress )
    elif mode == "BF_PAIRS":
        return BruteForcePairsSolver( processor, printProgress )
    elif mode == "POLY":
        return PolysSolver( processor, printProgress )
    elif mode == "COMMON":
        return CommonSolver( processor, printProgress )
    elif mode == "VERIFY":
        return VerifySolver( processor, printProgress )
    return None


def convert_int( value ):
    if value is None:
        return None
    if value == "None":
        return None
    return int( value )


def convert_hex( value ):
    if value is None:
        return None
    if value == "None":
        return None
    return int( value, 16 )


## ============================= main section ===================================


def main():
    parser = argparse.ArgumentParser(description='Finding CRC algorithm from data')
    parser.add_argument('--alg', action='store', required=True, choices=["HW", "DIV", "MOD"], help='Algorithm' )
    parser.add_argument('--mode', action='store', required=True, choices=["BF", "BF_PAIRS", "POLY", "COMMON", "VERIFY"], help='Mode' )
    parser.add_argument('--infile', action='store', required=True, help='File with data. Numbers strings are written in big endian notion and are directly converted by "int(str, 16)" invocation.' )
    parser.add_argument('--outfile', action='store', default=None, help='Results output file' )
    parser.add_argument('--mindsize', action='store', default=0, help='Minimal data size' )
    parser.add_argument('--poly', action='store', default=None, help='Polynomial (for VERIFY mode)' )
    parser.add_argument('--crc_size', action='store', default=None, help='CRC size (for VERIFY mode)' )
    parser.add_argument('--init_reg', action='store', default=None, help='Registry initial value' )
    parser.add_argument('--xor_val', action='store', default=None, help='CRC output xor (for VERIFY mode)' )
    parser.add_argument('--reverse_order', '-ro', action='store', default=None, help='Should input bytes be read in reverse? (for VERIFY mode)' )
    parser.add_argument('--reflect_bits', '-rb', action='store', default=None, help='Should reflect bits in each input byte? (for VERIFY mode)' )
    parser.add_argument('--print_progress', '-pp', action='store_const', const=True, default=False, help='Print progress' )
    parser.add_argument('--profile', action='store_const', const=True, default=False, help='Profile the code' )
    parser.add_argument('--pfile', action='store', default=None, help='Profile the code and output data to file' )


    args = parser.parse_args()


    logging.basicConfig(level=logging.DEBUG)

    print "Starting:", args.alg, args.mode


    starttime = time.time()
    profiler = None

    try:
        profiler_outfile = args.pfile
        if args.profile == True or profiler_outfile != None:
            if profiler_outfile is None:
                profiler_outfile = "out.prof"
            print "Starting profiler"
            profiler = cProfile.Profile()
            profiler.enable()

        dataParser = DataParser()
        ## return InputData
        data = dataParser.parseFile(args.infile)

        if len(data.numbersList) < 1:
            print "no data found"
            return 1

        print "input data:", data.numbersList

        printProgress = args.print_progress
        outfile       = args.outfile
        if outfile is None:
            filename = os.path.basename(args.infile)
            filenameroot = os.path.splitext( filename )[0]
            dirname = os.path.dirname(args.infile)
            outdir = os.path.join( dirname, "out" )
            if os.path.exists( outdir ) is False:
                os.makedirs( outdir )
            outname = "%s_%s_%s_%s_%s.txt" % ( filenameroot, args.alg, args.mode, args.init_reg, args.xor_val )
            outfile = os.path.join( outdir, outname )

        processor = create_processor( args.alg )
        if processor is None:
            print "invalid algorithm:", args.alg
            return 1

        ## type Reverse
        solver = create_solver( args.mode, processor, printProgress )
        if solver is None:
            print "invalid solver:", args.mode
            return 1

        poly    = convert_hex( args.poly )
        initReg = convert_hex( args.init_reg )
        xorVal  = convert_hex( args.xor_val )
        crcSize = convert_int( args.crc_size )
        minSearchData = int(args.mindsize)

        solver.setPoly( poly )
        solver.setInitValue( initReg )
        solver.setXorValue( xorVal )
        solver.setCRCSize( crcSize )
        solver.setReverseMode( args.reverse_order, args.reflect_bits )
        solver.setMinSearchData( minSearchData )

        solver.execute( data, outfile )

        timeDiff = (time.time()-starttime)
        print "Calculation time: {:13.8f}s".format(timeDiff)

    finally:
        print ""                    ## print new line
        if profiler != None:
            profiler.disable()
            if profiler_outfile == None:
                print "Generating profiler data"
                profiler.print_stats(1)
            else:
                print "Storing profiler data to", profiler_outfile
                profiler.dump_stats( profiler_outfile )
                print "pyprof2calltree -k -i", profiler_outfile

    return 0


if __name__ == '__main__':
    ret = main()
    sys.exit( ret )
