#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


CACHE_DIR=$SCRIPT_DIR/../tmp/.mypy_cache


cd $SCRIPT_DIR/../src


echo "running mypy"
mypy --py2 --cache-dir $CACHE_DIR --no-strict-optional --ignore-missing-imports -p crc -p fastcrc -p testcrc -p testfastcrc

echo "mypy finished"
