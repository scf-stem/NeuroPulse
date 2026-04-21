/**
 * ============================================================
 * http_client.h
 * HTTP 客户端封装头文件 / HTTP Client Wrapper Header
 * ============================================================
 *
 * 项目: 帕金森震颤监测手环 (Tremor Guard)
 * 功能: 封装 ESP32 HTTP 客户端，简化 API 调用
 *
 * ============================================================
 */

#ifndef HTTP_CLIENT_H
#define HTTP_CLIENT_H

#include <Arduino.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include "network_config.h"

// ============================================================
// HTTP 响应结构 (HTTP Response Structure)
// ============================================================

struct HttpResponse {
    int statusCode;         // HTTP 状态码
    String body;            // 响应体
    bool success;           // 是否成功 (2xx)
    String errorMessage;    // 错误信息
};

// ============================================================
// 函数声明 (Function Declarations)
// ============================================================

/**
 * 初始化 HTTP 客户端
 * Initialize HTTP client
 *
 * @param host 服务器地址
 * @param port 端口号
 * @param apiKey API 密钥
 * @param useHttps 是否使用 HTTPS
 */
void httpInit(const char* host, int port, const char* apiKey, bool useHttps = true);

/**
 * 发送 POST JSON 请求
 * Send POST JSON request
 *
 * @param path API 路径 (例: "/api/v1/data/upload")
 * @param jsonDoc JSON 文档
 * @return HttpResponse 响应结构
 */
HttpResponse httpPostJson(const char* path, JsonDocument& jsonDoc);

/**
 * 发送 POST JSON 字符串请求
 * Send POST JSON string request
 *
 * @param path API 路径
 * @param jsonString JSON 字符串
 * @return HttpResponse 响应结构
 */
HttpResponse httpPostJsonString(const char* path, const String& jsonString);

/**
 * 发送 GET 请求
 * Send GET request
 *
 * @param path API 路径
 * @return HttpResponse 响应结构
 */
HttpResponse httpGet(const char* path);

/**
 * 设置请求超时时间
 * Set request timeout
 *
 * @param timeout_ms 超时时间 (毫秒)
 */
void httpSetTimeout(int timeout_ms);

/**
 * 检查服务器是否配置
 * Check if server is configured
 *
 * @return true 如果已配置
 */
bool httpIsConfigured(void);

/**
 * 获取完整 URL
 * Get full URL
 *
 * @param path API 路径
 * @return 完整 URL 字符串
 */
String httpGetFullUrl(const char* path);

/**
 * 打印 HTTP 客户端配置
 * Print HTTP client configuration
 */
void httpPrintConfig(void);

#endif // HTTP_CLIENT_H
