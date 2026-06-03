#!/bin/bash
# Flash script for STM32 Vehicle ECU using STM32_Programmer_CLI

BINARY="/home/neeraj/Documents/Dashboard/stm32-virtual-vehicle-ecu/Debug/Vehicle_ECU.elf"
PROGRAMMER="/opt/st/stm32cubeide_1.19.0/plugins/com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.linux64_2.2.200.202503041107/tools/bin/STM32_Programmer_CLI"

echo "================================================"
echo "  STM32 Firmware Flasher"
echo "================================================"

if [ ! -f "$BINARY" ]; then
    echo "❌ Error: Binary not found at $BINARY"
    echo "   Please build the project in STM32CubeIDE first."
    exit 1
fi

if [ ! -f "$PROGRAMMER" ]; then
    echo "⚠️  Warning: STM32_Programmer_CLI not found at $PROGRAMMER"
    echo "   Falling back to system path..."
    PROGRAMMER="STM32_Programmer_CLI"
fi

echo "🚀 Flashing using STM32_Programmer_CLI..."
"$PROGRAMMER" -c port=SWD -w "$BINARY" -v -rst

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Flash successful!"
    exit 0
else
    echo ""
    echo "❌ Error: Flash failed."
    exit 1
fi
