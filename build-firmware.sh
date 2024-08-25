cd firmware
../.venv/bin/python -m platformio run
cd ..
cp firmware/.pio/build/lpl/firmware.hex emonth2-dual-sensor-firmware.hex
