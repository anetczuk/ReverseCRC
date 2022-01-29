#!/bin/bash

set -eu


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


FASTCRC_CLIB_ROOT=$SCRIPT_DIR/../clib
FASTCRC_SRC_ROOT=$FASTCRC_CLIB_ROOT/src
FASTCRC_LIB_DIR=$FASTCRC_CLIB_ROOT/build/install


BUILD_DIR=$SCRIPT_DIR/build


mkdir -p $BUILD_DIR
cd $BUILD_DIR


swig3.0 -python -outcurrentdir -I$FASTCRC_SRC_ROOT $SCRIPT_DIR/fastcrc.swg

#ld -shared example.o example_wrap.o -o _example.so 

gcc -fPIC -Wall -Wextra -shared fastcrc_wrap.c -o _swigoo_fastcrc.so \
    -I$SCRIPT_DIR \
    -L$FASTCRC_LIB_DIR/ -lfastcrc -I/usr/include/python2.7/ -lpython2.7 \
    -Wl,-rpath=$FASTCRC_LIB_DIR
