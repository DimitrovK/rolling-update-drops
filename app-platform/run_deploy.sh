#!/bin/bash
# run_deploy.sh <label> <new_gen> <shutdown_mode> <load_seconds>
set -u; export PATH=$HOME/.local/bin:$PATH
L=$1; G=$2; MODE=$3; SECS=${4:-420}
APP=$(cat app_id); URL=$(cat app_url); mkdir -p out/$L
python3 load.py "$URL" "$SECS" 20 out/$L/requests.json > out/$L/summary.txt 2>&1 &
LOAD=$!
python3 slowprobe.py "$URL" 150 out/$L/slow.json 20 > out/$L/slow_summary.txt 2>&1 &
SLOW=$!
sleep 30
sed -e "s/value: \"[0-9]*\"/value: \"$G\"/" -e "s/value: immediate\|value: graceful\|value: drain_conns/value: $MODE/" spec.yaml > out/$L/spec.yaml
echo "$(date +%s.%N) UPDATE_SUBMITTED gen=$G mode=$MODE" > out/$L/events.log
doctl apps update "$APP" --spec out/$L/spec.yaml --format ID --no-header >/dev/null 2>&1
prev=""
while kill -0 $LOAD 2>/dev/null; do
  ph=$(doctl apps list-deployments "$APP" --format ID,Phase --no-header 2>/dev/null | head -1 | tr -s ' ')
  if [ "$ph" != "$prev" ]; then echo "$(date +%s.%N) PHASE $ph" >> out/$L/events.log; prev="$ph"; fi
  sleep 3
done
wait $LOAD; wait $SLOW
echo "=== $L ==="; cat out/$L/summary.txt; cat out/$L/slow_summary.txt
grep PHASE out/$L/events.log | awk -v t0=$(head -1 out/$L/events.log | cut -d' ' -f1) '{printf "   t+%6.1fs  %s %s\n", $1-t0, $4, $5}'
