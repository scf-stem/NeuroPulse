<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'
import { legacyT } from '@/i18n'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps<{
  dataPoints: number[]
  labels?: string[]
  height?: number
  color?: string
}>()

const chartRef = ref(null)

// 图表配置
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    duration: 0 // 实时数据需关闭动画
  },
  interaction: {
    intersect: false
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      enabled: false
    }
  },
  scales: {
    x: {
      display: false,
      grid: {
        display: false
      }
    },
    y: {
      display: true,
      min: -2,
      max: 2,
      grid: {
        color: '#f3f4f6'
      },
      ticks: {
         stepSize: 1
      }
    }
  },
  elements: {
    point: {
      radius: 0
    },
    line: {
      tension: 0.4,
      borderWidth: 2
    }
  }
}

// 数据转换
const chartData = computed(() => {
  const gradientColor = props.color || '#F97316' // Primary Orange
  
  return {
    labels: props.labels ? [...props.labels] : Array(props.dataPoints.length).fill(''),
    datasets: [
      {
        label: legacyT('加速度 (g)'),
        data: [...props.dataPoints],
        borderColor: gradientColor,
        backgroundColor: (context: any) => {
          const ctx = context.chart.ctx
          const gradient = ctx.createLinearGradient(0, 0, 0, 300)
          gradient.addColorStop(0, `${gradientColor}40`) // 25% opacity
          gradient.addColorStop(1, `${gradientColor}00`) // 0% opacity
          return gradient
        },
        fill: true,
      }
    ]
  }
})


</script>

<template>
  <div class="w-full" :style="{ height: `${height || 200}px` }">
    <Line
      ref="chartRef"
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>
