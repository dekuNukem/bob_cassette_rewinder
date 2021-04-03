#ifndef __HELPERS_H
#define __HELPERS_H

#ifdef __cplusplus
 extern "C" {
#endif 

#include "stm32f0xx_hal.h"

#define EEPROM_SIZE 256
#define EEPROM_READ_ADDR 0xA1
#define EEPROM_WRITE_ADDR 0xA0

extern volatile uint8_t is_busy;
extern volatile uint8_t i2c_scan_result;

extern uint8_t fw_version_major;
extern uint8_t fw_version_minor;
extern uint8_t fw_version_patch;

typedef struct
{
  int32_t last_recv;
  int32_t curr_index;
  int32_t buf_size;
  uint8_t* buf;
} linear_buf;

uint8_t linear_buf_init(linear_buf *lb, int32_t size);
void linear_buf_reset(linear_buf *lb);
uint8_t linear_buf_add(linear_buf *lb, uint8_t c);
uint8_t linear_buf_add_str(linear_buf *lb, uint8_t *s, uint32_t len);
void parse_cmd(char* cmd);

uint8_t eeprom_read(uint16_t address);
void eeprom_write(uint16_t address, uint8_t data);

#ifdef __cplusplus
}
#endif

#endif


