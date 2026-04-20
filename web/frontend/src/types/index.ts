import { legacyT, localeText, severityLabel } from '@/i18n'

// ============================================================
// User Types
// ============================================================

export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  role: 'user' | 'doctor' | 'admin'
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

// ============================================================
// Device Types
// ============================================================

export interface Device {
  id: number
  device_id: string
  name?: string
  firmware_version?: string
  hardware_version?: string
  mac_address?: string
  is_online: boolean
  battery_level?: number
  last_seen?: string
  created_at: string
}

// ============================================================
// Tremor Data Types
// ============================================================

export interface TremorData {
  id: number
  session_id: number
  timestamp: string
  detected: boolean
  valid: boolean
  out_of_range: boolean
  frequency?: number
  peak_power?: number
  band_power?: number
  amplitude?: number
  rms_amplitude?: number
  severity: number
  severity_label?: string
}

export interface TremorSession {
  id: number
  user_id: number
  device_id: number
  start_time: string
  end_time?: string
  duration_seconds?: number
  total_analyses: number
  tremor_count: number
  avg_frequency?: number
  avg_amplitude?: number
  max_severity: number
  avg_severity?: number
  is_active: boolean
}

// ============================================================
// Analysis Types
// ============================================================

export interface DailyStats {
  date: string
  total_sessions: number
  total_analyses: number
  tremor_detections: number
  detection_rate: number
  avg_frequency?: number
  avg_amplitude?: number
  avg_severity?: number
  max_severity: number
}

export interface SeverityDistribution {
  level_0: number
  level_1: number
  level_2: number
  level_3: number
  level_4: number
  total: number
}

export interface WeeklyTrend {
  week_start: string
  week_end: string
  daily_stats: DailyStats[]
  overall_detection_rate: number
  severity_trend: 'improving' | 'stable' | 'worsening'
}

// ============================================================
// AI Types
// ============================================================

export interface AIAnalysisResponse {
  analysis_id: string
  timestamp: string
  analysis_type: string
  summary: string
  detailed_analysis: string
  key_findings: string[]
  recommendations: string[]
  risk_assessment: string
  confidence_score: number
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  action_card?: AIActionCard
}

export type AIActionType =
  | 'confirm_rehab_plan'
  | 'view_rehab_page'
  | 'download_rehab_pdf'
  | 'confirm_health_report'
  | 'view_health_report'
  | 'download_health_report_pdf'

export interface AIAction {
  type: AIActionType
  label: string
  api_path?: string
  route?: string
}

export interface AIActionCard {
  kind: 'rehab_plan' | 'health_report'
  title: string
  summary: string
  status: 'preview' | 'generated'
  payload?: Record<string, unknown>
  actions: AIAction[]
}

// ============================================================
// Report Types
// ============================================================

export type ReportFormat = 'pdf' | 'json' | 'csv'
export type ReportType = 'daily' | 'weekly' | 'monthly' | 'custom'

export interface ReportMetadata {
  report_id: string
  report_type: ReportType
  format: ReportFormat
  generated_at: string
  period_start: string
  period_end: string
  file_size?: number
  download_url?: string
}

// ============================================================
// Severity Helpers
// ============================================================

export const SEVERITY_LABELS: Record<number, string> = {
  0: 'Stable',
  1: 'Mild',
  2: 'Moderate',
  3: 'Elevated',
  4: 'Severe',
}

export const SEVERITY_COLORS: Record<number, string> = {
  0: '#10b981', // green
  1: '#84cc16', // lime
  2: '#eab308', // yellow
  3: '#f97316', // orange
  4: '#ef4444', // red
}

export function getSeverityLabel(severity: number): string {
  return severityLabel(severity) || SEVERITY_LABELS[severity] || severityLabel(-1)
}

export function getSeverityColor(severity: number): string {
  return SEVERITY_COLORS[severity] || '#6b7280'
}

// ============================================================
// Medication Types (用药关联模块)
// ============================================================

export type MedicationFrequency =
  | 'once_daily'
  | 'twice_daily'
  | 'three_times_daily'
  | 'four_times_daily'
  | 'as_needed'
  | 'custom'

export interface Medication {
  id: number
  user_id: number
  name: string
  generic_name?: string
  dosage: string
  frequency: MedicationFrequency
  times_per_day: number
  scheduled_times: string[]
  start_date: string
  end_date?: string
  purpose?: string
  notes?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface DosageRecord {
  id: number
  medication_id: number
  user_id: number
  taken_at: string
  scheduled_time?: string
  dosage_taken: string
  status: 'taken' | 'missed' | 'skipped'
  notes?: string
  side_effects?: string
  created_at: string
}

export interface MedicationReminder {
  id: number
  medication_id: number
  user_id: number
  reminder_time: string
  is_enabled: boolean
  notification_type: 'push' | 'email' | 'both'
  advance_minutes: number
  created_at: string
}

export interface MedicationEffectiveness {
  date: string
  medication_id: number
  medication_name: string
  dosage_times: string[]
  tremor_data: {
    time: string
    severity: number
    frequency?: number
  }[]
  avg_severity_before: number
  avg_severity_after: number
  effectiveness_score: number
}

export interface MedicationCreateRequest {
  name: string
  generic_name?: string
  dosage: string
  frequency: MedicationFrequency
  times_per_day: number
  scheduled_times: string[]
  start_date: string
  end_date?: string
  purpose?: string
  notes?: string
}

export interface DosageRecordCreateRequest {
  medication_id: number
  taken_at?: string
  scheduled_time?: string
  dosage_taken: string
  status: 'taken' | 'missed' | 'skipped'
  notes?: string
  side_effects?: string
}

export const MEDICATION_FREQUENCY_LABELS: Record<
  MedicationFrequency,
  { en: string; zh: string }
> = {
  once_daily: { en: 'Once daily', zh: '每日一次' },
  twice_daily: { en: 'Twice daily', zh: '每日两次' },
  three_times_daily: { en: 'Three times daily', zh: '每日三次' },
  four_times_daily: { en: 'Four times daily', zh: '每日四次' },
  as_needed: { en: 'As needed', zh: '按需服用' },
  custom: { en: 'Custom', zh: '自定义' },
}

export function getMedicationFrequencyLabel(frequency: MedicationFrequency): string {
  const label = MEDICATION_FREQUENCY_LABELS[frequency]
  if (!label) {
    return legacyT(frequency)
  }
  return localeText(label.en, label.zh)
}

// ============================================================
// Health Profile Types (健康档案模块)
// ============================================================

export interface HealthProfile {
  id: number
  user_id: number
  birth_date?: string
  gender?: 'male' | 'female' | 'other'
  height_cm?: number
  weight_kg?: number
  blood_type?: string
  diagnosis_date?: string
  hoehn_yahr_stage?: number
  primary_symptoms: string[]
  affected_side?: 'left' | 'right' | 'both'
  allergies: string[]
  chronic_conditions: string[]
  emergency_contact?: {
    name: string
    phone: string
    relationship: string
  }
  notes?: string
  created_at: string
  updated_at: string
}

export interface MedicalRecord {
  id: number
  user_id: number
  record_date: string
  record_type: 'symptom' | 'diagnosis' | 'test_result' | 'note'
  title: string
  description: string
  symptoms?: string[]
  diagnosis?: string
  severity?: number
  attachments?: string[]
  doctor_name?: string
  hospital_name?: string
  created_at: string
}

export interface FamilyHistory {
  id: number
  user_id: number
  relationship: 'parent' | 'sibling' | 'grandparent' | 'other'
  relationship_detail?: string
  condition: string
  has_parkinsons: boolean
  onset_age?: number
  notes?: string
  created_at: string
}

export interface VisitRecord {
  id: number
  user_id: number
  visit_date: string
  hospital_name: string
  department?: string
  doctor_name?: string
  visit_type: 'routine' | 'emergency' | 'follow_up' | 'specialist'
  chief_complaint: string
  diagnosis?: string
  treatment_plan?: string
  prescriptions?: {
    medication: string
    dosage: string
    frequency: string
    duration?: string
  }[]
  follow_up_date?: string
  notes?: string
  attachments?: string[]
  created_at: string
}

export const HOEHN_YAHR_STAGES: Record<number, { label: string; description: string }> = {
  1: { label: 'I期', description: '单侧受累，功能损害轻微或无' },
  2: { label: 'II期', description: '双侧或中线受累，无平衡障碍' },
  3: { label: 'III期', description: '轻至中度双侧受累，有姿势不稳' },
  4: { label: 'IV期', description: '严重残疾，仍能独立行走或站立' },
  5: { label: 'V期', description: '需要轮椅或卧床' },
}

export function getHoehnYahrStageMeta(stage?: number | null) {
  if (!stage || !HOEHN_YAHR_STAGES[stage]) {
    return undefined
  }

  const value = HOEHN_YAHR_STAGES[stage]
  return {
    label: legacyT(value.label),
    description: legacyT(value.description),
  }
}

export const VISIT_TYPE_LABELS: Record<string, string> = {
  routine: '常规复诊',
  emergency: '急诊',
  follow_up: '随访',
  specialist: '专家门诊',
}

export function getVisitTypeLabel(type: string): string {
  return legacyT(VISIT_TYPE_LABELS[type] || type)
}

// ============================================================
// Rehabilitation Types (运动康复模块)
// ============================================================

export type ExerciseCategory =
  | 'stretching'
  | 'balance'
  | 'strength'
  | 'coordination'
  | 'facial'
  | 'voice'
  | 'walking'
  | 'tai_chi'
  | 'yoga'
  | 'breathing'

export interface Exercise {
  id: number
  name: string
  category: ExerciseCategory
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  duration_minutes: number
  description: string
  benefits: string[]
  instructions: string[]
  precautions?: string[]
  video_url?: string
  thumbnail_url?: string
  target_symptoms: string[]
  recommended_frequency: string
  equipment_needed?: string[]
  created_at: string
}

export interface TrainingPlan {
  id: number
  user_id: number
  name: string
  description?: string
  exercises: TrainingPlanExercise[]
  schedule: {
    days_of_week: number[]
    time_of_day?: string
  }
  is_active: boolean
  start_date: string
  end_date?: string
  created_at: string
  updated_at: string
}

export interface TrainingPlanExercise {
  exercise_id: number
  exercise?: Exercise
  order: number
  sets?: number
  reps?: number
  duration_minutes?: number
  notes?: string
}

export interface TrainingCheckIn {
  id: number
  user_id: number
  plan_id?: number
  date: string
  exercises_completed: {
    exercise_id: number
    exercise_name: string
    completed: boolean
    sets_done?: number
    duration_minutes?: number
    difficulty_rating?: number
    notes?: string
  }[]
  total_duration_minutes: number
  mood_before?: number
  mood_after?: number
  tremor_before?: number
  tremor_after?: number
  overall_rating?: number
  notes?: string
  created_at: string
}

export interface TrainingStats {
  total_check_ins: number
  total_duration_minutes: number
  current_streak: number
  longest_streak: number
  weekly_summary: {
    week_start: string
    days_trained: number
    total_minutes: number
    exercises_completed: number
  }[]
  favorite_exercises: {
    exercise_id: number
    exercise_name: string
    count: number
  }[]
  avg_mood_improvement: number
  avg_tremor_improvement: number
}

export const EXERCISE_CATEGORY_LABELS: Record<ExerciseCategory, string> = {
  stretching: 'Stretching',
  balance: 'Balance',
  strength: 'Strength',
  coordination: 'Coordination',
  facial: 'Facial',
  voice: 'Voice',
  walking: 'Walking',
  tai_chi: 'Tai Chi',
  yoga: 'Yoga',
  breathing: 'Breathing',
}

export const DIFFICULTY_LABELS: Record<string, string> = {
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  advanced: 'Advanced',
}

// ============================================================
// Enhanced AI Types (AI医生增强模块)
// ============================================================

export interface DailyAnalysis {
  date: string
  summary: string
  tremor_summary: {
    total_detections: number
    avg_severity: number
    max_severity: number
    trend: 'better' | 'same' | 'worse'
    comparison_text: string
  }
  key_observations: string[]
  concerns: string[]
  positive_notes: string[]
  recommendations: string[]
  medication_notes?: string
  exercise_notes?: string
  generated_at: string
}

export interface PersonalizedAdvice {
  advice_id: string
  category: 'lifestyle' | 'exercise' | 'medication' | 'diet' | 'sleep' | 'mental'
  title: string
  content: string
  priority: 'high' | 'medium' | 'low'
  based_on: string[]
  action_items: string[]
  related_data?: {
    type: string
    value: string
  }[]
  generated_at: string
}

export interface DoctorVisitReport {
  report_id: string
  generated_at: string
  period: {
    start: string
    end: string
    days: number
  }
  patient_info: {
    name: string
    age?: number
    diagnosis_years?: number
    hoehn_yahr_stage?: number
  }
  summary: {
    executive_summary: string
    key_metrics: {
      metric: string
      value: string
      trend: string
    }[]
  }
  tremor_analysis: {
    frequency_analysis: string
    severity_distribution: Record<number, number>
    peak_times: string[]
    notable_patterns: string[]
  }
  medication_analysis?: {
    current_medications: string[]
    effectiveness_summary: string
    concerns: string[]
  }
  exercise_analysis?: {
    compliance_rate: number
    favorite_exercises: string[]
    observed_benefits: string[]
  }
  ai_observations: string[]
  questions_for_doctor: string[]
  data_appendix: {
    daily_summaries: {
      date: string
      detections: number
      avg_severity: number
    }[]
  }
}

export interface AIConversationContext {
  conversation_id: string
  context_type: 'general' | 'tremor_analysis' | 'medication' | 'exercise' | 'symptom_check'
  data_references?: {
    type: string
    id?: number
    summary?: string
  }[]
}

export interface SymptomCheckRequest {
  symptoms: string[]
  duration: string
  severity: number
  associated_factors?: string[]
}

export interface SymptomCheckResponse {
  assessment: string
  possible_causes: string[]
  urgency_level: 'routine' | 'soon' | 'urgent'
  recommendations: string[]
  should_see_doctor: boolean
  related_to_parkinsons_likelihood: 'low' | 'medium' | 'high'
}

export const ADVICE_CATEGORY_LABELS: Record<string, string> = {
  lifestyle: '生活方式',
  exercise: '运动康复',
  medication: '用药管理',
  diet: '饮食营养',
  sleep: '睡眠质量',
  mental: '心理健康',
}

export const ADVICE_PRIORITY_COLORS: Record<string, string> = {
  high: '#ef4444',
  medium: '#f97316',
  low: '#10b981',
}
