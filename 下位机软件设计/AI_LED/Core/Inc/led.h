/**
  ******************************************************************************
  * @file    led.h
  * @brief   LED控制头文件
  ******************************************************************************
  */
#ifndef __LED_H__
#define __LED_H__

#ifdef __cplusplus
extern "C" {
#endif

#include "main.h"

/* API函数 -----------------------------------------------------------*/
void LED_SetGreen(void);
void LED_SetYellow(void);
void LED_SetRed(void);
void LED_AllOff(void);

#ifdef __cplusplus
}
#endif
#endif /* __LED_H__ */
