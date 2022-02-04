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
import argparse
import logging

from crc.input import DataParser

from crc.hwcrc import HwCRCProcessorFactory
from crc.divisioncrc import DivisionCRC
from crc.modcrc import ModCRCProcessorFactory
from crc.solver.bruteforce import BruteForceSolver
from crc.solver.bruteforcepairs import BruteForcePairsSolver
from crc.solver.polys import PolysSolver
from crc.solver.common import CommonSolver
from crc.solver.verify import VerifySolver
from crc.solver.reverse import InputParams
from crc.solver.backward import BackwardSolver


_LOGGER = logging.getLogger(__name__)


# return CRCProcessorFactory
def create_alg_factory( algorithm ):
    if algorithm == "HW":
        return HwCRCProcessorFactory()
    elif algorithm == "DIV":
        return DivisionCRC()
    elif algorithm == "MOD":
        return ModCRCProcessorFactory()
#     elif args.alg == "COMMON":
#         finder = RevCRCCommon( printProgress )
    return None


## return Reverse
def create_solver( mode, printProgress ):
    if mode == "BF":
        return BruteForceSolver( printProgress )
    elif mode == "BF_PAIRS":
        return BruteForcePairsSolver( printProgress )
    elif mode == "POLY":
        return PolysSolver( printProgress )
    elif mode == "COMMON":
        return CommonSolver( printProgress )
    elif mode == "VERIFY":
        return VerifySolver( printProgress )
    elif mode == "BACKWARD":
        return BackwardSolver( printProgress )
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
    parser.add_argument('--mode', action='store', required=True, choices=["BF", "BF_PAIRS", "POLY", "COMMON", "VERIFY", "BACKWARD"], help='Mode' )
    parser.add_argument('--infile', action='store', required=True, help='File with data. Numbers strings are written in big endian notion and are directly converted by "int(str, 16)" invocation.' )
    parser.add_argument('--outfile', action='store', default=None, help='Results output file' )
    parser.add_argument('--default_outfile', '-dof', action='store_const', const=True, default=False, help='Use default output file' )
    parser.add_argument('--mindsize', action='store', default=0, help='Minimal data size' )
    parser.add_argument('--poly', action='store', default=None, help='Polynomial (for VERIFY mode)' )
    parser.add_argument('--crc_size', action='store', default=None, help='CRC size (for VERIFY mode)' )
    parser.add_argument('--init_reg', action='store', default=None, help='Registry initial value' )
    parser.add_argument('--xor_val', action='store', default=None, help='CRC output xor (for VERIFY mode)' )
    parser.add_argument('--reverse_order', '-ro', action='store', default=None, help='Should input bytes be read in reverse? (for VERIFY mode)' )
    parser.add_argument('--reflect_bits', '-rb', action='store', default=None, help='Should reflect bits in each input byte? (for VERIFY mode)' )
    parser.add_argument('--binding', '-b', action='store', choices=['auto', 'ctypes', 'cffi', 'swigraw', 'swigoo'], default=None, help='Set fastcrc binding' )
    parser.add_argument('--print_progress', '-pp', action='store_const', const=True, default=False, help='Print progress' )
    parser.add_argument('--silent', action='store_const', const=True, default=False, help='No output messages' )

    args = parser.parse_args()

    silentMode = args.silent
    if silentMode:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.DEBUG)

    _LOGGER.info( "Executed: %s", " ".join( sys.argv ) )
    _LOGGER.info( "Starting: %s %s", args.alg, args.mode )

    if args.binding is not None:
        os.environ[ "FASTCRC_BINDING" ] = args.binding

    dataParser = DataParser()
    ## return InputData
    data = dataParser.parseFile(args.infile)

    if data.empty():
        _LOGGER.error( "no data found" )
        return 1
    if data.ready() is False:
        _LOGGER.error( "input data not ready" )
        return 1

    _LOGGER.info( "input data: %s", data.numbersList )
    _LOGGER.info( "List size: {} Data size: {} CRC size: {}".format( len(data.numbersList), data.dataSize, data.crcSize ) )

    printProgress = args.print_progress

    processorFactory = create_alg_factory( args.alg )
    if processorFactory is None:
        _LOGGER.error( "invalid algorithm: %s", args.alg )
        return 1

    ## type Reverse
    solver = create_solver( args.mode, printProgress )
    if solver is None:
        _LOGGER.error( "invalid solver: %s", args.mode )
        return 1
    solver.setProcessorFactory( processorFactory )

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

    inputParams = InputParams()
    inputParams.data = data
    inputParams.crcSize = crcSize
    inputParams.poly = poly
    inputParams.initReg = initReg
    inputParams.xorVal  = xorVal
    inputParams.reverseOrder = args.reverse_order
    inputParams.reflectBits  = args.reflect_bits

    outfile = args.outfile
    if outfile is None and args.default_outfile:
        ## prepare output file path
        filename = os.path.basename(args.infile)
        filenameroot = os.path.splitext( filename )[0]
        dirname = os.path.dirname(args.infile)
        outdir = os.path.join( dirname, "out" )
        if os.path.exists( outdir ) is False:
            os.makedirs( outdir )
        outname = "%s_%s_%s_p%s_i%s_x%s_ro%s_rb%s.txt" % ( filenameroot, args.alg, args.mode, args.poly, args.init_reg, args.xor_val, inputParams.isReverseOrder(), inputParams.isReflectBits() )
        outfile = os.path.join( outdir, outname )

    _LOGGER.info( "input args, poly: %s init: %s, xor: %s crcsize: %s" % ( inputParams.poly, inputParams.initReg, inputParams.xorVal, inputParams.crcSize ) )
    _LOGGER.info( "output path: %s", outfile )

    solver.execute( inputParams, outfile )

    return 0


if __name__ == '__main__':
    ret = main()
    sys.exit( ret )
