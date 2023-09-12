#!/bin/bash

# /!\ PLEASE FILL IN THIS VALUE /!\
touch_device_name=""

if [ $1 == "--reset" ] ; then
    echo "Resetting touchpad transformation matrix"
    xinput set-prop $touch_device_name --type=float "Coordinate Transformation Matrix" 1 0 0 0 1 0 0 0 1
    return
fi

echo -e "\nRetrieving monitor information..."
lines=$(xrandr --listactivemonitors | wc -l)
raw=$(xrandr --listactivemonitors | tail -n $(($lines-1)))

echo $raw | cut -d ' ' -f 2-3

# /!\ PLEASE FILL IN THESE VALUES /!\
touch_area_width=
touch_area_height=
touch_area_x_offset=
touch_area_y_offset=
total_width=
total_height=

echo -e "\nCalculating transformation matrix values..."
c0=$(($touch_area_width / $total_width))
c1=$(($touch_area_x_offset / $total_width))

c2=$(($touch_area_height / $total_height))
c3=$(($touch_area_y_offset / $total_height))


echo -e "\nNew transformation matrix:"
echo -e "$c0 0 $c1 \n 0 $c2 $c3 \n 0 0 1\n"


read -r -p "Overwrite transformation matrix with these new values ? [y/n] " 
if [[ $REPLY = "y" ]]
then
    echo -e "\nUpdating touchpad transformation matrix ..."
    xinput set-prop $touch_device_name --type=float "Coordinate Transformation Matrix" $c0 0 $c1 0 $c2 $c3 0 0 1
else
    echo "Touchpad transformation matrix udpate canceled"
fi
