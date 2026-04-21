/**
 * ============================================================
 * tremor_detection.h
 * 震颤检测模块头文件 / Tremor Detection Module Header
 * ============================================================
 *
 * 项目: 帕金森震颤监测手环 (Tremor Guard)
 * 功能: 声明震颤检测相关的数据结构和函数接口
 *
 * ============================================================
 */

#ifndef TREMOR_DETECTION_H
#define TREMOR_DETECTION_H

#include <Arduino.h>
#include "tremor_config.h"

// ============================================================
// 数据结构定义 (Data Structure Definitions)
// ============================================================

/**
 * 频谱分析结果 / Spectrum Analysis Result
 * 存储 FFT 分析后的频谱特征
 */
struct SpectrumResult {
    float peakFrequency;    // 峰值频率 (Hz) / Peak frequency
    float peakPower;        // 峰值功率 / Peak power
    float bandPower;        // 4-6Hz 频段总功率 / Total power in 4-6Hz band
    float totalPower;       // 全频段总功率 / Total power across all frequencies
    float avgPower;         // 平均功率 / Average power
    int peakBin;            // 峰值对应的 FFT bin 索引 / Peak FFT bin index
};

/**
 * 震颤检测结果 / Tremor Detection Result
 * 完整的震颤分析结果，包含是否检测到震颤、频率、幅度、严重度等
 */
struct TremorResult {
    bool detected;              // 是否检测到震颤 / Tremor detected flag
    bool valid;                 // 测试是否有效 (RMS在有效范围内) / Test validity
    bool outOfRange;            // RMS是否超出上限 / RMS exceeded upper limit
    float frequency;            // 主频 (Hz) / Dominant frequency
    float amplitude;            // 幅度 (g) / Amplitude in g
    float rmsAmplitude;         // RMS 幅度 (g) / RMS amplitude in g
    float power;                // 功率 / Power
    float peakRatio;            // 峰值与平均功率比值 / Peak to average ratio
    int severity;               // 严重度 0-4 / Severity level 0-4
    const char* severityLabel;  // 严重度标签 / Severity label string
    unsigned long timestamp;    // 时间戳 (ms) / Timestamp in milliseconds
    SpectrumResult spectrum;    // 频谱分析详情 / Spectrum analysis details
};

/**
 * 震颤统计信息 / Tremor Statistics
 * 用于连续监测模式下的统计
 */
struct TremorStats {
    unsigned long totalAnalyses;    // 总分析次数 / Total analysis count
    unsigned long tremorCount;      // 检测到震颤次数 / Tremor detection count
    float avgFrequency;             // 平均频率 / Average frequency
    float avgAmplitude;             // 平均幅度 / Average amplitude
    int maxSeverity;                // 最高严重度 / Maximum severity
    unsigned long startTime;        // 开始时间 / Start time
};

// ============================================================
// 传感器数据读取函数类型定义
// Sensor Data Read Function Type Definition
// ============================================================

/**
 * 传感器数据读取回调函数类型
 * 用于从 MPU6050 读取原始数据
 *
 * @param accel 加速度数据数组 [x, y, z] (原始 LSB 值)
 * @param gyro  陀螺仪数据数组 [x, y, z] (原始 LSB 值)
 * @param temp  温度数据指针 (原始 LSB 值)
 * @return true 如果读取成功, false 如果失败
 */
typedef bool (*SensorReadCallback)(int16_t* accel, int16_t* gyro, int16_t* temp);

// ============================================================
// 函数声明 (Function Declarations)
// ============================================================

// ------------------------------------------------------------
// 初始化与配置 (Initialization & Configuration)
// ------------------------------------------------------------

/**
 * 初始化震颤检测模块
 * Initialize tremor detection module
 */
void tremorInit(void);

/**
 * 设置传感器数据读取回调函数
 * Set sensor data read callback function
 *
 * @param callback 读取传感器数据的函数指针
 */
void tremorSetSensorCallback(SensorReadCallback callback);

/**
 * 重置震颤统计信息
 * Reset tremor statistics
 */
void tremorResetStats(void);

// ------------------------------------------------------------
// 核心分析功能 (Core Analysis Functions)
// ------------------------------------------------------------

/**
 * 执行一次完整的震颤检测分析
 * Perform a complete tremor detection analysis
 *
 * 此函数会:
 * 1. 采集 FFT_SAMPLES 个加速度样本 (约2秒)
 * 2. 计算向量幅度
 * 3. 去除直流分量
 * 4. 应用窗函数
 * 5. 执行 FFT
 * 6. 在 4-6Hz 范围内检测峰值
 * 7. 评估震颤严重度
 *
 * @return TremorResult 震颤检测结果
 */
TremorResult tremorAnalyze(void);

/**
 * 仅获取频谱分析结果 (不进行完整检测)
 * Get spectrum analysis result only
 *
 * @return SpectrumResult 频谱分析结果
 */
SpectrumResult tremorGetSpectrum(void);

/**
 * 获取当前统计信息
 * Get current statistics
 *
 * @return TremorStats 统计信息
 */
TremorStats tremorGetStats(void);

// ------------------------------------------------------------
// 严重度评估 (Severity Assessment)
// ------------------------------------------------------------

/**
 * 根据幅度计算严重度等级
 * Calculate severity level from amplitude
 *
 * 严重度等级 (基于实测校准):
 * - 0: 无震颤 (None)      < 2.5g
 * - 1: 轻度 (Mild)        2.5-3.0g
 * - 2: 中轻度 (Mild-Mod)  3.0-3.5g
 * - 3: 中度 (Moderate)    3.5-4.0g
 * - 4: 重度 (Severe)      > 4.0g
 *
 * @param amplitude 震颤幅度 (g)
 * @return int 严重度等级 0-4
 */
int tremorCalculateSeverity(float amplitude);

/**
 * 获取严重度标签字符串
 * Get severity label string
 *
 * @param severity 严重度等级 0-4
 * @return const char* 严重度标签 (中文)
 */
const char* tremorGetSeverityLabel(int severity);

/**
 * 获取严重度英文标签
 * Get severity label in English
 *
 * @param severity 严重度等级 0-4
 * @return const char* 严重度英文标签
 */
const char* tremorGetSeverityLabelEN(int severity);

// ------------------------------------------------------------
// 输出与显示 (Output & Display)
// ------------------------------------------------------------

/**
 * 打印详细震颤分析报告
 * Print detailed tremor analysis report
 *
 * @param result 震颤检测结果
 */
void tremorPrintDetailedReport(const TremorResult& result);

/**
 * 打印简洁结果 (用于连续监测模式)
 * Print simple result (for continuous monitoring mode)
 *
 * @param result 震颤检测结果
 */
void tremorPrintSimpleResult(const TremorResult& result);

/**
 * 打印频谱数据 (用于调试)
 * Print spectrum data (for debugging)
 */
void tremorPrintSpectrum(void);

/**
 * 打印统计摘要
 * Print statistics summary
 */
void tremorPrintStats(void);

// ------------------------------------------------------------
// 辅助功能 (Utility Functions)
// ------------------------------------------------------------

/**
 * 检查模块是否已初始化
 * Check if module is initialized
 *
 * @return bool true 如果已初始化
 */
bool tremorIsInitialized(void);

/**
 * 获取采集进度 (0-100)
 * Get data collection progress (0-100)
 *
 * @return int 进度百分比
 */
int tremorGetCollectionProgress(void);

/**
 * 将频率转换为 FFT bin 索引
 * Convert frequency to FFT bin index
 *
 * @param frequency 频率 (Hz)
 * @return int FFT bin 索引
 */
int tremorFreqToBin(float frequency);

/**
 * 将 FFT bin 索引转换为频率
 * Convert FFT bin index to frequency
 *
 * @param bin FFT bin 索引
 * @return float 频率 (Hz)
 */
float tremorBinToFreq(int bin);

#endif // TREMOR_DETECTION_H
