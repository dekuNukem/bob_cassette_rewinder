#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "helpers.h"
#include "shared.h"

uint8_t linear_buf_init(linear_buf *lb, uint16_t size)
{
  lb->buf_size = size;
  lb->buf = malloc(size);
  lb->last_recv = 0;
  linear_buf_reset(lb);
  return 0;
}

void linear_buf_reset(linear_buf *lb)
{
  lb->curr_index = 0;
  memset(lb->buf, 0, lb->buf_size);
}

void linear_buf_add(linear_buf *lb, uint8_t c)
{
  if(c == '\r')
    return;
  lb->buf[lb->curr_index] = c;
  if(lb->curr_index < lb->buf_size)
    lb->curr_index++;
  lb->buf[lb->buf_size-1] = 0;
  lb->last_recv = HAL_GetTick();
}

uint8_t linear_buf_line_available(linear_buf *lb)
{
  if(lb->curr_index >= lb->buf_size)
  {
    linear_buf_reset(lb);
    return 0;
  }
  if(lb->buf[lb->curr_index - 1] == '\n')
    return 1;
  return 0;
}
