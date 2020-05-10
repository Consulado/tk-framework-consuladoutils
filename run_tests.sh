#!/bin/bash

DOTENV="$PWD/.env"

while IFS='=' read -r col1 col2
do
    export $col1=$col2
done < "$DOTENV"

export TK_FRAMEWORK_CONSULADOUTILS="$PWD"
coverage run -m unittest discover -s "./tests" -p '*_test.py'
