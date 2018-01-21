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


cd $SCRIPT_DIR


if [ $coverage -eq 0 ]; then
    python -m main "${args[@]}"
else
    ## requires coverage.py
    coverage run -m main "${args[@]}"
fi
