/**
 * ============================================================
 * network_config.h
 * 网络配置参数 / Network Configuration
 * ============================================================
 *
 * 项目: 帕金森震颤监测手环 (Tremor Guard)
 * 功能: 定义 WiFi 和服务器连接相关的配置常量
 *
 * ============================================================
 */

#ifndef NETWORK_CONFIG_H
#define NETWORK_CONFIG_H

// ============================================================
// 服务器配置 (Server Configuration)
// ============================================================

// 后端服务器地址 (Zeabur 部署后填写)
// 请将下面的 "your-app.zeabur.app" 替换为你的实际域名
#define SERVER_HOST         "parkinson.zeabur.app"      // Zeabur 域名
#define SERVER_PORT         443                         // HTTPS 端口
#define SERVER_USE_HTTPS    true                        // 使用 HTTPS

// API 路径 - 测试接口
#define API_BASE_PATH       "/api/test"
#define API_UPLOAD_PATH     "/api/test/receive"         // 单条数据上传 (测试)
#define API_BATCH_PATH      "/api/test/batch"           // 批量数据上传 (测试)
#define API_HEARTBEAT_PATH  "/api/test/heartbeat"       // 心跳接口 (测试)
#define API_REGISTER_PATH   "/api/test/receive"         // 设备注册 (测试)

// ============================================================
// 设备标识 (Device Identification)
// ============================================================

#define DEVICE_ID           "TG-ESP32-001"      // 设备唯一 ID
#define DEVICE_API_KEY      ""                  // API 密钥 (待配置)
#define FIRMWARE_VERSION    "1.0.0"             // 固件版本

// ============================================================
// 批量上传设置 (Batch Upload Settings)
// ============================================================

#define BATCH_SIZE              10              // 批量上传条数
#define BATCH_TIMEOUT_MS        30000           // 批量超时 (30秒强制上传)
#define UPLOAD_ALL_RESULTS      true            // 是否上传所有结果 (包括未检测到震颤的)

// ============================================================
// 网络超时设置 (Network Timeout Settings)
// ============================================================

#define WIFI_CONNECT_TIMEOUT_MS     15000       // WiFi 连接超时 (15秒)
#define WIFI_RECONNECT_INTERVAL_MS  30000       // WiFi 重连间隔 (30秒)
#define HTTP_TIMEOUT_MS             10000       // HTTP 请求超时 (10秒)
#define UPLOAD_RETRY_COUNT          3           // 上传重试次数

// ============================================================
// 心跳设置 (Heartbeat Settings)
// ============================================================

#define HEARTBEAT_INTERVAL_MS       300000      // 心跳间隔 (5分钟)
#define HEARTBEAT_ENABLED           true        // 是否启用心跳

// ============================================================
// 离线缓存设置 (Offline Buffer Settings)
// ============================================================

#define OFFLINE_BUFFER_SIZE         50          // 离线缓存条数 (循环覆盖)
#define OFFLINE_FLUSH_ON_CONNECT    true        // WiFi 恢复后自动上传缓存

// ============================================================
// 调试设置 (Debug Settings)
// ============================================================

#define NETWORK_DEBUG_ENABLED       true        // 启用网络调试输出

#endif // NETWORK_CONFIG_H
