#!/bin/bash
# timestamped record of which pod IPs are in the Service's EndpointSlice
while true; do
  printf '%s %s\n' "$(date +%s.%N)" \
    "$(kubectl get endpointslices -l kubernetes.io/service-name=web \
        -o jsonpath='{range .items[*].endpoints[*]}{.addresses[0]}={.conditions.ready}{" "}{end}' 2>/dev/null)"
  sleep 0.25
done
