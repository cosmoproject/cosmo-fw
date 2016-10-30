#!/usr/bin/env python

import cosmoavr.cosmoplank
import time

if __name__ == "__main__":
    c = cosmoavr.cosmoplank.CosmoPlank()
    b = 1
    while True:
        print ""
        print(c.knobs(raw=True))
        print(c.switches())
        c.set_led(0, b)
        b = (b+1)%2
        time.sleep(0.1)
