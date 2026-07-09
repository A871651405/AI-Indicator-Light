/**
  ******************************************************************************
  * @file    buzzer.h
  * @brief   蜂鸣器控制头文件 (硬件PWM, 1KHz, PB1/TIM3_CH4)
  *
  *   所有蜂鸣器触发均从 Flash 读取音量，并检查启用标志
  *   关闭蜂鸣器时，任何情况（包括上电自检）都不会响
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
  * @brief  检查蜂鸣器是否启用 (从Flash读取)
  * @retval 1=启用, 0=关闭
  */
uint8_t Buzzer_IsEnabled(void);

/**
  * @brief  蜂鸣器短响0.5秒 (使用Flash音量)
  *         用于绿灯指令和上电自检
  *         如果Flash中buzzer_enabled=0，不响
  */
void Buzzer_BeepShort(void);

/**
  * @brief  触发蜂鸣器 (使用Flash保存的音量/时长配置)
  *         用于红灯指令
  *         如果Flash中buzzer_enabled=0，不响
  */
void Buzzer_TriggerWithSavedSettings(void);

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
