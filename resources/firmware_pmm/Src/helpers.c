#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "helpers.h"
#include "shared.h"

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
  return;
  if(eeprom_read(address) == data)
    return;
  uint8_t upper_mask = (address >> 7) & 0x6;
  uint8_t lower = address & 0xff;
  uint8_t command_buf[2] = {lower, data};
  HAL_I2C_Master_Transmit(&hi2c1, EEPROM_WRITE_ADDR | upper_mask, command_buf, 2, 500);
  while(HAL_I2C_IsDeviceReady(&hi2c1, EEPROM_WRITE_ADDR, 1, 500) != HAL_OK)
    ;
}

void eeprom_erase(void)
{
  return;
  for (int i = 0; i < EEPROM_SIZE; ++i)
    eeprom_write(i, 0xff);
}
