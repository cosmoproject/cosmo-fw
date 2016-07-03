#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdbool.h>
#include <string.h>

#include "spicom.h"

#define ESCAPE 16
#define START   2
#define END     3

static uint8_t rx_buffer[2][16];
static uint8_t rx_buffer_count[2];
static uint8_t rx_buffer_ptr = 0;
static volatile int8_t rx_buffer_done = -1;

static const uint8_t *tx_buffer;
static uint8_t tx_buffer_count;
static volatile uint8_t transmitting = 1;

static bool needs_escape(uint8_t data) {
  switch(data) {
  case ESCAPE:
  case START:
  case END:
    return true;
  default:
    return false;
  }
}


static uint8_t next_txdata(void) {
  static enum {TX_IDLE, TX_DATA, TX_ESCAPE, TX_END} tx_state = TX_IDLE;
  static uint8_t tx_count = 0;
  uint8_t ret;
  switch (tx_state) {
  case TX_IDLE:
    if (transmitting) {
      ret = START;
      if (tx_buffer_count == 0)
	tx_state = TX_END;
      else
	tx_state = TX_DATA;
      tx_count = 0;
    }
    else {
      ret = 0;
    }
    break;
  case TX_DATA: {
    uint8_t data = tx_buffer[tx_count];
    if (needs_escape(data)) {
      ret = ESCAPE;
      tx_state = TX_ESCAPE;
    }
    else {
      ret = data;
      tx_count += 1;
      if (tx_count >= tx_buffer_count)
	tx_state = TX_END;
    }
    break;
  }
  case TX_ESCAPE:
    ret = tx_buffer[tx_count];
    tx_count += 1;
    if (tx_count >= tx_buffer_count)
      tx_state = TX_END;
    else
      tx_state = TX_DATA;
    break;
  case TX_END:
  default:
    ret = END;
    tx_state = TX_IDLE;
    transmitting = 0;
    break;
  }
  return ret;
}

static void rx_byte(uint8_t rx_data) {
  static enum {RX_IDLE, RX_IDLE_ESCAPE, RX_DATA, RX_ESCAPE} rx_state = RX_IDLE;

  if (rx_data == START && rx_state != RX_ESCAPE && rx_state != RX_IDLE_ESCAPE) {
    rx_state = RX_DATA;
    rx_buffer_count[rx_buffer_ptr] = 0;
    return;
  }
  switch (rx_state) {
  case RX_IDLE:
    // Ignore out-of-band data
    if (rx_data == ESCAPE)
      rx_state = RX_IDLE_ESCAPE;
    return;
  case RX_IDLE_ESCAPE:
    rx_state = RX_IDLE;
    return;
  case RX_DATA:
    if (rx_data == END) {
      // rx done
      rx_buffer_done = rx_buffer_ptr;
      rx_buffer_ptr = (rx_buffer_ptr + 1) & 1;
      rx_state = RX_IDLE;
      return;
    }
    if (rx_buffer_count[rx_buffer_ptr] >= sizeof(rx_buffer)) {
      // Overflow. Ignore package
      rx_state = RX_IDLE;
      return;
    }
    if (rx_data == ESCAPE) {
      rx_state = RX_ESCAPE;
      return;
    }
    
    rx_buffer[rx_buffer_ptr][rx_buffer_count[rx_buffer_ptr]] = rx_data;
    rx_buffer_count[rx_buffer_ptr] += 1;
    return;
  case RX_ESCAPE:
    rx_buffer[rx_buffer_ptr][rx_buffer_count[rx_buffer_ptr]] = rx_data;
    rx_buffer_count[rx_buffer_ptr] += 1;
    rx_state = RX_DATA;
    return;
  default: // Error
    rx_state = RX_IDLE;
    break;
  }
}

ISR(SPI_STC_vect) {
  static uint8_t txdata = 0;
  uint8_t rxdata = SPDR;
  SPDR = txdata;
  txdata = next_txdata();
  rx_byte(rxdata);
}

void spi_init(void) {
  DDRB |= (1<<PB6); // Enable MOSI output
  SPCR = (1<<SPIE) | (1<<SPE) | (0<<DORD) | (0<<MSTR) | (0<<CPOL) | (0<<CPHA);
}

uint8_t spi_receive(uint8_t const ** buffer) {
  while (rx_buffer_done < 0); // TODO: sleep
  *buffer = rx_buffer[rx_buffer_done];
  uint8_t ret = rx_buffer_count[rx_buffer_done];
  rx_buffer_done = -1;
  return ret;
}

void spi_send(const uint8_t *data, uint8_t length) {
  tx_buffer = data;
  tx_buffer_count = length;
  transmitting = 1;
  // TODO: set gpio
  while(transmitting); // TODO: sleep
}
