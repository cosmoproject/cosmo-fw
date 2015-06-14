#pragma once
#include <inttypes.h>

void spi_init(void);
uint8_t spi_receive(uint8_t const ** buffer);
void spi_send(const uint8_t *data, uint8_t length);
