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
  * @brief  设置蜂鸣器 (使用Flash保存的音量/时长配置)
  *         用于红灯指令触发
  */
void Buzzer_TriggerWithSavedSettings(void);

/**
  * @brief  蜂鸣器短响0.5秒 (固定音量100, 固定时长0.5s)
  *         用于绿灯指令触发，不可修改
  */
void Buzzer_BeepShort(void);

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
