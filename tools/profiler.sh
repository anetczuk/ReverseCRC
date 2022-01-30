#!/bin/bash

set -eu


out_file="$(pwd)/out.prof"

echo "Starting profiler"


python2 -m cProfile -o $out_file $@


echo ""
echo "View output: pyprof2calltree -k -i $out_file"
