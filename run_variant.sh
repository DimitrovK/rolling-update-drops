#!/bin/bash
# run_variant.sh <label> <seconds> <trigger_at>
set -u
export PATH=$HOME/.local/bin:$PATH
L="$1"; SECS="${2:-110}"; TRIG="${3:-25}"
IP=$(cat lb_ip)
mkdir -p out/$L
GEN=$(( $(date +%s) % 100000 ))

./watch_endpoints.sh > out/$L/endpoints.log 2>/dev/null &
W=$!
kubectl logs -l app=web --all-containers --prefix -f --since=1s > out/$L/pods.log 2>/dev/null &
P=$!

python3 load.py "http://$IP/" "$SECS" 20 out/$L/requests.json > out/$L/summary.txt 2>&1 &
LOAD=$!

sleep "$TRIG"
echo "$(date +%s.%N) ROLLOUT TRIGGERED" >> out/$L/events.log
kubectl set env deploy/web GEN="$GEN" >/dev/null 2>&1
kubectl rollout status deploy/web --timeout=180s > out/$L/rollout.txt 2>&1
echo "$(date +%s.%N) ROLLOUT COMPLETE" >> out/$L/events.log

wait $LOAD
kill $W $P 2>/dev/null
echo "=== $L ==="; cat out/$L/summary.txt
