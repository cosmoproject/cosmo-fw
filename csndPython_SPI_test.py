from __future__ import print_function
from cosmoavr.cosmohat import CosmoHat
import time
import csnd6

csoundFile = "../csound/audio-spi-input-test.csd"


def main(c):
    last_read1 = 0
    last_read2 = 0
    last_read3 = 0
    last_read4 = 0
    last_read5 = 0
    last_read6 = 0

    # we'll assume that the pot didn't move
    trim_pin_changed1 = False
    trim_pin_changed2 = False
    trim_pin_changed3 = False
    trim_pin_changed4 = False
    trim_pin_changed5 = False
    trim_pin_changed6 = False

    tolerance = 5
 
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
        #print("ADC:", adcs)
        pin1 = adcs[1]
	pin2 = adcs[2]
	pin3 = adcs[3]
	pin4 = adcs[4]
	pin5 = adcs[5]
	pin6 = adcs[0]

       # how much has it changed since the last read?
        pin_adjust1 = abs(pin1 - last_read1)
        pin_adjust2 = abs(pin2 - last_read2)
        pin_adjust3 = abs(pin3 - last_read3)
        pin_adjust4 = abs(pin4 - last_read4)
        pin_adjust5 = abs(pin5 - last_read5)
        pin_adjust6 = abs(pin6 - last_read6)

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
        if ( pin_adjust6 > tolerance ):
               trim_pin_changed6 = True

        if (trim_pin_changed1):
               val1 = (pin1 / 1024.)
               cs.SetChannel("P1", val1)

        if (trim_pin_changed2):
               val2 = (pin2 / 1024.)
               cs.SetChannel("P2", val2)

        if (trim_pin_changed3):
               val3 = (pin3 / 1024.)
               cs.SetChannel("P3", 1-val3)

        if (trim_pin_changed4):
               val4 = (pin4 / 1024.)
               cs.SetChannel("P4", val4)

        if (trim_pin_changed5):
               val5 = (pin5 / 1024.)
               cs.SetChannel("P5", 1-val5)

        if (trim_pin_changed6):
               val6 = (pin6 / 1024.)
               cs.SetChannel("P6", 1-val6)

        last_read1 = pin1
        last_read2 = pin2
        last_read3 = pin3
        last_read4 = pin4
        last_read5 = pin5
        last_read6 = pin6

#	print(pin1)
#	print(pin2)
#	print(pin3)
#	print(pin4)
#	print(pin5)
#	print(pin6)
        #print("GPIO:", c.get_gpios())
	led = 1024 - pin1
        c.set_gpios({0: (led > 1000/3, 1),
                     1: (led > 2000/3, 1),
                     2: (led > 1000, 1),
                     3: (i & 8, 1)})
#        b = adcs[1]
#	cs.SetChannel("P1", a / 1024)
#	cs.SetChannel("P2", b / 1024)
	time.sleep(0.1)


if __name__ == "__main__":
    c = CosmoHat()
    try:
        main(c)
    except KeyboardInterrupt:
        c.stop()

