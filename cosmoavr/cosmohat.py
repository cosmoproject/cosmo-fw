from __future__ import print_function, division
import cosmospi
from config import CosmoConfig
        
class CosmoHat(cosmospi.CosmoSpi):
    def __init__(self, config=None, switches=[], leds=[], knobs=[]):
        cosmospi.CosmoSpi.__init__(self)
        if config is None and not switches and not leds and not knobs:
            config = CosmoConfig()
        if config is not None:
            assert not switches and not leds and not knobs
            switches = config.switches
            leds = config.leds
            knobs = config.knobs
        assert len(switches) + len(leds) <= 8
        assert len(knobs) <= 8
        for sw in switches:
            assert 0 <= sw <= 7
            assert sw not in leds
        for led in leds:
            assert 0 <= led <= 7
        for knob, (zero, full) in knobs:
            assert 0 <= knob <=7
        self._switches = switches
        self._leds = leds
        self.nleds = len(leds)
        self._knobs = knobs
        self.start()
        settings = dict((sw, (0, 1)) for sw in switches)
        settings.update((led, (1, 0)) for led in leds)
        self._set_gpios(settings)

    def version(self):
        return ''.join(chr(x) for x in self.call(0))

    def switches(self):
        gpios = self._get_gpios()
        return [gpios[sw] for sw in self._switches]
    
    def set_led(self, n, setting):
        self.set_leds({n: setting})
    
    def set_leds(self, settings):
        self._set_gpios(dict((self._leds[n], (1, setting))
                             for n, setting in settings.items()))

    def knobs(self, raw=False):
        adcs = self._adcs(knob for knob, _ in self._knobs)
        ret = []
        for value, (knob, (zero, full)) in zip(adcs, self._knobs):
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
            mask |= 1<<adc
        ret = []
        data = self.call(1,[mask])
        assert len(data) == len(adcs)*2
        
        for i, j in enumerate(adcs):
            ret.append((data[2*i+1]<<8)|data[2*i])
        return ret

    def _get_gpios(self):
        data, = self.call(2)
        return [(data & (1<<i)) != 0 for i in xrange(8)]
    
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
        to_write = [3, mask, direction_mask, setting_mask]
        self.write(to_write)
