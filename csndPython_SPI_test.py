#!/usr/bin/python
from __future__ import print_function
from cosmoavr.cosmohat import CosmoHat
from time import sleep, time
import csnd6

#csoundFile = "/home/pi/csound/Pitchflex.csd"
#csoundFile = "/home/pi/csound/audio-spi-input-test.csd"
#csoundFile = "/home/pi/csound/reverb.csd"
#csoundFile = "/home/pi/csound/delay_stereo.csd"
#csoundFile = "/home/pi/csound/multi_delay_stereo.csd"
#csoundFile = "/home/pi/csound/conv.csd"
#csoundFile = "/home/pi/csound/grain.csd"
#csoundFile = "/home/pi/csound/pvsmooth.csd"
#csoundFile = "/home/pi/csound/pvsblur.csd"
#csoundFile = "/home/pi/csound/pvsfreeze.csd"
#csoundFile = "/home/pi/csound/Filter_Reverb_Delay.csd"
#csoundFile = "/home/pi/csound/audio-in-test.csd"
#csoundFile = "/home/pi/csound/FX4_Shutter2.csd"
#csoundFile = "/home/pi/csound/FX5_BerntDuo_Repeater2.csd"
#csoundFile = "/home/pi/csound/csound_conf2015.csd"
csoundFile = "/home/pi/cosmo-dsp/WorkshopTestFiles/synthesizer-knob-test.csd"

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
    last_nobs = c.nobs()
    tolerance = 0.001
    first = True

    count = 0
    now = time()
    while True:
        nobs = c.nobs()
        changed = [abs(n-l) > tolerance for n,l in zip(nobs, last_nobs)]
        last_nobs = nobs

        for i, (nob, change) in enumerate(zip(nobs, changed)):
            if change or first:
                cs.SetChannel("P"+str(i), nob)
                print("{}: ".format(i) + "=" * int(nob*80))

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
        for i in range(c.nleds):
            leds[i] = cs.GetChannel("L"+str(i)) != 0
            #leds[i] = switch_state[i]
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

