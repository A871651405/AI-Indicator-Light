/**
  ******************************************************************************
  * @file    buzzer.h
  * @brief   蜂鸣器控制头文件 (硬件PWM, 1KHz, PB1/TIM3_CH4)
  ******************************************************************************
  */
#ifndef __BUZZER_H__
#define __BUZZER_H__

#ifdef __cplusplus
extern "C" {
#endif

#include "main.h"

/* API函数 -----------------------------------------------------------*/

/**
  * @brief  蜂鸣器初始化 (启动TIM3 PWM)
  */
void Buzzer_Init(void);

/**
  * @brief  设置蜂鸣器
  * @param  volume: 音量 0-100
  * @param  duration_s: 持续时间(秒) 0-60, 0表示停止
  */
void Buzzer_Set(uint8_t volume, uint8_t duration_s);

/**
  * @brief  蜂鸣器处理函数 (在主循环中调用, 负责定时关闭)
  */
void Buzzer_Process(void);

/**
  * @brief  立即停止蜂鸣器
  */
void Buzzer_Stop(void);

#ifdef __cplusplus
}
#endif
#endif /* __BUZZER_H__ */
