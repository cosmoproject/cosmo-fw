#!/usr/bin/python
from __future__ import print_function
from cosmoavr.cosmohat import CosmoHat
from time import sleep, time
import csnd6


PRINT = False
TOLERANCE = 0.001

def safesleep(amt):
    if amt > 0:
        sleep(amt)

def run(c, cs, perf):
    switch_state = c.switches()
    switch_last = switch_state
    last_knobs = c.knobs()
    first = True

    count = 0
    now = time()
    while perf.GetStatus() == 0:
        knobs = c.knobs()
        changed = [abs(n-l) > TOLERANCE for n,l in zip(knobs, last_knobs)]
        last_knobs = knobs

        for i, (knob, change) in enumerate(zip(knobs, changed)):
            if change or first:
                cs.SetChannel("P"+str(i), knob)
                if PRINT:
                    print("{}: ".format(i) + "=" * int(knob*80))

        switches = c.switches()
        posedge = [s and not l for s,l in zip(switches, switch_last)]
        changed = [s != l for s,l in zip(switches, switch_last)]
        switch_last = switches

        for i, edge in enumerate(posedge):
            if edge or first:
                switch_state[i] = not switch_state[i]
                cs.SetChannel("T"+str(i), switch_state[i])

        for i, change in enumerate(changed):
            if change or first:
                cs.SetChannel("M"+str(i), switches[i])

        leds = {}
        blink = 0
        # If Csound doesnt run - blink with leds
        for i in range(c.nleds):
            leds[i] = cs.GetChannel("L"+str(i)) != 0
    
        c.set_leds(leds)
        
        now += 0.005
        safesleep(now-time())
        count += 1
        first = False



def main(csound_file):
    c = CosmoHat()
    try:
        while True:
            cs = csnd6.Csound()
            res = cs.Compile(csound_file)
            if res == 0:
                perf = csnd6.CsoundPerformanceThread(cs)
                perf.Play()
                try:
                    run(c, cs, perf)
                finally:
                    perf.Stop()
                    perf.Join()
                    cs.Stop()
                    cs.Cleanup()
            # Script stopped or didn't compile. Blink leds a couple of times
            on = {}
            off = {}
            for i in range(c.nleds):
                on[i] = True
                off[i] = False
            for i in range(5):
                for j in range(2):
                    c.set_leds(on)
                    sleep(0.1)
                    c.set_leds(off)
                    sleep(0.05)
                sleep(0.5)
    finally:
        c.stop()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: {} <file.csd>".format(sys.argv[0]))
        sys.exit(1)
    csound_file = sys.argv[1]
    try:
        main(csound_file)
    except KeyboardInterrupt:
        pass

