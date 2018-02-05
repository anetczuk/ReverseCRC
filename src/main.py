#!/usr/bin/python
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
from revcrc.reverse import RevHwCRC

    
    

## ============================= main section ===================================


if __name__ != '__main__':
    sys.exit(0)


parser = argparse.ArgumentParser(description='Finding CRC algorithm from data')
parser.add_argument('--mode', action='store', required=True, choices=["BF", "POLY", "COMMON"], help='Mode' )
parser.add_argument('--file', action='store', required=True, help='File with data' )
parser.add_argument('--profile', action='store_const', const=True, default=False, help='Profile the code' )
parser.add_argument('--pfile', action='store', default=None, help='Profile the code and output data to file' )
 
 
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

    
    if   args.mode == "BF":
        ## finding full key by forward algorithm
        finder = RevHwCRC(True)
#         finder = RevDivisionCRC(True)
#         finder = RevModCRC(True)
#         finder = RevCRCCommon(True)
        retList = finder.bruteForceInput(data, 48)
        print "Discovered keys[{:}]:".format( len(retList) )
        for key in retList:
            print key
    elif args.mode == "POLY":
        ## find polygons by xor-ing data pairs
        finder = RevHwCRC(True)
#         finder = RevDivisionCRC(True)
#         finder = RevModCRC(True)
#         finder = RevCRCCommon(True)
        retList = finder.findPolysInput(data, 48)
        print "Discovered polys[{:}]:".format( len(retList) )
        for poly in retList:
            print poly
    elif args.mode == "COMMON":
        ## finding full key by backward algorithm
        finder = RevHwCRC(True)
#         finder = RevDivisionCRC(True)
#         finder = RevModCRC(True)
#         finder = RevCRCCommon(True)
        retList = finder.findCommonInput(data, 48)
        print "Discovered keys[{:}]:".format( len(retList) )
        for key in retList:
            print key
    else:
        print "Invalid mode:", args.mode
        sys.exit(1)

finally:
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
    
    