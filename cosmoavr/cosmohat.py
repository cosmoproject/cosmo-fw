from __future__ import print_function
import cosmospi
        
class CosmoHat(cosmospi.CosmoSpi):
    def version(self):
        return ''.join(chr(x) for x in self.call(0))

    def adcs(self, adcs=[0,1,2,3,4,5,6,7]):
        mask = 0
        for adc in adcs:
            assert adc < 8
            mask |= 1<<adc
        ret = []
        data = self.call(1,[mask])
        assert len(data) == len(adcs)*2
        
        for i, j in enumerate(adcs):
            ret.append((data[2*i+1]<<8)|data[2*i])
        return ret

    def get_gpios(self):
        data, = self.call(2)
        return [(data & (1<<i)) != 0 for i in xrange(4)]
    
    def set_gpios(self, settings):
        mask = 0
        direction_mask = 0
        setting_mask = 0
        for num, (direction, setting) in settings.items():
            assert 3 >= num >= 0
            this_mask = 1<<num
            mask |= this_mask;
            if direction:
                direction_mask |= this_mask
            if setting:
                setting_mask |= this_mask
        self.write([3, mask, direction_mask, setting_mask])
