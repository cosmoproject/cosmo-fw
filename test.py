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

