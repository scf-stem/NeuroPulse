/**
 * ============================================================
 * data_uploader.cpp
 * 数据上传模块实现 / Data Uploader Implementation
 * ============================================================
 *
 * 项目: 帕金森震颤监测手环 (Tremor Guard)
 * 功能: 实现震颤数据的批量上传和离线缓存
 *
 * ============================================================
 */

#include "data_uploader.h"
#include "wifi_manager.h"
#include "http_client.h"
#include <ArduinoJson.h>

// ============================================================
// 内部数据结构 (Internal Data Structures)
// ============================================================

// 简化的上传数据结构
struct UploadDataItem {
    unsigned long deviceTimeMs;     // 设备时间 (millis)
    bool detected;
    bool valid;
    bool outOfRange;
    float frequency;
    float rmsAmplitude;
    int severity;
    char severityLabel[16];
    float peakPower;
    float bandPower;
    float amplitude;
};

// ============================================================
// 内部变量 (Internal Variables)
// ============================================================

static char deviceId[32] = DEVICE_ID;
static UploadDataItem dataQueue[OFFLINE_BUFFER_SIZE];
static int queueHead = 0;           // 队列头
static int queueCount = 0;          // 队列数量
static unsigned long lastUploadTime = 0;
static unsigned long lastHeartbeatTime = 0;
static int currentBatchId = 0;

static UploadStats stats = {0, 0, 0, 0, 0, 0, 0};

// 状态标签
static const char* STATUS_LABELS[] = {
    "成功",
    "失败",
    "WiFi未连接",
    "服务器未配置",
    "已加入队列",
    "缓冲区已满"
};

// ============================================================
// 初始化 (Initialization)
// ============================================================

void uploaderInit(void) {
    queueHead = 0;
    queueCount = 0;
    lastUploadTime = millis();
    lastHeartbeatTime = millis();
    currentBatchId = 0;

    memset(&stats, 0, sizeof(stats));

#ifdef NETWORK_DEBUG_ENABLED
    Serial.println("[Uploader] 数据上传模块已初始化");
    Serial.print("[Uploader] 设备 ID: ");
    Serial.println(deviceId);
    Serial.print("[Uploader] 批量大小: ");
    Serial.println(BATCH_SIZE);
    Serial.print("[Uploader] 缓冲区大小: ");
    Serial.println(OFFLINE_BUFFER_SIZE);
#endif
}

void uploaderSetDeviceId(const char* id) {
    strncpy(deviceId, id, sizeof(deviceId) - 1);
}

// ============================================================
// 数据队列操作 (Queue Operations)
// ============================================================

UploadStatus uploaderAddData(const TremorResult& result) {
    // 创建上传数据项
    UploadDataItem item;
    item.deviceTimeMs = result.timestamp;
    item.detected = result.detected;
    item.valid = result.valid;
    item.outOfRange = result.outOfRange;
    item.frequency = result.frequency;
    item.rmsAmplitude = result.rmsAmplitude;
    item.severity = result.severity;
    strncpy(item.severityLabel, result.severityLabel, sizeof(item.severityLabel) - 1);
    item.peakPower = result.spectrum.peakPower;
    item.bandPower = result.spectrum.bandPower;
    item.amplitude = result.amplitude;

    // 添加到队列
    int index = (queueHead + queueCount) % OFFLINE_BUFFER_SIZE;

    if (queueCount >= OFFLINE_BUFFER_SIZE) {
        // 缓冲区满，覆盖最旧的数据
        queueHead = (queueHead + 1) % OFFLINE_BUFFER_SIZE;
#ifdef NETWORK_DEBUG_ENABLED
        Serial.println("[Uploader] 警告: 缓冲区已满，覆盖最旧数据");
#endif
    } else {
        queueCount++;
    }

    dataQueue[index] = item;
    stats.queuedCount = queueCount;

#ifdef NETWORK_DEBUG_ENABLED
    Serial.print("[Uploader] 数据已加入队列 (");
    Serial.print(queueCount);
    Serial.print("/");
    Serial.print(BATCH_SIZE);
    Serial.println(")");
#endif

    return UPLOAD_QUEUED;
}

// ============================================================
// 批量上传 (Batch Upload)
// ============================================================

UploadStatus uploaderProcess(void) {
    unsigned long now = millis();

    // 检查是否需要上传
    bool shouldUpload = false;

    // 条件1: 达到批量大小
    if (queueCount >= BATCH_SIZE) {
        shouldUpload = true;
#ifdef NETWORK_DEBUG_ENABLED
        Serial.println("[Uploader] 达到批量大小，触发上传");
#endif
    }

    // 条件2: 超时 (有数据但未达到批量大小)
    if (queueCount > 0 && (now - lastUploadTime >= BATCH_TIMEOUT_MS)) {
        shouldUpload = true;
#ifdef NETWORK_DEBUG_ENABLED
        Serial.println("[Uploader] 超时，触发上传");
#endif
    }

    if (!shouldUpload || queueCount == 0) {
        return UPLOAD_QUEUED;
    }

    // 检查 WiFi
    if (!wifiIsConnected()) {
        stats.offlineCount = queueCount;
        return UPLOAD_NO_WIFI;
    }

    // 检查服务器配置
    if (!httpIsConfigured()) {
        return UPLOAD_NO_SERVER;
    }

    // 执行上传
    int uploaded = uploaderFlush();

    if (uploaded > 0) {
        return UPLOAD_SUCCESS;
    } else {
        return UPLOAD_FAILED;
    }
}

int uploaderFlush(void) {
    if (queueCount == 0) {
        return 0;
    }

    // 检查 WiFi
    if (!wifiIsConnected()) {
#ifdef NETWORK_DEBUG_ENABLED
        Serial.println("[Uploader] WiFi 未连接，无法上传");
#endif
        return 0;
    }

    // 构建 JSON
    JsonDocument doc;
    doc["device_id"] = deviceId;
    doc["batch_id"] = ++currentBatchId;

    JsonArray dataArray = doc["data"].to<JsonArray>();

    int count = queueCount;
    for (int i = 0; i < count; i++) {
        int index = (queueHead + i) % OFFLINE_BUFFER_SIZE;
        UploadDataItem& item = dataQueue[index];

        JsonObject obj = dataArray.add<JsonObject>();
        obj["device_time_ms"] = item.deviceTimeMs;
        obj["detected"] = item.detected;

        if (item.detected) {
            obj["valid"] = item.valid;
            obj["out_of_range"] = item.outOfRange;
            obj["frequency"] = round(item.frequency * 100) / 100.0;
            obj["rms_amplitude"] = round(item.rmsAmplitude * 1000) / 1000.0;
            obj["severity"] = item.severity;
            obj["severity_label"] = item.severityLabel;
            obj["peak_power"] = round(item.peakPower * 1000) / 1000.0;
            obj["band_power"] = round(item.bandPower * 1000) / 1000.0;
        } else {
            // 未检测到震颤时只发送基本数据
            obj["rms_amplitude"] = round(item.rmsAmplitude * 1000) / 1000.0;
        }
    }

#ifdef NETWORK_DEBUG_ENABLED
    Serial.print("[Uploader] 上传 ");
    Serial.print(count);
    Serial.println(" 条数据...");
#endif

    // 发送请求
    HttpResponse response = httpPostJson(API_BATCH_PATH, doc);

    if (response.success) {
        // 上传成功，清空队列
        queueHead = 0;
        queueCount = 0;
        lastUploadTime = millis();

        stats.successfulUploads++;
        stats.totalUploads++;
        stats.lastUploadTime = lastUploadTime;
        stats.queuedCount = 0;
        stats.offlineCount = 0;
        stats.batchId = currentBatchId;

#ifdef NETWORK_DEBUG_ENABLED
        Serial.print("[Uploader] 上传成功! 批次 #");
        Serial.println(currentBatchId);
#endif

        return count;
    } else {
        stats.failedUploads++;
        stats.totalUploads++;
        stats.offlineCount = queueCount;

#ifdef NETWORK_DEBUG_ENABLED
        Serial.print("[Uploader] 上传失败: ");
        Serial.println(response.errorMessage);
#endif

        return 0;
    }
}

// ============================================================
// 心跳 (Heartbeat)
// ============================================================

bool uploaderSendHeartbeat(void) {
    if (!wifiIsConnected() || !httpIsConfigured()) {
        return false;
    }

    JsonDocument doc;
    doc["device_id"] = deviceId;
    doc["firmware_version"] = FIRMWARE_VERSION;
    doc["wifi_rssi"] = wifiGetRSSI();
    doc["queue_count"] = queueCount;
    doc["uptime_ms"] = millis();

    HttpResponse response = httpPostJson(API_HEARTBEAT_PATH, doc);

#ifdef NETWORK_DEBUG_ENABLED
    if (response.success) {
        Serial.println("[Uploader] 心跳发送成功");
    } else {
        Serial.print("[Uploader] 心跳发送失败: ");
        Serial.println(response.errorMessage);
    }
#endif

    return response.success;
}

void uploaderHeartbeatCheck(void) {
    if (!HEARTBEAT_ENABLED) {
        return;
    }

    unsigned long now = millis();
    if (now - lastHeartbeatTime >= HEARTBEAT_INTERVAL_MS) {
        lastHeartbeatTime = now;
        uploaderSendHeartbeat();
    }
}

// ============================================================
// 统计与状态 (Statistics & Status)
// ============================================================

UploadStats uploaderGetStats(void) {
    stats.queuedCount = queueCount;
    return stats;
}

int uploaderGetQueueCount(void) {
    return queueCount;
}

int uploaderGetOfflineCount(void) {
    if (!wifiIsConnected()) {
        return queueCount;
    }
    return 0;
}

void uploaderClearQueue(void) {
    queueHead = 0;
    queueCount = 0;
    stats.queuedCount = 0;
    stats.offlineCount = 0;

#ifdef NETWORK_DEBUG_ENABLED
    Serial.println("[Uploader] 队列已清空");
#endif
}

void uploaderPrintStatus(void) {
    UploadStats s = uploaderGetStats();

    Serial.println();
    Serial.println("[Uploader] 上传状态:");
    Serial.println("────────────────────────────────────");

    Serial.print("  设备 ID: ");
    Serial.println(deviceId);

    Serial.print("  队列数量: ");
    Serial.print(queueCount);
    Serial.print(" / ");
    Serial.println(OFFLINE_BUFFER_SIZE);

    Serial.print("  总上传次数: ");
    Serial.println(s.totalUploads);

    Serial.print("  成功次数: ");
    Serial.println(s.successfulUploads);

    Serial.print("  失败次数: ");
    Serial.println(s.failedUploads);

    Serial.print("  当前批次: #");
    Serial.println(s.batchId);

    if (s.lastUploadTime > 0) {
        Serial.print("  上次上传: ");
        Serial.print((millis() - s.lastUploadTime) / 1000);
        Serial.println(" 秒前");
    }

    Serial.println("────────────────────────────────────");
}

const char* uploaderGetStatusLabel(UploadStatus status) {
    if (status >= 0 && status <= 5) {
        return STATUS_LABELS[status];
    }
    return "未知";
}
