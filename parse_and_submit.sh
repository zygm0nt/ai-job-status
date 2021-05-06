#!/bin/bash

stdin=$(cat)

app_id=$(echo $stdin | tail -1 | cut -d "/" -f 6 )

echo -n $app_id | nc localhost 3000