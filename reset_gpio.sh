#!/bin/sh
GPIO=25
echo ${GPIO} | sudo tee /sys/class/gpio/export > /dev/null
echo out | sudo tee /sys/class/gpio/gpio${GPIO}/direction > /dev/null
echo 1 | sudo tee /sys/class/gpio/gpio${GPIO}/value > /dev/null
