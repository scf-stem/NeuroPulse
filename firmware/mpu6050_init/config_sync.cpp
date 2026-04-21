/**
 * ============================================================
 * config_sync.cpp
 * 云端配置同步模块实现 / Cloud Config Sync Implementation
 * ============================================================
 *
 * 项目: 帕金森震颤监测手环 (Tremor Guard)
 * 功能: 从云端服务器拉取震颤检测参数配置
 *
 * ============================================================
 */

#include "config_sync.h"
#include "wifi_manager.h"
#include "http_client.h"
#include <ArduinoJson.h>

// ============================================================
// 内部变量 (Internal Variables)
// ============================================================

static ConfigSyncStatus lastSyncStatus = SYNC_NO_WIFI;
static unsigned long lastSyncTime = 0;
static int syncCount = 0;

// 状态标签
static const char* SYNC_STATUS_LABELS[] = {
    "同步成功",
    "WiFi 未连接",
    "HTTP 请求错误",
    "JSON 解析错误",
    "无需更新",
    "应用配置失败"
};

// ============================================================
// 初始化 (Initialization)
// ============================================================

void configSyncInit(void) {
    lastSyncStatus = SYNC_NO_WIFI;
    lastSyncTime = 0;
    syncCount = 0;

    Serial.println("[ConfigSync] 配置同步模块已初始化");
}

// ============================================================
// 云端同步 (Cloud Sync)
// ============================================================

ConfigSyncStatus configSyncFromCloud(void) {
    Serial.println();
    Serial.println("[ConfigSync] 开始从云端同步配置...");

    // 检查 WiFi
    if (!wifiIsConnected()) {
        Serial.println("[ConfigSync] 错误: WiFi 未连接");
        lastSyncStatus = SYNC_NO_WIFI;
        return SYNC_NO_WIFI;
    }

    // 检查服务器配置
    if (!httpIsConfigured()) {
        Serial.println("[ConfigSync] 错误: 服务器未配置");
        lastSyncStatus = SYNC_HTTP_ERROR;
        return SYNC_HTTP_ERROR;
    }

    Serial.print("[ConfigSync] 请求: GET ");
    Serial.println("/api/config/current");

    // 发送 GET 请求
    HttpResponse response = httpGet("/api/config/current");

    if (!response.success) {
        Serial.print("[ConfigSync] HTTP 请求失败: ");
        Serial.println(response.errorMessage);
        lastSyncStatus = SYNC_HTTP_ERROR;
        return SYNC_HTTP_ERROR;
    }

    Serial.println("[ConfigSync] 收到响应，开始解析...");

    // 解析 JSON
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, response.body);

    if (error) {
        Serial.print("[ConfigSync] JSON 解析失败: ");
        Serial.println(error.c_str());
        lastSyncStatus = SYNC_PARSE_ERROR;
        return SYNC_PARSE_ERROR;
    }

    // 获取版本号
    int cloudVersion = doc["version"] | 0;
    const char* updatedAt = doc["updated_at"] | "unknown";

    Serial.print("[ConfigSync] 云端配置版本: v");
    Serial.print(cloudVersion);
    Serial.print(" (更新时间: ");
    Serial.print(updatedAt);
    Serial.println(")");

    Serial.print("[ConfigSync] 本地配置版本: v");
    Serial.println(tremorConfig.configVersion);

    // 检查是否需要更新
    if (cloudVersion <= tremorConfig.configVersion) {
        Serial.println("[ConfigSync] 本地配置已是最新，无需更新");
        lastSyncStatus = SYNC_NO_UPDATE;
        lastSyncTime = millis();
        syncCount++;
        return SYNC_NO_UPDATE;
    }

    // 解析参数
    JsonObject params = doc["params"];
    if (params.isNull()) {
        Serial.println("[ConfigSync] 错误: 配置参数为空");
        lastSyncStatus = SYNC_PARSE_ERROR;
        return SYNC_PARSE_ERROR;
    }

    // 创建新配置
    TremorRuntimeConfig newConfig;
    newConfig.rmsMin = params["rms_min"] | TREMOR_RMS_MIN;
    newConfig.rmsMax = params["rms_max"] | TREMOR_RMS_MAX;
    newConfig.powerThreshold = params["power_threshold"] | TREMOR_POWER_THRESHOLD;
    newConfig.freqMin = params["freq_min"] | TREMOR_FREQ_MIN;
    newConfig.freqMax = params["freq_max"] | TREMOR_FREQ_MAX;

    // 解析严重度阈值数组
    JsonArray thresholds = params["severity_thresholds"];
    if (thresholds.size() >= 4) {
        newConfig.severityThresholds[0] = thresholds[0] | SEVERITY_THRESHOLD_0;
        newConfig.severityThresholds[1] = thresholds[1] | SEVERITY_THRESHOLD_1;
        newConfig.severityThresholds[2] = thresholds[2] | SEVERITY_THRESHOLD_2;
        newConfig.severityThresholds[3] = thresholds[3] | SEVERITY_THRESHOLD_3;
    } else {
        // 使用默认值
        newConfig.severityThresholds[0] = SEVERITY_THRESHOLD_0;
        newConfig.severityThresholds[1] = SEVERITY_THRESHOLD_1;
        newConfig.severityThresholds[2] = SEVERITY_THRESHOLD_2;
        newConfig.severityThresholds[3] = SEVERITY_THRESHOLD_3;
    }

    newConfig.configVersion = cloudVersion;

    // 打印将要应用的配置
    Serial.println();
    Serial.println("[ConfigSync] 云端配置内容:");
    Serial.print("  RMS 范围: ");
    Serial.print(newConfig.rmsMin, 2);
    Serial.print("g - ");
    Serial.print(newConfig.rmsMax, 2);
    Serial.println("g");
    Serial.print("  功率阈值: ");
    Serial.println(newConfig.powerThreshold, 2);
    Serial.print("  频率范围: ");
    Serial.print(newConfig.freqMin, 1);
    Serial.print("Hz - ");
    Serial.print(newConfig.freqMax, 1);
    Serial.println("Hz");

    // 应用配置
    if (tremorConfigUpdate(&newConfig)) {
        Serial.println();
        Serial.println("[ConfigSync] ✓ 配置同步成功!");
        lastSyncStatus = SYNC_SUCCESS;
        lastSyncTime = millis();
        syncCount++;
        return SYNC_SUCCESS;
    } else {
        Serial.println("[ConfigSync] 错误: 应用配置失败");
        lastSyncStatus = SYNC_APPLY_ERROR;
        return SYNC_APPLY_ERROR;
    }
}

// ============================================================
// 状态与标签 (Status & Labels)
// ============================================================

const char* configSyncGetStatusLabel(ConfigSyncStatus status) {
    if (status >= 0 && status <= 5) {
        return SYNC_STATUS_LABELS[status];
    }
    return "未知";
}

void configSyncPrintStatus(void) {
    Serial.println();
    Serial.println("[ConfigSync] 同步状态:");
    Serial.println("────────────────────────────────────");

    Serial.print("  上次状态: ");
    Serial.println(configSyncGetStatusLabel(lastSyncStatus));

    Serial.print("  同步次数: ");
    Serial.println(syncCount);

    if (lastSyncTime > 0) {
        Serial.print("  上次同步: ");
        Serial.print((millis() - lastSyncTime) / 1000);
        Serial.println(" 秒前");
    }

    Serial.print("  当前配置版本: v");
    Serial.println(tremorConfig.configVersion);

    Serial.println("────────────────────────────────────");
}

// ============================================================
// 上传配置到云端 (Upload Config to Cloud)
// ============================================================

ConfigSyncStatus configSyncUploadToCloud(void) {
    Serial.println();
    Serial.println("[ConfigSync] 正在上传配置到云端...");

    // 检查 WiFi
    if (!wifiIsConnected()) {
        Serial.println("[ConfigSync] 错误: WiFi 未连接");
        return SYNC_NO_WIFI;
    }

    // 检查服务器配置
    if (!httpIsConfigured()) {
        Serial.println("[ConfigSync] 错误: 服务器未配置");
        return SYNC_HTTP_ERROR;
    }

    // 构建 JSON 请求体
    JsonDocument doc;
    doc["device_id"] = DEVICE_ID;
    doc["config_version"] = tremorConfig.configVersion;
    doc["rms_min"] = tremorConfig.rmsMin;
    doc["rms_max"] = tremorConfig.rmsMax;
    doc["power_threshold"] = tremorConfig.powerThreshold;
    doc["freq_min"] = tremorConfig.freqMin;
    doc["freq_max"] = tremorConfig.freqMax;

    JsonArray thresholds = doc["severity_thresholds"].to<JsonArray>();
    thresholds.add(tremorConfig.severityThresholds[0]);
    thresholds.add(tremorConfig.severityThresholds[1]);
    thresholds.add(tremorConfig.severityThresholds[2]);
    thresholds.add(tremorConfig.severityThresholds[3]);

    Serial.print("[ConfigSync] 请求: POST ");
    Serial.println("/api/config/upload");

    // 发送 POST 请求
    HttpResponse response = httpPostJson("/api/config/upload", doc);

    if (!response.success) {
        Serial.print("[ConfigSync] HTTP 请求失败: ");
        Serial.println(response.errorMessage);
        return SYNC_HTTP_ERROR;
    }

    // 解析响应
    JsonDocument respDoc;
    DeserializationError error = deserializeJson(respDoc, response.body);

    if (error) {
        Serial.print("[ConfigSync] 响应解析失败: ");
        Serial.println(error.c_str());
        return SYNC_PARSE_ERROR;
    }

    // 获取响应信息
    int cloudVersion = respDoc["cloud_version"] | 0;
    bool needUpdate = respDoc["need_update"] | false;

    Serial.println("[ConfigSync] ✓ 配置上传成功!");
    Serial.print("  设备版本: v");
    Serial.println(tremorConfig.configVersion);
    Serial.print("  云端版本: v");
    Serial.println(cloudVersion);

    if (needUpdate) {
        Serial.println();
        Serial.println("[ConfigSync] 提示: 云端有新配置，请执行 update 命令同步");
    } else {
        Serial.println("[ConfigSync] 设备配置已是最新");
    }

    lastSyncTime = millis();
    syncCount++;
    lastSyncStatus = SYNC_SUCCESS;

    return SYNC_SUCCESS;
}
