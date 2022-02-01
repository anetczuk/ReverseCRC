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
import random
from collections import defaultdict

import imp
import pandas
import tempfile

import matplotlib

# # Make sure that we are using QT5
# matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
    

script_dir = os.path.dirname(os.path.abspath(__file__))

benchmarking_path = os.path.join( script_dir, os.pardir, "tools", "microbenchmark.py" )
main_path         = os.path.join( script_dir, os.pardir, "src", "find.py" )
out_dir           = os.path.join( script_dir, "measurements" )


if not os.path.exists( out_dir ):
    os.makedirs( out_dir )


_LOGGER = logging.getLogger(__name__)


## ==================================================


def prepare_filename( params ):
    fileName = params
    fileName = fileName.replace( ", ", "_" )
    fileName = fileName.replace( ": ", "-" )
    fileName = fileName.replace( ":", "-" )
    fileName = fileName.replace( " ", "_" )
    return fileName


def avg( data_list ):
    return sum( data_list ) / len( data_list )


def sample():
    retList = []
    for _ in range(0, 5):
        retList.append( random.uniform( 0.0, 1.0 ) )
    return retList
    

## crc_size = ( crc_index + 1 ) * 8
def measure( data_bytes_list=[8, 16, 24, 32], data_rows=1, crc_index=0, mode="BF", poly=None, data_generator="FF" ):
    print "data bytes list:", data_bytes_list
    print "data rows:", data_rows
    print "data generator:", data_generator
    
    crc_string  = "FF" * (crc_index + 1)
#     poly_string = "0x1" + crc_string
    
    benchmarking_module = imp.load_source( 'micro', benchmarking_path )
    
    raw_data = defaultdict( list )
    bits_sizes_list = []
 
    polyParam = ""
    if poly is not None:
        polyParam = " --poly %s" % hex(poly)
 
    backends = [ "ctypes", "cffi", "swigraw", "swigoo" ]
 
    total_measurements = len( data_bytes_list ) * len( backends )
    counter = 0
 
    ## in bytes
    for data_bytes_num in data_bytes_list:
        bits_sizes_list.append( data_bytes_num )
        
        with tempfile.NamedTemporaryFile( prefix="revcrc.data-%s." % data_bytes_num, delete=False ) as tmpData:
            data_string = data_generator * data_bytes_num
            for _ in range(0, data_rows):
                tmpData.write( "%s %s\n" % (data_string, crc_string) )
            tmpData.flush()
                
            for back in backends:
                counter += 1
                binding_data = raw_data[ back ]

                print "Calculating measurement %s of %s" % ( counter, total_measurements )

                cmd_line = main_path + " --alg HW --mode %s --infile %s -b %s%s --silent" % ( mode, tmpData.name, back, polyParam )
                sublist = cmd_line.split( " " )
                  
                measurements = benchmarking_module.measure( sublist, 0, 5, silent=True, method="sub" )
                times_avg = avg( measurements )
                binding_data.append( times_avg )

    dataFrame = pandas.DataFrame( raw_data, index=bits_sizes_list )

    if len( data_bytes_list ) > 1:
        ## lines: matplotlib.axes._subplots.AxesSubplot
        lines = dataFrame.plot.line( title="performance of Python bindings in %s mode" % mode )
        lines.set_xlabel( "data size [B]" )
        lines.set_ylabel( "time [s]" )
    else:
        ## lines: matplotlib.axes._subplots.AxesSubplot
        lines = dataFrame.plot.bar( title="performance of Python bindings in %s mode" % mode )
        lines.set_xlabel( "data size [B]" )
        lines.set_ylabel( "time [s]" )

    data_bytes = prepare_filename( str(data_bytes_list) ) 
    crc_size = ( crc_index + 1 ) * 8
    timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
    plot_output_name = "%s_db%s_crc%s_dr%s_dg%s_sub_%s.png" % (mode, data_bytes, crc_size, data_rows, data_generator, timestr)
    plot_output_path = os.path.join( out_dir, plot_output_name )
    
    print "Saving plot to:", plot_output_path
    plt.savefig( plot_output_path )


def main():
    starttime = time.time()
    
# #     data_bytes = [ element * 2 * 8 for element in [1, 2, 3, 4] ]
# #     data_bytes = [ 32, 64, 96, 128 ]

    data_bytes = [ 8, 16, 32, 64 ]
    measure( data_bytes_list=data_bytes, data_rows= 2, mode="BF" )
    measure( data_bytes_list=data_bytes, data_rows=16, mode="BF" )

    data_bytes = [ 8, 16, 32, 64 ]
    measure( data_bytes_list=data_bytes, data_rows= 2, crc_index=1, mode="BACKWARD", poly=0x1335D )
    measure( data_bytes_list=data_bytes, data_rows=16, crc_index=1, mode="BACKWARD", poly=0x1335D )

    timeDiff = time.time() - starttime
    print "\nTotal measurement time: {:13.8f}s".format(timeDiff)
    
    plt.show()
    return 0


if __name__ == '__main__':
    ret = main()
    sys.exit( ret )