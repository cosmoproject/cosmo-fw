from __future__ import print_function
from cosmoavr.cosmohat import CosmoHat
import time

def main(c):
    c.start()
    print("Got version '{}'".format(c.version()))
    c.set_gpios({0: (1, 1),
                 1: (1, 1),
                 2: (1, 1),
                 3: (1, 1)})
    i = 0
    while True:
        adcs = c.adcs()
        print("ADC:", adcs)
        a = adcs[0]
        #print("GPIO:", c.get_gpios())
        c.set_gpios({0: (a > 1000/3, 1),
                     1: (a > 2000/3, 1),
                     2: (a > 1000, 1),
                     3: (i & 8, 1)})
        time.sleep(0.1)
                
        
if __name__ == "__main__":
    c = CosmoHat()
    try:
        main(c)
    except KeyboardInterrupt:
        c.stop()

