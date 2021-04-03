#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "helpers.h"
#include "shared.h"
#include "my_usb.h"

volatile uint8_t is_busy;
volatile uint8_t i2c_scan_result;

uint8_t fw_version_major;
uint8_t fw_version_minor;
uint8_t fw_version_patch;

char *addr_start;
char *value_start;
uint8_t addr_to_write, value_to_write;

uint8_t eeprom_read(uint16_t address)
{
  uint8_t lower = address & 0xff;
  uint8_t ret = 69;
  HAL_I2C_Master_Transmit(&hi2c1, EEPROM_WRITE_ADDR, &lower, 1, 500);
  HAL_I2C_Master_Receive(&hi2c1, EEPROM_READ_ADDR, &ret, 1, 1000);
  return ret;
}

void eeprom_write(uint16_t address, uint8_t data)
{
  if(eeprom_read(address) == data)
    return;
  uint8_t lower = address & 0xff;
  uint8_t command_buf[2] = {lower, data};
  HAL_I2C_Master_Transmit(&hi2c1, EEPROM_WRITE_ADDR, command_buf, 2, 500);
  while(HAL_I2C_IsDeviceReady(&hi2c1, EEPROM_WRITE_ADDR, 1, 500) != HAL_OK)
    ;
}

char* goto_next_arg(char* buf)
{
  char* curr = buf;
  if(curr == NULL)
    return NULL;
  char* buf_end = curr + strlen(curr);
  if(curr >= buf_end)
    return NULL;
  while(curr < buf_end && *curr != ' ')
      curr++;
  while(curr < buf_end && *curr == ' ')
      curr++;
  if(curr >= buf_end)
    return NULL;
  return curr;
}

void parse_cmd(char* cmd)
{
  if(cmd == NULL)
    return;
  // printf("received: %s\n", cmd);
  if(strcmp(cmd, "dump") == 0)
  {
    printf("FW V%d.%d.%d\n", fw_version_major, fw_version_minor, fw_version_patch);
    if(i2c_scan_result != 0)
    {
      printf("no bob cassette detected!\n");
      return;
    }
    is_busy = 1;
    for (int i = 0; i < EEPROM_SIZE; i++)
      printf("dump %d %d\n", i, eeprom_read(i));
    is_busy = 0;
    printf("dump done!\n");
  }
  else if(strncmp(cmd, "write ", 6) == 0)
  {
    if(i2c_scan_result != 0)
    {
      printf("no bob cassette detected!\n");
      return;
    }
    addr_start = goto_next_arg(cmd);
    value_start = goto_next_arg(addr_start);
    if(addr_start == NULL || value_start == NULL)
    {
      printf("invalid args\n");
      return;
    }
    addr_to_write = atoi(addr_start);
    value_to_write = atoi(value_start);
    is_busy = 1;
    eeprom_write(addr_to_write, value_to_write);
    is_busy = 0;
    printf("done %d %d\n", addr_to_write, value_to_write);
  }
}

uint8_t linear_buf_init(linear_buf *lb, int32_t size)
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

uint8_t linear_buf_add(linear_buf *lb, uint8_t c)
{
  lb->buf[lb->curr_index] = c;
  if(lb->curr_index < lb->buf_size)
    lb->curr_index++;
  lb->buf[lb->buf_size-1] = 0;
  lb->last_recv = HAL_GetTick();
  return 0;
}

uint8_t linear_buf_add_str(linear_buf *lb, uint8_t *s, uint32_t len)
{
  for(uint32_t i = 0; i < len; i++)
    linear_buf_add(lb, s[i]);
  return 0;
}
