#!/usr/bin/python
from __future__ import print_function
from cosmoavr.cosmohat import CosmoHat
import time

def main(c):
    print("Got version '{}'".format(c.version()))
    i = 0
    while True:
        i += 1
        inputs = c.switches()
        #print(inputs)
        for i, nob in enumerate(c.nobs()):
            print("{}: ".format(i) + "=" * int(nob*80))
        print("")
        c.set_leds(dict((i, inp) for i, inp in enumerate(inputs)))
        
        #adcs = c.adcs()
        #print("ADC:", adcs)
        time.sleep(0.05)
                
        
if __name__ == "__main__":
    c = CosmoHat()
    try:
        main(c)
    except KeyboardInterrupt:
        c.stop()

