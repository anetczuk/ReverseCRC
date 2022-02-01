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

import sys
import os
import argparse
import logging

import time
import subprocess
import imp


script_dir = os.path.dirname(os.path.abspath(__file__))


_LOGGER = logging.getLogger(__name__)


def single_step_sub( sublist ):
    try:
        subprocess.call( sublist )
    except SystemExit as ex:
        err_code = ex.code
        if err_code != 0:
            print "\nScript terminated with error[%s], terminating" % err_code
            return False
    return True
 
 
def single_step_imp( sublist ):
    try:
        sys.argv = sublist
        subprogram = sublist[0]
        imp.load_source( 'subprogram', subprogram )
    except SystemExit as ex:
        err_code = ex.code
        if err_code != 0:
            print "\nScript terminated with error[%s], terminating" % err_code
            return False
#             sys.exit( err_code )
               
    return True
 
 
def single_step_exec( sublist ):
    try:
        sys.argv = sublist
        subprogram = sublist[0]
       
        script_content = ""
        with open( subprogram, "r" ) as script_file:
            script_content = script_file.read()
        exec( script_content )
    except SystemExit as ex:
        err_code = ex.code
        if err_code != 0:
            print "\nScript terminated with error[%s], terminating" % err_code
            return False
#             sys.exit( err_code )
                
    return True


## "sub" gives close results to running as separate program
## "imp" and "exec" gives similar timings, but distinguishes from "sub"
METHOD_DICT = { "imp": single_step_imp, "sub": single_step_sub, "exec": single_step_exec }


def measure( sublist, warmup_number, steps_number, silent=False, method="imp" ):
    subprogram = sublist[0]
    
    root_dir = os.path.dirname( subprogram )
    sys.path.append( root_dir )
    
    single_step = METHOD_DICT[ method ]
    
    ## warmup
    for i in range(0, warmup_number):
        if silent is False:
            print "\n============ warmup step", i+1, "of", warmup_number, "============"
        if single_step( sublist ) is False:
            return 1
    
    
    ## iterating
    stats_list = []
    
    for i in range(0, steps_number):
        if silent is False:
            print "\n============ benchmark step", i+1, "of", steps_number, "============"
    
        starttime = time.time()
        if single_step( sublist ) is False:
            return 1
    
        timeDiff = (time.time()-starttime)
        if silent is False:
            print "\nStep time: {:13.8f}s".format(timeDiff)
        
        stats_list.append( timeDiff )
        
    return stats_list


## ==================================================


def main():
    parser = argparse.ArgumentParser(description='Script microbenchmarking')
    parser.add_argument('--warmup', '-w', action='store', type=int, default=0, help='Warmup iterations number' )
    parser.add_argument('--iterations', '-i', action='store', type=int, default=3, help='Measurement iterations number' )
    parser.add_argument('args', nargs=argparse.REMAINDER)
    
    
    args = parser.parse_args()
    
    
    warmup_number = args.warmup
    steps_number  = args.iterations
    
    subprogram = args.args[0]
    subargs    = args.args[1:]
    print "Benchmarking:", subprogram, subargs
    
    stats_list = measure( args.args, warmup_number, steps_number )
    
    print "\n============ results ============"
    
    print "warmup:", warmup_number
    print "steps: ", steps_number
    
    min_time = min( stats_list )
    max_time = max( stats_list )
    
    print "min: ", min_time
    print "avg: ", sum( stats_list ) / len( stats_list )
    print "max: ", max_time
    print "span:", max_time - min_time

    return 0


if __name__ == '__main__':
    ret = main()
    sys.exit( ret )
