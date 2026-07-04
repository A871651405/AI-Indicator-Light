/**
  ******************************************************************************
  * @file    storage.c
  * @brief   Flash存储模块实现
  *          使用STM32F030最后1页(0x08003C00-0x08003FFF)存储配置
  *          实际数据写在0x08003F00开始的256字节
  ******************************************************************************
  */
#include "storage.h"
#include <string.h>

/* 私有变量：内存中的配置缓存 */
static Storage_Data_t s_config;

/**
  * @brief  初始化存储模块
  */
void Storage_Init(void)
{
    /* 从Flash读取配置 */
    memcpy(&s_config, (const void *)STORAGE_FLASH_BASE, sizeof(Storage_Data_t));

    /* 检查魔数，判断Flash是否已初始化 */
    if (s_config.magic != STORAGE_MAGIC) {
        /* 未初始化，写入默认值 */
        s_config.magic = STORAGE_MAGIC;
        s_config.buzzer_volume = DEFAULT_BUZZER_VOLUME;
        s_config.buzzer_duration = DEFAULT_BUZZER_DURATION;
        memset(s_config.reserved, 0xFF, sizeof(s_config.reserved));

        /* 写入Flash */
        HAL_FLASH_Unlock();

        /* 擦除最后一页 (0x08003C00-0x08003FFF, 1KB) */
        FLASH_EraseInitTypeDef erase;
        uint32_t page_error = 0;

        erase.TypeErase = FLASH_TYPEERASE_PAGES;
        erase.PageAddress = STORAGE_FLASH_BASE & ~(STORAGE_PAGE_SIZE - 1); /* 0x08003C00 */
        erase.NbPages = 1;

        HAL_FLASHEx_Erase(&erase, &page_error);

        /* 写入数据 (按半字16位写入，STM32F0要求) */
        uint16_t *src = (uint16_t *)&s_config;
        uint32_t addr = STORAGE_FLASH_BASE;
        for (uint32_t i = 0; i < sizeof(Storage_Data_t) / 2; i++) {
            HAL_FLASH_Program(FLASH_TYPEPROGRAM_HALFWORD, addr, src[i]);
            addr += 2;
        }

        HAL_FLASH_Lock();
    }
}

/**
  * @brief  读取蜂鸣器音量
  */
uint8_t Storage_GetBuzzerVolume(void)
{
    return s_config.buzzer_volume;
}

/**
  * @brief  读取蜂鸣器时长
  */
uint8_t Storage_GetBuzzerDuration(void)
{
    return s_config.buzzer_duration;
}

/**
  * @brief  保存蜂鸣器设置到Flash
  */
int Storage_SaveBuzzerSettings(uint8_t volume, uint8_t duration)
{
    /* 限幅 */
    if (volume > 100) volume = 100;
    if (duration > 60) duration = 60;

    /* 更新内存缓存 */
    s_config.buzzer_volume = volume;
    s_config.buzzer_duration = duration;

    HAL_FLASH_Unlock();

    /* 擦除最后一页 */
    FLASH_EraseInitTypeDef erase;
    uint32_t page_error = 0;

    erase.TypeErase = FLASH_TYPEERASE_PAGES;
    erase.PageAddress = STORAGE_FLASH_BASE & ~(STORAGE_PAGE_SIZE - 1);
    erase.NbPages = 1;

    HAL_StatusTypeDef status = HAL_FLASHEx_Erase(&erase, &page_error);
    if (status != HAL_OK) {
        HAL_FLASH_Lock();
        return -1;
    }

    /* 写入数据 (按半字) */
    uint16_t *src = (uint16_t *)&s_config;
    uint32_t addr = STORAGE_FLASH_BASE;
    for (uint32_t i = 0; i < sizeof(Storage_Data_t) / 2; i++) {
        status = HAL_FLASH_Program(FLASH_TYPEPROGRAM_HALFWORD, addr, src[i]);
        if (status != HAL_OK) {
            HAL_FLASH_Lock();
            return -1;
        }
        addr += 2;
    }

    HAL_FLASH_Lock();
    return 0;
}
