from __future__ import print_function
from cosmoavr.cosmohat import CosmoHat
import time
import csnd6

#csoundFile = "../csound/audio-spi-input-test.csd"
csoundFile = "../csound/reverb_tremo.csd"

def main(c):
    last_read1 = 0
    last_read2 = 0
    last_read3 = 0
    last_read4 = 0
    last_read5 = 0
    last_read8 = 0

    # we'll assume that the pot didn't move
    trim_pin_changed1 = False
    trim_pin_changed2 = False
    trim_pin_changed3 = False
    trim_pin_changed4 = False
    trim_pin_changed5 = False
    trim_pin_changed8 = False

    tolerance = 150
 
    c.start()
    print("Got version '{}'".format(c.version()))
    c.set_gpios({0: (1, 1),
                 1: (1, 1),
                 2: (1, 1),
                 3: (1, 1)})
    cs = csnd6.Csound()
    res = cs.Compile(csoundFile)
    if res == 0:
	perf = csnd6.CsoundPerformanceThread(cs)
	perf.Play()
    i = 0
    while True:
        adcs = c.adcs()
#        print("ADC:", adcs)
        pin1 = adcs[0]
	pin2 = adcs[1]
	pin3 = adcs[2]
	pin4 = adcs[3]
	pin5 = adcs[4]
	pin8 = adcs[7]

       # how much has it changed since the last read?
        pin_adjust1 = abs(pin1 - last_read1)
        pin_adjust2 = abs(pin2 - last_read2)
        pin_adjust3 = abs(pin3 - last_read3)
        pin_adjust4 = abs(pin4 - last_read4)
        pin_adjust5 = abs(pin5 - last_read5)
        pin_adjust8 = abs(pin8 - last_read8)

        if ( pin_adjust1 > tolerance ):
               trim_pin_changed1 = True
        if ( pin_adjust2 > tolerance ):
               trim_pin_changed2 = True
        if ( pin_adjust3 > tolerance ):
               trim_pin_changed3 = True
        if ( pin_adjust4 > tolerance ):
               trim_pin_changed4 = True
        if ( pin_adjust5 > tolerance ):
               trim_pin_changed5 = True
        if ( pin_adjust8 > tolerance ):
               trim_pin_changed8 = True

	scale = 8192.

        if (trim_pin_changed1):
               val1 = (pin1 / scale)
               cs.SetChannel("P1", val1)

        if (trim_pin_changed2):
               val2 = (pin2 / scale)
               cs.SetChannel("P2", val2)

        if (trim_pin_changed3):
               val3 = (pin3 / scale)
               cs.SetChannel("P3", 1-val3)

        if (trim_pin_changed4):
               val4 = (pin4 / scale)
               cs.SetChannel("P4", val4)

        if (trim_pin_changed5):
               val5 = (pin5 / scale)
               cs.SetChannel("P5", 1-val5)

        if (trim_pin_changed8):
               val8 = (pin8 / scale)
               cs.SetChannel("P8", 1-val8)

        last_read1 = pin1
        last_read2 = pin2
        last_read3 = pin3
        last_read4 = pin4
        last_read5 = pin5
        last_read8 = pin8

#	print(pin1)
#	print(pin2)
#	print(pin3)
#	print(pin4)
#	print(pin5)
#	print(pin8)

#	led = 1024 - pin1
#        c.set_gpios({0: (led > 1000/3, 1),
#                     1: (led > 2000/3, 1),
#                     2: (led > 1000, 1),
#                     3: (i & 8, 1)})

	time.sleep(0.2)


if __name__ == "__main__":
    c = CosmoHat()
    try:
        main(c)
    except KeyboardInterrupt:
        c.stop()

