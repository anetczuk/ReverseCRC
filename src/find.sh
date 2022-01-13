#!/bin/bash


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


args=()
coverage=0

for i in "$@"; do
case $i in
    --coverage)             coverage=1
                            shift                   # past argument with no value
                            ;;
    *)                      args+=($i)              ## add to array
                            ;;                      # unknown option
esac
done


if [ $coverage -eq 0 ]; then
    $SCRIPT_DIR/main.py "${args[@]}"
else
    cd $SCRIPT_DIR
    
    tmprootdir=$(dirname $(mktemp -u))
    revCrcTmpDir="$tmprootdir/revcrc"
    htmlcovdir="$revCrcTmpDir/htmlcov"
    mkdir -p $htmlcovdir
    
    ## requires coverage.py
    coverage run --branch -m main "${args[@]}"
    ## generate html pages in htmlcov directory based on coverage data
    coverage html -d $htmlcovdir
    echo -e "\nCoverage HTML output: $htmlcovdir/index.html"
fi
