/**
  ******************************************************************************
  * @file    storage.h
  * @brief   Flash存储模块 - 掉电保存蜂鸣器设置
  *          STM32F030F4Px: 16KB Flash (0x08000000-0x08003FFF)
  *          使用最后256字节 (0x08003F00-0x08003FFF) 存储用户配置
  ******************************************************************************
  */
#ifndef __STORAGE_H__
#define __STORAGE_H__

#ifdef __cplusplus
extern "C" {
#endif

#include "main.h"

/* Flash存储地址 (16KB Flash的最后256字节) */
#define STORAGE_FLASH_BASE    0x08003F00U
#define STORAGE_FLASH_SIZE    256U
#define STORAGE_PAGE_SIZE     1024U   /* STM32F030每页1KB */

/* 存储数据标识魔数，用于判断是否已初始化 */
#define STORAGE_MAGIC         0xA5A5

/* 默认值 */
#define DEFAULT_BUZZER_VOLUME     50
#define DEFAULT_BUZZER_DURATION   5
#define DEFAULT_BUZZER_ENABLED    1    /* 默认启用蜂鸣器 */

/* 存储数据结构 (紧凑布局，方便整页读写) */
typedef struct {
    uint16_t magic;             /* 魔数 0xA5A5，表示已初始化 */
    uint8_t  buzzer_volume;     /* 蜂鸣器音量 0-100 */
    uint8_t  buzzer_duration;   /* 蜂鸣器响铃时长 0-60秒 */
    uint8_t  buzzer_enabled;    /* 蜂鸣器启用标志: 1=启用, 0=关闭 */
    uint8_t  reserved[251];     /* 保留字段，凑齐256字节，方便未来扩展 */
} Storage_Data_t;

/* API函数 -----------------------------------------------------------*/

/**
  * @brief  初始化存储模块，从Flash读取配置
  *         如果Flash未初始化，写入默认值
  */
void Storage_Init(void);

/**
  * @brief  读取蜂鸣器音量
  * @retval 音量 0-100
  */
uint8_t Storage_GetBuzzerVolume(void);

/**
  * @brief  读取蜂鸣器时长
  * @retval 时长(秒) 0-60
  */
uint8_t Storage_GetBuzzerDuration(void);

/**
  * @brief  读取蜂鸣器启用标志
  * @retval 1=启用, 0=关闭
  */
uint8_t Storage_GetBuzzerEnabled(void);

/**
  * @brief  保存蜂鸣器设置到Flash (掉电保存)
  * @param  volume: 音量 0-100
  * @param  duration: 时长(秒) 0-60
  * @param  enabled: 启用标志 1=启用, 0=关闭
  * @retval 0:成功, -1:失败
  */
int Storage_SaveBuzzerSettings(uint8_t volume, uint8_t duration, uint8_t enabled);

#ifdef __cplusplus
}
#endif
#endif /* __STORAGE_H__ */
