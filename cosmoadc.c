#include <avr/io.h>
#include <avr/interrupt.h>
#include <inttypes.h>
#include <string.h>

#include "spicom.h"
#include "adc.h"

enum commands {
  CMD_VERSION = 0,
  CMD_READ_ADC = 1,
  CMD_READ_GPIO = 2,
  CMD_SET_GPIO = 3,
};


static void read_adc(const uint8_t *data, uint8_t count) {
  if (count < 1)
    return;
  uint8_t channel_mask = data[0];
  uint8_t i;
  uint8_t j = 0;
  uint8_t reply_buffer[16+1];
  reply_buffer[0] = CMD_READ_ADC;
  uint16_t *readings = (uint16_t *)&reply_buffer[1];
  for (i = 0; i < 8; i++) {
    if (channel_mask & 1) {
      readings[j] = adc_read(i);
      j += 1;
    }
    channel_mask >>= 1;
  }
  spi_send(reply_buffer, 2*j+1);
}
/* GPIOS:
      avr  rpi
   1: PD4  GPIO5
   2: PD5  GPIO6
   3: PD6  GPIO13
   4: PD7  GPIO19
   5: PC2  GPIO26
   6: PC3  GPIO12
   7: PC4  GPIO16
   8: PC5  GPIO20
 */

static void read_gpio(const uint8_t *data, uint8_t count) {
  (void)data;
  (void)count;
  // 76543210 CCCCDDDD
  uint8_t reply_buffer[] = {CMD_READ_GPIO, (PIND>>4) | ((PINC & 0x3c)<<2)};
  spi_send(reply_buffer, sizeof(reply_buffer));
}

static void set_gpio(const uint8_t *data, uint8_t count) {
  if (count < 3)
    return;
  uint8_t mask = data[0]<<4;
  uint8_t dir = data[1]<<4;
  uint8_t set = data[2]<<4;
  
  uint8_t dmask = (mask << 4) & 0xf0;
  DDRD = (DDRD & ~dmask) | (dir << 4);
  PORTD = (PORTD & ~dmask) | (set << 4);

  uint8_t cmask = ((mask>>2) & 0x3c);
  DDRC = (DDRC & ~cmask) | ((dir>>2) & 0x3c);
  PORTD = (PORTD & ~cmask) | ((set>>2) & 0x3c);
}

int main() {
  adc_init();
  spi_init();
  //midi_init();
  sei();
  while(1) {
    const uint8_t *rxbuf;
    uint8_t count = spi_receive(&rxbuf);
    if (count == 0)
      continue;
    enum commands command = rxbuf[0];
    rxbuf = &rxbuf[1];
    count -= 1;
    switch(command) {
    case CMD_VERSION: {
      const uint8_t data[] = {CMD_VERSION, 'C', 'o', 's', 'm', 'o', ' ', '0', '.', '2'};
      spi_send(data, sizeof(data));
      break;
    }
    case CMD_READ_ADC:
      read_adc(rxbuf, count);
      break;
    case CMD_READ_GPIO:
      read_gpio(rxbuf, count);
      break;
    case CMD_SET_GPIO:
      set_gpio(rxbuf, count);
      break;
    }
  }
}
