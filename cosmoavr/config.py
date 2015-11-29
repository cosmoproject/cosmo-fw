import os
import os.path
import ConfigParser

class CosmoConfig(object):
    def __init__(self, conffile=None):
        if conffile is None:
            conffile = os.path.join(os.environ['HOME'], ".cosmo")
        self.conffile = conffile
        self.config = ConfigParser.SafeConfigParser()
        self.dirty = False
        self.read()
        
    def read(self):
        self.config.read(self.conffile)
        if not self.config.has_section("hardware"):
            self.config.add_section("hardware")
            self.dirty = True
        try:
            switches = self.config.get("hardware", "switches")
            if switches.strip() == "":
                self.switches = []
            else:
                self.switches = [int(x.strip()) for x in switches.split(",")]
        except ConfigParser.NoOptionError:
            self.config.set("hardware", "switches", "")
            self.switches = []
            self.dirty = True
        try:
            leds = self.config.get("hardware", "leds")
            if leds.strip() == "":
                self.leds = []
            else:
                self.leds = [int(x.strip()) for x in leds.split(",")]
        except ConfigParser.NoOptionError:
            self.config.set("hardware", "leds", "")
            self.leds = []
            self.dirty = True
        self.write()
        self.knobs = []
        for i in range(8):
            section = "knob"+str(i)
            try:
                pin = self.config.getint(section, "pin")
                zero = self.config.getint(section, "zero")
                full = self.config.getint(section, "full")
                self.knobs.append((pin, (zero, full)))
            except ConfigParser.NoSectionError:
                pass

    def write(self):
        if not self.dirty:
            return
        self.config.write(open(self.conffile, 'w'))
        self.dirty = False
        
