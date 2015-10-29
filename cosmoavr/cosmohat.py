from __future__ import print_function, division
import cosmospi
        
class CosmoHat(cosmospi.CosmoSpi):
    def __init__(self, switches=[], leds=[], nobs=[]):
        cosmospi.CosmoSpi.__init__(self)
        assert len(switches) + len(leds) <= 8
        assert len(nobs) <= 8
        for sw in switches:
            assert 0 <= sw <= 7
            assert sw not in leds
        for led in leds:
            assert 0 <= led <= 7
        for nob, (zero, full) in nobs:
            assert 0 <= nob <=7
        self._switches = switches
        self._leds = leds
        self._nobs = nobs
        self.start()
        settings = dict((sw, (0, 1)) for sw in switches)
        settings.update((led, (1, 0)) for led in leds)

    def version(self):
        return ''.join(chr(x) for x in self.call(0))

    def ws2812(self, leds):
        cmd = [4]
        for r, g, b in leds:
            cmd.extend((r, g, b))
        self.write(cmd)

    def switches(self):
        gpios = self._get_gpios()
        return [gpios[sw] for sw in self._switches]
    
    def set_led(self, n, setting):
        self.set_leds({n: setting})
    
    def set_leds(self, settings):
        self._set_gpios(dict((self._leds[n], (1, setting))
                             for n, setting in settings.items()))

    def nobs(self):
        adcs = self._adcs(nob for nob, _ in self._nobs)
        ret = []
        for value, (nob, (zero, full)) in zip(adcs, self._nobs):
            if zero > full:
                ret.append((value-zero)/(full-zero))
            else:
                ret.append((value-full)/(zero-full))
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
