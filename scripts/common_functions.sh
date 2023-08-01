#!/usr/bin/bash


function exit_with_info() {
    local return_code=$1
    shift
    local info=$*

    if [ $return_code -eq 0 ]; then
        echo $info
        exit 0
    else
        >&2 echo $info
        exit $return_code
    fi
}


function return_with_info() {
    exit_with_info 0 $@
}


function do_tox() {
    info "Check if python version meets the requirement defined in tox.ini"
}


eval $@
