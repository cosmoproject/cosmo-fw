from __future__ import print_function, division
import cosmospi
import smbus
import RPi.GPIO as GPIO
from config import CosmoConfig
GPIO.setmode(GPIO.BCM)

CLK     = 16 # Clock
DIN     = 12 # Digital in
DOUT    = 26  # Digital out
CS      = 6  # Chip-Select

class CosmoException(Exception):
    pass

class CosmoPlank(object):
    def __init__(self, config=None):
        if config is None:
            config = CosmoConfig()
        self.config = config
        if len(config.switches) > 8:
            raise CosmoException("Max 8 switches, not {}.".format(switches))
        if len(config.knobs) > 8:
            raise CosmoException("Max 8 knobs, not {}".format(switches))
        for knob, (zero, full) in config.knobs:
            assert 0 <= knob <=7
        for led in config.leds:
            assert 0 <= led <= 7

        self.nleds = len(config.leds)
        self.i2c = smbus.SMBus(1)
        self.i2c.write_byte_data(0x20, 0x0e, 0x0f)
        self.i2c.write_byte_data(0x20, 0x0f, 0x0c)
        self.i2c.write_byte_data(0x20, 7, 0)
        GPIO.setup(CLK,  GPIO.OUT)
        GPIO.setup(DIN,  GPIO.OUT)
        GPIO.setup(DOUT, GPIO.IN)
        GPIO.setup(CS,   GPIO.OUT)

    def stop(self):
        pass
    def version(self):
        return 'CosmoPlank 1.0'

    def switches(self):
        gpios = self._get_gpios()
        return [gpios[sw] for sw in self.config.switches]
    
    def set_led(self, n, setting):
        self.set_leds({n: setting})
    
    def set_leds(self, settings):
        self._set_gpios(dict((self.config.leds[n], (1, setting))
                             for n, setting in settings.items()))

    def knobs(self, raw=False):
        adcs = self._adcs(knob for knob, _ in self.config.knobs)
        ret = []
        for value, (knob, (zero, full)) in zip(adcs, self.config.knobs):
            if not raw:
                if zero > full:
                    value = (value-zero)/(full-zero)
                else:
                    value = (value-full)/(zero-full)
                value = max(0, value)
                value = min(1, value)
            ret.append(value)
        return ret

    def _adcs(self, adcs=[0,1,2,3,4,5,6,7]):
        mask = 0
        adcs = list(adcs)
        for adc in adcs:
            assert adc < 8
        return [self._read_one_adc(n) for n in adcs]

    def _read_one_adc(self, num):
        o = GPIO.output
        o(CS,  1)    
        o(CS,  0)
        o(CLK, 0)  
        cmd = num
        cmd |= 0b11000
        for i in range(5, -1, -1):
            o(DIN, (cmd & (1<<i)) != 0)
            o(CLK, 1)
            o(CLK, 0)

        adchvalue = 0 
        inp = GPIO.input
        for i in range(11):
            o(CLK, 1)
            o(CLK, 0)
            adchvalue <<= 1 # 1 Postition nach links schieben
            adchvalue |= inp(DOUT)
        return adchvalue & 0x3ff

    def _get_gpios(self, return_raw=False):
        retry = 10
        error = None
        while retry:
            try:
                raw = self.i2c.read_byte_data(0x20, 0x0)
            except IOError as e:
                error = e
                time.sleep(0.001*2**(20-retry))
                retry -= 1
            else:
                break
        if not retry:
            raise error
        if return_raw:
            return raw
        return [(raw & (1<<i)) == 0 for i in range(8)]
    
    def _set_gpios(self, settings):
        mask = 0
        direction_mask = 0
        setting_mask = 0
        for num, (direction, setting) in settings.items():
            assert 7 >= num >= 0
            this_mask = 1<<num
            mask |= this_mask;
            if direction:
                direction_mask |= this_mask
            if setting:
                setting_mask |= this_mask
                retry = 10
        error = None
        retry = 10
        while retry:
            try:
                self.i2c.write_byte_data(0x20, 3, setting_mask)
            except IOError as e:
                error = e
                time.sleep(0.001*2**(20-retry))
                retry -= 1
            else:
                break
        if not retry:
            raise error
