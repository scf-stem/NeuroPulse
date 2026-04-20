/**
 * ============================================================
 * config_sync.h
 * 云端配置同步模块头文件 / Cloud Config Sync Header
 * ============================================================
 *
 * 项目: 帕金森震颤监测手环 (Tremor Guard)
 * 功能: 从云端服务器拉取震颤检测参数配置
 *
 * ============================================================
 */

#ifndef CONFIG_SYNC_H
#define CONFIG_SYNC_H

#include <Arduino.h>
#include "tremor_config.h"
#include "network_config.h"

// ============================================================
// 同步状态枚举 (Sync Status Enum)
// ============================================================

enum ConfigSyncStatus {
    SYNC_SUCCESS,           // 同步成功
    SYNC_NO_WIFI,           // WiFi 未连接
    SYNC_HTTP_ERROR,        // HTTP 请求错误
    SYNC_PARSE_ERROR,       // JSON 解析错误
    SYNC_NO_UPDATE,         // 无需更新 (版本相同)
    SYNC_APPLY_ERROR        // 应用配置失败
};

// ============================================================
// 函数声明 (Function Declarations)
// ============================================================

/**
 * 初始化配置同步模块
 * Initialize config sync module
 */
void configSyncInit(void);

/**
 * 从云端同步配置
 * Sync configuration from cloud
 *
 * @return ConfigSyncStatus 同步状态
 */
ConfigSyncStatus configSyncFromCloud(void);

/**
 * 获取同步状态标签
 * Get sync status label
 *
 * @param status 状态枚举
 * @return 状态标签字符串
 */
const char* configSyncGetStatusLabel(ConfigSyncStatus status);

/**
 * 打印同步状态
 * Print sync status
 */
void configSyncPrintStatus(void);

/**
 * 上传当前配置到云端
 * Upload current config to cloud
 *
 * @return ConfigSyncStatus 上传状态
 */
ConfigSyncStatus configSyncUploadToCloud(void);

#endif // CONFIG_SYNC_H
