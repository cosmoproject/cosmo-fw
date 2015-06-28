#include <avr/io.h>
#include <avr/interrupt.h>

#include "adc.h"

static const uint8_t N_OVERSAMPLES = 8;

static uint16_t results[8];
static uint8_t dirty = 0;
ISR(ADC_vect) {
  static uint8_t adc = 0;
  static uint8_t count[8] = {};
  static uint16_t tmp[8] = {};
  uint8_t last = (adc - 1) & 7;
  tmp[last] += ADC;
  adc = (adc + 1) & 7;
  ADMUX = (1<<REFS0) | adc; // Current transaction have already started.
  count[last] += 1;
  if (count[last] >= N_OVERSAMPLES) {
    results[last] = tmp[last];
    dirty |= (1<<last);
  }
}

void adc_init(void) {
  DIDR0 = 0xff;
  ADMUX = (1<<REFS0) | 7;
  ADCSRA = (1<<ADEN) | (1<<ADSC) | (1<<ADATE) | (1<<ADIE) | (7<<ADPS0);
}

uint16_t adc_read(uint8_t mux) {
  mux &= 7;
  uint8_t mask = 1<<mux;
  while((dirty & mask) == 0);
  uint16_t ret = results[mux];
  cli();
  dirty &= ~mask;
  sei();
  return ret;
}
