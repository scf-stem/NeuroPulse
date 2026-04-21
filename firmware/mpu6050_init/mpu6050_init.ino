/*
 * ============================================================================
 * MPU6050 初始化与硬件检测程序 (含震颤检测功能)
 * Tremor Guard - Parkinson's Tremor Monitoring Wristband
 * ============================================================================
 *
 * 项目: 帕金森震颤监测手环 (Tremor Guard)
 * 硬件: Seeed XIAO ESP32-C3 + MPU6050
 * 作者: [Your Name]
 * 日期: 2024
 *
 * 功能说明:
 * 本程序用于检测MPU6050传感器的硬件连接，并提供帕金森震颤检测功能：
 * 1. I2C总线扫描 - 检测是否能发现I2C设备
 * 2. WHO_AM_I验证 - 确认芯片身份
 * 3. MPU6050初始化 - 配置传感器参数
 * 4. 数据读取测试 - 验证传感器数据输出
 * 5. FFT震颤检测 - 检测4-6Hz帕金森特征震颤
 *
 * 串口命令:
 * - test     : 运行完整硬件测试
 * - scan     : 仅扫描I2C总线
 * - read     : 读取一次传感器数据
 * - stream   : 开始/停止连续数据输出
 * - reset    : 复位MPU6050
 * - tremor   : 开始/停止连续震颤检测模式
 * - analyze  : 执行一次震颤分析
 * - spectrum : 显示频谱数据 (调试用)
 * - stats    : 显示震颤检测统计
 * - help     : 显示帮助信息
 *
 * 硬件连接:
 * XIAO ESP32-C3    MPU6050
 * D7 (GPIO7)  -->  SDA
 * D6 (GPIO6)  -->  SCL
 * D5 (GPIO5)  -->  INT (可选)
 * 3V3         -->  VDD, VLOGIC
 * GND         -->  GND
 *
 * ============================================================================
 */

#include <Wire.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include "tremor_detection.h"
#include "network_config.h"
#include "wifi_manager.h"
#include "http_client.h"
#include "data_uploader.h"
#include "config_sync.h"

// ============================================================================
// WiFi 配置 (WiFi Configuration)
// 请在此处填写您的 WiFi 信息
// ============================================================================
const char* WIFI_SSID     = "SCF-XIAOMI";     // WiFi 名称 (SSID)
const char* WIFI_PASSWORD = "scf888888";     // WiFi 密码 (Password)

// 后端服务器配置 (Backend Server Configuration)
// 服务器地址在 network_config.h 中定义 (SERVER_HOST, SERVER_PORT)

// WiFi 状态
bool wifi_connected = false;

// ============================================================================
// 引脚定义 - XIAO ESP32-C3 官方I2C引脚
// D4 = GPIO6 = SDA (绿色IIC标记)
// D5 = GPIO7 = SCL (绿色IIC标记)
// ============================================================================
#define I2C_SDA_PIN     6       // XIAO ESP32-C3 D4 (GPIO6) -> MPU6050 SDA
#define I2C_SCL_PIN     7       // XIAO ESP32-C3 D5 (GPIO7) -> MPU6050 SCL
#define MPU6050_INT_PIN 5       // XIAO ESP32-C3 D3 (GPIO5) -> MPU6050 INT (中断/唤醒)

// I2C通信参数
// 调试时使用较低速度，确认通信正常后可改为400000
#define I2C_CLOCK_SPEED 100000  // I2C时钟频率: 100kHz (Standard Mode)

// ============================================================================
// MPU6050 I2C地址
// ============================================================================
#define MPU6050_ADDR    0x68    // AD0引脚接地时的I2C地址

// ============================================================================
// MPU6050 寄存器地址定义
// 参考文档: MPU-6000/MPU-6050 Register Map (RM-MPU-6000A-00)
// ============================================================================

// 采样率和配置寄存器
#define REG_SMPLRT_DIV      0x19    // 采样率分频器
#define REG_CONFIG          0x1A    // 配置寄存器 (DLPF数字低通滤波器)
#define REG_GYRO_CONFIG     0x1B    // 陀螺仪配置 (量程选择)
#define REG_ACCEL_CONFIG    0x1C    // 加速度计配置 (量程选择)

// 中断相关寄存器
#define REG_INT_PIN_CFG     0x37    // 中断引脚配置
#define REG_INT_ENABLE      0x38    // 中断使能
#define REG_INT_STATUS      0x3A    // 中断状态

// 传感器数据寄存器 (每个轴2字节，高字节在前)
#define REG_ACCEL_XOUT_H    0x3B    // 加速度计X轴高字节
#define REG_ACCEL_XOUT_L    0x3C    // 加速度计X轴低字节
#define REG_ACCEL_YOUT_H    0x3D    // 加速度计Y轴高字节
#define REG_ACCEL_YOUT_L    0x3E    // 加速度计Y轴低字节
#define REG_ACCEL_ZOUT_H    0x3F    // 加速度计Z轴高字节
#define REG_ACCEL_ZOUT_L    0x40    // 加速度计Z轴低字节
#define REG_TEMP_OUT_H      0x41    // 温度高字节
#define REG_TEMP_OUT_L      0x42    // 温度低字节
#define REG_GYRO_XOUT_H     0x43    // 陀螺仪X轴高字节
#define REG_GYRO_XOUT_L     0x44    // 陀螺仪X轴低字节
#define REG_GYRO_YOUT_H     0x45    // 陀螺仪Y轴高字节
#define REG_GYRO_YOUT_L     0x46    // 陀螺仪Y轴低字节
#define REG_GYRO_ZOUT_H     0x47    // 陀螺仪Z轴高字节
#define REG_GYRO_ZOUT_L     0x48    // 陀螺仪Z轴低字节

// 电源管理寄存器
#define REG_PWR_MGMT_1      0x6B    // 电源管理1 (复位、睡眠、时钟源)
#define REG_PWR_MGMT_2      0x6C    // 电源管理2 (低功耗模式)

// 芯片ID寄存器
#define REG_WHO_AM_I        0x75    // 芯片ID寄存器，应返回0x68

// ============================================================================
// PWR_MGMT_1 寄存器位定义
// ============================================================================
#define PWR_MGMT_1_RESET    0x80    // Bit7: 设备复位
#define PWR_MGMT_1_SLEEP    0x40    // Bit6: 睡眠模式
#define PWR_MGMT_1_CYCLE    0x20    // Bit5: 循环模式
#define PWR_MGMT_1_TEMP_DIS 0x08    // Bit3: 禁用温度传感器
// Bits 2:0: 时钟源选择
#define CLKSEL_INTERNAL     0x00    // 内部8MHz振荡器
#define CLKSEL_PLL_X        0x01    // PLL with X axis gyroscope reference
#define CLKSEL_PLL_Y        0x02    // PLL with Y axis gyroscope reference
#define CLKSEL_PLL_Z        0x03    // PLL with Z axis gyroscope reference

// ============================================================================
// 量程配置值
// ============================================================================
// 陀螺仪量程 (GYRO_CONFIG寄存器 Bits 4:3)
#define GYRO_FS_250         0x00    // ±250 °/s  (灵敏度: 131 LSB/°/s)
#define GYRO_FS_500         0x08    // ±500 °/s  (灵敏度: 65.5 LSB/°/s)
#define GYRO_FS_1000        0x10    // ±1000 °/s (灵敏度: 32.8 LSB/°/s)
#define GYRO_FS_2000        0x18    // ±2000 °/s (灵敏度: 16.4 LSB/°/s)

// 加速度计量程 (ACCEL_CONFIG寄存器 Bits 4:3)
#define ACCEL_FS_2G         0x00    // ±2g  (灵敏度: 16384 LSB/g)
#define ACCEL_FS_4G         0x08    // ±4g  (灵敏度: 8192 LSB/g)
#define ACCEL_FS_8G         0x10    // ±8g  (灵敏度: 4096 LSB/g)
#define ACCEL_FS_16G        0x18    // ±16g (灵敏度: 2048 LSB/g)

// ============================================================================
// 灵敏度系数 (用于将原始值转换为物理单位)
// ============================================================================
#define ACCEL_SENSITIVITY_2G    16384.0f    // LSB/g
#define GYRO_SENSITIVITY_250    131.0f      // LSB/(°/s)

// ============================================================================
// 全局变量
// ============================================================================
bool mpu6050_initialized = false;   // MPU6050初始化状态标志
bool i2c_initialized = false;       // I2C总线初始化状态
bool streaming_mode = false;        // 连续数据输出模式
bool tremor_mode = false;           // 震颤检测模式
unsigned long lastTremorAnalysis = 0;   // 上次震颤分析时间
String inputBuffer = "";            // 串口输入缓冲区

// ============================================================================
// 函数声明
// ============================================================================
void printSeparator(void);
void printHeader(const char* title);
void printHelp(void);
void processCommand(String cmd);
bool initI2C(void);
int scanI2CBus(void);
bool verifyWhoAmI(void);
bool initMPU6050(void);
bool resetMPU6050(void);
uint8_t readRegister(uint8_t reg);
bool writeRegister(uint8_t reg, uint8_t value);
bool readSensorData(int16_t* accel, int16_t* gyro, int16_t* temp);
void printSensorData(int16_t* accel, int16_t* gyro, int16_t temp);
void readAndPrintOnce(void);
bool runHardwareTest(void);

// ============================================================================
// 辅助函数: 打印分隔线
// ============================================================================
void printSeparator(void) {
    Serial.println("------------------------------------------------------------");
}

// ============================================================================
// 辅助函数: 打印标题
// ============================================================================
void printHeader(const char* title) {
    Serial.println();
    printSeparator();
    Serial.print("  ");
    Serial.println(title);
    printSeparator();
}

// ============================================================================
// 打印帮助信息
// ============================================================================
void printHelp(void) {
    Serial.println();
    Serial.println("================ 可用命令 ================");
    Serial.println();
    Serial.println("  [基础命令]");
    Serial.println("  test     - 运行完整硬件测试");
    Serial.println("  scan     - 扫描I2C总线设备");
    Serial.println("  read     - 读取一次传感器数据");
    Serial.println("  stream   - 开始/停止连续数据输出");
    Serial.println("  reset    - 复位MPU6050传感器");
    Serial.println();
    Serial.println("  [震颤检测命令]");
    Serial.println("  tremor   - 开始/停止连续震颤检测");
    Serial.println("  analyze  - 执行一次震颤分析");
    Serial.println("  spectrum - 显示4-6Hz频谱数据");
    Serial.println("  stats    - 显示震颤检测统计");
    Serial.println();
    Serial.println("  [网络命令]");
    Serial.println("  wifi     - 显示WiFi连接状态");
    Serial.println("  connect  - 连接WiFi");
    Serial.println("  disconnect - 断开WiFi");
    Serial.println("  upload   - 显示上传状态/手动上传");
    Serial.println("  flush    - 强制上传所有缓存数据");
    Serial.println("  server   - 显示服务器配置");
    Serial.println();
    Serial.println("  [配置命令]");
    Serial.println("  cfgup    - 上传当前配置到云端");
    Serial.println("  update   - 从云端拉取最新配置");
    Serial.println("  config   - 显示当前运行时配置");
    Serial.println();
    Serial.println("  help     - 显示此帮助信息");
    Serial.println("==========================================");
    Serial.println();
    Serial.print("> ");  // 命令提示符
}

// ============================================================================
// 处理串口命令
// ============================================================================
void processCommand(String cmd) {
    // 转换为小写并去除空格
    cmd.trim();
    cmd.toLowerCase();

    if (cmd.length() == 0) {
        Serial.print("> ");
        return;
    }

    Serial.println();  // 换行

    if (cmd == "test") {
        // 运行完整硬件测试
        runHardwareTest();

    } else if (cmd == "scan") {
        // 仅扫描I2C总线
        if (!i2c_initialized) {
            initI2C();
            i2c_initialized = true;
        }
        scanI2CBus();

    } else if (cmd == "read") {
        // 读取一次传感器数据
        readAndPrintOnce();

    } else if (cmd == "stream") {
        // 切换连续输出模式
        streaming_mode = !streaming_mode;
        if (streaming_mode) {
            if (!mpu6050_initialized) {
                Serial.println("[警告] MPU6050未初始化，请先执行 test 命令");
                streaming_mode = false;
            } else {
                Serial.println("[Stream] 连续数据输出已开启 (输入 stream 停止)");
            }
        } else {
            Serial.println("[Stream] 连续数据输出已停止");
        }

    } else if (cmd == "reset") {
        // 复位MPU6050
        resetMPU6050();

    } else if (cmd == "tremor") {
        // 切换震颤检测模式
        if (!mpu6050_initialized) {
            Serial.println("[警告] MPU6050未初始化，请先执行 test 命令");
        } else if (!tremorIsInitialized()) {
            Serial.println("[警告] 震颤检测模块未初始化");
        } else {
            tremor_mode = !tremor_mode;
            if (tremor_mode) {
                streaming_mode = false;  // 关闭数据流模式
                tremorResetStats();      // 重置统计
                lastTremorAnalysis = 0;  // 立即开始第一次分析
                Serial.println();
                Serial.println("[Tremor] 震颤检测模式已开启");
                Serial.print("         分析间隔: ");
                Serial.print(TREMOR_ANALYSIS_INTERVAL_MS);
                Serial.println(" ms");
                Serial.println("         输入 tremor 停止");
                Serial.println();
            } else {
                Serial.println();
                Serial.println("[Tremor] 震颤检测模式已停止");
                tremorPrintStats();
            }
        }

    } else if (cmd == "analyze") {
        // 执行一次震颤分析
        if (!mpu6050_initialized) {
            Serial.println("[警告] MPU6050未初始化，请先执行 test 命令");
        } else if (!tremorIsInitialized()) {
            Serial.println("[警告] 震颤检测模块未初始化");
        } else {
            Serial.println();
            Serial.println("[Analyze] 正在采集数据，请保持静止或自然状态...");
            Serial.print("[Analyze] 采集中: ");

            // 显示进度条
            int lastProgress = 0;
            TremorResult result = tremorAnalyze();

            Serial.println(" 完成!");
            Serial.println();

            // 打印详细报告
            tremorPrintDetailedReport(result);
        }

    } else if (cmd == "spectrum") {
        // 显示频谱数据
        if (!mpu6050_initialized) {
            Serial.println("[警告] MPU6050未初始化，请先执行 test 命令");
        } else if (!tremorIsInitialized()) {
            Serial.println("[警告] 震颤检测模块未初始化");
        } else {
            // 先执行一次分析以获取频谱数据
            Serial.println();
            Serial.println("[Spectrum] 正在采集数据...");
            TremorResult result = tremorAnalyze();
            tremorPrintSpectrum();
        }

    } else if (cmd == "stats") {
        // 显示统计信息
        tremorPrintStats();

    // ========================================
    // 网络相关命令
    // ========================================
    } else if (cmd == "wifi") {
        // 显示WiFi状态
        wifiPrintStatus();

    } else if (cmd == "connect") {
        // 连接WiFi
        if (wifiIsConnected()) {
            Serial.println("[WiFi] 已连接，无需重新连接");
            wifiPrintStatus();
        } else {
            Serial.println("[WiFi] 正在连接...");
            if (wifiConnect(15000)) {
                Serial.println("[WiFi] 连接成功!");
                wifiPrintStatus();
                // 初始化HTTP客户端和上传器
                if (strlen(SERVER_HOST) > 0) {
                    httpInit(SERVER_HOST, SERVER_PORT, DEVICE_API_KEY);
                    uploaderInit();
                    Serial.println("[Network] 网络模块已初始化");
                }
            } else {
                Serial.println("[WiFi] 连接失败，请检查SSID和密码");
            }
        }

    } else if (cmd == "disconnect") {
        // 断开WiFi
        if (wifiIsConnected()) {
            wifiDisconnect();
            Serial.println("[WiFi] 已断开连接");
        } else {
            Serial.println("[WiFi] 当前未连接");
        }

    } else if (cmd == "upload") {
        // 显示上传状态
        uploaderPrintStatus();

    } else if (cmd == "flush") {
        // 强制上传所有缓存数据
        if (!wifiIsConnected()) {
            Serial.println("[Upload] WiFi未连接，无法上传");
        } else if (!httpIsConfigured()) {
            Serial.println("[Upload] 服务器未配置");
        } else {
            Serial.println("[Upload] 正在上传缓存数据...");
            int count = uploaderFlush();
            if (count > 0) {
                Serial.print("[Upload] 成功上传 ");
                Serial.print(count);
                Serial.println(" 条数据");
            } else {
                Serial.println("[Upload] 无数据需要上传或上传失败");
            }
        }

    } else if (cmd == "server") {
        // 显示服务器配置
        Serial.println();
        Serial.println("[Server] 服务器配置:");
        Serial.println("────────────────────────────────────");
        Serial.print("  地址: ");
        if (strlen(SERVER_HOST) > 0) {
            Serial.println(SERVER_HOST);
        } else {
            Serial.println("(未配置)");
        }
        Serial.print("  端口: ");
        Serial.println(SERVER_PORT);
        Serial.print("  设备ID: ");
        Serial.println(DEVICE_ID);
        Serial.print("  批量大小: ");
        Serial.println(BATCH_SIZE);
        Serial.print("  缓冲区大小: ");
        Serial.println(OFFLINE_BUFFER_SIZE);
        Serial.print("  HTTP已配置: ");
        Serial.println(httpIsConfigured() ? "是" : "否");
        Serial.println("────────────────────────────────────");

    // ========================================
    // 配置相关命令
    // ========================================
    } else if (cmd == "cfgup") {
        // 上传当前配置到云端
        if (!wifiIsConnected()) {
            Serial.println("[ConfigUp] 错误: WiFi 未连接");
            Serial.println("           请先执行 connect 命令连接WiFi");
        } else if (!httpIsConfigured()) {
            Serial.println("[ConfigUp] 错误: 服务器未配置");
        } else {
            ConfigSyncStatus status = configSyncUploadToCloud();

            if (status == SYNC_SUCCESS) {
                Serial.println("[ConfigUp] 配置上传完成!");
            } else {
                Serial.print("[ConfigUp] 上传失败: ");
                Serial.println(configSyncGetStatusLabel(status));
            }
        }

    } else if (cmd == "update") {
        // 从云端拉取最新配置
        if (!wifiIsConnected()) {
            Serial.println("[Update] 错误: WiFi 未连接");
            Serial.println("         请先执行 connect 命令连接WiFi");
        } else if (!httpIsConfigured()) {
            Serial.println("[Update] 错误: 服务器未配置");
        } else {
            Serial.println("[Update] 正在从云端拉取配置...");
            ConfigSyncStatus status = configSyncFromCloud();

            if (status == SYNC_SUCCESS) {
                Serial.println("[Update] 配置已更新，新参数立即生效!");
            } else if (status == SYNC_NO_UPDATE) {
                Serial.println("[Update] 配置已是最新版本");
            } else {
                Serial.print("[Update] 同步失败: ");
                Serial.println(configSyncGetStatusLabel(status));
            }
        }

    } else if (cmd == "config") {
        // 显示当前运行时配置
        tremorConfigPrint();

    } else if (cmd == "help" || cmd == "?") {
        // 显示帮助
        printHelp();
        return;  // 不再打印提示符，因为printHelp已经打印了

    } else {
        Serial.print("[错误] 未知命令: ");
        Serial.println(cmd);
        Serial.println("输入 help 查看可用命令");
    }

    Serial.println();
    Serial.print("> ");  // 打印命令提示符
}

// ============================================================================
// I2C初始化函数
// 功能: 初始化I2C总线，配置SDA/SCL引脚和通信速率
// 返回: true=成功, false=失败
// ============================================================================
bool initI2C(void) {
    Serial.println("[I2C] 正在初始化I2C总线...");
    Serial.print("      SDA引脚: GPIO");
    Serial.println(I2C_SDA_PIN);
    Serial.print("      SCL引脚: GPIO");
    Serial.println(I2C_SCL_PIN);
    Serial.print("      时钟频率: ");
    Serial.print(I2C_CLOCK_SPEED / 1000);
    Serial.println(" kHz");

    // 初始化I2C，指定SDA和SCL引脚
    // Wire.begin(SDA, SCL) 是ESP32特有的API
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);

    // 设置I2C时钟频率
    Wire.setClock(I2C_CLOCK_SPEED);

    // 等待I2C总线稳定
    delay(10);

    Serial.println("[I2C] I2C总线初始化完成");
    i2c_initialized = true;
    return true;
}

// ============================================================================
// I2C总线扫描函数
// 功能: 扫描I2C总线上的所有设备地址(0x01-0x7F)
// 返回: 发现的设备数量
// ============================================================================
int scanI2CBus(void) {
    Serial.println("[I2C] 正在扫描I2C总线...");
    Serial.println("      扫描地址范围: 0x01 - 0x7F");

    int deviceCount = 0;
    bool foundMPU6050 = false;

    // 扫描所有有效的I2C地址
    for (uint8_t addr = 1; addr < 127; addr++) {
        Wire.beginTransmission(addr);
        uint8_t error = Wire.endTransmission();
        delay(5);  // 给设备一点响应时间

        // error = 0 表示设备响应了ACK
        if (error == 0) {
            deviceCount++;
            Serial.print("      发现设备: 0x");
            if (addr < 16) Serial.print("0");
            Serial.print(addr, HEX);

            // 检查是否是MPU6050
            if (addr == MPU6050_ADDR) {
                Serial.print(" <-- MPU6050 (预期地址)");
                foundMPU6050 = true;
            } else if (addr == 0x69) {
                Serial.print(" <-- 可能是MPU6050 (AD0=HIGH)");
            }
            Serial.println();
        }
    }

    Serial.print("[I2C] 扫描完成，共发现 ");
    Serial.print(deviceCount);
    Serial.println(" 个设备");

    // 如果没有找到MPU6050，输出诊断建议
    if (!foundMPU6050 && deviceCount == 0) {
        Serial.println();
        Serial.println("[警告] 未发现任何I2C设备！请检查:");
        Serial.println("       1. SDA/SCL连线是否正确 (D7->SDA, D6->SCL)");
        Serial.println("       2. 4.7kΩ上拉电阻是否已焊接");
        Serial.println("       3. MPU6050电源是否正常 (VDD和VLOGIC接3.3V)");
        Serial.println("       4. 焊接点是否有虚焊");
    } else if (!foundMPU6050) {
        Serial.println();
        Serial.println("[警告] 未在0x68地址发现MPU6050！");
        Serial.println("       如果在0x69发现设备，请检查AD0引脚是否意外接高");
    }

    return deviceCount;
}

// ============================================================================
// 读取单个寄存器
// 参数: reg - 寄存器地址
// 返回: 寄存器值
// ============================================================================
uint8_t readRegister(uint8_t reg) {
    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(reg);                        // 发送寄存器地址
    Wire.endTransmission(false);            // 重复启动，不释放总线

    Wire.requestFrom(MPU6050_ADDR, 1);      // 请求1字节数据

    if (Wire.available()) {
        return Wire.read();
    }
    return 0xFF;                            // 读取失败返回0xFF
}

// ============================================================================
// 写入单个寄存器
// 参数: reg - 寄存器地址, value - 要写入的值
// 返回: true=成功, false=失败
// ============================================================================
bool writeRegister(uint8_t reg, uint8_t value) {
    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(reg);                        // 发送寄存器地址
    Wire.write(value);                      // 发送数据
    uint8_t error = Wire.endTransmission();

    return (error == 0);
}

// ============================================================================
// WHO_AM_I验证函数
// 功能: 读取WHO_AM_I寄存器(0x75)验证芯片身份
// 返回: true=验证通过, false=验证失败
// ============================================================================
bool verifyWhoAmI(void) {
    Serial.println("[MPU6050] 正在验证芯片身份 (WHO_AM_I)...");

    // 读取WHO_AM_I寄存器
    uint8_t whoami = readRegister(REG_WHO_AM_I);

    Serial.print("          WHO_AM_I寄存器值: 0x");
    if (whoami < 16) Serial.print("0");
    Serial.print(whoami, HEX);

    // MPU6050的WHO_AM_I返回0x68，MPU6500返回0x70
    // 两者寄存器兼容，都可以使用
    if (whoami == 0x68) {
        Serial.println(" (MPU6050)");
        Serial.println("[MPU6050] 芯片身份验证通过!");
        return true;
    } else if (whoami == 0x70) {
        Serial.println(" (MPU6500 - 兼容MPU6050)");
        Serial.println("[MPU6050] 芯片身份验证通过! (检测到MPU6500)");
        return true;
    } else if (whoami == 0x71) {
        Serial.println(" (MPU9250 - 兼容MPU6050)");
        Serial.println("[MPU6050] 芯片身份验证通过! (检测到MPU9250)");
        return true;
    } else if (whoami == 0xFF) {
        Serial.println(" (读取失败，可能I2C通信有问题)");
        return false;
    } else {
        Serial.print(" (未知芯片ID: 0x");
        Serial.print(whoami, HEX);
        Serial.println(")");
        return false;
    }
}

// ============================================================================
// MPU6050初始化函数
// 功能: 复位并配置MPU6050传感器
// 返回: true=成功, false=失败
// ============================================================================
bool initMPU6050(void) {
    Serial.println("[MPU6050] 正在初始化传感器...");

    // ----------------------------------------
    // 步骤1: 设备复位
    // ----------------------------------------
    Serial.println("          步骤1: 复位设备...");
    if (!writeRegister(REG_PWR_MGMT_1, PWR_MGMT_1_RESET)) {
        Serial.println("          [错误] 复位命令写入失败!");
        return false;
    }

    // 等待复位完成 (数据手册建议等待100ms)
    delay(100);
    Serial.println("          复位完成，等待100ms");

    // ----------------------------------------
    // 步骤2: 唤醒设备并设置时钟源
    // ----------------------------------------
    Serial.println("          步骤2: 唤醒设备，选择PLL时钟源...");
    // 使用X轴陀螺仪PLL作为时钟源，精度更高
    if (!writeRegister(REG_PWR_MGMT_1, CLKSEL_PLL_X)) {
        Serial.println("          [错误] 唤醒命令写入失败!");
        return false;
    }
    delay(10);

    // 验证设备已唤醒
    uint8_t pwr_mgmt = readRegister(REG_PWR_MGMT_1);
    Serial.print("          PWR_MGMT_1 = 0x");
    Serial.print(pwr_mgmt, HEX);
    if (pwr_mgmt & PWR_MGMT_1_SLEEP) {
        Serial.println(" (仍在睡眠模式!)");
        return false;
    } else {
        Serial.println(" (设备已唤醒)");
    }

    // ----------------------------------------
    // 步骤3: 配置采样率
    // ----------------------------------------
    Serial.println("          步骤3: 配置采样率...");
    // 采样率 = 陀螺仪输出率 / (1 + SMPLRT_DIV)
    // 当DLPF启用时，陀螺仪输出率 = 1kHz
    // SMPLRT_DIV = 7 -> 采样率 = 1000 / (1+7) = 125Hz
    if (!writeRegister(REG_SMPLRT_DIV, 0x07)) {
        Serial.println("          [错误] 采样率配置失败!");
        return false;
    }
    Serial.println("          采样率: 125Hz");

    // ----------------------------------------
    // 步骤4: 配置数字低通滤波器 (DLPF)
    // ----------------------------------------
    Serial.println("          步骤4: 配置数字低通滤波器...");
    // CONFIG寄存器 Bits 2:0 选择DLPF带宽
    // 0x03 = 带宽44Hz，延迟4.9ms
    if (!writeRegister(REG_CONFIG, 0x03)) {
        Serial.println("          [错误] DLPF配置失败!");
        return false;
    }
    Serial.println("          DLPF带宽: 44Hz");

    // ----------------------------------------
    // 步骤5: 配置陀螺仪量程
    // ----------------------------------------
    Serial.println("          步骤5: 配置陀螺仪量程...");
    if (!writeRegister(REG_GYRO_CONFIG, GYRO_FS_250)) {
        Serial.println("          [错误] 陀螺仪配置失败!");
        return false;
    }
    Serial.println("          陀螺仪量程: ±250°/s");

    // ----------------------------------------
    // 步骤6: 配置加速度计量程
    // ----------------------------------------
    Serial.println("          步骤6: 配置加速度计量程...");
    if (!writeRegister(REG_ACCEL_CONFIG, ACCEL_FS_2G)) {
        Serial.println("          [错误] 加速度计配置失败!");
        return false;
    }
    Serial.println("          加速度计量程: ±2g");

    // ----------------------------------------
    // 验证配置
    // ----------------------------------------
    Serial.println("          验证配置...");
    uint8_t gyro_cfg = readRegister(REG_GYRO_CONFIG);
    uint8_t accel_cfg = readRegister(REG_ACCEL_CONFIG);
    Serial.print("          GYRO_CONFIG = 0x");
    Serial.println(gyro_cfg, HEX);
    Serial.print("          ACCEL_CONFIG = 0x");
    Serial.println(accel_cfg, HEX);

    Serial.println("[MPU6050] 传感器初始化完成!");
    mpu6050_initialized = true;
    return true;
}

// ============================================================================
// MPU6050复位函数
// 功能: 复位并重新初始化MPU6050
// 返回: true=成功, false=失败
// ============================================================================
bool resetMPU6050(void) {
    Serial.println("[MPU6050] 正在复位传感器...");

    // 确保I2C已初始化
    if (!i2c_initialized) {
        initI2C();
    }

    // 发送复位命令
    if (!writeRegister(REG_PWR_MGMT_1, PWR_MGMT_1_RESET)) {
        Serial.println("[错误] 复位命令发送失败!");
        return false;
    }

    delay(100);  // 等待复位完成
    mpu6050_initialized = false;

    Serial.println("[MPU6050] 复位完成");
    Serial.println("[提示] 请执行 test 命令重新初始化传感器");
    return true;
}

// ============================================================================
// 读取传感器数据
// 参数: accel[3] - 加速度计XYZ, gyro[3] - 陀螺仪XYZ, temp - 温度
// 返回: true=成功, false=失败
// ============================================================================
bool readSensorData(int16_t* accel, int16_t* gyro, int16_t* temp) {
    // 从0x3B开始连续读取14字节数据
    // 顺序: ACCEL_X, ACCEL_Y, ACCEL_Z, TEMP, GYRO_X, GYRO_Y, GYRO_Z
    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(REG_ACCEL_XOUT_H);           // 起始寄存器地址
    Wire.endTransmission(false);

    Wire.requestFrom(MPU6050_ADDR, 14);     // 请求14字节

    if (Wire.available() < 14) {
        return false;
    }

    // 读取加速度计数据 (高字节在前，大端格式)
    accel[0] = (Wire.read() << 8) | Wire.read();    // X轴
    accel[1] = (Wire.read() << 8) | Wire.read();    // Y轴
    accel[2] = (Wire.read() << 8) | Wire.read();    // Z轴

    // 读取温度数据
    *temp = (Wire.read() << 8) | Wire.read();

    // 读取陀螺仪数据
    gyro[0] = (Wire.read() << 8) | Wire.read();     // X轴
    gyro[1] = (Wire.read() << 8) | Wire.read();     // Y轴
    gyro[2] = (Wire.read() << 8) | Wire.read();     // Z轴

    return true;
}

// ============================================================================
// 打印传感器数据
// ============================================================================
void printSensorData(int16_t* accel, int16_t* gyro, int16_t temp) {
    // 计算物理值
    float ax = accel[0] / ACCEL_SENSITIVITY_2G;     // 单位: g
    float ay = accel[1] / ACCEL_SENSITIVITY_2G;
    float az = accel[2] / ACCEL_SENSITIVITY_2G;

    float gx = gyro[0] / GYRO_SENSITIVITY_250;      // 单位: °/s
    float gy = gyro[1] / GYRO_SENSITIVITY_250;
    float gz = gyro[2] / GYRO_SENSITIVITY_250;

    // 温度计算公式: Temperature = TEMP_OUT / 340 + 36.53
    float temperature = temp / 340.0f + 36.53f;     // 单位: °C

    Serial.println("------ 传感器数据 ------");

    // 加速度计
    Serial.println("加速度计 (Accelerometer):");
    Serial.print("  原始值: X=");
    Serial.print(accel[0]);
    Serial.print(" Y=");
    Serial.print(accel[1]);
    Serial.print(" Z=");
    Serial.println(accel[2]);
    Serial.print("  物理值: X=");
    Serial.print(ax, 3);
    Serial.print("g Y=");
    Serial.print(ay, 3);
    Serial.print("g Z=");
    Serial.print(az, 3);
    Serial.println("g");

    // 陀螺仪
    Serial.println("陀螺仪 (Gyroscope):");
    Serial.print("  原始值: X=");
    Serial.print(gyro[0]);
    Serial.print(" Y=");
    Serial.print(gyro[1]);
    Serial.print(" Z=");
    Serial.println(gyro[2]);
    Serial.print("  物理值: X=");
    Serial.print(gx, 2);
    Serial.print("°/s Y=");
    Serial.print(gy, 2);
    Serial.print("°/s Z=");
    Serial.print(gz, 2);
    Serial.println("°/s");

    // 温度
    Serial.print("温度: ");
    Serial.print(temperature, 1);
    Serial.println("°C");

    // 数据有效性检查
    Serial.println();
    Serial.print("数据检查: ");

    // 静止状态下，Z轴加速度应该接近1g
    if (az > 0.8 && az < 1.2) {
        Serial.println("加速度计数据看起来正常 (Z轴约1g)");
    } else if (az < 0.1 && az > -0.1) {
        Serial.println("[注意] Z轴加速度接近0，传感器可能是水平放置?");
    } else {
        Serial.println("[注意] 加速度计数据可能需要校准");
    }
}

// ============================================================================
// 读取并打印一次传感器数据
// ============================================================================
void readAndPrintOnce(void) {
    if (!mpu6050_initialized) {
        Serial.println("[警告] MPU6050未初始化，请先执行 test 命令");
        return;
    }

    int16_t accel[3], gyro[3], temp;
    if (readSensorData(accel, gyro, &temp)) {
        printSensorData(accel, gyro, temp);
    } else {
        Serial.println("[错误] 数据读取失败!");
    }
}

// ============================================================================
// 综合硬件测试函数
// 返回: true=所有测试通过, false=存在问题
// ============================================================================
bool runHardwareTest(void) {
    bool allTestsPassed = true;

    printHeader("MPU6050 硬件连接测试");

    Serial.println("测试环境:");
    Serial.println("  MCU: Seeed XIAO ESP32-C3");
    Serial.println("  传感器: MPU6050");
    Serial.print("  I2C地址: 0x");
    Serial.println(MPU6050_ADDR, HEX);
    Serial.println();

    // ----------------------------------------
    // 测试1: I2C总线初始化
    // ----------------------------------------
    printHeader("测试1: I2C总线初始化");
    if (initI2C()) {
        Serial.println("[通过] I2C总线初始化成功");
    } else {
        Serial.println("[失败] I2C总线初始化失败");
        allTestsPassed = false;
    }

    // ----------------------------------------
    // 测试2: I2C设备扫描
    // ----------------------------------------
    printHeader("测试2: I2C设备扫描");
    int deviceCount = scanI2CBus();
    if (deviceCount > 0) {
        Serial.println("[通过] 发现I2C设备");
    } else {
        Serial.println("[失败] 未发现任何I2C设备");
        allTestsPassed = false;
        // 如果没有发现设备，后续测试无意义
        return false;
    }

    // ----------------------------------------
    // 测试3: WHO_AM_I验证
    // ----------------------------------------
    printHeader("测试3: WHO_AM_I芯片身份验证");
    if (verifyWhoAmI()) {
        Serial.println("[通过] MPU6050芯片身份确认");
    } else {
        Serial.println("[失败] 无法确认MPU6050芯片身份");
        allTestsPassed = false;
        return false;
    }

    // ----------------------------------------
    // 测试4: MPU6050初始化
    // ----------------------------------------
    printHeader("测试4: MPU6050初始化配置");
    if (initMPU6050()) {
        Serial.println("[通过] MPU6050初始化成功");
    } else {
        Serial.println("[失败] MPU6050初始化失败");
        allTestsPassed = false;
        return false;
    }

    // ----------------------------------------
    // 测试5: 传感器数据读取
    // ----------------------------------------
    printHeader("测试5: 传感器数据读取");
    int16_t accel[3], gyro[3], temp;

    // 等待数据稳定
    delay(100);

    if (readSensorData(accel, gyro, &temp)) {
        Serial.println("[通过] 传感器数据读取成功");
        Serial.println();
        printSensorData(accel, gyro, temp);
    } else {
        Serial.println("[失败] 传感器数据读取失败");
        allTestsPassed = false;
    }

    // ----------------------------------------
    // 测试结果汇总
    // ----------------------------------------
    printHeader("测试结果汇总");
    if (allTestsPassed) {
        Serial.println("============================================");
        Serial.println("       所有测试通过! 硬件连接正常!           ");
        Serial.println("============================================");
        Serial.println();
        Serial.println("你的MPU6050传感器已准备就绪，可以开始开发姿态检测功能。");
    } else {
        Serial.println("============================================");
        Serial.println("     部分测试未通过，请检查硬件连接!         ");
        Serial.println("============================================");
        Serial.println();
        Serial.println("排查建议:");
        Serial.println("  1. 检查焊接点是否有虚焊");
        Serial.println("  2. 使用万用表测量电压");
        Serial.println("  3. 检查I2C上拉电阻");
    }

    return allTestsPassed;
}

// ============================================================================
// 传感器数据读取适配器 (供震颤检测模块使用)
// ============================================================================
bool sensorReadAdapter(int16_t* accel, int16_t* gyro, int16_t* temp) {
    return readSensorData(accel, gyro, temp);
}

// ============================================================================
// Arduino setup() 函数
// 在程序启动时执行一次
// ============================================================================
void setup() {
    // 初始化串口通信
    Serial.begin(115200);

    // 等待串口连接 (USB-CDC需要)
    delay(2000);

    // 打印启动信息
    Serial.println();
    Serial.println("============================================================");
    Serial.println("    帕金森震颤监测手环 - Tremor Guard");
    Serial.println("    Hardware: Seeed XIAO ESP32-C3 + MPU6050");
    Serial.println("    Version: 1.1.0 (含FFT震颤检测 + 网络上传)");
    Serial.println("============================================================");
    Serial.println();

    // 初始化震颤检测模块
    tremorInit();
    tremorSetSensorCallback(sensorReadAdapter);

    // 初始化配置同步模块
    configSyncInit();

    // ----------------------------------------
    // 网络初始化 (WiFi + HTTP + Uploader)
    // ----------------------------------------
    Serial.println("[Network] 正在初始化网络模块...");

    // 初始化WiFi管理器
    wifiInit(WIFI_SSID, WIFI_PASSWORD);

    // 尝试连接WiFi
    Serial.print("[WiFi] 正在连接到: ");
    Serial.println(WIFI_SSID);

    if (wifiConnect(15000)) {
        wifi_connected = true;
        Serial.print("[WiFi] 连接成功! IP: ");
        Serial.println(wifiGetIP());
        Serial.print("[WiFi] 信号强度: ");
        Serial.print(wifiGetRSSI());
        Serial.println(" dBm");

        // 初始化HTTP客户端
        if (strlen(SERVER_HOST) > 0) {
            httpInit(SERVER_HOST, SERVER_PORT, DEVICE_API_KEY);
            Serial.print("[HTTP] 服务器: ");
            Serial.print(SERVER_HOST);
            Serial.print(":");
            Serial.println(SERVER_PORT);

            // 初始化数据上传器
            uploaderInit();
            Serial.println("[Uploader] 数据上传模块已初始化");
        } else {
            Serial.println("[HTTP] 警告: 服务器地址未配置");
            Serial.println("       请在代码中设置 SERVER_HOST");
        }
    } else {
        wifi_connected = false;
        Serial.println("[WiFi] 连接失败，将离线运行");
        Serial.println("       数据将缓存到本地，WiFi恢复后自动上传");
        Serial.println("       输入 connect 手动重试连接");
    }

    Serial.println();
    Serial.println("程序已启动，等待命令...");
    Serial.println("输入 test 开始硬件测试，输入 help 查看所有命令");
    Serial.println();
    Serial.print("> ");  // 命令提示符
}

// ============================================================================
// Arduino loop() 函数
// 主循环，持续执行
// ============================================================================
void loop() {
    // ----------------------------------------
    // 处理串口输入命令
    // ----------------------------------------
    while (Serial.available()) {
        char c = Serial.read();

        // 回显字符
        Serial.print(c);

        if (c == '\n' || c == '\r') {
            // 收到换行符，处理命令
            if (inputBuffer.length() > 0) {
                processCommand(inputBuffer);
                inputBuffer = "";  // 清空缓冲区
            }
        } else if (c == '\b' || c == 127) {
            // 处理退格键
            if (inputBuffer.length() > 0) {
                inputBuffer.remove(inputBuffer.length() - 1);
                Serial.print(" \b");  // 清除字符
            }
        } else {
            // 添加字符到缓冲区
            inputBuffer += c;
        }
    }

    // ----------------------------------------
    // 连续数据输出模式
    // ----------------------------------------
    if (streaming_mode && mpu6050_initialized) {
        int16_t accel[3], gyro[3], temp;

        if (readSensorData(accel, gyro, &temp)) {
            // 简洁格式输出，便于绘图或分析
            Serial.print("A:");
            Serial.print(accel[0]); Serial.print(",");
            Serial.print(accel[1]); Serial.print(",");
            Serial.print(accel[2]);
            Serial.print(" G:");
            Serial.print(gyro[0]); Serial.print(",");
            Serial.print(gyro[1]); Serial.print(",");
            Serial.print(gyro[2]);
            Serial.print(" T:");
            Serial.println(temp);
        }

        delay(100);  // 10Hz输出频率
    }

    // ----------------------------------------
    // 震颤检测模式
    // ----------------------------------------
    if (tremor_mode && mpu6050_initialized && tremorIsInitialized()) {
        unsigned long currentTime = millis();

        // 检查是否到达分析间隔
        if (currentTime - lastTremorAnalysis >= TREMOR_ANALYSIS_INTERVAL_MS) {
            lastTremorAnalysis = currentTime;

            // 执行震颤分析
            TremorResult result = tremorAnalyze();

            // 使用简洁格式输出
            tremorPrintSimpleResult(result);

            // 将数据加入上传队列 (无论是否检测到震颤)
            if (UPLOAD_ALL_RESULTS || result.detected) {
                UploadStatus uploadStatus = uploaderAddData(result);

#ifdef NETWORK_DEBUG_ENABLED
                if (uploadStatus == UPLOAD_QUEUED) {
                    Serial.print("[Upload] 数据已加入队列 (");
                    Serial.print(uploaderGetQueueCount());
                    Serial.println(")");
                }
#endif
            }
        }
    }

    // ----------------------------------------
    // 网络处理 (每次循环执行)
    // ----------------------------------------
    // WiFi 自动重连
    wifiAutoReconnect();

    // 处理数据上传 (检查是否需要批量上传)
    uploaderProcess();

    // 心跳检查
    uploaderHeartbeatCheck();
}
