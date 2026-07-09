/**
  ******************************************************************************
  * @file    buzzer.c
  * @brief   蜂鸣器控制实现
  *          使用 TIM3_CH4 (PB1) 硬件PWM输出, 频率1KHz
  *
  *   逻辑说明:
  *   - 所有蜂鸣器触发均从 Flash 读取音量，并检查启用标志
  *   - 关闭蜂鸣器时，任何情况（包括上电自检）都不会响
  *   - Buzzer_BeepShort() → 使用 Flash 音量 + 固定 0.5s
  *   - Buzzer_TriggerWithSavedSettings() → 使用 Flash 音量/时长
  *
  *   音量和时长由 storage 模块掉电保存
  ******************************************************************************
  */
#include "buzzer.h"
#include "tim.h"
#include "storage.h"

/* PWM周期值: 1000 (对应0-999的占空比范围) */
#define BUZZER_PWM_PERIOD  1000

/* 私有变量 ----------------------------------------------------------*/
static uint8_t  buzzer_active = 0;       /* 蜂鸣器是否活跃 */
static uint32_t buzzer_end_tick = 0;     /* 停止时间点(ms) */

/**
  * @brief  蜂鸣器初始化, 启动TIM3 CH4 PWM输出 (初始占空比为0)
  */
void Buzzer_Init(void)
{
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_4, 0);
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_4);

    buzzer_active = 0;
    buzzer_end_tick = 0;
}

/**
  * @brief  检查蜂鸣器是否启用
  * @retval 1=启用, 0=关闭
  */
uint8_t Buzzer_IsEnabled(void)
{
    return Storage_GetBuzzerEnabled();
}

/**
  * @brief  内部: 启动蜂鸣器 (指定音量和时长ms)
  * @param  volume: 音量 0-100
  * @param  duration_ms: 持续时间(毫秒)
  */
static void Buzzer_Start(uint8_t volume, uint32_t duration_ms)
{
    if (volume > 100) volume = 100;
    if (volume == 0 || duration_ms == 0) {
        Buzzer_Stop();
        return;
    }

    /* 音量0-100 → PWM占空比 0-999 */
    uint32_t pulse = (uint32_t)volume * (BUZZER_PWM_PERIOD - 1) / 100;
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_4, pulse);

    buzzer_end_tick = HAL_GetTick() + duration_ms;
    buzzer_active = 1;
}

/**
  * @brief  蜂鸣器短响0.5秒 (使用Flash保存的音量)
  *         用于上电自检和绿灯指令触发
  *         如果蜂鸣器已关闭(Flash中buzzer_enabled=0)，则不响
  */
void Buzzer_BeepShort(void)
{
    if (!Storage_GetBuzzerEnabled()) {
        return;   /* 蜂鸣器已关闭，不响 */
    }
    uint8_t volume = Storage_GetBuzzerVolume();
    Buzzer_Start(volume, 500);   /* 使用Flash音量, 固定时长500ms */
}

/**
  * @brief  设置蜂鸣器 (使用Flash保存的音量/时长配置)
  *         用于红灯指令触发
  *         如果蜂鸣器已关闭(Flash中buzzer_enabled=0)，则不响
  */
void Buzzer_TriggerWithSavedSettings(void)
{
    if (!Storage_GetBuzzerEnabled()) {
        return;   /* 蜂鸣器已关闭，不响 */
    }
    uint8_t volume = Storage_GetBuzzerVolume();
    uint8_t duration_s = Storage_GetBuzzerDuration();
    Buzzer_Start(volume, (uint32_t)duration_s * 1000);
}

/**
  * @brief  蜂鸣器处理函数 (在主循环中调用, 负责定时关闭)
  */
void Buzzer_Process(void)
{
    if (buzzer_active && HAL_GetTick() >= buzzer_end_tick) {
        Buzzer_Stop();
    }
}

/**
  * @brief  立即停止蜂鸣器
  */
void Buzzer_Stop(void)
{
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_4, 0);
    buzzer_active = 0;
}
