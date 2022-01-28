#!/usr/bin/env python2
##
##
##
##

import os
from cffi import FFI

import imp


SCRIPT_DIR         = os.path.realpath( os.path.dirname( __file__ ) )
fastcrc_paths_path = os.path.join( SCRIPT_DIR, os.pardir, "paths.py" )

fastcrc_paths = imp.load_source( 'fastcrc_paths', fastcrc_paths_path )

FASTCRC_INCLUDE_DIR = os.path.join( fastcrc_paths.FASTCRC_CLIB_SRC_DIR, "crchw" )

CFFI_BUILD_DIR  = os.path.join( SCRIPT_DIR, "build" )


ffibuilder = FFI()


with open( os.path.join( SCRIPT_DIR, "fastcrc_interface.h"  )) as f:
    ffibuilder.cdef( f.read() )


ffibuilder.set_source(
    "cffi_fastcrc",
    ## no source neede, because linking to existing library
    r"""
#include "crc8hw.h"
#include "crc16hw.h"
#include "crc16hwinvert.h"
""",
    include_dirs=[ FASTCRC_INCLUDE_DIR ],

    libraries=["fastcrc"],
    library_dirs=[ fastcrc_paths.FASTCRC_CLIB_BIN_DIR ],
    extra_link_args=[ '-Wl,-rpath=' + fastcrc_paths.FASTCRC_CLIB_BIN_DIR ]
)


ffibuilder.compile( tmpdir=CFFI_BUILD_DIR )


print "build completed"
