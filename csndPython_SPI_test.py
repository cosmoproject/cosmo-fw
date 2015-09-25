from __future__ import print_function
from cosmoavr.cosmohat import CosmoHat
from time import sleep, time
import csnd6

csoundFile = "../csound/spi-input-test.csd"
#csoundFile = "../csound/audio-spi-input-test.csd"
#csoundFile = "../csound/reverb_tremo.csd"
#csoundFile = "../csound/Filter_Reverb_Delay.csd"

def safesleep(amt):
    if amt > 0:
        sleep(amt)

def main(c):
 
    cs = csnd6.Csound()
    res = cs.Compile(csoundFile)
    if res == 0:
	perf = csnd6.CsoundPerformanceThread(cs)
	perf.Play()
 
    last_nobs = c.nobs()
    tolerance = 0.001

    count = 0
    now = time()
    while True:
        nobs = c.nobs()
        changed = [abs(n-l) > tolerance for n,l in zip(nobs, last_nobs)]
        last_nobs = nobs

        for i, (nob, change) in enumerate(zip(nobs, changed)):
            if change:
                cs.SetChannel("P"+str(i), nob)
                print("{}: ".format(i) + "=" * int(nob*80))
        leds = {}
        for i, sw in enumerate(c.switches()):
            leds[i] = sw != ((count+i) % 8 != 0)
        c.set_leds(leds)
        
        now += 0.01
        safesleep(now-time())
        count += 1



if __name__ == "__main__":
    c = CosmoHat(
        switches=[0,1,2,3],
        leds=[4,7,6,5],
        nobs=[(0, (8057, 0)),
              (1, (8056, 0)),
              (2, (8056, 0)),
              (3, (8057, 0)),
              (4, (8056, 0)),
              (6, (8056, 0)),
              (7, (8058, 0))])
    try:
        main(c)
    except KeyboardInterrupt:
        c.stop()

