#pragma once
struct color {
  uint8_t r,g,b;
};
void ws2812_init(void);
void ws2812_set(const struct color *settings, uint8_t n);
