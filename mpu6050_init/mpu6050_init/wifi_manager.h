/**
 * ============================================================
 * wifi_manager.h
 * WiFi 连接管理模块头文件 / WiFi Manager Header
 * ============================================================
 *
 * 项目: 帕金森震颤监测手环 (Tremor Guard)
 * 功能: 管理 ESP32 的 WiFi 连接、重连和状态监控
 *
 * ============================================================
 */

#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <Arduino.h>
#include <WiFi.h>
#include "network_config.h"

// ============================================================
// WiFi 状态枚举 (WiFi Status Enum)
// ============================================================

enum WifiConnectionStatus {
    WIFI_STATUS_DISCONNECTED,       // 未连接
    WIFI_STATUS_CONNECTING,         // 正在连接
    WIFI_STATUS_CONNECTED,          // 已连接
    WIFI_STATUS_CONNECTION_FAILED,  // 连接失败
    WIFI_STATUS_NO_SSID             // 未配置 SSID
};

// ============================================================
// WiFi 信息结构 (WiFi Info Structure)
// ============================================================

struct WifiInfo {
    WifiConnectionStatus status;    // 连接状态
    char ssid[64];                  // SSID
    char ip[16];                    // IP 地址
    int rssi;                       // 信号强度 dBm
    unsigned long connectedTime;    // 连接时间 (millis)
    unsigned long lastReconnectAttempt; // 上次重连尝试时间
    int reconnectCount;             // 重连次数
};

// ============================================================
// 函数声明 (Function Declarations)
// ============================================================

/**
 * 初始化 WiFi 管理器
 * Initialize WiFi manager
 *
 * @param ssid WiFi 名称
 * @param password WiFi 密码
 */
void wifiInit(const char* ssid, const char* password);

/**
 * 连接 WiFi
 * Connect to WiFi
 *
 * @param timeout_ms 超时时间 (毫秒)
 * @return true 如果连接成功
 */
bool wifiConnect(int timeout_ms = WIFI_CONNECT_TIMEOUT_MS);

/**
 * 断开 WiFi 连接
 * Disconnect from WiFi
 */
void wifiDisconnect(void);

/**
 * 检查 WiFi 是否已连接
 * Check if WiFi is connected
 *
 * @return true 如果已连接
 */
bool wifiIsConnected(void);

/**
 * 获取 WiFi 状态
 * Get WiFi status
 *
 * @return WifiConnectionStatus 状态枚举
 */
WifiConnectionStatus wifiGetStatus(void);

/**
 * 获取 WiFi 详细信息
 * Get WiFi detailed info
 *
 * @return WifiInfo 结构体
 */
WifiInfo wifiGetInfo(void);

/**
 * 获取 IP 地址字符串
 * Get IP address string
 *
 * @return IP 地址
 */
String wifiGetIP(void);

/**
 * 获取信号强度
 * Get signal strength (RSSI)
 *
 * @return RSSI 值 (dBm)
 */
int wifiGetRSSI(void);

/**
 * 自动重连检查 (在 loop 中调用)
 * Auto reconnect check (call in loop)
 *
 * 如果 WiFi 断开且超过重连间隔，自动尝试重连
 */
void wifiAutoReconnect(void);

/**
 * 打印 WiFi 状态信息
 * Print WiFi status info
 */
void wifiPrintStatus(void);

/**
 * 获取状态标签字符串
 * Get status label string
 *
 * @param status 状态枚举
 * @return 状态标签
 */
const char* wifiGetStatusLabel(WifiConnectionStatus status);

/**
 * 重置 WiFi (断开并清除配置)
 * Reset WiFi (disconnect and clear config)
 */
void wifiReset(void);

#endif // WIFI_MANAGER_H
