/**
  ******************************************************************************
  * @file    buzzer.c
  * @brief   蜂鸣器控制实现
  *          使用 TIM3_CH4 (PB1) 硬件PWM输出, 频率1KHz
  *          音量0-100 通过修改PWM占空比实现
  *          时长0-60s 通过软件定时关闭
  ******************************************************************************
  */
#include "buzzer.h"
#include "tim.h"

/* PWM周期值: 1000 (对应0-999的占空比范围) */
#define BUZZER_PWM_PERIOD  1000

/* 私有变量 ----------------------------------------------------------*/
static uint8_t  buzzer_active = 0;       /* 蜂鸣器是否活跃 */
static uint32_t buzzer_end_tick = 0;     /* 停止时间点 */

/**
  * @brief  蜂鸣器初始化, 启动TIM3 CH4 PWM输出 (初始占空比为0)
  */
void Buzzer_Init(void)
{
    /* 设置初始占空比为0 (静音) */
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_4, 0);

    /* 启动PWM输出 */
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_4);

    buzzer_active = 0;
    buzzer_end_tick = 0;
}

/**
  * @brief  设置蜂鸣器
  * @param  volume: 音量 0-100
  * @param  duration_s: 持续时间(秒) 0-60
  */
void Buzzer_Set(uint8_t volume, uint8_t duration_s)
{
    /* 限幅 */
    if (volume > 100) volume = 100;
    if (duration_s > 60) duration_s = 60;

    if (volume == 0 || duration_s == 0) {
        /* 音量为0或时长为0, 直接停止 */
        Buzzer_Stop();
        return;
    }

    /* 音量0-100 映射到PWM占空比 0-999 */
    uint32_t pulse = (uint32_t)volume * (BUZZER_PWM_PERIOD - 1) / 100;
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_4, pulse);

    /* 记录停止时间点 */
    buzzer_end_tick = HAL_GetTick() + (uint32_t)duration_s * 1000;
    buzzer_active = 1;
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
