#!/bin/bash

CPU_THRESHOLD=80
SERVICE_NAME="laravel"

while true; do
  CPU_USAGE=$(top -b -n1 | grep "$SERVICE_NAME" | awk '{print $9}' | cut -d. -f1)
  if [ "$CPU_USAGE" -gt "$CPU_THRESHOLD" ]; then
    echo "CPU usage ($CPU_USAGE%) exceeded threshold. Restarting $SERVICE_NAME..."
    systemctl restart $SERVICE_NAME
  fi
  sleep 10
done