#ifndef __HELPERS_H
#define __HELPERS_H

#ifdef __cplusplus
 extern "C" {
#endif 

#include "stm32f0xx_hal.h"

typedef struct
{
  uint32_t last_recv;
  uint16_t curr_index;
  uint16_t buf_size;
  uint8_t* buf;
} linear_buf;

uint8_t linear_buf_init(linear_buf *lb, uint16_t size);
void linear_buf_reset(linear_buf *lb);
void linear_buf_add(linear_buf *lb, uint8_t c);
uint8_t linear_buf_line_available(linear_buf *lb);

#ifdef __cplusplus
}
#endif

#endif


