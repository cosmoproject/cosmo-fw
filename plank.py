#!/usr/bin/env python

import cosmoavr.cosmoplank
import time

if __name__ == "__main__":
    c = cosmoavr.cosmoplank.CosmoPlank()
    b = 1
    while True:
        print ""
        print(c.knobs(raw=False))
        print(c.knobs(raw=True))
        print(c.switches())
        for i in range(8):
            c.set_led(i, (1<<i) & b)
        b += 1
        time.sleep(0.1)
