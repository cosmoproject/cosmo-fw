#include <stdint.h>
#include <avr/io.h>
#include <avr/sleep.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>

#include "ws2812.h"

static const uint32_t BAUD = 800000;
#define UBRR_SETTING (F_CPU/(2*BAUD) - 1)
static uint8_t txbuf[3*20];
static uint8_t bufsize;
static uint8_t count;
static volatile uint8_t tx_busy = 0;

const uint8_t PROGMEM gamma[] = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2,
    2, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5,
    5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10,
    10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
    17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
    25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
    37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
    51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
    69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
    90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
    115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
    144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
    177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
    215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255 };

static void start_timer8(uint8_t delay_8cycles) {
  TCCR0A = 0;
  TCNT0 = 0;
  TCCR0B = (2 << CS00); // div8 prescaler
  OCR0A = delay_8cycles;
  TIMSK0 = (1<<OCIE0A);
}
static void update_transmit() {
  if (count >= bufsize) {
    // Transmission almost done, just wait 50us
    UCSR0B &= ~(1<<UDRIE0);

    UDR0 = 0;
    start_timer8(1000/8);
    return;
  }

  UCSR0B |= (1<<UDRIE0);
  UDR0 = txbuf[count];
  count += 1;
}

ISR(USART_UDRE_vect)
{
  update_transmit();
}
ISR(TIMER0_COMPA_vect)
{
    tx_busy = 0;
    TCCR0B = 0; // Stop timer
    TIMSK0 = 0; // Disable interrupts
}
static void start_transmit() {
  while(tx_busy) /*sleep*/;
  tx_busy = 1;
  count = 0;
  update_transmit();
}

void ws2812_init() {
  DDRB = (1<<PB0); // XCK pin
  UBRR0 = 0;
  UCSR0C = (1<<UMSEL01) | (1<<UMSEL00) | (1 << UCPHA0) | (0 << UCPOL0);
  UCSR0B = (1<<TXEN0);
  // Important: The baud rate must be set after the transmitter is enabled
  UBRR0 = UBRR_SETTING;
}
void ws2812_set(const struct color *settings, uint8_t n) {
  uint8_t i, j;
  for (i = 0, j = 0; i < n; i += 1, j += 3) {
    txbuf[j+0] = pgm_read_byte(&gamma[settings[i].g]);
    txbuf[j+1] = pgm_read_byte(&gamma[settings[i].r]);
    txbuf[j+2] = pgm_read_byte(&gamma[settings[i].b]);
  }
  bufsize = j;
}
