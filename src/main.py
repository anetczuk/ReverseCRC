#!/usr/bin/python2
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


import sys
import time
import argparse 
import logging
import cProfile

from revcrc.input import DataParser
from revcrc.reverse import RevHwCRC, RevDivisionCRC, RevModCRC

from collections import Counter


def find_crc( args, finder, data ):
    minSearchData = int(args.mindsize)
    
    if   args.mode == "BF":
        ## finding full key by forward algorithm
        retList = finder.bruteForceStandardInput(data, minSearchData)
        if len(retList) < 1:
            print "\nNo keys discovered"
        else:
            print "\nDiscovered keys[{:}]:".format( len(retList) )
            for poly in retList.most_common():
                print poly[0], poly[1]
                
            with open(outfile, "w") as text_file:
                text_file.write( "\nDiscovered keys[{:}]:\n".format( len(retList) ) )
                for poly in retList.most_common():
                    text_file.write( "{:} {:}\n".format( poly[0], poly[1] ) )
            
    elif   args.mode == "BF_PAIRS":
        ## finding full key by forward algorithm using pair xoring
        keysList = finder.bruteForcePairsInput(data, minSearchData)
        if len(keysList) < 1:
            print "\nNo keys discovered"
        else:
            retList = Counter()
            retList.update( keysList )
            print "\nDiscovered keys[{:}]:".format( len(retList) )
            for poly in retList.most_common():
                print poly[0], poly[1]
#             print "\nDiscovered keys[{:}]:".format( len(retList) )
#             for key in retList:
#                 print key
            print "Found results: ", len(retList)
            
            with open(outfile, "w") as text_file:
                text_file.write( "\nDiscovered keys[{:}]:\n".format( len(retList) ) )
                for poly in retList.most_common():
                    text_file.write( "{:} {:}\n".format( poly[0], poly[1] ) )
                    
    elif args.mode == "POLY":
        ## find polygons by xor-ing data pairs
        retList = finder.findPolysInput(data, minSearchData)
        if len(retList) < 1:
            print "\nNo polys discovered"
        else:
            print "\nDiscovered polys[{:}]:".format( len(retList) )
            for poly in retList.most_common():
                print poly[0], poly[1]
                
            with open(outfile, "w") as text_file:
                text_file.write( "\nDiscovered keys[{:}]:\n".format( len(retList) ) )
                for poly in retList.most_common():
                    text_file.write( "{:} {:}\n".format( poly[0], poly[1] ) )

    elif args.mode == "COMMON":
        ## finding full key by backward algorithm
        retList = finder.findCommonInput(data, minSearchData)
        if len(retList) < 1:
            print "\nNo keys discovered"
        else:
            print "\nDiscovered keys[{:}]:".format( len(retList) )
            for poly in retList.most_common():
                print poly[0], poly[1]
                
            with open(outfile, "w") as text_file:
                text_file.write( "\nDiscovered keys[{:}]:\n".format( len(retList) ) )
                for poly in retList.most_common():
                    text_file.write( "{:} {:}\n".format( poly[0], poly[1] ) )

    else:
        print "Invalid mode:", args.mode
        sys.exit(1)


def verify_crc( args, finder, data ):
#     ret = finder.verify( data, 0x11D, 0x00, 0x8F )
#     ret = finder.verify( data, 0x11D, 0x8F, 0x8F )
    ret = finder.verify( data, 0x11D, 0x00, 0x70 )
#     ret = finder.verify( data, 0x11D, 0x70, 0x70 )
    if ret is True:
        print "\nPoly matches all data"


## ============================= main section ===================================


if __name__ != '__main__':
    sys.exit(0)


parser = argparse.ArgumentParser(description='Finding CRC algorithm from data')
parser.add_argument('--mode', action='store', required=True, choices=["BF", "BF_PAIRS", "POLY", "COMMON", "VERIFY"], help='Mode' )
parser.add_argument('--file', action='store', required=True, help='File with data. Numbers strings are written in big endian notion and are directly converted by "int(str, 16)" invocation.' )
parser.add_argument('--outfile', action='store', default="out.txt", help='Results output file' )
parser.add_argument('--profile', action='store_const', const=True, default=False, help='Profile the code' )
parser.add_argument('--pfile', action='store', default=None, help='Profile the code and output data to file' )
parser.add_argument('--mindsize', action='store', default=0, help='Minimal data size' )
parser.add_argument('--algo', action='store', required=True, choices=["HW", "DIV", "MOD"], help='Algorithm' )
parser.add_argument('--print_progress', '-pp', action='store_const', const=True, default=False, help='Print progress' )

 
 
args = parser.parse_args()
 

logging.basicConfig(level=logging.DEBUG)

print "Starting"


starttime = time.time()
profiler = None

try:

    profiler_outfile = args.pfile
    if args.profile == True or profiler_outfile != None:
        print "Starting profiler"
        profiler = cProfile.Profile()
        profiler.enable()
    
    dataParser = DataParser()
    data = dataParser.parseFile(args.file)
    # print "xxxx:", data.numbersList

    printProgress = args.print_progress
    outfile       = args.outfile
    
    finder = None
    if args.algo == "HW":
        finder = RevHwCRC( printProgress )
    elif args.algo == "DIV":
        finder = RevDivisionCRC( printProgress )
    elif args.algo == "MOD":
        finder = RevModCRC( printProgress )
#     elif args.algo == "COMMON":
#         finder = RevCRCCommon( printProgress )
    
    if   args.mode != "VERIFY":
        find_crc( args, finder, data )
    else:
        verify_crc( args, finder, data )
    

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
        
    timeDiff = (time.time()-starttime)*1000.0
    print "Calculation time: {:13.8f}ms".format(timeDiff)
    
    
