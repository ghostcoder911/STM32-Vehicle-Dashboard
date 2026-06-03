#!/bin/bash
# Unified script to flash STM32 and start the Vehicle Dashboard

echo "================================================"
echo "  STM32 Flash & Dashboard Startup"
echo "================================================"
echo ""

# 1. Flash the STM32
echo "📡 Step 1: Flashing STM32 Firmware..."
./flash_stm32.sh
if [ $? -ne 0 ]; then
    echo "❌ Error: Flashing failed. Aborting."
    exit 1
fi

echo ""
echo "✅ Flash successful! Waiting for board to reset..."
sleep 2

# 2. Kill any existing dashboard process
echo "🔍 Step 2: Cleaning up existing dashboard processes..."
fuser -k 5000/tcp &> /dev/null

# 3. Start the dashboard
echo "🚀 Step 3: Starting Vehicle Dashboard..."
cd dashboard && ./run_dashboard.sh
