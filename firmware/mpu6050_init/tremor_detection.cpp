/**
 * ============================================================
 * tremor_detection.cpp
 * 震颤检测模块核心实现 / Tremor Detection Module Implementation
 * ============================================================
 *
 * 项目: 帕金森震颤监测手环 (Tremor Guard)
 * 功能: 实现基于 FFT 的帕金森震颤 (4-6Hz) 检测算法
 *
 * 算法流程:
 * 1. 采集加速度数据 (256样本 @ 125Hz ≈ 2秒)
 * 2. 计算向量幅度 √(x² + y² + z²)
 * 3. 去除直流分量 (减去平均值)
 * 4. 应用 Hamming 窗函数
 * 5. 执行快速傅里叶变换 (FFT)
 * 6. 在 4-6Hz 范围内检测峰值
 * 7. 评估震颤严重度 (0-4级)
 *
 * ============================================================
 */

#include "tremor_detection.h"
#include <arduinoFFT.h>
#include <math.h>

// ============================================================
// 内部变量 (Internal Variables)
// ============================================================

// FFT 数据缓冲区
static double vReal[FFT_SAMPLES];
static double vImag[FFT_SAMPLES];

// ArduinoFFT 对象
static ArduinoFFT<double> FFT = ArduinoFFT<double>(vReal, vImag, FFT_SAMPLES, SAMPLE_RATE);

// 传感器读取回调函数
static SensorReadCallback sensorReadCallback = nullptr;

// 模块状态
static bool moduleInitialized = false;
static int collectionProgress = 0;

// 最后一次频谱分析结果
static SpectrumResult lastSpectrum;

// 统计信息
static TremorStats stats = {0, 0, 0, 0, 0, 0};

// 严重度标签 (中文)
static const char* SEVERITY_LABELS_CN[] = {
    "无", "轻微", "轻度", "中度", "重度"
};

// 严重度标签 (英文)
static const char* SEVERITY_LABELS_EN[] = {
    "None", "Slight", "Mild", "Moderate", "Severe"
};

// 频率分辨率
static const float FREQ_RESOLUTION = (float)SAMPLE_RATE / FFT_SAMPLES;

// ============================================================
// 运行时配置 (Runtime Configuration)
// ============================================================

// 全局运行时配置变量 (使用默认值初始化)
TremorRuntimeConfig tremorConfig = {
    .rmsMin = TREMOR_RMS_MIN,                    // 2.5g
    .rmsMax = TREMOR_RMS_MAX,                    // 5.0g
    .powerThreshold = TREMOR_POWER_THRESHOLD,   // 0.5
    .freqMin = TREMOR_FREQ_MIN,                 // 4.0Hz
    .freqMax = TREMOR_FREQ_MAX,                 // 6.0Hz
    .severityThresholds = {
        SEVERITY_THRESHOLD_0,   // 2.5g
        SEVERITY_THRESHOLD_1,   // 3.0g
        SEVERITY_THRESHOLD_2,   // 3.5g
        SEVERITY_THRESHOLD_3    // 4.0g
    },
    .configVersion = 0
};

void tremorConfigInit(void) {
    // 使用编译时默认值初始化
    tremorConfig.rmsMin = TREMOR_RMS_MIN;
    tremorConfig.rmsMax = TREMOR_RMS_MAX;
    tremorConfig.powerThreshold = TREMOR_POWER_THRESHOLD;
    tremorConfig.freqMin = TREMOR_FREQ_MIN;
    tremorConfig.freqMax = TREMOR_FREQ_MAX;
    tremorConfig.severityThresholds[0] = SEVERITY_THRESHOLD_0;
    tremorConfig.severityThresholds[1] = SEVERITY_THRESHOLD_1;
    tremorConfig.severityThresholds[2] = SEVERITY_THRESHOLD_2;
    tremorConfig.severityThresholds[3] = SEVERITY_THRESHOLD_3;
    tremorConfig.configVersion = 0;

    Serial.println("[Config] 配置已初始化为默认值");
}

void tremorConfigPrint(void) {
    Serial.println();
    Serial.println("[Config] 当前运行时配置:");
    Serial.println("────────────────────────────────────");
    Serial.print("  版本: v");
    Serial.println(tremorConfig.configVersion);
    Serial.println();
    Serial.println("  检测阈值:");
    Serial.print("    RMS 下限: ");
    Serial.print(tremorConfig.rmsMin, 2);
    Serial.println(" g");
    Serial.print("    RMS 上限: ");
    Serial.print(tremorConfig.rmsMax, 2);
    Serial.println(" g");
    Serial.print("    功率阈值: ");
    Serial.println(tremorConfig.powerThreshold, 2);
    Serial.println();
    Serial.println("  频率范围:");
    Serial.print("    下限: ");
    Serial.print(tremorConfig.freqMin, 1);
    Serial.println(" Hz");
    Serial.print("    上限: ");
    Serial.print(tremorConfig.freqMax, 1);
    Serial.println(" Hz");
    Serial.println();
    Serial.println("  严重度阈值 (g):");
    Serial.print("    0级 (无): < ");
    Serial.println(tremorConfig.severityThresholds[0], 1);
    Serial.print("    1级 (轻微): ");
    Serial.print(tremorConfig.severityThresholds[0], 1);
    Serial.print(" - ");
    Serial.println(tremorConfig.severityThresholds[1], 1);
    Serial.print("    2级 (轻度): ");
    Serial.print(tremorConfig.severityThresholds[1], 1);
    Serial.print(" - ");
    Serial.println(tremorConfig.severityThresholds[2], 1);
    Serial.print("    3级 (中度): ");
    Serial.print(tremorConfig.severityThresholds[2], 1);
    Serial.print(" - ");
    Serial.println(tremorConfig.severityThresholds[3], 1);
    Serial.print("    4级 (重度): > ");
    Serial.println(tremorConfig.severityThresholds[3], 1);
    Serial.println("────────────────────────────────────");
}

bool tremorConfigUpdate(const TremorRuntimeConfig* newConfig) {
    if (newConfig == nullptr) {
        return false;
    }

    // 验证配置值的合理性
    if (newConfig->rmsMin <= 0 || newConfig->rmsMax <= newConfig->rmsMin) {
        Serial.println("[Config] 错误: RMS 范围无效");
        return false;
    }
    if (newConfig->freqMin <= 0 || newConfig->freqMax <= newConfig->freqMin) {
        Serial.println("[Config] 错误: 频率范围无效");
        return false;
    }
    if (newConfig->powerThreshold <= 0) {
        Serial.println("[Config] 错误: 功率阈值无效");
        return false;
    }

    // 更新配置
    tremorConfig = *newConfig;

    Serial.println("[Config] 配置已更新!");
    tremorConfigPrint();

    return true;
}

// ============================================================
// 内部函数声明 (Internal Function Declarations)
// ============================================================

static void collectSamples(void);
static void removeDC(void);
static void performFFTAnalysis(void);
static SpectrumResult analyzeSpectrum(void);
static bool detectTremorInSpectrum(const SpectrumResult& spectrum);

// ============================================================
// 初始化与配置 (Initialization & Configuration)
// ============================================================

void tremorInit(void) {
    // 清空 FFT 缓冲区
    memset(vReal, 0, sizeof(vReal));
    memset(vImag, 0, sizeof(vImag));

    // 清空频谱结果
    memset(&lastSpectrum, 0, sizeof(lastSpectrum));

    // 重置统计
    tremorResetStats();

    // 重置进度
    collectionProgress = 0;

    moduleInitialized = true;

    Serial.println("[Tremor] 震颤检测模块已初始化");
    Serial.print("[Tremor] FFT样本数: ");
    Serial.print(FFT_SAMPLES);
    Serial.print(", 采样率: ");
    Serial.print(SAMPLE_RATE);
    Serial.print("Hz, 频率分辨率: ");
    Serial.print(FREQ_RESOLUTION, 3);
    Serial.println("Hz");
}

void tremorSetSensorCallback(SensorReadCallback callback) {
    sensorReadCallback = callback;
}

void tremorResetStats(void) {
    stats.totalAnalyses = 0;
    stats.tremorCount = 0;
    stats.avgFrequency = 0;
    stats.avgAmplitude = 0;
    stats.maxSeverity = 0;
    stats.startTime = millis();
}

bool tremorIsInitialized(void) {
    return moduleInitialized && (sensorReadCallback != nullptr);
}

int tremorGetCollectionProgress(void) {
    return collectionProgress;
}

// ============================================================
// 数据采集 (Data Collection)
// ============================================================

static void collectSamples(void) {
    if (sensorReadCallback == nullptr) {
        Serial.println("[Tremor] 错误: 传感器回调未设置");
        return;
    }

    int16_t accel[3], gyro[3], temp;
    collectionProgress = 0;

    for (int i = 0; i < FFT_SAMPLES; i++) {
        // 读取传感器数据
        if (sensorReadCallback(accel, gyro, &temp)) {
            // 转换为 g 单位
            float ax = accel[0] / ACCEL_SENSITIVITY;
            float ay = accel[1] / ACCEL_SENSITIVITY;
            float az = accel[2] / ACCEL_SENSITIVITY;

            // 计算向量幅度 (合成加速度)
            vReal[i] = sqrt(ax * ax + ay * ay + az * az);
            vImag[i] = 0;
        } else {
            // 读取失败，使用0填充
            vReal[i] = 0;
            vImag[i] = 0;
        }

        // 更新进度
        collectionProgress = (i + 1) * 100 / FFT_SAMPLES;

        // 等待采样间隔
        delay(SAMPLE_INTERVAL_MS);
    }
}

// ============================================================
// 信号预处理 (Signal Preprocessing)
// ============================================================

static void removeDC(void) {
    // 计算平均值 (直流分量)
    double mean = 0;
    for (int i = 0; i < FFT_SAMPLES; i++) {
        mean += vReal[i];
    }
    mean /= FFT_SAMPLES;

    // 减去直流分量
    for (int i = 0; i < FFT_SAMPLES; i++) {
        vReal[i] -= mean;
    }

#ifdef TREMOR_DEBUG_ENABLED
    Serial.print("[Tremor Debug] 直流分量 (平均值): ");
    Serial.println(mean, 4);
#endif
}

// ============================================================
// FFT 分析 (FFT Analysis)
// ============================================================

static void performFFTAnalysis(void) {
    // 应用 Hamming 窗函数
    FFT.windowing(FFTWindow::Hamming, FFTDirection::Forward);

    // 执行 FFT
    FFT.compute(FFTDirection::Forward);

    // 转换为幅度谱
    FFT.complexToMagnitude();
}

static SpectrumResult analyzeSpectrum(void) {
    SpectrumResult result = {0, 0, 0, 0, 0, 0};

    // 计算目标频率范围的 bin 索引
    int startBin = (int)(TREMOR_FREQ_MIN / FREQ_RESOLUTION);
    int endBin = (int)(TREMOR_FREQ_MAX / FREQ_RESOLUTION);

    // 确保索引在有效范围内
    if (startBin < 1) startBin = 1;  // 跳过 DC 分量 (bin 0)
    if (endBin >= FFT_SAMPLES / 2) endBin = FFT_SAMPLES / 2 - 1;

    // 在 4-6Hz 范围内寻找峰值
    double maxPower = 0;
    int maxBin = startBin;
    double bandPower = 0;
    double totalPower = 0;

    // 计算总功率 (跳过 DC)
    for (int i = 1; i < FFT_SAMPLES / 2; i++) {
        totalPower += vReal[i];
    }

    // 计算 4-6Hz 频段功率和峰值
    for (int i = startBin; i <= endBin; i++) {
        bandPower += vReal[i];
        if (vReal[i] > maxPower) {
            maxPower = vReal[i];
            maxBin = i;
        }
    }

    // 填充结果
    result.peakFrequency = maxBin * FREQ_RESOLUTION;
    result.peakPower = maxPower;
    result.bandPower = bandPower;
    result.totalPower = totalPower;
    result.avgPower = totalPower / (FFT_SAMPLES / 2 - 1);
    result.peakBin = maxBin;

    // 保存最后的频谱结果
    lastSpectrum = result;

    return result;
}

// ============================================================
// 震颤检测 (Tremor Detection)
// ============================================================

// 用于存储检测条件结果 (供报告使用)
static bool lastPowerOK = false;
static bool lastFreqOK = false;
static bool lastRmsOK = false;
static float lastRmsValue = 0;

static bool detectTremorInSpectrum(const SpectrumResult& spectrum) {
    // 条件1: 频段功率超过阈值 (使用运行时配置)
    lastPowerOK = spectrum.bandPower > TREMOR_RT_POWER_THRESHOLD;

    // 条件2: 峰值频率在目标范围内 (使用运行时配置)
    lastFreqOK = (spectrum.peakFrequency >= TREMOR_RT_FREQ_MIN) &&
                 (spectrum.peakFrequency <= TREMOR_RT_FREQ_MAX);

#ifdef TREMOR_DEBUG_ENABLED
    Serial.println("[Tremor Debug] 检测条件:");
    Serial.print("  功率条件: ");
    Serial.print(lastPowerOK ? "满足" : "不满足");
    Serial.print(" (");
    Serial.print(spectrum.bandPower, 4);
    Serial.print(" > ");
    Serial.print(TREMOR_RT_POWER_THRESHOLD, 4);
    Serial.println(")");

    Serial.print("  频率条件: ");
    Serial.print(lastFreqOK ? "满足" : "不满足");
    Serial.print(" (");
    Serial.print(spectrum.peakFrequency, 2);
    Serial.println("Hz)");
#endif

    // 频谱条件: 功率 + 频率 (RMS 条件在 tremorAnalyze 中额外检查)
    return lastPowerOK && lastFreqOK;
}

TremorResult tremorAnalyze(void) {
    TremorResult result;
    memset(&result, 0, sizeof(result));
    result.severityLabel = SEVERITY_LABELS_CN[0];
    result.timestamp = millis();
    result.valid = true;       // 默认有效
    result.outOfRange = false; // 默认未超出范围

    // 检查初始化状态
    if (!tremorIsInitialized()) {
        Serial.println("[Tremor] 错误: 模块未正确初始化");
        result.valid = false;
        return result;
    }

    // 步骤1: 采集数据
    collectSamples();

    // 步骤2: 去除直流分量
    removeDC();

    // 步骤3: 执行 FFT 分析
    performFFTAnalysis();

    // 步骤4: 分析频谱
    SpectrumResult spectrum = analyzeSpectrum();
    result.spectrum = spectrum;

    // 步骤5: 初步检测震颤 (频谱条件)
    bool spectrumDetected = detectTremorInSpectrum(spectrum);

    // 无论是否检测到震颤，都填充基本数据 (用于诊断)
    result.frequency = spectrum.peakFrequency;
    result.power = spectrum.peakPower;

    // 计算峰值比
    if (spectrum.avgPower > 0) {
        result.peakRatio = spectrum.peakPower / spectrum.avgPower;
    }

    // 计算幅度 (使用频段功率估算)
    result.amplitude = spectrum.bandPower / (FFT_SAMPLES / 2);

    // 计算 RMS 幅度 (从原始数据)
    double rms = 0;
    for (int i = 0; i < FFT_SAMPLES; i++) {
        rms += vReal[i] * vReal[i];
    }
    result.rmsAmplitude = sqrt(rms / FFT_SAMPLES);

    // 步骤6: 检查 RMS 是否在有效范围内 (使用运行时配置)
    lastRmsValue = result.rmsAmplitude;

    // 检查上限 - 超过上限则测试无效
    if (result.rmsAmplitude > TREMOR_RT_RMS_MAX) {
        result.outOfRange = true;
        result.valid = false;
        result.detected = false;
        result.severity = 0;
        result.severityLabel = SEVERITY_LABELS_CN[0];
        stats.totalAnalyses++;  // 仍计入总次数
        return result;
    }

    // 检查下限 - 低于下限则无震颤 (使用运行时配置)
    lastRmsOK = result.rmsAmplitude >= TREMOR_RT_RMS_MIN;

    // 最终判断: 频谱条件 + RMS 在有效范围内
    result.detected = spectrumDetected && lastRmsOK;

    if (result.detected) {
        // 使用 RMS 幅度来评估严重度
        result.severity = tremorCalculateSeverity(result.rmsAmplitude);
        result.severityLabel = SEVERITY_LABELS_CN[result.severity];

        // 更新统计
        stats.tremorCount++;
        stats.avgFrequency = (stats.avgFrequency * (stats.tremorCount - 1) + result.frequency) / stats.tremorCount;
        stats.avgAmplitude = (stats.avgAmplitude * (stats.tremorCount - 1) + result.rmsAmplitude) / stats.tremorCount;
        if (result.severity > stats.maxSeverity) {
            stats.maxSeverity = result.severity;
        }
    }

    // 更新总分析次数
    stats.totalAnalyses++;

    return result;
}

SpectrumResult tremorGetSpectrum(void) {
    return lastSpectrum;
}

TremorStats tremorGetStats(void) {
    return stats;
}

// ============================================================
// 严重度评估 (Severity Assessment)
// ============================================================

int tremorCalculateSeverity(float amplitude) {
    // 使用运行时配置的严重度阈值
    if (amplitude < TREMOR_RT_SEVERITY_0) {
        return 0;  // 无震颤
    } else if (amplitude < TREMOR_RT_SEVERITY_1) {
        return 1;  // 轻微
    } else if (amplitude < TREMOR_RT_SEVERITY_2) {
        return 2;  // 轻度
    } else if (amplitude < TREMOR_RT_SEVERITY_3) {
        return 3;  // 中度
    } else {
        return 4;  // 重度
    }
}

const char* tremorGetSeverityLabel(int severity) {
    if (severity < 0) severity = 0;
    if (severity > 4) severity = 4;
    return SEVERITY_LABELS_CN[severity];
}

const char* tremorGetSeverityLabelEN(int severity) {
    if (severity < 0) severity = 0;
    if (severity > 4) severity = 4;
    return SEVERITY_LABELS_EN[severity];
}

// ============================================================
// 辅助函数 (Utility Functions)
// ============================================================

int tremorFreqToBin(float frequency) {
    return (int)(frequency / FREQ_RESOLUTION);
}

float tremorBinToFreq(int bin) {
    return bin * FREQ_RESOLUTION;
}

// ============================================================
// 输出与显示 (Output & Display)
// ============================================================

void tremorPrintDetailedReport(const TremorResult& result) {
    Serial.println();
    Serial.println("======================================================================");
    Serial.println("                     震颤分析详细报告                                ");
    Serial.println("                  Tremor Analysis Report                             ");
    Serial.println("======================================================================");
    Serial.println();

    // 检测状态
    if (result.outOfRange) {
        Serial.println("  检测状态: ⚠ 测试无效 - RMS超出上限 (Test Invalid - RMS Out of Range)");
        Serial.print("  RMS 幅度: ");
        Serial.print(result.rmsAmplitude, 2);
        Serial.print("g > ");
        Serial.print(TREMOR_RT_RMS_MAX, 1);
        Serial.println("g (上限)");
        Serial.println();
        Serial.println("  说明: 震动幅度超出有效检测范围，本次测试结果已抛弃。");
        Serial.println("======================================================================");
        return;
    } else if (result.detected) {
        Serial.println("  检测状态: ● 检测到震颤 (Tremor Detected)");
    } else {
        Serial.println("  检测状态: ○ 未检测到震颤 (No Tremor Detected)");
    }
    Serial.println();

    // 频率特征
    Serial.println("  ┌──────────────────────────────────────────────────────────────┐");
    Serial.println("  │ 频率特征 (Frequency Characteristics)                         │");
    Serial.print("  │   主频 (Dominant Frequency): ");
    Serial.print(result.frequency, 2);
    Serial.println(" Hz                          │");
    Serial.println("  │   频率范围: 4-6 Hz (帕金森特征范围)                          │");
    Serial.print("  │   峰值功率 (Peak Power): ");
    Serial.print(result.spectrum.peakPower, 4);
    Serial.println("                            │");
    Serial.print("  │   频段总功率 (Band Power): ");
    Serial.print(result.spectrum.bandPower, 4);
    Serial.println("                          │");
    Serial.println("  └──────────────────────────────────────────────────────────────┘");
    Serial.println();

    // 幅度特征
    Serial.println("  ┌──────────────────────────────────────────────────────────────┐");
    Serial.println("  │ 幅度特征 (Amplitude Characteristics)                         │");
    Serial.print("  │   震颤幅度 (Amplitude): ");
    Serial.print(result.amplitude, 4);
    Serial.println(" g                              │");
    Serial.print("  │   RMS 幅度 (RMS Amplitude): ");
    Serial.print(result.rmsAmplitude, 4);
    Serial.println(" g                          │");
    Serial.print("  │   峰值比 (Peak Ratio): ");
    Serial.print(result.peakRatio, 2);
    Serial.println("                                  │");
    Serial.println("  └──────────────────────────────────────────────────────────────┘");
    Serial.println();

    // 严重度评估
    Serial.println("  ┌──────────────────────────────────────────────────────────────┐");
    Serial.println("  │ 严重度评估 (Severity Assessment)                             │");
    Serial.print("  │   等级 (Level): ");
    Serial.print(result.severity);
    Serial.println(" / 4                                           │");
    Serial.print("  │   标签 (Label): ");
    Serial.print(result.severityLabel);
    Serial.print(" (");
    Serial.print(tremorGetSeverityLabelEN(result.severity));
    Serial.println(")                                   │");
    Serial.println("  │                                                              │");

    // 严重度条形图
    Serial.print("  │   ");
    Serial.print("[");
    int bars = result.severity * 5;  // 每级5格，共20格
    for (int i = 0; i < 20; i++) {
        if (i < bars) {
            Serial.print("█");
        } else {
            Serial.print("░");
        }
    }
    Serial.print("] ");
    Serial.print(result.severity * 25);
    Serial.println("%                        │");

    Serial.println("  │    无   轻微  轻度  中度  重度                               │");
    Serial.println("  └──────────────────────────────────────────────────────────────┘");
    Serial.println();

    // 时间信息
    Serial.print("  时间戳 (Timestamp): ");
    Serial.print(result.timestamp);
    Serial.println(" ms");

    Serial.print("  采样参数: ");
    Serial.print(FFT_SAMPLES);
    Serial.print(" samples @ ");
    Serial.print(SAMPLE_RATE);
    Serial.print("Hz (");
    Serial.print((float)FFT_SAMPLES / SAMPLE_RATE, 3);
    Serial.println("秒)");

    // 如果未检测到震颤，显示诊断信息
    if (!result.detected) {
        Serial.println();
        Serial.println("  ┌──────────────────────────────────────────────────────────────┐");
        Serial.println("  │ 诊断信息 (Diagnostic Info)                                   │");

        // 检查功率条件
        Serial.print("  │   频段功率: ");
        Serial.print(lastPowerOK ? "✓" : "✗");
        Serial.print(" ");
        Serial.print(result.spectrum.bandPower, 2);
        if (!lastPowerOK) {
            Serial.print(" < ");
            Serial.print(TREMOR_RT_POWER_THRESHOLD, 1);
        }
        Serial.println("                              │");

        // 检查频率条件
        Serial.print("  │   频率范围: ");
        Serial.print(lastFreqOK ? "✓" : "✗");
        Serial.print(" ");
        Serial.print(result.frequency, 2);
        Serial.print("Hz");
        if (!lastFreqOK) {
            Serial.print(" (不在");
            Serial.print(TREMOR_RT_FREQ_MIN, 0);
            Serial.print("-");
            Serial.print(TREMOR_RT_FREQ_MAX, 0);
            Serial.print("Hz)");
        }
        Serial.println("                           │");

        // 检查 RMS 条件
        Serial.print("  │   RMS幅度:  ");
        Serial.print(lastRmsOK ? "✓" : "✗");
        Serial.print(" ");
        Serial.print(result.rmsAmplitude, 2);
        Serial.print("g");
        if (!lastRmsOK) {
            Serial.print(" < ");
            Serial.print(TREMOR_RT_RMS_MIN, 1);
            Serial.print("g (下限)");
        }
        Serial.println("                     │");

        Serial.println("  │                                                              │");
        Serial.print("  │   有效范围: ");
        Serial.print(TREMOR_RT_RMS_MIN, 1);
        Serial.print("g - ");
        Serial.print(TREMOR_RT_RMS_MAX, 1);
        Serial.println("g                                  │");
        Serial.println("  │   说明: RMS需在有效范围内且满足频谱条件才判定为震颤          │");
        Serial.println("  └──────────────────────────────────────────────────────────────┘");
    }

    Serial.println();
    Serial.println("======================================================================");
}

void tremorPrintSimpleResult(const TremorResult& result) {
    // 格式: [时间] ● 频率:X.XXHz 幅度:X.XXXg 严重度:X(标签)
    //   或: [时间] ○ 未检测到震颤
    //   或: [时间] ⚠ 测试无效 (超出范围)

    Serial.print("[");
    // 简单时间格式 (秒)
    unsigned long secs = result.timestamp / 1000;
    unsigned long mins = secs / 60;
    secs = secs % 60;
    if (mins < 10) Serial.print("0");
    Serial.print(mins);
    Serial.print(":");
    if (secs < 10) Serial.print("0");
    Serial.print(secs);
    Serial.print("] ");

    if (result.outOfRange) {
        Serial.print("⚠ 测试无效 (RMS:");
        Serial.print(result.rmsAmplitude, 1);
        Serial.print("g > ");
        Serial.print(TREMOR_RT_RMS_MAX, 1);
        Serial.println("g)");
    } else if (result.detected) {
        Serial.print("● ");
        Serial.print("频率:");
        Serial.print(result.frequency, 2);
        Serial.print("Hz ");
        Serial.print("幅度:");
        Serial.print(result.rmsAmplitude, 2);
        Serial.print("g ");
        Serial.print("严重度:");
        Serial.print(result.severity);
        Serial.print("(");
        Serial.print(result.severityLabel);
        Serial.println(")");
    } else {
        Serial.print("○ 未检测到震颤 (RMS:");
        Serial.print(result.rmsAmplitude, 2);
        Serial.println("g)");
    }
}

void tremorPrintSpectrum(void) {
    Serial.println();
    Serial.println("[Spectrum] 4-6Hz 频段频谱数据:");
    Serial.println();
    Serial.println("频率(Hz)  功率      图示");
    Serial.println("────────────────────────────────────");

    int startBin = tremorFreqToBin(TREMOR_FREQ_MIN) - 1;
    int endBin = tremorFreqToBin(TREMOR_FREQ_MAX) + 1;
    if (startBin < 1) startBin = 1;
    if (endBin >= FFT_SAMPLES / 2) endBin = FFT_SAMPLES / 2 - 1;

    // 找最大功率用于归一化
    double maxPower = 0;
    for (int i = startBin; i <= endBin; i++) {
        if (vReal[i] > maxPower) maxPower = vReal[i];
    }

    // 打印每个 bin
    for (int i = startBin; i <= endBin; i++) {
        float freq = tremorBinToFreq(i);
        float power = vReal[i];

        // 频率
        if (freq < 10) Serial.print(" ");
        Serial.print(freq, 2);
        Serial.print("    ");

        // 功率
        Serial.print(power, 4);
        Serial.print("    ");

        // 条形图
        int barLen = (maxPower > 0) ? (int)(power / maxPower * 20) : 0;
        for (int j = 0; j < barLen; j++) {
            Serial.print("█");
        }

        // 标记峰值
        if (i == lastSpectrum.peakBin) {
            Serial.print("  ← 峰值");
        }

        Serial.println();
    }

    Serial.println("────────────────────────────────────");
    Serial.println();
}

void tremorPrintStats(void) {
    Serial.println();
    Serial.println("[Stats] 震颤检测统计:");
    Serial.println("────────────────────────────────────");

    Serial.print("  总分析次数: ");
    Serial.println(stats.totalAnalyses);

    Serial.print("  检测到震颤: ");
    Serial.print(stats.tremorCount);
    Serial.print(" 次");

    if (stats.totalAnalyses > 0) {
        float rate = (float)stats.tremorCount / stats.totalAnalyses * 100;
        Serial.print(" (");
        Serial.print(rate, 1);
        Serial.println("%)");
    } else {
        Serial.println();
    }

    if (stats.tremorCount > 0) {
        Serial.print("  平均频率: ");
        Serial.print(stats.avgFrequency, 2);
        Serial.println(" Hz");

        Serial.print("  平均幅度: ");
        Serial.print(stats.avgAmplitude, 4);
        Serial.println(" g");

        Serial.print("  最高严重度: ");
        Serial.print(stats.maxSeverity);
        Serial.print(" (");
        Serial.print(tremorGetSeverityLabel(stats.maxSeverity));
        Serial.println(")");
    }

    unsigned long duration = millis() - stats.startTime;
    Serial.print("  监测时长: ");
    Serial.print(duration / 1000);
    Serial.println(" 秒");

    Serial.println("────────────────────────────────────");
}
