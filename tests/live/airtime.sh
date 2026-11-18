#!/bin/bash
# needs: export URA_HUB_PW=<hub web password>
# airtime.sh <pct_hour>  — set Ludwigsburg's hourly airtime limit, print before/after
h=https://127.0.0.1:8091; j=/tmp/ura-t/cj.air
curl -sk -c $j -o /dev/null -H 'Content-Type: application/json' -d "{\"password\":\"$URA_HUB_PW\"}" $h/api/login
curl -sk -b $j $h/api/config | python3 -c "import json,sys; print('before:', json.load(sys.stdin)['airtime'])"
curl -sk -b $j -H 'Content-Type: application/json' -d "{\"airtime\":{\"pct_hour\":$1,\"pct_day\":0}}" $h/api/hub; echo
rm -f $j
