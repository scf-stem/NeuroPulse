<template>
  <div class="min-h-screen bg-warmGray-900 text-white p-6">
    <div class="max-w-5xl mx-auto">
      <!-- 页面标题 -->
      <div class="flex items-center justify-between mb-8 animate-fade-in-up">
        <div>
          <div class="flex items-center gap-3 mb-2">
            <div class="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-500/30">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <h1 class="text-3xl font-bold text-primary-400">{{ lt('Configuration', '参数配置') }}</h1>
              <p class="text-warmGray-400 mt-1">{{ lt('Tune key tremor-detection parameters (desktop console mode)', '调整震颤检测算法的关键参数 (上位机模式)') }}</p>
            </div>
          </div>
        </div>
        <div class="flex gap-3">
          <button
            @click="refreshStatus"
            :disabled="loading"
            class="px-4 py-2.5 bg-warmGray-700 hover:bg-warmGray-600 rounded-xl flex items-center gap-2 transition-all duration-200"
          >
            <svg class="w-5 h-5" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ lt('Refresh', '刷新') }}
          </button>
          <button
            @click="resetToDefaults"
            class="px-4 py-2.5 bg-warmGray-700 hover:bg-warmGray-600 rounded-xl transition-all duration-200"
          >
            {{ lt('Restore defaults', '恢复默认') }}
          </button>
          <button
            @click="saveConfig"
            :disabled="saving"
            class="px-5 py-2.5 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 rounded-xl flex items-center gap-2 disabled:opacity-50 shadow-lg shadow-primary-500/30 transition-all duration-200"
          >
            <svg v-if="!saving" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            {{ lt('Save configuration', '保存配置') }}
          </button>
        </div>
      </div>

      <!-- 状态卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
        <!-- 设备状态 -->
        <div class="bg-warmGray-800/80 backdrop-blur rounded-2xl p-5 border border-warmGray-700/50 animate-fade-in-up" style="animation-delay: 50ms;">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gradient-to-br from-mint-400 to-mint-600 rounded-xl flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h2 class="text-lg font-semibold text-mint-400">{{ lt('Device status', '设备状态') }}</h2>
            </div>
            <span
              :class="deviceStatus.connected ? 'bg-mint-500/20 text-mint-400 border-mint-500/30' : 'bg-warmGray-600/50 text-warmGray-400 border-warmGray-500/30'"
              class="px-3 py-1 rounded-full text-xs font-medium border"
            >
              {{ deviceStatus.connected ? lt('Connected', '已连接') : lt('Disconnected', '未连接') }}
            </span>
          </div>
          <div v-if="deviceStatus.connected" class="space-y-3 text-sm">
            <div class="flex justify-between items-center p-2 bg-warmGray-700/50 rounded-lg">
              <span class="text-warmGray-400">{{ lt('Device ID:', '设备 ID:') }}</span>
              <span class="font-mono text-mint-400">{{ deviceStatus.device_id }}</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-warmGray-700/50 rounded-lg">
              <span class="text-warmGray-400">{{ lt('Device IP:', '设备 IP:') }}</span>
              <span class="font-mono">{{ deviceStatus.ip }}</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-warmGray-700/50 rounded-lg">
              <span class="text-warmGray-400">{{ lt('Config version:', '配置版本:') }}</span>
              <span class="font-mono">v{{ deviceStatus.version }}</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-warmGray-700/50 rounded-lg">
              <span class="text-warmGray-400">{{ lt('Last upload:', '最后上报:') }}</span>
              <span class="font-mono">{{ formatTime(deviceStatus.last_seen) }}</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-warmGray-700/50 rounded-lg">
              <span class="text-warmGray-400">{{ lt('Sync status:', '同步状态:') }}</span>
              <span :class="deviceStatus.synced ? 'text-mint-400' : 'text-yellow-400'">
                {{ deviceStatus.synced ? lt('Synced', '已同步') : lt('Pending sync', '待同步') }}
              </span>
            </div>
          </div>
          <div v-else class="text-warmGray-500 text-sm">
            <p>{{ lt('Waiting for device connection...', '等待设备连接...') }}</p>
            <p class="mt-2 text-xs">{{ lt('Run ', '设备需执行 ') }}<code class="bg-warmGray-700 px-2 py-0.5 rounded-lg text-primary-400">cfgup</code>{{ lt(' on the device to upload the current config', ' 命令上传配置') }}</p>
          </div>
        </div>

        <!-- 云端配置状态 -->
        <div class="bg-warmGray-800/80 backdrop-blur rounded-2xl p-5 border border-warmGray-700/50 animate-fade-in-up" style="animation-delay: 100ms;">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
                </svg>
              </div>
              <h2 class="text-lg font-semibold text-primary-400">{{ lt('Cloud configuration', '云端配置') }}</h2>
            </div>
            <span class="bg-primary-500/20 text-primary-400 border border-primary-500/30 px-3 py-1 rounded-full text-xs font-medium">
              v{{ cloudStatus.version }}
            </span>
          </div>
          <div class="space-y-3 text-sm">
            <div class="flex justify-between items-center p-2 bg-warmGray-700/50 rounded-lg">
              <span class="text-warmGray-400">{{ lt('Config source:', '配置来源:') }}</span>
              <span class="font-mono">{{ getSourceLabel(cloudStatus.source) }}</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-warmGray-700/50 rounded-lg">
              <span class="text-warmGray-400">{{ lt('Updated at:', '更新时间:') }}</span>
              <span class="font-mono">{{ formatTime(cloudStatus.updated_at) }}</span>
            </div>
          </div>
          <div class="mt-4 p-4 bg-warmGray-700/50 rounded-xl text-xs">
            <p class="text-warmGray-400 mb-2 font-medium">{{ lt('Workflow:', '使用流程:') }}</p>
            <ol class="list-decimal list-inside space-y-2 text-warmGray-300">
              <li>{{ lt('Run ', '设备执行 ') }}<code class="bg-warmGray-600 px-1.5 py-0.5 rounded text-primary-400">cfgup</code>{{ lt(' on the device to upload the current config', ' 上传当前配置') }}</li>
              <li>{{ lt('Adjust parameters on this page and save them', '在此页面修改参数并保存') }}</li>
              <li>{{ lt('Run ', '设备执行 ') }}<code class="bg-warmGray-600 px-1.5 py-0.5 rounded text-primary-400">update</code>{{ lt(' on the device to pull the updated config', ' 拉取新配置') }}</li>
            </ol>
          </div>
        </div>
      </div>

      <!-- 配置对比 (如果设备已连接) -->
      <div v-if="deviceStatus.connected && deviceStatus.params" class="bg-warmGray-800/80 backdrop-blur rounded-2xl p-5 mb-6 border border-warmGray-700/50 animate-fade-in-up" style="animation-delay: 150ms;">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <h2 class="text-lg font-semibold text-lavender-400">{{ lt('Configuration comparison', '配置对比') }}</h2>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-warmGray-700/70 text-left">
              <tr>
                <th class="p-3 rounded-l-xl">{{ lt('Parameter', '参数') }}</th>
                <th class="p-3 text-mint-400">{{ lt('Current device value', '设备当前值') }}</th>
                <th class="p-3 text-primary-400">{{ lt('Cloud config value', '云端配置值') }}</th>
                <th class="p-3 rounded-r-xl">{{ lt('Status', '状态') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-warmGray-700/50">
              <tr class="hover:bg-warmGray-700/30 transition-colors">
                <td class="p-3">{{ lt('RMS minimum', 'RMS 下限') }}</td>
                <td class="p-3 font-mono">{{ deviceStatus.params.rms_min?.toFixed(2) }} g</td>
                <td class="p-3 font-mono">{{ config.rms_min.toFixed(2) }} g</td>
                <td class="p-3">
                  <span v-if="deviceStatus.params.rms_min === config.rms_min" class="text-mint-400">✓</span>
                  <span v-else class="text-yellow-400">≠</span>
                </td>
              </tr>
              <tr class="hover:bg-warmGray-700/30 transition-colors">
                <td class="p-3">{{ lt('RMS maximum', 'RMS 上限') }}</td>
                <td class="p-3 font-mono">{{ deviceStatus.params.rms_max?.toFixed(2) }} g</td>
                <td class="p-3 font-mono">{{ config.rms_max.toFixed(2) }} g</td>
                <td class="p-3">
                  <span v-if="deviceStatus.params.rms_max === config.rms_max" class="text-mint-400">✓</span>
                  <span v-else class="text-yellow-400">≠</span>
                </td>
              </tr>
              <tr class="hover:bg-warmGray-700/30 transition-colors">
                <td class="p-3">{{ lt('Power threshold', '功率阈值') }}</td>
                <td class="p-3 font-mono">{{ deviceStatus.params.power_threshold?.toFixed(2) }}</td>
                <td class="p-3 font-mono">{{ config.power_threshold.toFixed(2) }}</td>
                <td class="p-3">
                  <span v-if="deviceStatus.params.power_threshold === config.power_threshold" class="text-mint-400">✓</span>
                  <span v-else class="text-yellow-400">≠</span>
                </td>
              </tr>
              <tr class="hover:bg-warmGray-700/30 transition-colors">
                <td class="p-3">{{ lt('Frequency range', '频率范围') }}</td>
                <td class="p-3 font-mono">{{ deviceStatus.params.freq_min?.toFixed(1) }} - {{ deviceStatus.params.freq_max?.toFixed(1) }} Hz</td>
                <td class="p-3 font-mono">{{ config.freq_min.toFixed(1) }} - {{ config.freq_max.toFixed(1) }} Hz</td>
                <td class="p-3">
                  <span v-if="deviceStatus.params.freq_min === config.freq_min && deviceStatus.params.freq_max === config.freq_max" class="text-mint-400">✓</span>
                  <span v-else class="text-yellow-400">≠</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 配置面板 -->
      <div class="space-y-6">
        <!-- RMS 幅度范围 -->
        <div class="bg-warmGray-800/80 backdrop-blur rounded-2xl p-6 border border-warmGray-700/50 animate-fade-in-up" style="animation-delay: 200ms;">
          <h2 class="text-lg font-semibold text-primary-400 mb-4 flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            {{ lt('RMS amplitude range (g)', 'RMS 幅度范围 (g)') }}
          </h2>
          <p class="text-warmGray-400 text-sm mb-6 ml-13">
            {{ lt('Define the RMS acceleration range treated as valid tremor. Values below the minimum are ignored, and values above the maximum are treated as out of range.', '定义有效震颤的 RMS 加速度范围。低于下限不判定为震颤，高于上限判定为超出范围。') }}
          </p>

          <div class="space-y-6">
            <div>
              <div class="flex items-center justify-between mb-3">
                <label class="text-sm text-warmGray-300">{{ lt('Minimum (rms_min)', '下限 (rms_min)') }}</label>
                <span class="font-mono text-primary-400 text-lg bg-warmGray-700/50 px-3 py-1 rounded-lg">{{ config.rms_min.toFixed(1) }} g</span>
              </div>
              <input
                type="range"
                v-model.number="config.rms_min"
                min="0.1"
                max="5.0"
                step="0.1"
                class="w-full h-2 bg-warmGray-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <div class="flex justify-between text-xs text-warmGray-500 mt-2">
                <span>0.1</span>
                <span>5.0</span>
              </div>
            </div>

            <div>
              <div class="flex items-center justify-between mb-3">
                <label class="text-sm text-warmGray-300">{{ lt('Maximum (rms_max)', '上限 (rms_max)') }}</label>
                <span class="font-mono text-primary-400 text-lg bg-warmGray-700/50 px-3 py-1 rounded-lg">{{ config.rms_max.toFixed(1) }} g</span>
              </div>
              <input
                type="range"
                v-model.number="config.rms_max"
                min="1.0"
                max="20.0"
                step="0.5"
                class="w-full h-2 bg-warmGray-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <div class="flex justify-between text-xs text-warmGray-500 mt-2">
                <span>1.0</span>
                <span>20.0</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 功率阈值 -->
        <div class="bg-warmGray-800/80 backdrop-blur rounded-2xl p-6 border border-warmGray-700/50 animate-fade-in-up" style="animation-delay: 250ms;">
          <h2 class="text-lg font-semibold text-yellow-400 mb-4 flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            {{ lt('Power threshold', '功率阈值') }}
          </h2>
          <p class="text-warmGray-400 text-sm mb-6 ml-13">
            {{ lt('Power in the 4-6 Hz tremor band must exceed this threshold before tremor is detected. Lower values increase sensitivity.', '震颤频段 (4-6Hz) 的功率需超过此阈值才判定为震颤。降低此值可提高灵敏度。') }}
          </p>

          <div>
            <div class="flex items-center justify-between mb-3">
              <label class="text-sm text-warmGray-300">power_threshold</label>
              <span class="font-mono text-yellow-400 text-lg bg-warmGray-700/50 px-3 py-1 rounded-lg">{{ config.power_threshold.toFixed(2) }}</span>
            </div>
            <input
              type="range"
              v-model.number="config.power_threshold"
              min="0.01"
              max="2.0"
              step="0.01"
              class="w-full h-2 bg-warmGray-700 rounded-lg appearance-none cursor-pointer slider-yellow"
            />
            <div class="flex justify-between text-xs text-warmGray-500 mt-2">
              <span>{{ lt('0.01 (high sensitivity)', '0.01 (高灵敏度)') }}</span>
              <span>{{ lt('2.0 (low sensitivity)', '2.0 (低灵敏度)') }}</span>
            </div>
          </div>
        </div>

        <!-- 频率范围 -->
        <div class="bg-warmGray-800/80 backdrop-blur rounded-2xl p-6 border border-warmGray-700/50 animate-fade-in-up" style="animation-delay: 300ms;">
          <h2 class="text-lg font-semibold text-mint-400 mb-4 flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-mint-400 to-mint-600 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
              </svg>
            </div>
            {{ lt('Frequency range (Hz)', '频率范围 (Hz)') }}
          </h2>
          <p class="text-warmGray-400 text-sm mb-6 ml-13">
            {{ lt('Typical Parkinsonian tremor falls within 4-6 Hz. Adjust the range for different tremor profiles.', '帕金森震颤的典型频率为 4-6Hz。调整此范围可适应不同类型的震颤检测。') }}
          </p>

          <div class="space-y-6">
            <div>
              <div class="flex items-center justify-between mb-3">
                <label class="text-sm text-warmGray-300">{{ lt('Minimum (freq_min)', '下限 (freq_min)') }}</label>
                <span class="font-mono text-mint-400 text-lg bg-warmGray-700/50 px-3 py-1 rounded-lg">{{ config.freq_min.toFixed(1) }} Hz</span>
              </div>
              <input
                type="range"
                v-model.number="config.freq_min"
                min="1.0"
                max="8.0"
                step="0.5"
                class="w-full h-2 bg-warmGray-700 rounded-lg appearance-none cursor-pointer slider-green"
              />
              <div class="flex justify-between text-xs text-warmGray-500 mt-2">
                <span>1.0</span>
                <span>8.0</span>
              </div>
            </div>

            <div>
              <div class="flex items-center justify-between mb-3">
                <label class="text-sm text-warmGray-300">{{ lt('Maximum (freq_max)', '上限 (freq_max)') }}</label>
                <span class="font-mono text-mint-400 text-lg bg-warmGray-700/50 px-3 py-1 rounded-lg">{{ config.freq_max.toFixed(1) }} Hz</span>
              </div>
              <input
                type="range"
                v-model.number="config.freq_max"
                min="4.0"
                max="15.0"
                step="0.5"
                class="w-full h-2 bg-warmGray-700 rounded-lg appearance-none cursor-pointer slider-green"
              />
              <div class="flex justify-between text-xs text-warmGray-500 mt-2">
                <span>4.0</span>
                <span>15.0</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 严重度分级阈值 -->
        <div class="bg-warmGray-800/80 backdrop-blur rounded-2xl p-6 border border-warmGray-700/50 animate-fade-in-up" style="animation-delay: 350ms;">
          <h2 class="text-lg font-semibold text-lavender-400 mb-4 flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            {{ lt('Severity thresholds (g)', '严重度分级阈值 (g)') }}
          </h2>
          <p class="text-warmGray-400 text-sm mb-6 ml-13">
            {{ lt('Split tremor severity into levels 0-4 based on RMS amplitude. Each value defines a threshold boundary.', '根据 RMS 幅度将震颤分为 0-4 级。数值为各级别的分界点。') }}
          </p>

          <div class="space-y-6">
            <div v-for="(label, index) in severityLabels" :key="index">
              <div class="flex items-center justify-between mb-3">
                <label class="text-sm text-warmGray-300 flex items-center gap-2">
                  <span :class="getSeverityBadgeClass(index)" class="px-2.5 py-1 rounded-lg text-xs font-medium">{{ lt(`Level ${index}`, `${index}级`) }}</span>
                  {{ label }}
                </label>
                <span class="font-mono text-lavender-400 text-lg bg-warmGray-700/50 px-3 py-1 rounded-lg">{{ config.severity_thresholds[index]?.toFixed(1) }} g</span>
              </div>
              <input
                type="range"
                v-model.number="config.severity_thresholds[index]"
                min="0.5"
                max="8.0"
                step="0.1"
                class="w-full h-2 bg-warmGray-700 rounded-lg appearance-none cursor-pointer slider-purple"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 保存成功提示 -->
      <Transition name="slide-up">
        <div
          v-if="saveSuccess"
          class="fixed bottom-6 right-6 bg-gradient-to-r from-mint-500 to-mint-600 text-white px-6 py-4 rounded-2xl shadow-xl shadow-mint-500/30 flex items-center gap-3"
        >
          <div class="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <span class="font-medium">{{ lt(`Configuration saved (v${cloudStatus.version})`, `配置已保存 (版本 v${cloudStatus.version})`) }}</span>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { formatDateTime, legacyT, localeText } from '@/i18n'

interface TremorConfig {
  rms_min: number
  rms_max: number
  power_threshold: number
  freq_min: number
  freq_max: number
  severity_thresholds: number[]
}

interface DeviceStatus {
  connected: boolean
  version: number
  last_seen: string | null
  ip: string | null
  device_id: string | null
  params: TremorConfig | null
  synced: boolean
}

interface CloudStatus {
  version: number
  updated_at: string
  source: string
  params: TremorConfig
}

const config = reactive<TremorConfig>({
  rms_min: 2.5,
  rms_max: 5.0,
  power_threshold: 0.5,
  freq_min: 4.0,
  freq_max: 6.0,
  severity_thresholds: [2.5, 3.0, 3.5, 4.0]
})

const deviceStatus = reactive<DeviceStatus>({
  connected: false,
  version: 0,
  last_seen: null,
  ip: null,
  device_id: null,
  params: null,
  synced: false
})

const cloudStatus = reactive<CloudStatus>({
  version: 1,
  updated_at: '',
  source: 'default',
  params: { ...config }
})

const loading = ref(false)
const saving = ref(false)
const saveSuccess = ref(false)
const lt = (en: string, zh: string) => localeText(en, zh)

const severityLabels = [
  lt('Minimal', '无/极轻'),
  lt('Slight', '轻微'),
  lt('Mild', '轻度'),
  lt('Moderate', '中度'),
]

const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'

let refreshInterval: number | null = null

async function loadStatus() {
  try {
    const response = await axios.get(`${apiBase}/config/status`)
    const data = response.data

    // 更新云端状态
    cloudStatus.version = data.cloud.version
    cloudStatus.updated_at = data.cloud.updated_at
    cloudStatus.source = data.cloud.source
    Object.assign(config, data.cloud.params)

    // 更新设备状态
    deviceStatus.connected = data.device.connected
    deviceStatus.version = data.device.version
    deviceStatus.last_seen = data.device.last_seen
    deviceStatus.ip = data.device.ip
    deviceStatus.device_id = data.device.device_id
    deviceStatus.params = data.device.params
    deviceStatus.synced = data.device.synced
  } catch (error) {
    console.error('加载状态失败:', error)
  }
}

async function refreshStatus() {
  loading.value = true
  try {
    await loadStatus()
  } finally {
    loading.value = false
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const response = await axios.post(`${apiBase}/config/save`, {
      rms_min: config.rms_min,
      rms_max: config.rms_max,
      power_threshold: config.power_threshold,
      freq_min: config.freq_min,
      freq_max: config.freq_max,
      severity_thresholds: config.severity_thresholds
    })

    cloudStatus.version = response.data.version
    cloudStatus.updated_at = response.data.updated_at
    cloudStatus.source = 'web'

    // 更新同步状态
    deviceStatus.synced = deviceStatus.version >= cloudStatus.version

    // 显示成功提示
    saveSuccess.value = true
    setTimeout(() => {
      saveSuccess.value = false
    }, 3000)
  } catch (error) {
    console.error('保存配置失败:', error)
    alert(legacyT('保存失败，请重试'))
  } finally {
    saving.value = false
  }
}

async function resetToDefaults() {
  if (!confirm(legacyT('确定要恢复默认配置吗？'))) return

  try {
    const response = await axios.post(`${apiBase}/config/reset`)
    cloudStatus.version = response.data.version
    cloudStatus.updated_at = response.data.updated_at

    // 重新加载状态
    await loadStatus()
  } catch (error) {
    console.error('重置配置失败:', error)
  }
}

function formatTime(isoString: string | null | undefined): string {
  if (!isoString) return '-'
  try {
    return formatDateTime(isoString)
  } catch {
    return isoString
  }
}

function getSourceLabel(source: string): string {
  switch (source) {
    case 'default': return lt('Default configuration', '默认配置')
    case 'device': return lt('Uploaded from device', '设备上传')
    case 'web': return lt('Edited on web', '网页修改')
    default: return source
  }
}

function getSeverityBadgeClass(level: number): string {
  const classes = [
    'bg-warmGray-600 text-warmGray-200',
    'bg-yellow-600/80 text-yellow-100',
    'bg-orange-600/80 text-orange-100',
    'bg-red-600/80 text-red-100'
  ]
  return classes[level] || 'bg-warmGray-600 text-warmGray-200'
}

onMounted(() => {
  loadStatus()
  // 每 5 秒刷新一次状态
  refreshInterval = window.setInterval(loadStatus, 5000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
/* 自定义滑块样式 - Primary (Orange) */
.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FB923C, #EA580C);
  cursor: pointer;
  box-shadow: 0 0 12px rgba(249, 115, 22, 0.5);
  transition: transform 0.2s, box-shadow 0.2s;
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 0 16px rgba(249, 115, 22, 0.7);
}

.slider::-moz-range-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FB923C, #EA580C);
  cursor: pointer;
  border: none;
}

/* Yellow slider */
.slider-yellow::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FACC15, #EAB308);
  cursor: pointer;
  box-shadow: 0 0 12px rgba(250, 204, 21, 0.5);
  transition: transform 0.2s, box-shadow 0.2s;
}

.slider-yellow::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 0 16px rgba(250, 204, 21, 0.7);
}

.slider-yellow::-moz-range-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FACC15, #EAB308);
  cursor: pointer;
  border: none;
}

/* Green slider */
.slider-green::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #34D399, #10B981);
  cursor: pointer;
  box-shadow: 0 0 12px rgba(52, 211, 153, 0.5);
  transition: transform 0.2s, box-shadow 0.2s;
}

.slider-green::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 0 16px rgba(52, 211, 153, 0.7);
}

.slider-green::-moz-range-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #34D399, #10B981);
  cursor: pointer;
  border: none;
}

/* Purple slider */
.slider-purple::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #C084FC, #A855F7);
  cursor: pointer;
  box-shadow: 0 0 12px rgba(192, 132, 252, 0.5);
  transition: transform 0.2s, box-shadow 0.2s;
}

.slider-purple::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 0 16px rgba(192, 132, 252, 0.7);
}

.slider-purple::-moz-range-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #C084FC, #A855F7);
  cursor: pointer;
  border: none;
}

/* Slide up transition */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease-out;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.ml-13 {
  margin-left: 3.25rem;
}
</style>
