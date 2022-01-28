##
##
##

import os


SCRIPT_DIR      = os.path.realpath( os.path.dirname( __file__ ) )
FASTCRC_ROOT    = os.path.join( SCRIPT_DIR )

FASTCRC_CLIB_DIR      = os.path.join( FASTCRC_ROOT, "clib" )
FASTCRC_CLIB_SRC_DIR  = os.path.join( FASTCRC_CLIB_DIR, "src" )
FASTCRC_CLIB_BIN_DIR  = os.path.join( FASTCRC_CLIB_DIR, "build", "install" )

FASTCRC_CLIB_LIB_PATH = os.path.join( FASTCRC_CLIB_BIN_DIR, "libfastcrc.so" )
