#!/bin/bash

raw=$(xrandr --listactivemonitors | tail -n 2)
names=$(echo "$raw" | cut -d ' ' -f 3)
dims=$(echo "$raw" | cut -d ' ' -f 3 | )

echo Choose the monitor with the touchpad
