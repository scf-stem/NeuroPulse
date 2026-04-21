/**
 * ============================================================
 * wifi_manager.cpp
 * WiFi 连接管理模块实现 / WiFi Manager Implementation
 * ============================================================
 *
 * 项目: 帕金森震颤监测手环 (Tremor Guard)
 * 功能: 实现 WiFi 连接、重连和状态监控
 *
 * ============================================================
 */

#include "wifi_manager.h"

// ============================================================
// 内部变量 (Internal Variables)
// ============================================================

static char savedSSID[64] = "";
static char savedPassword[64] = "";
static WifiInfo wifiInfo = {
    WIFI_STATUS_DISCONNECTED,
    "",
    "",
    0,
    0,
    0,
    0
};

// 状态标签
static const char* STATUS_LABELS[] = {
    "未连接",
    "连接中",
    "已连接",
    "连接失败",
    "未配置"
};

// ============================================================
// 初始化 (Initialization)
// ============================================================

void wifiInit(const char* ssid, const char* password) {
    // 保存配置
    strncpy(savedSSID, ssid, sizeof(savedSSID) - 1);
    strncpy(savedPassword, password, sizeof(savedPassword) - 1);
    strncpy(wifiInfo.ssid, ssid, sizeof(wifiInfo.ssid) - 1);

    // 检查是否配置了 SSID
    if (strlen(ssid) == 0) {
        wifiInfo.status = WIFI_STATUS_NO_SSID;
        Serial.println("[WiFi] 警告: SSID 未配置");
        return;
    }

    // 设置 WiFi 模式
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(false);  // 手动控制重连

    wifiInfo.status = WIFI_STATUS_DISCONNECTED;

#ifdef NETWORK_DEBUG_ENABLED
    Serial.println("[WiFi] 管理器已初始化");
    Serial.print("[WiFi] SSID: ");
    Serial.println(savedSSID);
#endif
}

// ============================================================
// 连接 (Connect)
// ============================================================

bool wifiConnect(int timeout_ms) {
    // 检查配置
    if (strlen(savedSSID) == 0) {
        Serial.println("[WiFi] 错误: SSID 未配置");
        wifiInfo.status = WIFI_STATUS_NO_SSID;
        return false;
    }

    // 如果已连接，直接返回
    if (WiFi.status() == WL_CONNECTED) {
        wifiInfo.status = WIFI_STATUS_CONNECTED;
        return true;
    }

    wifiInfo.status = WIFI_STATUS_CONNECTING;

    Serial.print("[WiFi] 正在连接到 ");
    Serial.print(savedSSID);
    Serial.print(" ");

    // 开始连接
    WiFi.begin(savedSSID, savedPassword);

    // 等待连接
    unsigned long startTime = millis();
    while (WiFi.status() != WL_CONNECTED) {
        if (millis() - startTime > timeout_ms) {
            Serial.println(" 超时!");
            wifiInfo.status = WIFI_STATUS_CONNECTION_FAILED;
            wifiInfo.reconnectCount++;
            WiFi.disconnect();
            return false;
        }
        delay(500);
        Serial.print(".");
    }

    // 连接成功
    Serial.println(" 成功!");
    wifiInfo.status = WIFI_STATUS_CONNECTED;
    wifiInfo.connectedTime = millis();
    wifiInfo.rssi = WiFi.RSSI();

    // 获取 IP
    IPAddress ip = WiFi.localIP();
    snprintf(wifiInfo.ip, sizeof(wifiInfo.ip), "%d.%d.%d.%d",
             ip[0], ip[1], ip[2], ip[3]);

#ifdef NETWORK_DEBUG_ENABLED
    Serial.print("[WiFi] IP 地址: ");
    Serial.println(wifiInfo.ip);
    Serial.print("[WiFi] 信号强度: ");
    Serial.print(wifiInfo.rssi);
    Serial.println(" dBm");
#endif

    return true;
}

// ============================================================
// 断开连接 (Disconnect)
// ============================================================

void wifiDisconnect(void) {
    WiFi.disconnect();
    wifiInfo.status = WIFI_STATUS_DISCONNECTED;
    wifiInfo.ip[0] = '\0';
    wifiInfo.rssi = 0;

#ifdef NETWORK_DEBUG_ENABLED
    Serial.println("[WiFi] 已断开连接");
#endif
}

// ============================================================
// 状态查询 (Status Query)
// ============================================================

bool wifiIsConnected(void) {
    return WiFi.status() == WL_CONNECTED;
}

WifiConnectionStatus wifiGetStatus(void) {
    // 同步实际状态
    if (WiFi.status() == WL_CONNECTED) {
        wifiInfo.status = WIFI_STATUS_CONNECTED;
    } else if (wifiInfo.status == WIFI_STATUS_CONNECTED) {
        // 之前是连接的，现在断开了
        wifiInfo.status = WIFI_STATUS_DISCONNECTED;
    }
    return wifiInfo.status;
}

WifiInfo wifiGetInfo(void) {
    // 更新状态
    wifiGetStatus();

    // 更新 RSSI
    if (WiFi.status() == WL_CONNECTED) {
        wifiInfo.rssi = WiFi.RSSI();
    }

    return wifiInfo;
}

String wifiGetIP(void) {
    if (WiFi.status() == WL_CONNECTED) {
        return WiFi.localIP().toString();
    }
    return "0.0.0.0";
}

int wifiGetRSSI(void) {
    if (WiFi.status() == WL_CONNECTED) {
        return WiFi.RSSI();
    }
    return 0;
}

// ============================================================
// 自动重连 (Auto Reconnect)
// ============================================================

void wifiAutoReconnect(void) {
    // 如果已连接，不需要重连
    if (WiFi.status() == WL_CONNECTED) {
        if (wifiInfo.status != WIFI_STATUS_CONNECTED) {
            wifiInfo.status = WIFI_STATUS_CONNECTED;
            wifiInfo.connectedTime = millis();

#ifdef NETWORK_DEBUG_ENABLED
            Serial.println("[WiFi] 连接已恢复");
#endif
        }
        return;
    }

    // 如果未配置 SSID，不尝试重连
    if (strlen(savedSSID) == 0) {
        return;
    }

    // 更新状态
    if (wifiInfo.status == WIFI_STATUS_CONNECTED) {
        wifiInfo.status = WIFI_STATUS_DISCONNECTED;
#ifdef NETWORK_DEBUG_ENABLED
        Serial.println("[WiFi] 连接已断开");
#endif
    }

    // 检查是否需要重连
    unsigned long now = millis();
    if (now - wifiInfo.lastReconnectAttempt >= WIFI_RECONNECT_INTERVAL_MS) {
        wifiInfo.lastReconnectAttempt = now;

#ifdef NETWORK_DEBUG_ENABLED
        Serial.print("[WiFi] 尝试重连 (第 ");
        Serial.print(wifiInfo.reconnectCount + 1);
        Serial.println(" 次)...");
#endif

        wifiConnect(WIFI_CONNECT_TIMEOUT_MS);
    }
}

// ============================================================
// 状态打印 (Status Print)
// ============================================================

void wifiPrintStatus(void) {
    WifiInfo info = wifiGetInfo();

    Serial.println();
    Serial.println("[WiFi] 状态信息:");
    Serial.println("────────────────────────────────────");

    Serial.print("  状态: ");
    Serial.println(wifiGetStatusLabel(info.status));

    Serial.print("  SSID: ");
    if (strlen(info.ssid) > 0) {
        Serial.println(info.ssid);
    } else {
        Serial.println("(未配置)");
    }

    if (info.status == WIFI_STATUS_CONNECTED) {
        Serial.print("  IP 地址: ");
        Serial.println(wifiGetIP());

        Serial.print("  信号强度: ");
        Serial.print(info.rssi);
        Serial.print(" dBm ");

        // 信号强度图示
        Serial.print("[");
        int bars = 0;
        if (info.rssi > -50) bars = 5;
        else if (info.rssi > -60) bars = 4;
        else if (info.rssi > -70) bars = 3;
        else if (info.rssi > -80) bars = 2;
        else if (info.rssi > -90) bars = 1;

        for (int i = 0; i < 5; i++) {
            if (i < bars) Serial.print("█");
            else Serial.print("░");
        }
        Serial.println("]");

        Serial.print("  连接时长: ");
        unsigned long duration = millis() - info.connectedTime;
        Serial.print(duration / 1000);
        Serial.println(" 秒");
    }

    Serial.print("  重连次数: ");
    Serial.println(info.reconnectCount);

    Serial.println("────────────────────────────────────");
}

const char* wifiGetStatusLabel(WifiConnectionStatus status) {
    if (status >= 0 && status <= 4) {
        return STATUS_LABELS[status];
    }
    return "未知";
}

// ============================================================
// 重置 (Reset)
// ============================================================

void wifiReset(void) {
    wifiDisconnect();
    savedSSID[0] = '\0';
    savedPassword[0] = '\0';
    wifiInfo.ssid[0] = '\0';
    wifiInfo.ip[0] = '\0';
    wifiInfo.status = WIFI_STATUS_NO_SSID;
    wifiInfo.reconnectCount = 0;

    Serial.println("[WiFi] 已重置");
}
