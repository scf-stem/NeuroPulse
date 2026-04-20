/**
 * Mock Service
 * 用于在无硬件环境下模拟医疗级传感器数据
 */

import { reactive } from 'vue'
import type { TremorData } from '@/types'

// 模拟配置
export const mockConfig = reactive({
    enabled: true,
    tremorType: 'random' as 'resting' | 'action' | 'random' | 'clean', // 静止性 | 动作性 | 随机 | 无震颤
    baseAmplitude: 0.1, // 基础重力加速度 (g)
    noiseLevel: 0.05, // 噪声水平
    tremorFrequency: 5.0, // 震颤主频 (Hz)
    tremorIntensity: 0.0 // 震颤强度 (0-1)
})

class MockService {
    private timer: number | null = null

    // 模拟数据生成器
    // @ts-ignore
    generateWavePoint(timestamp: number): number {
        // 基础噪声
        let value = (Math.random() - 0.5) * mockConfig.noiseLevel

        // 如果有震颤，叠加正弦波
        if (mockConfig.tremorIntensity > 0) {
            // 叠加主频 (4-6Hz)
            const t = timestamp / 1000
            value += Math.sin(2 * Math.PI * mockConfig.tremorFrequency * t) * mockConfig.tremorIntensity * 2.0

            // 叠加谐波 (8-12Hz)
            value += Math.sin(2 * Math.PI * (mockConfig.tremorFrequency * 2) * t) * (mockConfig.tremorIntensity * 0.5)
        }

        return value
    }

    // 生成历史趋势数据
    generateTrendData(days: number) {
        const data = []
        const now = new Date()

        for (let i = days - 1; i >= 0; i--) {
            const date = new Date(now)
            date.setDate(date.getDate() - i)

            // 模拟波动：早起症状轻，下午重
            // const dailyBase = 0.5 + Math.random() * 0.5

            data.push({
                date: date.toISOString(),
                detection_rate: Math.min(100, Math.floor(20 + Math.random() * 60)),
                avg_severity: Math.min(4, Math.max(0, 1 + Math.random() * 2)),
                tremor_count: Math.floor(50 + Math.random() * 200)
            })
        }
        return data
    }

    // 生成频谱数据 (FFT模拟)
    generateSpectrumData(pointCount = 64) {
        const labels = []
        const data = []

        for (let i = 0; i < pointCount; i++) {
            const freq = i * (25 / pointCount) // 0-25Hz
            labels.push(freq.toFixed(1))

            let amp = Math.random() * 0.1 // 底噪

            // 在主频附近增加能量
            if (Math.abs(freq - mockConfig.tremorFrequency) < 1.0) {
                amp += mockConfig.tremorIntensity * 2.0
            }

            data.push(amp)
        }

        return { labels, data }
    }

    // 开始实时模拟
    startSimulation(callback: (data: TremorData) => void) {
        if (this.timer) clearInterval(this.timer)

        const startTime = Date.now()

        this.timer = window.setInterval(() => {
            const now = Date.now()
            const amplitude = this.generateWavePoint(now - startTime)

            // 计算 RMS (简单模拟)
            const rms = Math.abs(amplitude)

            // 判定严重度
            let severity = 0
            if (rms > 1.5) severity = 4
            else if (rms > 1.0) severity = 3
            else if (rms > 0.5) severity = 2
            else if (rms > 0.2) severity = 1

            const data: TremorData = {
                id: now,
                timestamp: new Date().toISOString(),
                session_id: 1, // Mock session ID (number)
                valid: true,
                out_of_range: false,
                detected: rms > 0.3,
                frequency: mockConfig.tremorFrequency + (Math.random() - 0.5),
                amplitude: amplitude,
                rms_amplitude: rms,
                severity: severity
            }

            callback(data)
        }, 50) // 20Hz 更新率 (为了前端流畅展示，不需要125Hz)
    }

    stopSimulation() {
        if (this.timer) {
            clearInterval(this.timer)
            this.timer = null
        }
    }
}

export const mockService = new MockService()
