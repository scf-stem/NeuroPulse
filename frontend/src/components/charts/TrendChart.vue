<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale
} from 'chart.js'
import { Bar } from 'vue-chartjs'
import { t } from '@/i18n'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps<{
  dateLabels: string[]
  severityData: number[] // Line
  tremorCountData: number[] // Bar
}>()

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false,
  },
  plugins: {
    title: {
      display: true,
      text: t('dashboard.weeklyTrend'),
      align: 'start' as const,
      font: {
          size: 16,
          weight: 'bold' as const
      }
    }
  },
  scales: {
    y: {
      type: 'linear' as const,
      display: true,
      position: 'left' as const,
      title: {
          display: true,
          text: t('dashboard.avgSeverity')
      },
      min: 0,
      max: 4
    },
    y1: {
      type: 'linear' as const,
      display: true,
      position: 'right' as const,
      title: {
          display: true,
          text: t('dashboard.tremorCount')
      },
      grid: {
        drawOnChartArea: false, // only want the grid lines for one axis to show up
      },
    },
  }
}

const chartData = computed(() => {
  return {
    labels: props.dateLabels,
    datasets: [
      {
        type: 'line' as const,
        label: t('dashboard.avgSeverity'),
        backgroundColor: '#FB923C', // Orange-400
        borderColor: '#FB923C',
        data: props.severityData,
        yAxisID: 'y',
        tension: 0.3
      },
      {
        type: 'bar' as const,
        label: t('dashboard.tremorCount'),
        backgroundColor: '#E5E7EB', // Gray-200
        data: props.tremorCountData,
        yAxisID: 'y1',
        borderRadius: 4
      }
    ] as any[]
  }
})
</script>

<template>
  <div class="w-full h-80">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>
