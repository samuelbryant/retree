#!/bin/bash
# This represents everything that should be run before pushing to main branch
# Eventually this will be automated.


export PROJECT="retree"
export SEC_START_SYMBOL="∇"
export SEC_HEADER_SYMBOL="-"
export SEC_FINISH_SYMBOL="∆"

function start_section {
    print_fill_line "$SEC_START_SYMBOL"
    echo -e ">> \e[34m$1\e[0;0m"
    print_fill_line "$SEC_HEADER_SYMBOL"
}

function finish_section {
    print_fill_line "$SEC_FINISH_SYMBOL"
    echo ""
}

function print_fill_line {
    symbol="$1"
    line=""
    for ((i = 0; i<80; i++)) {
        line="${line}${symbol}"
    }
    echo "$line"
}

function check_result {
    if [ "$?" -eq "0" ]; then    
        echo -e ">> \e[32m$1 successful!\e[0;0m"
        finish_section
    else
        echo -e ">> \e[31;1m$1 failed!\e[0;0m" >> /dev/stderr
        finish_section
        exit 1
    fi
}

start_section "(1/3) Running type checker"
mypy src
check_result "Type checking"

start_section "(2/3) Running unit tests"
. setup_test.sh
python tests/test_retree.py >> /dev/null
check_result "Unit tests"

start_section "(3/3) Running code linting"
ruff check src/
check_result "Linting"

echo -e "\e[32;1mAll tests passed!\e[0;0m"
