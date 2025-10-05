#!/usr/bin/env bash
# Simulate the exact behavior of: curl ... | bash

echo "Simulating: curl -sSL ... | bash"
echo "=================================="
echo

# Extract only the critical parts that run before installation
cat install.sh | head -180 | bash

echo
echo "=================================="
echo "Test completed without hanging!"
