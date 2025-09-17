#!/bin/bash

# Combined pentest script staging for crash-only-at-boot conditions
# Alternates between different attack vectors to test ECU resilience

set -e

VENV_PATH="venv/bin/activate"
TIMEOUT=10  # seconds per test phase
RESET_DELAY=2  # seconds between phases

echo "Starting combined pentest staging..."
echo "======================================="

# Ensure virtual environment is active
source $VENV_PATH

echo "[Phase 1] Initial bus reset storm to establish baseline"
echo "Running rapid_reset_host.py with 50 cycles..."
timeout $TIMEOUT python examples/pentest/rapid_reset_host.py --cycles 50 --reset-delay 0.05 --settle 0.01 || echo "Phase 1 timeout/completed"

sleep $RESET_DELAY

echo "[Phase 2] Control transfer oversizing attack"
echo "Running ctrl_transfer_oversize.py..."
timeout $TIMEOUT python examples/pentest/ctrl_transfer_oversize.py --max-payload 8192 --spray-interval 0.1 || echo "Phase 2 timeout/completed"

sleep $RESET_DELAY

echo "[Phase 3] Descriptor fuzzing to confuse enumeration"
echo "Running descriptor_fuzzer.py..."
timeout $TIMEOUT python examples/pentest/descriptor_fuzzer.py || echo "Phase 3 timeout/completed"

sleep $RESET_DELAY

echo "[Phase 4] Reset storm during enumeration confusion"
echo "Running rapid_reset_host.py with rapid cycles..."
timeout $TIMEOUT python examples/pentest/rapid_reset_host.py --cycles 100 --reset-delay 0.02 --settle 0.005 || echo "Phase 4 timeout/completed"

sleep $RESET_DELAY

echo "[Phase 5] Composite device stress test"
echo "Running composite_hid_mass.py with test payload..."
# Create temporary disk image if it doesn't exist
if [ ! -f /tmp/test_disk.img ]; then
    dd if=/dev/zero of=/tmp/test_disk.img bs=1M count=1 2>/dev/null
fi
timeout $TIMEOUT python examples/pentest/composite_hid_mass.py /tmp/test_disk.img --payload "CRASH TEST" || echo "Phase 5 timeout/completed"

sleep $RESET_DELAY

echo "[Phase 6] Final reset storm to test crash-only-at-boot"
echo "Running rapid_reset_host.py with sustained pressure..."
timeout $TIMEOUT python examples/pentest/rapid_reset_host.py --cycles 200 --reset-delay 0.01 --settle 0.002 || echo "Phase 6 timeout/completed"

echo ""
echo "Combined pentest staging completed!"
echo "=================================="
echo "Monitor target device for:"
echo "- Boot failures after reset storms"
echo "- Enumeration hangs or crashes"
echo "- Unexpected device behavior"
echo "- Memory corruption indicators"