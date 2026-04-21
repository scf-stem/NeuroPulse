<script setup lang="ts">
/**
 * Tremor Guard - Health Profile View
 * 震颤卫士 - 健康档案页面
 */

import { ref, reactive, onMounted } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
import { useHealthStore } from '@/stores/health'
import { healthApi } from '@/api/health'
import { formatDate as formatLocaleDate, legacyT, localeText } from '@/i18n'
import { getHoehnYahrStageMeta, HOEHN_YAHR_STAGES } from '@/types'
import type { HealthProfile, MedicalRecord, FamilyHistory, VisitRecord } from '@/types'

const healthStore = useHealthStore()
const lt = (en: string, zh: string) => localeText(en, zh)

// Tab 状态
const activeTab = ref<'profile' | 'medical' | 'family' | 'visits'>('profile')

// Tab 配置
const tabs = [
  { key: 'profile', name: lt('Basic information', '基本信息'), icon: 'user' },
  { key: 'medical', name: lt('Clinical records', '病历记录'), icon: 'document' },
  { key: 'family', name: lt('Family history', '家族病史'), icon: 'users' },
  { key: 'visits', name: lt('Visits', '就诊记录'), icon: 'hospital' },
]

// ============================================================
// 档案编辑相关
// ============================================================
const showProfileModal = ref(false)
const profileForm = reactive<Partial<HealthProfile>>({
  birth_date: '',
  gender: undefined,
  height_cm: undefined,
  weight_kg: undefined,
  blood_type: '',
  diagnosis_date: '',
  hoehn_yahr_stage: undefined,
  affected_side: undefined,
  primary_symptoms: [],
  allergies: [],
  chronic_conditions: [],
  emergency_contact: {
    name: '',
    phone: '',
    relationship: '',
  },
  notes: '',
})

const genderOptions = [
  { value: 'male', label: legacyT('男') },
  { value: 'female', label: legacyT('女') },
  { value: 'other', label: legacyT('其他') },
]

const bloodTypeOptions = ['A', 'B', 'AB', 'O', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', '未知']

const affectedSideOptions = [
  { value: 'left', label: legacyT('左侧') },
  { value: 'right', label: legacyT('右侧') },
  { value: 'both', label: legacyT('双侧') },
]

const commonSymptoms = [
  '静止性震颤',
  '运动迟缓',
  '肌强直',
  '姿势不稳',
  '步态障碍',
  '面具脸',
  '书写困难',
  '吞咽困难',
  '语言障碍',
  '便秘',
  '睡眠障碍',
  '嗅觉减退',
]

const commonAllergies = ['青霉素', '磺胺类', '头孢类', '阿司匹林', '花粉', '海鲜', '乳制品']

const commonConditions = ['高血压', '糖尿病', '冠心病', '高血脂', '甲状腺疾病', '骨质疏松']

// 新建/编辑档案
function openProfileModal() {
  if (healthStore.profile) {
    Object.assign(profileForm, {
      ...healthStore.profile,
      emergency_contact: healthStore.profile.emergency_contact || {
        name: '',
        phone: '',
        relationship: '',
      },
    })
  }
  showProfileModal.value = true
}

async function saveProfile() {
  try {
    if (healthStore.hasProfile) {
      await healthStore.updateProfile(profileForm)
    } else {
      await healthStore.createProfile(profileForm as any)
    }
    showProfileModal.value = false
  } catch (e) {
    console.error('保存档案失败:', e)
  }
}

function toggleSymptom(symptom: string) {
  const idx = profileForm.primary_symptoms?.indexOf(symptom) ?? -1
  if (idx === -1) {
    profileForm.primary_symptoms = [...(profileForm.primary_symptoms || []), symptom]
  } else {
    profileForm.primary_symptoms = profileForm.primary_symptoms?.filter((s) => s !== symptom)
  }
}

function toggleAllergy(allergy: string) {
  const idx = profileForm.allergies?.indexOf(allergy) ?? -1
  if (idx === -1) {
    profileForm.allergies = [...(profileForm.allergies || []), allergy]
  } else {
    profileForm.allergies = profileForm.allergies?.filter((a) => a !== allergy)
  }
}

function toggleCondition(condition: string) {
  const idx = profileForm.chronic_conditions?.indexOf(condition) ?? -1
  if (idx === -1) {
    profileForm.chronic_conditions = [...(profileForm.chronic_conditions || []), condition]
  } else {
    profileForm.chronic_conditions = profileForm.chronic_conditions?.filter((c) => c !== condition)
  }
}

// ============================================================
// 病历记录相关
// ============================================================
const showMedicalModal = ref(false)
const editingMedical = ref<MedicalRecord | null>(null)
const medicalForm = reactive<Partial<MedicalRecord>>({
  record_date: new Date().toISOString().split('T')[0],
  record_type: 'symptom',
  title: '',
  description: '',
  symptoms: [],
  diagnosis: '',
  severity: undefined,
  doctor_name: '',
  hospital_name: '',
  attachments: [],
})

// 附件上传状态
const uploadingMedicalAttachment = ref(false)
const uploadingVisitAttachment = ref(false)

const recordTypeOptions = [
  { value: 'symptom', label: legacyT('症状记录') },
  { value: 'diagnosis', label: legacyT('诊断记录') },
  { value: 'test_result', label: legacyT('检查结果') },
  { value: 'note', label: legacyT('备注') },
]

function openMedicalModal(record?: MedicalRecord) {
  if (record) {
    editingMedical.value = record
    Object.assign(medicalForm, {
      ...record,
      attachments: record.attachments || [],
    })
  } else {
    editingMedical.value = null
    Object.assign(medicalForm, {
      record_date: new Date().toISOString().split('T')[0],
      record_type: 'symptom',
      title: '',
      description: '',
      symptoms: [],
      diagnosis: '',
      severity: undefined,
      doctor_name: '',
      hospital_name: '',
      attachments: [],
    })
  }
  showMedicalModal.value = true
}

async function saveMedicalRecord() {
  try {
    if (editingMedical.value) {
      await healthStore.updateMedicalRecord(editingMedical.value.id, medicalForm)
    } else {
      await healthStore.addMedicalRecord(medicalForm as any)
    }
    showMedicalModal.value = false
  } catch (e) {
    console.error('保存病历失败:', e)
  }
}

async function deleteMedicalRecord(id: number) {
  if (confirm(legacyT('确定要删除这条病历记录吗？'))) {
    try {
      await healthStore.deleteMedicalRecord(id)
    } catch (e) {
      console.error('删除病历失败:', e)
    }
  }
}

function toggleMedicalSymptom(symptom: string) {
  const idx = medicalForm.symptoms?.indexOf(symptom) ?? -1
  if (idx === -1) {
    medicalForm.symptoms = [...(medicalForm.symptoms || []), symptom]
  } else {
    medicalForm.symptoms = medicalForm.symptoms?.filter((s) => s !== symptom)
  }
}

function getRecordTypeLabel(type: string) {
  return recordTypeOptions.find((o) => o.value === type)?.label || legacyT(type)
}

function getRecordTypeColor(type: string) {
  const colors: Record<string, string> = {
    symptom: 'bg-yellow-100 text-yellow-700',
    diagnosis: 'bg-blue-100 text-blue-700',
    test_result: 'bg-green-100 text-green-700',
    note: 'bg-gray-100 text-gray-700',
  }
  return colors[type] || 'bg-gray-100 text-gray-700'
}

// ============================================================
// 家族病史相关
// ============================================================
const showFamilyModal = ref(false)
const familyForm = reactive<Partial<FamilyHistory>>({
  relationship: 'parent',
  relationship_detail: '',
  condition: '',
  has_parkinsons: false,
  onset_age: undefined,
  notes: '',
})

const relationshipOptions = [
  { value: 'parent', label: legacyT('父母') },
  { value: 'sibling', label: legacyT('兄弟姐妹') },
  { value: 'grandparent', label: legacyT('祖父母/外祖父母') },
  { value: 'other', label: legacyT('其他') },
]

function openFamilyModal() {
  Object.assign(familyForm, {
    relationship: 'parent',
    relationship_detail: '',
    condition: '',
    has_parkinsons: false,
    onset_age: undefined,
    notes: '',
  })
  showFamilyModal.value = true
}

async function saveFamilyHistory() {
  try {
    await healthStore.addFamilyHistory(familyForm as any)
    showFamilyModal.value = false
  } catch (e) {
    console.error('保存家族病史失败:', e)
  }
}

async function deleteFamilyHistory(id: number) {
  if (confirm(legacyT('确定要删除这条家族病史吗？'))) {
    try {
      await healthStore.deleteFamilyHistory(id)
    } catch (e) {
      console.error('删除家族病史失败:', e)
    }
  }
}

function getRelationshipLabel(rel: string) {
  return relationshipOptions.find((o) => o.value === rel)?.label || legacyT(rel)
}

// ============================================================
// 就诊记录相关
// ============================================================
const showVisitModal = ref(false)
const editingVisit = ref<VisitRecord | null>(null)
const visitForm = reactive<Partial<VisitRecord>>({
  visit_date: new Date().toISOString().split('T')[0],
  hospital_name: '',
  department: '',
  doctor_name: '',
  visit_type: 'routine',
  chief_complaint: '',
  diagnosis: '',
  treatment_plan: '',
  prescriptions: [],
  follow_up_date: '',
  notes: '',
  attachments: [],
})

const visitTypeOptions = [
  { value: 'routine', label: legacyT('常规复诊') },
  { value: 'emergency', label: legacyT('急诊') },
  { value: 'follow_up', label: legacyT('随访') },
  { value: 'specialist', label: legacyT('专家门诊') },
]

function openVisitModal(record?: VisitRecord) {
  if (record) {
    editingVisit.value = record
    Object.assign(visitForm, {
      ...record,
      prescriptions: record.prescriptions || [],
      attachments: record.attachments || [],
    })
  } else {
    editingVisit.value = null
    Object.assign(visitForm, {
      visit_date: new Date().toISOString().split('T')[0],
      hospital_name: '',
      department: '',
      doctor_name: '',
      visit_type: 'routine',
      chief_complaint: '',
      diagnosis: '',
      treatment_plan: '',
      prescriptions: [],
      follow_up_date: '',
      notes: '',
      attachments: [],
    })
  }
  showVisitModal.value = true
}

async function saveVisitRecord() {
  try {
    if (editingVisit.value) {
      await healthStore.updateVisitRecord(editingVisit.value.id, visitForm)
    } else {
      await healthStore.addVisitRecord(visitForm as any)
    }
    showVisitModal.value = false
  } catch (e) {
    console.error('保存就诊记录失败:', e)
  }
}

async function deleteVisitRecord(id: number) {
  if (confirm(legacyT('确定要删除这条就诊记录吗？'))) {
    try {
      await healthStore.deleteVisitRecord(id)
    } catch (e) {
      console.error('删除就诊记录失败:', e)
    }
  }
}

function addPrescription() {
  if (!visitForm.prescriptions) {
    visitForm.prescriptions = []
  }
  visitForm.prescriptions.push({
    medication: '',
    dosage: '',
    frequency: '',
    duration: '',
  })
}

function removePrescription(index: number) {
  visitForm.prescriptions?.splice(index, 1)
}

function getVisitTypeLabel(type: string) {
  return visitTypeOptions.find((o) => o.value === type)?.label || legacyT(type)
}

function getVisitTypeColor(type: string) {
  const colors: Record<string, string> = {
    routine: 'bg-blue-100 text-blue-700',
    emergency: 'bg-red-100 text-red-700',
    follow_up: 'bg-green-100 text-green-700',
    specialist: 'bg-purple-100 text-purple-700',
  }
  return colors[type] || 'bg-gray-100 text-gray-700'
}

// 格式化日期
function formatDate(dateStr: string) {
  if (!dateStr) return '--'
  return formatLocaleDate(dateStr, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

// ============================================================
// 附件上传功能
// ============================================================

// 上传病历附件
async function handleMedicalAttachmentUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return

  const file = input.files[0]
  uploadingMedicalAttachment.value = true
  try {
    const result = await healthApi.uploadAttachment(file, 'medical')
    if (!medicalForm.attachments) {
      medicalForm.attachments = []
    }
    medicalForm.attachments.push(result.url)
  } catch (error) {
    console.error('上传附件失败:', error)
    alert(legacyT('上传附件失败，请重试'))
  } finally {
    uploadingMedicalAttachment.value = false
    input.value = '' // 清空输入
  }
}

// 删除病历附件
function removeMedicalAttachment(index: number) {
  medicalForm.attachments?.splice(index, 1)
}

// 上传就诊附件
async function handleVisitAttachmentUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return

  const file = input.files[0]
  uploadingVisitAttachment.value = true
  try {
    const result = await healthApi.uploadAttachment(file, 'visit')
    if (!visitForm.attachments) {
      visitForm.attachments = []
    }
    visitForm.attachments.push(result.url)
  } catch (error) {
    console.error('上传附件失败:', error)
    alert(legacyT('上传附件失败，请重试'))
  } finally {
    uploadingVisitAttachment.value = false
    input.value = '' // 清空输入
  }
}

// 删除就诊附件
function removeVisitAttachment(index: number) {
  visitForm.attachments?.splice(index, 1)
}

// 获取文件名（从URL提取）
function getFileName(url: string) {
  const parts = url.split('/')
  return parts[parts.length - 1] || legacyT('附件')
}

// 判断是否为图片
function isImage(url: string) {
  const ext = url.split('.').pop()?.toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext || '')
}

// 初始化
onMounted(async () => {
  await healthStore.initialize()
})
</script>

<template>
  <AppLayout>
    <div class="max-w-7xl mx-auto space-y-6">
      <!-- 页面标题 -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div
            class="w-14 h-14 bg-gradient-to-br from-primary-400 to-primary-600 rounded-2xl shadow-soft flex items-center justify-center"
          >
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-800">{{ lt('Health profile', '健康档案') }}</h1>
            <p class="text-gray-500">{{ lt('Manage personal health information and clinical records', '管理您的个人健康信息和病历记录') }}</p>
          </div>
        </div>
      </div>

      <!-- 档案概览卡片 -->
      <div v-if="healthStore.hasProfile" class="grid gap-4 md:grid-cols-4">
        <!-- 基本信息 -->
        <div class="card-gradient p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-500">{{ lt('Age', '年龄') }}</p>
              <p class="text-lg font-semibold text-gray-800">{{ healthStore.age || '--' }}{{ healthStore.age ? lt(' years', ' 岁') : '' }}</p>
            </div>
          </div>
        </div>

        <!-- 确诊年数 -->
        <div class="card-gradient p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-lavender-100 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-lavender-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-500">{{ lt('Years since diagnosis', '确诊年数') }}</p>
              <p class="text-lg font-semibold text-gray-800">
                {{ healthStore.diagnosisYears !== null ? `${healthStore.diagnosisYears}${lt(' years', ' 年')}` : '--' }}
              </p>
            </div>
          </div>
        </div>

        <!-- H-Y 分期 -->
        <div class="card-gradient p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-mint-100 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-mint-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-500">{{ lt('H-Y stage', 'H-Y 分期') }}</p>
              <p class="text-lg font-semibold text-gray-800">
                {{ healthStore.hoehYahrStage ? getHoehnYahrStageMeta(healthStore.hoehYahrStage)?.label : '--' }}
              </p>
            </div>
          </div>
        </div>

        <!-- 复诊提醒 -->
        <div class="card-gradient p-4">
          <div class="flex items-center gap-3">
            <div
              :class="[
                'w-10 h-10 rounded-xl flex items-center justify-center',
                healthStore.hasUpcomingFollowUp ? 'bg-red-100' : 'bg-gray-100',
              ]"
            >
              <svg
                :class="['w-5 h-5', healthStore.hasUpcomingFollowUp ? 'text-red-600' : 'text-gray-400']"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-500">{{ lt('Follow-up reminder', '复诊提醒') }}</p>
              <p class="text-lg font-semibold text-gray-800">
                {{ healthStore.hasUpcomingFollowUp ? lt('Follow-up pending', '有待复诊') : lt('None', '暂无') }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 导航 -->
      <div class="card-gradient p-1.5">
        <div class="flex space-x-1">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key as any"
            :class="[
              'flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200',
              activeTab === tab.key
                ? 'bg-white text-primary-600 shadow-soft'
                : 'text-gray-500 hover:text-gray-700 hover:bg-white/50',
            ]"
          >
            <!-- Tab 图标 -->
            <svg v-if="tab.icon === 'user'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            <svg
              v-else-if="tab.icon === 'document'"
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <svg v-else-if="tab.icon === 'users'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
              />
            </svg>
            <svg
              v-else-if="tab.icon === 'hospital'"
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
              />
            </svg>
            {{ tab.name }}
          </button>
        </div>
      </div>

      <!-- Tab 内容 -->
      <div class="card-gradient p-6">
        <!-- 加载状态 -->
        <div v-if="healthStore.loading" class="flex items-center justify-center py-12">
          <div class="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
        </div>

        <!-- 基本信息 Tab -->
        <div v-else-if="activeTab === 'profile'">
          <div v-if="!healthStore.hasProfile" class="text-center py-12">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-800 mb-2">{{ legacyT('尚未创建健康档案') }}</h3>
            <p class="text-gray-500 mb-4">{{ legacyT('创建您的健康档案，以便更好地追踪病情') }}</p>
            <button class="btn btn-primary" @click="openProfileModal">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              {{ legacyT('创建健康档案') }}
            </button>
          </div>

          <!-- 档案详情 -->
          <div v-else class="space-y-6">
            <div class="grid gap-6 md:grid-cols-2">
              <!-- 个人信息 -->
              <div class="space-y-4">
                <h3 class="text-lg font-semibold text-gray-800 border-b border-warmGray-200 pb-2">{{ lt('Profile', '个人信息') }}</h3>
                <div class="grid gap-4">
                  <div class="flex justify-between py-2">
                    <span class="text-gray-500">{{ lt('Gender', '性别') }}</span>
                    <span class="text-gray-800">
                      {{
                        healthStore.profile?.gender === 'male'
                          ? legacyT('男')
                          : healthStore.profile?.gender === 'female'
                            ? legacyT('女')
                            : '--'
                      }}
                    </span>
                  </div>
                  <div class="flex justify-between py-2">
                    <span class="text-gray-500">{{ lt('Birth date', '出生日期') }}</span>
                    <span class="text-gray-800">{{ healthStore.profile?.birth_date || '--' }}</span>
                  </div>
                  <div class="flex justify-between py-2">
                    <span class="text-gray-500">{{ lt('Height', '身高') }}</span>
                    <span class="text-gray-800">{{
                      healthStore.profile?.height_cm ? healthStore.profile.height_cm + ' cm' : '--'
                    }}</span>
                  </div>
                  <div class="flex justify-between py-2">
                    <span class="text-gray-500">{{ lt('Weight', '体重') }}</span>
                    <span class="text-gray-800">{{
                      healthStore.profile?.weight_kg ? healthStore.profile.weight_kg + ' kg' : '--'
                    }}</span>
                  </div>
                  <div class="flex justify-between py-2">
                    <span class="text-gray-500">{{ lt('Blood type', '血型') }}</span>
                    <span class="text-gray-800">{{ healthStore.profile?.blood_type || '--' }}</span>
                  </div>
                </div>
              </div>

              <!-- 疾病信息 -->
              <div class="space-y-4">
                <h3 class="text-lg font-semibold text-gray-800 border-b border-warmGray-200 pb-2">{{ lt('Condition details', '疾病信息') }}</h3>
                <div class="grid gap-4">
                  <div class="flex justify-between py-2">
                    <span class="text-gray-500">{{ lt('Diagnosis date', '确诊日期') }}</span>
                    <span class="text-gray-800">{{ healthStore.profile?.diagnosis_date || '--' }}</span>
                  </div>
                  <div class="flex justify-between py-2">
                    <span class="text-gray-500">{{ lt('H-Y stage', 'H-Y 分期') }}</span>
                    <span class="text-gray-800">
                      {{
                        healthStore.profile?.hoehn_yahr_stage
                          ? getHoehnYahrStageMeta(healthStore.profile.hoehn_yahr_stage)?.label
                          : '--'
                      }}
                    </span>
                  </div>
                  <div class="flex justify-between py-2">
                    <span class="text-gray-500">{{ lt('Affected side', '受累侧') }}</span>
                    <span class="text-gray-800">
                      {{
                        healthStore.profile?.affected_side === 'left'
                          ? legacyT('左侧')
                          : healthStore.profile?.affected_side === 'right'
                            ? legacyT('右侧')
                            : healthStore.profile?.affected_side === 'both'
                              ? legacyT('双侧')
                              : '--'
                      }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 主要症状 -->
            <div class="space-y-3" v-if="healthStore.profile?.primary_symptoms?.length">
                <h3 class="text-lg font-semibold text-gray-800 border-b border-warmGray-200 pb-2">{{ legacyT('主要症状') }}</h3>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="symptom in healthStore.profile.primary_symptoms"
                  :key="symptom"
                  class="px-3 py-1.5 bg-primary-50 text-primary-700 rounded-full text-sm"
                >
                  {{ legacyT(symptom) }}
                </span>
              </div>
            </div>

            <!-- 过敏史 -->
            <div class="space-y-3" v-if="healthStore.profile?.allergies?.length">
              <h3 class="text-lg font-semibold text-gray-800 border-b border-warmGray-200 pb-2">{{ legacyT('过敏史') }}</h3>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="allergy in healthStore.profile.allergies"
                  :key="allergy"
                  class="px-3 py-1.5 bg-red-50 text-red-700 rounded-full text-sm"
                >
                  {{ legacyT(allergy) }}
                </span>
              </div>
            </div>

            <!-- 慢性病史 -->
            <div class="space-y-3" v-if="healthStore.profile?.chronic_conditions?.length">
              <h3 class="text-lg font-semibold text-gray-800 border-b border-warmGray-200 pb-2">{{ legacyT('慢性病史') }}</h3>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="condition in healthStore.profile.chronic_conditions"
                  :key="condition"
                  class="px-3 py-1.5 bg-yellow-50 text-yellow-700 rounded-full text-sm"
                >
                  {{ legacyT(condition) }}
                </span>
              </div>
            </div>

            <!-- 紧急联系人 -->
            <div class="space-y-3" v-if="healthStore.profile?.emergency_contact?.name">
              <h3 class="text-lg font-semibold text-gray-800 border-b border-warmGray-200 pb-2">{{ legacyT('紧急联系人') }}</h3>
              <div class="grid gap-4 md:grid-cols-3">
                <div class="flex justify-between py-2">
                  <span class="text-gray-500">{{ legacyT('姓名') }}</span>
                  <span class="text-gray-800">{{ healthStore.profile.emergency_contact.name }}</span>
                </div>
                <div class="flex justify-between py-2">
                  <span class="text-gray-500">{{ legacyT('电话') }}</span>
                  <span class="text-gray-800">{{ healthStore.profile.emergency_contact.phone }}</span>
                </div>
                <div class="flex justify-between py-2">
                  <span class="text-gray-500">{{ legacyT('关系') }}</span>
                  <span class="text-gray-800">{{ healthStore.profile.emergency_contact.relationship }}</span>
                </div>
              </div>
            </div>

            <div class="flex justify-end">
              <button class="btn btn-secondary" @click="openProfileModal">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
                {{ lt('Edit profile', '编辑档案') }}
              </button>
            </div>
          </div>
        </div>

        <!-- 病历记录 Tab -->
        <div v-else-if="activeTab === 'medical'">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold text-gray-800">{{ legacyT('病历记录') }}</h3>
            <button class="btn btn-primary" @click="openMedicalModal()">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              {{ legacyT('添加记录') }}
            </button>
          </div>

          <div v-if="healthStore.medicalRecords.length === 0" class="text-center py-12">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-800 mb-2">{{ legacyT('暂无病历记录') }}</h3>
            <p class="text-gray-500">{{ legacyT('记录您的症状和诊断信息') }}</p>
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="record in healthStore.medicalRecords"
              :key="record.id"
              class="border border-warmGray-200 rounded-xl p-4 hover:shadow-md transition-shadow"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <span :class="['px-2 py-1 rounded-full text-xs font-medium', getRecordTypeColor(record.record_type)]">
                      {{ getRecordTypeLabel(record.record_type) }}
                    </span>
                    <span class="text-sm text-gray-500">{{ formatDate(record.record_date) }}</span>
                  </div>
                  <h4 class="font-semibold text-gray-800 mb-1">{{ record.title }}</h4>
                  <p class="text-gray-600 text-sm line-clamp-2">{{ record.description }}</p>
                  <div v-if="record.symptoms?.length" class="flex flex-wrap gap-1 mt-2">
                    <span
                      v-for="symptom in record.symptoms.slice(0, 3)"
                      :key="symptom"
                      class="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
                    >
                      {{ legacyT(symptom) }}
                    </span>
                    <span v-if="record.symptoms.length > 3" class="text-xs text-gray-400">
                      +{{ record.symptoms.length - 3 }}
                    </span>
                  </div>
                  <div v-if="record.hospital_name || record.doctor_name" class="mt-2 text-sm text-gray-500">
                    <span v-if="record.hospital_name">{{ record.hospital_name }}</span>
                    <span v-if="record.hospital_name && record.doctor_name"> · </span>
                    <span v-if="record.doctor_name">{{ record.doctor_name }}</span>
                  </div>
                </div>
                <div class="flex items-center gap-2 ml-4">
                  <button
                    class="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    @click="openMedicalModal(record)"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                      />
                    </svg>
                  </button>
                  <button
                    class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    @click="deleteMedicalRecord(record.id)"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 家族病史 Tab -->
        <div v-else-if="activeTab === 'family'">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold text-gray-800">{{ legacyT('家族病史') }}</h3>
            <button class="btn btn-primary" @click="openFamilyModal">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              {{ legacyT('添加记录') }}
            </button>
          </div>

          <!-- 帕金森家族史提示 -->
          <div
            v-if="healthStore.hasFamilyParkinsons"
            class="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-xl flex items-start gap-3"
          >
            <svg class="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <div>
              <p class="font-medium text-yellow-800">{{ legacyT('存在帕金森病家族史') }}</p>
              <p class="text-sm text-yellow-700 mt-1">{{ legacyT('您的家族中有帕金森病患者，请定期进行相关检查。') }}</p>
            </div>
          </div>

          <div v-if="healthStore.familyHistory.length === 0" class="text-center py-12">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-800 mb-2">{{ legacyT('暂无家族病史') }}</h3>
            <p class="text-gray-500">{{ legacyT('记录家族成员的健康状况') }}</p>
          </div>

          <div v-else class="grid gap-4 md:grid-cols-2">
            <div
              v-for="history in healthStore.familyHistory"
              :key="history.id"
              class="border border-warmGray-200 rounded-xl p-4"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <span class="font-semibold text-gray-800">
                      {{ getRelationshipLabel(history.relationship) }}
                      <span v-if="history.relationship_detail" class="font-normal text-gray-500">
                        ({{ history.relationship_detail }})
                      </span>
                    </span>
                    <span
                      v-if="history.has_parkinsons"
                      class="px-2 py-0.5 bg-red-100 text-red-700 rounded-full text-xs font-medium"
                    >
                      {{ legacyT('帕金森') }}
                    </span>
                  </div>
                  <p class="text-gray-600">{{ history.condition }}</p>
                  <p v-if="history.onset_age" class="text-sm text-gray-500 mt-1">{{ legacyT('发病年龄：') }}{{ history.onset_age }} {{ legacyT('岁') }}</p>
                  <p v-if="history.notes" class="text-sm text-gray-500 mt-1">{{ history.notes }}</p>
                </div>
                <button
                  class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  @click="deleteFamilyHistory(history.id)"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 就诊记录 Tab -->
        <div v-else-if="activeTab === 'visits'">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold text-gray-800">{{ legacyT('就诊记录') }}</h3>
            <button class="btn btn-primary" @click="openVisitModal()">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              {{ legacyT('添加记录') }}
            </button>
          </div>

          <!-- 即将复诊提醒 -->
          <div
            v-if="healthStore.upcomingFollowUps.length > 0"
            class="mb-6 p-4 bg-primary-50 border border-primary-200 rounded-xl"
          >
            <h4 class="font-medium text-primary-800 mb-2 flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              {{ legacyT('即将到来的复诊') }}
            </h4>
            <div class="space-y-2">
              <div
                v-for="followUp in healthStore.upcomingFollowUps"
                :key="followUp.id"
                class="flex items-center justify-between text-sm"
              >
                <span class="text-primary-700">
                  {{ formatDate(followUp.follow_up_date!) }} - {{ followUp.hospital_name }}
                </span>
                <span class="text-primary-600">{{ followUp.doctor_name }}</span>
              </div>
            </div>
          </div>

          <div v-if="healthStore.visitRecords.length === 0" class="text-center py-12">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-800 mb-2">{{ legacyT('暂无就诊记录') }}</h3>
            <p class="text-gray-500">{{ legacyT('记录您的就诊和处方信息') }}</p>
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="visit in healthStore.visitRecords"
              :key="visit.id"
              class="border border-warmGray-200 rounded-xl p-4 hover:shadow-md transition-shadow"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <span :class="['px-2 py-1 rounded-full text-xs font-medium', getVisitTypeColor(visit.visit_type)]">
                      {{ getVisitTypeLabel(visit.visit_type) }}
                    </span>
                    <span class="text-sm text-gray-500">{{ formatDate(visit.visit_date) }}</span>
                  </div>
                  <h4 class="font-semibold text-gray-800">{{ visit.hospital_name }}</h4>
                  <div class="text-sm text-gray-500 mt-1">
                    <span v-if="visit.department">{{ visit.department }}</span>
                    <span v-if="visit.department && visit.doctor_name"> · </span>
                    <span v-if="visit.doctor_name">{{ visit.doctor_name }} {{ legacyT('医生') }}</span>
                  </div>
                  <p class="text-gray-600 text-sm mt-2">{{ visit.chief_complaint }}</p>
                  <p v-if="visit.diagnosis" class="text-sm mt-2">
                    <span class="text-gray-500">{{ legacyT('诊断：') }}</span>
                    <span class="text-gray-800">{{ visit.diagnosis }}</span>
                  </p>
                  <div v-if="visit.prescriptions?.length" class="mt-3">
                    <p class="text-sm text-gray-500 mb-1">{{ legacyT('处方：') }}</p>
                    <div class="flex flex-wrap gap-2">
                      <span
                        v-for="(rx, idx) in visit.prescriptions.slice(0, 3)"
                        :key="idx"
                        class="px-2 py-1 bg-green-50 text-green-700 rounded text-xs"
                      >
                        {{ rx.medication }} {{ rx.dosage }}
                      </span>
                      <span v-if="visit.prescriptions.length > 3" class="text-xs text-gray-400">
                        +{{ visit.prescriptions.length - 3 }}
                      </span>
                    </div>
                  </div>
                  <div
                    v-if="visit.follow_up_date"
                    class="mt-3 flex items-center gap-2 text-sm text-primary-600"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                    {{ legacyT('复诊日期：') }}{{ formatDate(visit.follow_up_date) }}
                  </div>
                </div>
                <div class="flex items-center gap-2 ml-4">
                  <button
                    class="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    @click="openVisitModal(visit)"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                      />
                    </svg>
                  </button>
                  <button
                    class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    @click="deleteVisitRecord(visit.id)"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 档案编辑弹窗 -->
    <Teleport to="body">
      <div
        v-if="showProfileModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showProfileModal = false"
      >
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
          <div class="p-6 border-b border-warmGray-200">
            <h3 class="text-xl font-semibold text-gray-800">
              {{ healthStore.hasProfile ? legacyT('编辑健康档案') : legacyT('创建健康档案') }}
            </h3>
          </div>

          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <!-- 基本信息 -->
            <div class="space-y-4">
              <h4 class="font-medium text-gray-700">{{ legacyT('基本信息') }}</h4>
              <div class="grid gap-4 md:grid-cols-2">
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">{{ legacyT('性别') }}</label>
                  <div class="flex gap-2">
                    <button
                      v-for="opt in genderOptions"
                      :key="opt.value"
                      type="button"
                      @click="profileForm.gender = opt.value as any"
                      :class="[
                        'flex-1 px-4 py-2 rounded-lg border text-sm font-medium transition-all',
                        profileForm.gender === opt.value
                          ? 'border-primary-500 bg-primary-50 text-primary-700'
                          : 'border-warmGray-200 text-gray-600 hover:bg-gray-50',
                      ]"
                    >
                      {{ opt.label }}
                    </button>
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">{{ legacyT('出生日期') }}</label>
                  <input
                    v-model="profileForm.birth_date"
                    type="date"
                    class="input"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">{{ legacyT('身高 (cm)') }}</label>
                  <input
                    v-model.number="profileForm.height_cm"
                    type="number"
                    class="input"
                    :placeholder="legacyT('例如：170')"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">{{ legacyT('体重 (kg)') }}</label>
                  <input
                    v-model.number="profileForm.weight_kg"
                    type="number"
                    class="input"
                    :placeholder="legacyT('例如：65')"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">{{ legacyT('血型') }}</label>
                  <select v-model="profileForm.blood_type" class="input">
                    <option value="">{{ legacyT('请选择') }}</option>
                    <option v-for="bt in bloodTypeOptions" :key="bt" :value="bt">{{ bt === '未知' ? legacyT(bt) : bt }}</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- 疾病信息 -->
            <div class="space-y-4">
              <h4 class="font-medium text-gray-700">{{ legacyT('疾病信息') }}</h4>
              <div class="grid gap-4 md:grid-cols-2">
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">{{ legacyT('确诊日期') }}</label>
                  <input
                    v-model="profileForm.diagnosis_date"
                    type="date"
                    class="input"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">{{ legacyT('Hoehn-Yahr 分期') }}</label>
                  <select v-model.number="profileForm.hoehn_yahr_stage" class="input">
                    <option value="">{{ legacyT('请选择') }}</option>
                    <option v-for="(stage, key) in HOEHN_YAHR_STAGES" :key="key" :value="key">
                      {{ getHoehnYahrStageMeta(Number(key))?.label || stage.label }} - {{ getHoehnYahrStageMeta(Number(key))?.description || stage.description }}
                    </option>
                  </select>
                </div>
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-600 mb-1">{{ legacyT('受累侧') }}</label>
                  <div class="flex gap-2">
                    <button
                      v-for="opt in affectedSideOptions"
                      :key="opt.value"
                      type="button"
                      @click="profileForm.affected_side = opt.value as any"
                      :class="[
                        'flex-1 px-4 py-2 rounded-lg border text-sm font-medium transition-all',
                        profileForm.affected_side === opt.value
                          ? 'border-primary-500 bg-primary-50 text-primary-700'
                          : 'border-warmGray-200 text-gray-600 hover:bg-gray-50',
                      ]"
                    >
                      {{ opt.label }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 主要症状 -->
            <div class="space-y-3">
              <h4 class="font-medium text-gray-700">{{ legacyT('主要症状') }}</h4>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="symptom in commonSymptoms"
                  :key="symptom"
                  type="button"
                  @click="toggleSymptom(symptom)"
                  :class="[
                    'px-3 py-1.5 rounded-full text-sm font-medium transition-all',
                    profileForm.primary_symptoms?.includes(symptom)
                      ? 'bg-primary-500 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
                  ]"
                >
                  {{ legacyT(symptom) }}
                </button>
              </div>
            </div>

            <!-- 过敏史 -->
            <div class="space-y-3">
              <h4 class="font-medium text-gray-700">{{ legacyT('过敏史') }}</h4>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="allergy in commonAllergies"
                  :key="allergy"
                  type="button"
                  @click="toggleAllergy(allergy)"
                  :class="[
                    'px-3 py-1.5 rounded-full text-sm font-medium transition-all',
                    profileForm.allergies?.includes(allergy)
                      ? 'bg-red-500 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
                  ]"
                >
                  {{ legacyT(allergy) }}
                </button>
              </div>
            </div>

            <!-- 慢性病史 -->
            <div class="space-y-3">
              <h4 class="font-medium text-gray-700">{{ legacyT('慢性病史') }}</h4>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="condition in commonConditions"
                  :key="condition"
                  type="button"
                  @click="toggleCondition(condition)"
                  :class="[
                    'px-3 py-1.5 rounded-full text-sm font-medium transition-all',
                    profileForm.chronic_conditions?.includes(condition)
                      ? 'bg-yellow-500 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
                  ]"
                >
                  {{ legacyT(condition) }}
                </button>
              </div>
            </div>

            <!-- 紧急联系人 -->
            <div class="space-y-4">
              <h4 class="font-medium text-gray-700">{{ legacyT('紧急联系人') }}</h4>
              <div class="grid gap-4 md:grid-cols-3">
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">{{ legacyT('姓名') }}</label>
                  <input
                    v-model="profileForm.emergency_contact!.name"
                    type="text"
                    class="input"
                    :placeholder="legacyT('联系人姓名')"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">{{ legacyT('电话') }}</label>
                  <input
                    v-model="profileForm.emergency_contact!.phone"
                    type="tel"
                    class="input"
                    :placeholder="legacyT('联系人电话')"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-600 mb-1">{{ legacyT('关系') }}</label>
                  <input
                    v-model="profileForm.emergency_contact!.relationship"
                    type="text"
                    class="input"
                    :placeholder="legacyT('如：配偶、子女')"
                  />
                </div>
              </div>
            </div>

            <!-- 备注 -->
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">{{ legacyT('备注') }}</label>
              <textarea
                v-model="profileForm.notes"
                rows="3"
                class="input"
                :placeholder="legacyT('其他需要记录的信息...')"
              ></textarea>
            </div>
          </div>

          <div class="p-6 border-t border-warmGray-200 flex justify-end gap-3">
            <button class="btn btn-secondary" @click="showProfileModal = false">{{ legacyT('取消') }}</button>
            <button class="btn btn-primary" @click="saveProfile" :disabled="healthStore.loading">
              {{ healthStore.loading ? legacyT('保存中...') : legacyT('保存') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 病历记录弹窗 -->
    <Teleport to="body">
      <div
        v-if="showMedicalModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showMedicalModal = false"
      >
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-hidden flex flex-col">
          <div class="p-6 border-b border-warmGray-200">
            <h3 class="text-xl font-semibold text-gray-800">
              {{ editingMedical ? '编辑病历' : '添加病历' }}
            </h3>
          </div>

          <div class="flex-1 overflow-y-auto p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">记录类型</label>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="opt in recordTypeOptions"
                  :key="opt.value"
                  type="button"
                  @click="medicalForm.record_type = opt.value as any"
                  :class="[
                    'px-3 py-1.5 rounded-lg border text-sm font-medium transition-all',
                    medicalForm.record_type === opt.value
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-warmGray-200 text-gray-600 hover:bg-gray-50',
                  ]"
                >
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">记录日期 *</label>
              <input v-model="medicalForm.record_date" type="date" class="input" required />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">标题 *</label>
              <input v-model="medicalForm.title" type="text" class="input" placeholder="简要描述" required />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">详细描述 *</label>
              <textarea
                v-model="medicalForm.description"
                rows="3"
                class="input"
                placeholder="详细描述症状或诊断..."
                required
              ></textarea>
            </div>

            <div v-if="medicalForm.record_type === 'symptom'">
              <label class="block text-sm font-medium text-gray-600 mb-1">相关症状</label>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="symptom in commonSymptoms"
                  :key="symptom"
                  type="button"
                  @click="toggleMedicalSymptom(symptom)"
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium transition-all',
                    medicalForm.symptoms?.includes(symptom)
                      ? 'bg-primary-500 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
                  ]"
                >
                  {{ symptom }}
                </button>
              </div>
            </div>

            <div v-if="medicalForm.record_type === 'symptom'">
              <label class="block text-sm font-medium text-gray-600 mb-1">严重程度 (1-10)</label>
              <input
                v-model.number="medicalForm.severity"
                type="range"
                min="1"
                max="10"
                class="w-full"
              />
              <div class="flex justify-between text-xs text-gray-500">
                <span>轻微</span>
                <span>{{ medicalForm.severity || '-' }}</span>
                <span>严重</span>
              </div>
            </div>

            <div v-if="medicalForm.record_type === 'diagnosis'">
              <label class="block text-sm font-medium text-gray-600 mb-1">诊断结果</label>
              <input v-model="medicalForm.diagnosis" type="text" class="input" placeholder="诊断结论" />
            </div>

            <div class="grid gap-4 md:grid-cols-2">
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1">医院</label>
                <input v-model="medicalForm.hospital_name" type="text" class="input" placeholder="医院名称" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1">医生</label>
                <input v-model="medicalForm.doctor_name" type="text" class="input" placeholder="医生姓名" />
              </div>
            </div>

            <!-- 附件上传 -->
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <label class="text-sm font-medium text-gray-600">附件（检查报告、图片等）</label>
                <label class="cursor-pointer">
                  <input
                    type="file"
                    class="hidden"
                    accept="image/*,.pdf,.doc,.docx"
                    @change="handleMedicalAttachmentUpload"
                    :disabled="uploadingMedicalAttachment"
                  />
                  <span
                    :class="[
                      'text-sm font-medium',
                      uploadingMedicalAttachment
                        ? 'text-gray-400 cursor-not-allowed'
                        : 'text-primary-600 hover:text-primary-700 cursor-pointer'
                    ]"
                  >
                    {{ uploadingMedicalAttachment ? '上传中...' : '+ 上传附件' }}
                  </span>
                </label>
              </div>
              <div v-if="medicalForm.attachments?.length" class="space-y-2">
                <div
                  v-for="(url, idx) in medicalForm.attachments"
                  :key="idx"
                  class="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                >
                  <div class="flex items-center gap-2 flex-1 min-w-0">
                    <div v-if="isImage(url)" class="w-10 h-10 rounded overflow-hidden flex-shrink-0">
                      <img :src="url" class="w-full h-full object-cover" />
                    </div>
                    <svg v-else class="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <a :href="url" target="_blank" class="text-sm text-primary-600 hover:underline truncate">
                      {{ getFileName(url) }}
                    </a>
                  </div>
                  <button
                    type="button"
                    @click="removeMedicalAttachment(idx)"
                    class="p-1 text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="p-6 border-t border-warmGray-200 flex justify-end gap-3">
            <button class="btn btn-secondary" @click="showMedicalModal = false">取消</button>
            <button
              class="btn btn-primary"
              @click="saveMedicalRecord"
              :disabled="healthStore.loading || !medicalForm.title || !medicalForm.description"
            >
              {{ healthStore.loading ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 家族病史弹窗 -->
    <Teleport to="body">
      <div
        v-if="showFamilyModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showFamilyModal = false"
      >
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md">
          <div class="p-6 border-b border-warmGray-200">
            <h3 class="text-xl font-semibold text-gray-800">添加家族病史</h3>
          </div>

          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">亲属关系 *</label>
              <select v-model="familyForm.relationship" class="input">
                <option v-for="opt in relationshipOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>

            <div v-if="familyForm.relationship === 'other'">
              <label class="block text-sm font-medium text-gray-600 mb-1">具体关系</label>
              <input v-model="familyForm.relationship_detail" type="text" class="input" placeholder="如：叔叔、表兄" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">疾病/健康状况 *</label>
              <input v-model="familyForm.condition" type="text" class="input" placeholder="如：高血压、糖尿病" required />
            </div>

            <div class="flex items-center gap-3">
              <input
                v-model="familyForm.has_parkinsons"
                type="checkbox"
                id="has_parkinsons"
                class="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
              />
              <label for="has_parkinsons" class="text-sm text-gray-700">患有帕金森病</label>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">发病年龄</label>
              <input v-model.number="familyForm.onset_age" type="number" class="input" placeholder="岁" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">备注</label>
              <textarea v-model="familyForm.notes" rows="2" class="input" placeholder="其他信息..."></textarea>
            </div>
          </div>

          <div class="p-6 border-t border-warmGray-200 flex justify-end gap-3">
            <button class="btn btn-secondary" @click="showFamilyModal = false">取消</button>
            <button
              class="btn btn-primary"
              @click="saveFamilyHistory"
              :disabled="healthStore.loading || !familyForm.condition"
            >
              {{ healthStore.loading ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 就诊记录弹窗 -->
    <Teleport to="body">
      <div
        v-if="showVisitModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showVisitModal = false"
      >
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
          <div class="p-6 border-b border-warmGray-200">
            <h3 class="text-xl font-semibold text-gray-800">
              {{ editingVisit ? '编辑就诊记录' : '添加就诊记录' }}
            </h3>
          </div>

          <div class="flex-1 overflow-y-auto p-6 space-y-4">
            <div class="grid gap-4 md:grid-cols-2">
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1">就诊日期 *</label>
                <input v-model="visitForm.visit_date" type="date" class="input" required />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1">就诊类型</label>
                <select v-model="visitForm.visit_type" class="input">
                  <option v-for="opt in visitTypeOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
              </div>
            </div>

            <div class="grid gap-4 md:grid-cols-2">
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1">医院名称 *</label>
                <input v-model="visitForm.hospital_name" type="text" class="input" placeholder="医院名称" required />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1">科室</label>
                <input v-model="visitForm.department" type="text" class="input" placeholder="如：神经内科" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">医生姓名</label>
              <input v-model="visitForm.doctor_name" type="text" class="input" placeholder="主治医生" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">主诉 *</label>
              <textarea
                v-model="visitForm.chief_complaint"
                rows="2"
                class="input"
                placeholder="就诊原因和主要症状..."
                required
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">诊断结果</label>
              <input v-model="visitForm.diagnosis" type="text" class="input" placeholder="医生诊断" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">治疗方案</label>
              <textarea
                v-model="visitForm.treatment_plan"
                rows="2"
                class="input"
                placeholder="治疗建议和方案..."
              ></textarea>
            </div>

            <!-- 处方列表 -->
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <label class="text-sm font-medium text-gray-600">处方药物</label>
                <button type="button" class="text-sm text-primary-600 hover:text-primary-700" @click="addPrescription">
                  + 添加药物
                </button>
              </div>
              <div v-for="(rx, idx) in visitForm.prescriptions" :key="idx" class="p-3 bg-gray-50 rounded-lg space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm font-medium text-gray-700">药物 {{ idx + 1 }}</span>
                  <button
                    type="button"
                    class="text-red-500 hover:text-red-600 text-sm"
                    @click="removePrescription(idx)"
                  >
                    删除
                  </button>
                </div>
                <div class="grid gap-2 md:grid-cols-2">
                  <input v-model="rx.medication" type="text" class="input text-sm" placeholder="药物名称" />
                  <input v-model="rx.dosage" type="text" class="input text-sm" placeholder="剂量 (如: 25mg)" />
                  <input v-model="rx.frequency" type="text" class="input text-sm" placeholder="用法 (如: 每日3次)" />
                  <input v-model="rx.duration" type="text" class="input text-sm" placeholder="疗程 (如: 2周)" />
                </div>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">复诊日期</label>
              <input v-model="visitForm.follow_up_date" type="date" class="input" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1">备注</label>
              <textarea v-model="visitForm.notes" rows="2" class="input" placeholder="其他需要记录的信息..."></textarea>
            </div>

            <!-- 附件上传 -->
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <label class="text-sm font-medium text-gray-600">附件（病历、检查单、处方等）</label>
                <label class="cursor-pointer">
                  <input
                    type="file"
                    class="hidden"
                    accept="image/*,.pdf,.doc,.docx"
                    @change="handleVisitAttachmentUpload"
                    :disabled="uploadingVisitAttachment"
                  />
                  <span
                    :class="[
                      'text-sm font-medium',
                      uploadingVisitAttachment
                        ? 'text-gray-400 cursor-not-allowed'
                        : 'text-primary-600 hover:text-primary-700 cursor-pointer'
                    ]"
                  >
                    {{ uploadingVisitAttachment ? '上传中...' : '+ 上传附件' }}
                  </span>
                </label>
              </div>
              <div v-if="visitForm.attachments?.length" class="space-y-2">
                <div
                  v-for="(url, idx) in visitForm.attachments"
                  :key="idx"
                  class="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                >
                  <div class="flex items-center gap-2 flex-1 min-w-0">
                    <div v-if="isImage(url)" class="w-10 h-10 rounded overflow-hidden flex-shrink-0">
                      <img :src="url" class="w-full h-full object-cover" />
                    </div>
                    <svg v-else class="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <a :href="url" target="_blank" class="text-sm text-primary-600 hover:underline truncate">
                      {{ getFileName(url) }}
                    </a>
                  </div>
                  <button
                    type="button"
                    @click="removeVisitAttachment(idx)"
                    class="p-1 text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="p-6 border-t border-warmGray-200 flex justify-end gap-3">
            <button class="btn btn-secondary" @click="showVisitModal = false">取消</button>
            <button
              class="btn btn-primary"
              @click="saveVisitRecord"
              :disabled="healthStore.loading || !visitForm.hospital_name || !visitForm.chief_complaint"
            >
              {{ healthStore.loading ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </AppLayout>
</template>
