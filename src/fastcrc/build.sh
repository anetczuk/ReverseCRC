#!/bin/bash

set -eu


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


SRC_ROOT=$SCRIPT_DIR/src
BUILD_DIR=$SCRIPT_DIR/build


mkdir -p $BUILD_DIR
cd $BUILD_DIR


## configure
cmake $SRC_ROOT . 

## build and install
cmake --build . --target install
