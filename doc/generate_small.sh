#!/bin/bash

set -eu

## ‘**’ used in a input_name expansion context will match all files and zero or more directories and subdirectories
shopt -s globstar


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


## $1 -- command format
## $2 -- from file (suffix)
## $3 -- to file (suffix)
convert_files() {
    local convert_command="$1"
    local from_suffix="$2"
    local to_suffix="$3"
    
    for input_name in $SCRIPT_DIR/**; do
        if [[ $input_name != *"${from_suffix}"* ]]; then
            continue
        fi
        if [[ $input_name == *"${to_suffix}"* ]]; then
            continue
        fi
        output_name=${input_name/$from_suffix/$to_suffix}
        echo "converting: $input_name -> $output_name"

        printf -v cmd "$convert_command" "$input_name" "$output_name"
        
        ## executing command        
        ##echo "executing $cmd"
        eval "$cmd"
    done
}


### convert $input_name -resize 320 $output_name
### convert $input_name -resize 200x100 $output_name
## $1 -- file extension
convert_images() {
    local cmd="convert %s -resize 320 %s"
    local file_ext="$1"
    convert_files "$cmd" ".$file_ext" "-small.$file_ext"
}


### ffmpeg -hide_banner -loglevel error -y -i $input_name $output_name
## convert mp4 to giff
convert_mp4() {
    local cmd="ffmpeg -hide_banner -loglevel error -y -i %s -vf scale=320:-1 %s"
    convert_files "$cmd" ".mp4" "-small.gif"
}


### gifsicle $input_name --resize-width 240 > $output_name
## convert giff to small one
convert_giffs() {
    local cmd="gifsicle %s --resize-width 240 > %s"
    convert_files "$cmd" ".gif" "-small.gif"
}


convert_images "png"
convert_mp4
convert_giffs


echo "done"
