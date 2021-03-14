#ifndef __HELPERS_H
#define __HELPERS_H

#ifdef __cplusplus
 extern "C" {
#endif 

#include "stm32f0xx_hal.h"

#define EEPROM_SIZE 256
#define EEPROM_READ_ADDR 0xA1
#define EEPROM_WRITE_ADDR 0xA0

uint8_t eeprom_read(uint16_t address);
void eeprom_write(uint16_t address, uint8_t data);
void eeprom_erase(void);

#ifdef __cplusplus
}
#endif

#endif


