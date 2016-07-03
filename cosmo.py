#!/usr/bin/python
from __future__ import print_function
from cosmoavr.cosmohat import CosmoHat
from time import sleep, time
import csnd6

#csoundFile = "/home/pi/cosmo-dsp/WorkshopTestFiles/knob-test.csd"
#csoundFile = "/home/pi/cosmo-dsp/WorkshopTestFiles/switch-led-test.csd"
#csoundFile = "/home/pi/cosmo-dsp/WorkshopTestFiles/synthesizer.csd"
#csoundFile = "/home/pi/cosmo-dsp/WorkshopTestFiles/knob-test.csd"
csoundFile = "/home/pi/cosmo-dsp/Instruments/UDOInstrumentSetup.csd"
#csoundFile = "/home/pi/cosmo-dsp/Effects/ExampleSetup.csd"

PRINT = False

def safesleep(amt):
    if amt > 0:
        sleep(amt)

def main(c):
 
    cs = csnd6.Csound()
    res = cs.Compile(csoundFile)
    if res == 0:
	perf = csnd6.CsoundPerformanceThread(cs)
	perf.Play()


    switch_state = c.switches()
    switch_last = switch_state
    last_knobs = c.knobs()
    tolerance = 0.001
    first = True

    count = 0
    now = time()
    while True:
        knobs = c.knobs()
        changed = [abs(n-l) > tolerance for n,l in zip(knobs, last_knobs)]
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
        for i in range(c.nleds):
	    if res == 0:
		leds[i] = cs.GetChannel("L"+str(i)) != 0
            	#leds[i] = switch_state[i]
	    else: # If Csound doesnt run - blink with leds
		leds[i] = blink + 1
		blink = blink % 2
        c.set_leds(leds)
        
        now += 0.005
        safesleep(now-time())
        count += 1
        first = False



if __name__ == "__main__":
    c = CosmoHat()
    try:
        main(c)
    except KeyboardInterrupt:
        c.stop()

