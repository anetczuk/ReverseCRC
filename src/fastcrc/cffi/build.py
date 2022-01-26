#!/usr/bin/env python2
##
##
##
##

import os
from cffi import FFI


SCRIPT_DIR      = os.path.realpath( os.path.dirname( __file__ ) )
FASTCRC_ROOT    = os.path.join( SCRIPT_DIR, os.pardir )

FASTCRC_SRC_DIR = os.path.join( FASTCRC_ROOT, "src", "crchw" )
FASTCRC_LIB_DIR = os.path.join( FASTCRC_ROOT, "build", "install" )
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
    include_dirs=[ FASTCRC_SRC_DIR ],

    libraries=["fastcrc"],
    library_dirs=[ FASTCRC_LIB_DIR ],
    extra_link_args=[ '-Wl,-rpath=' + FASTCRC_LIB_DIR ]
)


ffibuilder.compile( tmpdir=CFFI_BUILD_DIR )


print "build completed"
