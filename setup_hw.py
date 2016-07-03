#!/usr/bin/python
from __future__ import print_function
from cosmoavr.cosmohat import CosmoHat
import time

def main():
    
    c = CosmoHat()
    print("Got version '{}'".format(c.version()))
    j = 0;

    knobs = list(c.knobs(raw=True))
    lowest = knobs[:]
    highest = knobs[:]
    
    while True:
        for i, knob in enumerate(c.knobs(raw=True)):
            lowest[i] = min(lowest[i], knob)
            highest[i] = max(highest[i], knob)
            print("knob {}: {:4} ({}-{})".format(i, int(knob), lowest[i], highest[i]))
        print("")
        for i, sw in enumerate(c.switches()):
            print("sw {}: {}".format(i, sw))
        print("")
        if c.nleds:
            for i in range(c.nleds):
                c.set_led(i, i == j)
            j = (j + 1) % c.nleds
        time.sleep(.5)
    
    
    
if __name__ == "__main__":
    main()
