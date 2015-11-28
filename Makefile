PROJECT := cosmoadc
MCU_TARGET := atmega1284p
AVRDUDE := avrdude -c linuxspi -p m1284p -P /dev/spidev0.0
CC := avr-gcc
OBJDUMP := avr-objdump
CFLAGS := -g3 -Os -Wall -MMD -std=gnu99 -mmcu=$(MCU_TARGET) -fshort-enums -Wno-pointer-sign -Wextra -DF_CPU=16000000ul
LDFLAGS := $(CFLAGS)

OBJECTS := $(patsubst %.c,%.o,$(wildcard *.c))

.PHONY: all clean program fuse
all: $(PROJECT).elf $(PROJECT).lst
	avr-size $(PROJECT).elf

clean:
	rm -f *.elf $(OBJECTS) *.map *~ *.lst *.d

fuse:
	$(AVRDUDE) -U lfuse:w:0xd7:m -U hfuse:w:0xd1:m -U efuse:w:0xfd:m
	./reset_gpio.sh

program: $(PROJECT).elf
	$(AVRDUDE) -U flash:w:$(PROJECT).elf:e
	./reset_gpio.sh

$(PROJECT).elf: $(OBJECTS)
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@
$(PROJECT).lst: $(PROJECT).elf
	$(OBJDUMP) -h -S $< > $@

-include $(OBJECTS:%.o=%.d)
