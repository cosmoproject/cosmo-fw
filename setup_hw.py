#!/usr/bin/python
from __future__ import print_function
from cosmoavr.cosmohat import CosmoHat
import time

def main():
    
    c = CosmoHat()
    print("Got version '{}'".format(c.version()))
    j = 0;
    while True:
        for i, knob in enumerate(c.knobs(raw=True)):
            print("knob {}: {}".format(i, int(knob)))
        print("")
        for i, sw in enumerate(c.switches()):
            print("sw {}: {}".format(i, sw))
        print("")
        for i in range(c.nleds):
            c.set_led(i, i == j)
        j = (j + 1) % c.nleds
        time.sleep(.5)
    
    
    
if __name__ == "__main__":
    main()
