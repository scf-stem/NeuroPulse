/**
 * ============================================================
 * http_client.cpp
 * HTTP 客户端封装实现 / HTTP Client Wrapper Implementation
 * ============================================================
 *
 * 项目: 帕金森震颤监测手环 (Tremor Guard)
 * 功能: 实现 HTTP POST/GET 请求封装
 *
 * ============================================================
 */

#include "http_client.h"
#include "wifi_manager.h"

// ============================================================
// 内部变量 (Internal Variables)
// ============================================================

static char serverHost[128] = "";
static int serverPort = 443;
static char apiKey[128] = "";
static bool useHttps = true;
static int requestTimeout = HTTP_TIMEOUT_MS;
static bool configured = false;

// HTTPS 客户端
static WiFiClientSecure secureClient;

// ============================================================
// 初始化 (Initialization)
// ============================================================

void httpInit(const char* host, int port, const char* key, bool https) {
    strncpy(serverHost, host, sizeof(serverHost) - 1);
    serverPort = port;
    strncpy(apiKey, key, sizeof(apiKey) - 1);
    useHttps = https;

    configured = (strlen(serverHost) > 0);

    // HTTPS 设置 (不验证证书，适合开发阶段)
    if (useHttps) {
        secureClient.setInsecure();  // 跳过证书验证
    }

#ifdef NETWORK_DEBUG_ENABLED
    Serial.println("[HTTP] 客户端已初始化");
    httpPrintConfig();
#endif
}

// ============================================================
// POST JSON 请求 (POST JSON Request)
// ============================================================

HttpResponse httpPostJson(const char* path, JsonDocument& jsonDoc) {
    String jsonString;
    serializeJson(jsonDoc, jsonString);
    return httpPostJsonString(path, jsonString);
}

HttpResponse httpPostJsonString(const char* path, const String& jsonString) {
    HttpResponse response = {0, "", false, ""};

    // 检查配置
    if (!configured) {
        response.statusCode = -1;
        response.errorMessage = "服务器未配置";
        return response;
    }

    // 检查 WiFi
    if (!wifiIsConnected()) {
        response.statusCode = -2;
        response.errorMessage = "WiFi 未连接";
        return response;
    }

    HTTPClient http;
    String url = httpGetFullUrl(path);

#ifdef NETWORK_DEBUG_ENABLED
    Serial.print("[HTTP] POST ");
    Serial.println(url);
    Serial.print("[HTTP] Body: ");
    Serial.println(jsonString);
#endif

    // 开始请求
    bool beginResult;
    if (useHttps) {
        beginResult = http.begin(secureClient, url);
    } else {
        beginResult = http.begin(url);
    }

    if (!beginResult) {
        response.statusCode = -3;
        response.errorMessage = "无法连接服务器";
        return response;
    }

    // 设置请求头
    http.setTimeout(requestTimeout);
    http.addHeader("Content-Type", "application/json");

    if (strlen(apiKey) > 0) {
        http.addHeader("X-Device-Key", apiKey);
    }

    // 发送请求
    int httpCode = http.POST(jsonString);

    if (httpCode > 0) {
        response.statusCode = httpCode;
        response.body = http.getString();
        response.success = (httpCode >= 200 && httpCode < 300);

#ifdef NETWORK_DEBUG_ENABLED
        Serial.print("[HTTP] 响应码: ");
        Serial.println(httpCode);
        Serial.print("[HTTP] 响应体: ");
        Serial.println(response.body);
#endif
    } else {
        response.statusCode = httpCode;
        response.success = false;
        response.errorMessage = http.errorToString(httpCode);

#ifdef NETWORK_DEBUG_ENABLED
        Serial.print("[HTTP] 错误: ");
        Serial.println(response.errorMessage);
#endif
    }

    http.end();
    return response;
}

// ============================================================
// GET 请求 (GET Request)
// ============================================================

HttpResponse httpGet(const char* path) {
    HttpResponse response = {0, "", false, ""};

    // 检查配置
    if (!configured) {
        response.statusCode = -1;
        response.errorMessage = "服务器未配置";
        return response;
    }

    // 检查 WiFi
    if (!wifiIsConnected()) {
        response.statusCode = -2;
        response.errorMessage = "WiFi 未连接";
        return response;
    }

    HTTPClient http;
    String url = httpGetFullUrl(path);

#ifdef NETWORK_DEBUG_ENABLED
    Serial.print("[HTTP] GET ");
    Serial.println(url);
#endif

    // 开始请求
    bool beginResult;
    if (useHttps) {
        beginResult = http.begin(secureClient, url);
    } else {
        beginResult = http.begin(url);
    }

    if (!beginResult) {
        response.statusCode = -3;
        response.errorMessage = "无法连接服务器";
        return response;
    }

    // 设置请求头
    http.setTimeout(requestTimeout);

    if (strlen(apiKey) > 0) {
        http.addHeader("X-Device-Key", apiKey);
    }

    // 发送请求
    int httpCode = http.GET();

    if (httpCode > 0) {
        response.statusCode = httpCode;
        response.body = http.getString();
        response.success = (httpCode >= 200 && httpCode < 300);

#ifdef NETWORK_DEBUG_ENABLED
        Serial.print("[HTTP] 响应码: ");
        Serial.println(httpCode);
#endif
    } else {
        response.statusCode = httpCode;
        response.success = false;
        response.errorMessage = http.errorToString(httpCode);

#ifdef NETWORK_DEBUG_ENABLED
        Serial.print("[HTTP] 错误: ");
        Serial.println(response.errorMessage);
#endif
    }

    http.end();
    return response;
}

// ============================================================
// 辅助函数 (Helper Functions)
// ============================================================

void httpSetTimeout(int timeout_ms) {
    requestTimeout = timeout_ms;
}

bool httpIsConfigured(void) {
    return configured;
}

String httpGetFullUrl(const char* path) {
    String url = "";

    if (useHttps) {
        url += "https://";
    } else {
        url += "http://";
    }

    url += serverHost;

    // 非标准端口时添加端口号
    if ((useHttps && serverPort != 443) || (!useHttps && serverPort != 80)) {
        url += ":";
        url += String(serverPort);
    }

    url += path;

    return url;
}

void httpPrintConfig(void) {
    Serial.println();
    Serial.println("[HTTP] 客户端配置:");
    Serial.println("────────────────────────────────────");

    Serial.print("  服务器: ");
    if (strlen(serverHost) > 0) {
        Serial.print(useHttps ? "https://" : "http://");
        Serial.print(serverHost);
        if ((useHttps && serverPort != 443) || (!useHttps && serverPort != 80)) {
            Serial.print(":");
            Serial.print(serverPort);
        }
        Serial.println();
    } else {
        Serial.println("(未配置)");
    }

    Serial.print("  API Key: ");
    if (strlen(apiKey) > 0) {
        Serial.print(apiKey[0]);
        Serial.print("***");
        Serial.println(apiKey[strlen(apiKey) - 1]);
    } else {
        Serial.println("(未配置)");
    }

    Serial.print("  超时时间: ");
    Serial.print(requestTimeout);
    Serial.println(" ms");

    Serial.print("  状态: ");
    Serial.println(configured ? "已配置" : "未配置");

    Serial.println("────────────────────────────────────");
}
