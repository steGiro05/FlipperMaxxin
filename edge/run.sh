#!/bin/bash
set -e

echo "Searching for Flipper in /dev/serial/by-id/ ..."

DEVICE=""
for i in {1..10}; do
    DEVICE=$(ls /dev/serial/by-id/ 2>/dev/null | grep "usb-Flipper" || true)
    if [ -n "$DEVICE" ]; then
        break
    fi
    echo "Device not found, retry ($i/10)..."
    sleep 2
done

if [ -z "$DEVICE" ]; then
    echo "ERROR: no Flipper found in /dev/serial/by-id/"
    exit 1
fi

DEVICE_PATH="/dev/serial/by-id/$DEVICE"
REAL_PATH=$(readlink -f "$DEVICE_PATH")

echo "Flipper found: $DEVICE_PATH -> $REAL_PATH"

# chmod 666 "$REAL_PATH" 2>/dev/null || {
#     echo "ERROR: failed to modify permissions for $REAL_PATH."
#     exit 1
# }

echo "$DEVICE_PATH" > .conf

source .venv/bin/activate
exec python3 flipper_manager.py --config .conf