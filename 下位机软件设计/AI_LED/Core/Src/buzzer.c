/**
  ******************************************************************************
  * @file    buzzer.c
  * @brief   蜂鸣器控制实现
  *          使用 TIM3_CH4 (PB1) 硬件PWM输出, 频率1KHz
  *
  *   逻辑说明:
  *   - 绿灯指令 → Buzzer_BeepShort()   固定0.5s, 音量100, 不可改
  *   - 红灯指令 → Buzzer_TriggerWithSavedSettings()  使用Flash保存的音量/时长
  *   - 黄灯/关闭 → 不触发蜂鸣器
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
  * @brief  蜂鸣器短响0.5秒 (固定音量100, 固定时长0.5s)
  *         用于绿灯指令触发，不可修改
  */
void Buzzer_BeepShort(void)
{
    Buzzer_Start(100, 500);   /* 音量100%, 时长500ms */
}

/**
  * @brief  设置蜂鸣器 (使用Flash保存的音量/时长配置)
  *         用于红灯指令触发
  */
void Buzzer_TriggerWithSavedSettings(void)
{
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
