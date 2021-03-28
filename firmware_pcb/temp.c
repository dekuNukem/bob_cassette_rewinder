  // printf("-------\n");
  // printf("value: 0x%x\n", value);
  // printf("spi_buf[0]: 0x%x\n", spi_buf[0]);
  // printf("spi_buf[1]: 0x%x\n", spi_buf[1]);

    // printf("%d\n", HAL_GetTick());
    // HAL_GPIO_TogglePin(USER_LED_GPIO_Port, USER_LED_Pin);
    // spi_test(keypad);
    // HAL_Delay(500);

    // printf("%d\n", HAL_GetTick());
    // HAL_GPIO_TogglePin(USER_LED_GPIO_Port, USER_LED_Pin);
    // spi_test(0);
    // HAL_Delay(500);

/* USER CODE BEGIN 2 */
  HAL_Delay(500);
  printf("bobhack\n");

  while (1)
  {
    printf("Scanning I2C bus...\n");
    uint8_t scan_result = HAL_I2C_IsDeviceReady(&hi2c1, EEPROM_READ_ADDR, 1, 50);
    if(scan_result != 0)
      printf("EEPROM not found, retrying...\n");
    else
      break;
    HAL_Delay(500);
  }
  printf("Bob cassette found!\n");
  HAL_Delay(500);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */


  for (int i = 0; i < EEPROM_SIZE; i++)
  {
    uint8_t this_byte = eeprom_read(i);
    printf("bobdump %d %d\n", i, this_byte);
  }
  printf("done!\n");
  while (1)
  {
    HAL_GPIO_TogglePin(USER_LED_GPIO_Port, USER_LED_Pin);
    HAL_Delay(500);

  /* USER CODE END WHILE */

  /* USER CODE BEGIN 3 */

  }
  /* USER CODE END 3 */