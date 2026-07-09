/**
  ******************************************************************************
  * @file    protocol.h
  * @brief   AI指示灯通信协议头文件
  *          帧格式: [起始位 0xAA][命令字][数据长度][数据][校验和]
  ******************************************************************************
  */
#ifndef __PROTOCOL_H__
#define __PROTOCOL_H__

#ifdef __cplusplus
extern "C" {
#endif

#include "main.h"

/* 协议常量 ----------------------------------------------------------*/
#define PROTOCOL_START_BYTE      0xAA
#define PROTOCOL_MAX_DATA_LEN    32
#define PROTOCOL_FRAME_TIMEOUT   50   /* 帧超时(ms) */

/* 命令字定义 --------------------------------------------------------*/
#define CMD_GREEN         0x01   /* 绿灯 (AI空闲) */
#define CMD_YELLOW        0x02   /* 黄灯 (AI思考) */
#define CMD_RED           0x03   /* 红灯 (故障/异常) */
#define CMD_OFF           0x04   /* 关闭灯光 */
#define CMD_BUZZER        0x05   /* 蜂鸣器设置 [音量][时长][启用标志] */
#define CMD_READ_PARAMS   0x06   /* 读取下位机参数（音量、时长、启用标志） */

/* 响应码 ------------------------------------------------------------*/
#define RESP_OK      0x00
#define RESP_ERROR   0xFF

/* 解析状态机 --------------------------------------------------------*/
typedef enum {
    STATE_WAIT_START = 0,  /* 等待起始位 */
    STATE_READ_CMD,        /* 读取命令字 */
    STATE_READ_LEN,        /* 读取数据长度 */
    STATE_READ_DATA,       /* 读取数据 */
    STATE_READ_CHECKSUM    /* 读取校验和 */
} ProtocolState_t;

/* 协议解析器结构体 --------------------------------------------------*/
typedef struct {
    ProtocolState_t state;          /* 当前状态 */
    uint8_t cmd;                    /* 命令字 */
    uint8_t data_len;               /* 数据长度 */
    uint8_t data[PROTOCOL_MAX_DATA_LEN]; /* 数据缓冲区 */
    uint8_t data_index;             /* 数据索引 */
    uint8_t checksum;               /* 接收到的校验和 */
    uint32_t last_tick;             /* 上次接收时间 */
} ProtocolParser_t;

/* API函数 -----------------------------------------------------------*/
void Protocol_Init(void);
void Protocol_OnByteReceived(uint8_t byte);
void Protocol_Process(void);
uint8_t Protocol_CalcChecksum(const uint8_t *data, uint8_t len);
void Protocol_SendResponse(uint8_t resp_code);
void Protocol_SendDataFrame(uint8_t cmd, const uint8_t *data, uint8_t data_len);

#ifdef __cplusplus
}
#endif
#endif /* __PROTOCOL_H__ */
