#!/bin/bash

function error {
    echo "Error: $1"
}

# Check if this script is being sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    error "this script must be sourced"
    return 1
fi

# Ensure this is being executed from the project directory
if [[ ! -f "./setup_test.sh" ]] || [[ ! -d "./src/retree" ]]; then
    error "this script must be sourced from root directory of retree repository"
    return 1
fi

project_dir=$(realpath ".")
module_dir="${project_dir}/src/retree"
export PYTHONPATH="${module_dir}:$PYTHONPATH"
