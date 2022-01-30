#!/bin/bash

set -eu


## SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


tmpdir=$(dirname $(mktemp -u))
timestamp=$(date +%s)

out_file=$(mktemp ${tmpdir}/out.prof.${timestamp}.XXXXXX)
#out_file="$(pwd)/out.prof"


echo "Starting profiler"


python2 -m cProfile -o $out_file $@


echo ""
echo "View output: pyprof2calltree -k -i $out_file"

### browser based, installation: pip2 install snakeviz
echo "Borowser-based view output: snakeviz $out_file"


##rm ${out_file}
