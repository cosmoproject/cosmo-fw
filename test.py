from __future__ import print_function
from cosmoavr.cosmohat import CosmoHat

def main(c):
    c.start()
    print("Got version '{}'".format(c.version()))
    while True:
        #print("ADC:", c.adcs([0]))
        print("GPIO:", c.get_gpios())
        #time.sleep(0.5)
                
        
if __name__ == "__main__":
    c = CosmoHat()
    try:
        main(c)
    except KeyboardInterrupt:
        c.stop()

