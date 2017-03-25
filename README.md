# Firmware for COSMO-HAT and COSMO plank

### How to configure the COSMO plank 

1. Log in to the Raspberry Pi
2. Type **```cp cosmo-fw/cosmo.config.plank.sample .cosmo```**
3. Type **```nano .cosmo```***
4. You can now list which inputs are used for switches and which outputs are used for LEDs and change the order
5. Each analogue input will have two values, min and max, which can be used to calibrate each input (values have to be in the range from 0 to 1023) and invert the signal (setting max value as min and vica verca) 

### How to configure the COSMO HAT 

1. Log in to the Raspberry Pi
2. Type **```cp cosmo-fw/cosmo.config.hat.sample .cosmo```**
3. Type **```nano .cosmo```***
4. You can now list which inputs are used for switches and which outputs are used for LEDs and change the order
5. Each analogue input will have two values, min and max, which can be used to calibrate each input (values have to be in the range from 0 to 8192) and invert the signal (setting max value as min and vica verca) 

### How to test the COSMO plank

1. Log in to the Raspberry Pi
2. Kill any running instances of python/csound by typing **```killall python```** 3 times
3. Type **```cd cosmo-fw```**
4. Type **```python check_plank.py```**
5. All leds will blink in a binary counting pattern and you will see the values for all pots and switches when you twist and push them
6. Note down all maximum and minimum values for the analoge inputs

### How to test the COSMO HAT

1. Log in to the Raspberry Pi
2. Kill any running instances of python/csound by typing **```killall python```** 3 times
3. Type **```cd cosmo-fw```**
4. Type **```python check_hat.py```**
5. All leds will blink in a single running light 
6. Note down all maximum and minimum values for the analoge inputs

