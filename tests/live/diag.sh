#!/bin/bash
# diag.sh <hub-url> <node> <kind...>
h=$1; node=$2; shift 2; j=/tmp/ura-t/cj.diag.$$
curl -sk -c $j -o /dev/null -H 'Content-Type: application/json' -d '{"password":"${URA_HUB_PW}"}' $h/api/login
for k in "$@"; do echo "$k: $(curl -sk -m 700 -b $j -H 'Content-Type: application/json' -d "{\"node\":\"$node\",\"kind\":\"$k\",\"text\":\"Ura test from the hub (please ignore)\"}" $h/api/diag)"; done
rm -f $j
