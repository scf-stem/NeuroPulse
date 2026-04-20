/**
 * ============================================================
 * data_uploader.h
 * 数据上传模块头文件 / Data Uploader Header
 * ============================================================
 *
 * 项目: 帕金森震颤监测手环 (Tremor Guard)
 * 功能: 管理震颤数据的批量上传和离线缓存
 *
 * ============================================================
 */

#ifndef DATA_UPLOADER_H
#define DATA_UPLOADER_H

#include <Arduino.h>
#include "tremor_detection.h"
#include "network_config.h"

// ============================================================
// 上传状态枚举 (Upload Status Enum)
// ============================================================

enum UploadStatus {
    UPLOAD_SUCCESS,         // 上传成功
    UPLOAD_FAILED,          // 上传失败
    UPLOAD_NO_WIFI,         // WiFi 未连接
    UPLOAD_NO_SERVER,       // 服务器未配置
    UPLOAD_QUEUED,          // 已加入队列 (批量/离线)
    UPLOAD_BUFFER_FULL      // 缓冲区已满
};

// ============================================================
// 上传统计结构 (Upload Statistics)
// ============================================================

struct UploadStats {
    unsigned long totalUploads;         // 总上传次数
    unsigned long successfulUploads;    // 成功次数
    unsigned long failedUploads;        // 失败次数
    unsigned long queuedCount;          // 当前队列数量
    unsigned long offlineCount;         // 离线缓存数量
    unsigned long lastUploadTime;       // 上次上传时间
    int batchId;                        // 当前批次 ID
};

// ============================================================
// 函数声明 (Function Declarations)
// ============================================================

/**
 * 初始化数据上传模块
 * Initialize data uploader module
 */
void uploaderInit(void);

/**
 * 设置设备 ID
 * Set device ID
 *
 * @param deviceId 设备 ID 字符串
 */
void uploaderSetDeviceId(const char* deviceId);

/**
 * 添加数据到上传队列
 * Add data to upload queue
 *
 * @param result 震颤检测结果
 * @return UploadStatus 状态
 */
UploadStatus uploaderAddData(const TremorResult& result);

/**
 * 检查并执行批量上传
 * Check and perform batch upload
 *
 * 在 loop() 中定期调用，满足条件时自动上传
 *
 * @return UploadStatus 状态
 */
UploadStatus uploaderProcess(void);

/**
 * 强制上传当前队列中的所有数据
 * Force upload all data in queue
 *
 * @return 成功上传的数据条数
 */
int uploaderFlush(void);

/**
 * 发送心跳
 * Send heartbeat
 *
 * @return true 如果成功
 */
bool uploaderSendHeartbeat(void);

/**
 * 检查并发送心跳 (在 loop 中调用)
 * Check and send heartbeat (call in loop)
 */
void uploaderHeartbeatCheck(void);

/**
 * 获取上传统计信息
 * Get upload statistics
 *
 * @return UploadStats 结构体
 */
UploadStats uploaderGetStats(void);

/**
 * 获取队列中的数据数量
 * Get number of items in queue
 *
 * @return 数据数量
 */
int uploaderGetQueueCount(void);

/**
 * 获取离线缓存数量
 * Get offline buffer count
 *
 * @return 离线缓存数量
 */
int uploaderGetOfflineCount(void);

/**
 * 清空队列
 * Clear queue
 */
void uploaderClearQueue(void);

/**
 * 打印上传状态
 * Print upload status
 */
void uploaderPrintStatus(void);

/**
 * 获取上传状态标签
 * Get upload status label
 *
 * @param status 状态枚举
 * @return 状态标签字符串
 */
const char* uploaderGetStatusLabel(UploadStatus status);

#endif // DATA_UPLOADER_H
