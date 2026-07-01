/**
  ******************************************************************************
  * @file    protocol.c
  * @brief   AI指示灯通信协议实现
  *          帧格式: [起始位 0xAA][命令字][数据长度][数据][校验和]
  *          校验和: 从起始位到数据结束所有字节的XOR
  ******************************************************************************
  */
#include "protocol.h"
#include "usart.h"
#include "led.h"
#include "buzzer.h"

/* 私有变量 ----------------------------------------------------------*/
static ProtocolParser_t parser;
static uint8_t frame_ready = 0;   /* 帧完成标志 */

/* 私有函数 ----------------------------------------------------------*/

/**
  * @brief  计算校验和 (XOR)
  * @param  data: 数据指针
  * @param  len: 数据长度
  * @retval 校验和
  */
uint8_t Protocol_CalcChecksum(const uint8_t *data, uint8_t len)
{
    uint8_t checksum = 0;
    for (uint8_t i = 0; i < len; i++) {
        checksum ^= data[i];
    }
    return checksum;
}

/**
  * @brief  协议初始化
  */
void Protocol_Init(void)
{
    parser.state = STATE_WAIT_START;
    parser.data_index = 0;
    parser.last_tick = HAL_GetTick();
    frame_ready = 0;
}

/**
  * @brief  串口接收中断中调用，逐字节喂入状态机
  * @param  byte: 接收到的字节
  */
void Protocol_OnByteReceived(uint8_t byte)
{
    uint32_t now = HAL_GetTick();

    /* 帧超时检测：超过50ms未完成则重置 */
    if ((now - parser.last_tick) > PROTOCOL_FRAME_TIMEOUT) {
        parser.state = STATE_WAIT_START;
        parser.data_index = 0;
    }
    parser.last_tick = now;

    switch (parser.state) {
        case STATE_WAIT_START:
            if (byte == PROTOCOL_START_BYTE) {
                parser.state = STATE_READ_CMD;
                parser.data_index = 0;
            }
            break;

        case STATE_READ_CMD:
            parser.cmd = byte;
            parser.state = STATE_READ_LEN;
            break;

        case STATE_READ_LEN:
            parser.data_len = byte;
            if (parser.data_len == 0) {
                parser.state = STATE_READ_CHECKSUM;
            } else if (parser.data_len <= PROTOCOL_MAX_DATA_LEN) {
                parser.state = STATE_READ_DATA;
                parser.data_index = 0;
            } else {
                /* 数据长度超限，重置 */
                parser.state = STATE_WAIT_START;
            }
            break;

        case STATE_READ_DATA:
            parser.data[parser.data_index++] = byte;
            if (parser.data_index >= parser.data_len) {
                parser.state = STATE_READ_CHECKSUM;
            }
            break;

        case STATE_READ_CHECKSUM:
            parser.checksum = byte;
            frame_ready = 1;
            parser.state = STATE_WAIT_START;
            break;

        default:
            parser.state = STATE_WAIT_START;
            break;
    }
}

/**
  * @brief  发送响应到上位机
  * @param  resp_code: 响应码 (RESP_OK / RESP_ERROR)
  */
void Protocol_SendResponse(uint8_t resp_code)
{
    HAL_UART_Transmit(&huart1, &resp_code, 1, HAL_MAX_DELAY);
}

/**
  * @brief  处理一帧完整的命令 (在主循环中调用)
  */
void Protocol_Process(void)
{
    if (!frame_ready) {
        return;
    }
    frame_ready = 0;

    /* 构建校验数据：起始位 + 命令字 + 数据长度 + 数据 */
    uint8_t check_buf[3 + PROTOCOL_MAX_DATA_LEN];
    check_buf[0] = PROTOCOL_START_BYTE;
    check_buf[1] = parser.cmd;
    check_buf[2] = parser.data_len;
    for (uint8_t i = 0; i < parser.data_len; i++) {
        check_buf[3 + i] = parser.data[i];
    }

    /* 计算并验证校验和 */
    uint8_t calc_checksum = Protocol_CalcChecksum(check_buf, 3 + parser.data_len);
    if (calc_checksum != parser.checksum) {
        Protocol_SendResponse(RESP_ERROR);
        return;
    }

    /* 执行命令 */
    switch (parser.cmd) {
        case CMD_GREEN:
            LED_SetGreen();
            Protocol_SendResponse(RESP_OK);
            break;

        case CMD_YELLOW:
            LED_SetYellow();
            Protocol_SendResponse(RESP_OK);
            break;

        case CMD_RED:
            LED_SetRed();
            Protocol_SendResponse(RESP_OK);
            break;

        case CMD_OFF:
            LED_AllOff();
            Protocol_SendResponse(RESP_OK);
            break;

        case CMD_BUZZER:
            if (parser.data_len >= 2) {
                uint8_t volume = parser.data[0];
                uint8_t duration = parser.data[1];
                Buzzer_Set(volume, duration);
                Protocol_SendResponse(RESP_OK);
            } else {
                Protocol_SendResponse(RESP_ERROR);
            }
            break;

        default:
            Protocol_SendResponse(RESP_ERROR);
            break;
    }
}
