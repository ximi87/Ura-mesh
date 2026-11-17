#!/bin/bash
# start test server + 2 hubs (no radios) on localhost
T=/tmp/ura-t
for port in 8199 8198 8197 8196; do pid=$(ss -ltnp "sport = :$port" | grep -oP 'pid=\K[0-9]+' | head -1); [ -n "$pid" ] && kill $pid; done
sleep 1
rm -rf $T/sdata $T/hA $T/hB
cd $T/server && URA_DATA=$T/sdata URA_PORT=8198 URA_WEB_PORT=8199 setsid nohup python3 -u ura_server.py > $T/server.log 2>&1 < /dev/null &
cd $T/hub && URA_DATA=$T/hA URA_WEB_PORT=8197 setsid nohup /opt/fleet/venv/bin/python -u ura_hub.py > $T/hubA.log 2>&1 < /dev/null &
cd $T/hub && URA_DATA=$T/hB URA_WEB_PORT=8196 setsid nohup /opt/fleet/venv/bin/python -u ura_hub.py > $T/hubB.log 2>&1 < /dev/null &
sleep 4
tail -n 2 $T/server.log; tail -n 1 $T/hubA.log $T/hubB.log
