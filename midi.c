#include <avr/io.h>
#include <avr/interrupt.h>

void midi_init(void) {
  UBRR1 = (F_CPU)/(16ul*31250ul) - 1ul;
  
  UCSR1B = (1<<RXCIE1) | (1<<UDRIE1) | (1<<RXEN1) | (1<<TXEN1);
  UCSR1C = (3<<UCSZ10);
  
}
