# Setup of COSMO

1. Download and flash raspbian to SD card
2. Boot raspbian, ssh into it.
3. Install ssh key, and change password
4. Run `sudo raspi-setup`. Expand SD-card image. Change hostname. Advanced -> Enable SPI (yes, yes)
5. Update and upgrade `sudo apt-get update && sudo apt-get dist-upgrade`
6. Install spidev for python 
   * `sudo apt-get install python-dev`
   * `git clone https://github.com/doceme/py-spidev.git`
   * `cd py-spidev; sudo python setup.py install`
7. Install gcc-avr `sudo apt-get install gcc-avr avr-libc`
8. Install spi-supporting version of avrdude
   * `sudo apt-get install libelf-dev flex bison autoconf`
   * `git clone https://github.com/kcuzner/avrdude.git`
   * `cd avrdude/avrdude; ./bootstrap && ./configure && make && sudo make install`
   * `sudo chmod u+s /usr/local/bin/avrdude`
   * Test connection to the COSMO-hat card `avrdude -c linuxspi -p m1284p -P /dev/spidev0.0`
9. Check out cosmo-adc project
   * `git clone https://github.com/kristofferkoch/cosmo-avr.git`
   * `make fuse`
   * `make program`
   * `python test.py`

