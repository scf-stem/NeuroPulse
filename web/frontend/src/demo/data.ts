import type {
  ChatMessage,
  DailyAnalysis,
  PersonalizedAdvice,
  DoctorVisitReport,
  SymptomCheckResponse,
} from '@/types'

import { demoUser } from './index'

const now = new Date('2026-04-18T08:30:00Z')

export const demoDashboardSessions = [
  { id: 1, start: '14:30', duration: '15 min', tremors: 12, maxSeverity: 2, isActive: false },
  { id: 2, start: '10:15', duration: '20 min', tremors: 5, maxSeverity: 1, isActive: false },
  { id: 3, start: '08:45', duration: '10 min', tremors: 28, maxSeverity: 3, isActive: false },
]

export const demoDevices = [
  {
    id: 1,
    device_id: 'NP-AX92-001',
    name: 'Primary Wristband',
    firmware_version: 'v2.4.1',
    hardware_version: 'Rev B',
    mac_address: '8C:4B:14:92:00:11',
    is_online: true,
    battery_level: 87,
    last_seen: now.toISOString(),
    created_at: '2026-03-25T10:00:00Z',
  },
  {
    id: 2,
    device_id: 'NP-CLINIC-014',
    name: 'Clinic Backup Unit',
    firmware_version: 'v2.3.8',
    hardware_version: 'Rev B',
    mac_address: '8C:4B:14:92:00:99',
    is_online: false,
    battery_level: 42,
    last_seen: '2026-04-17T14:10:00Z',
    created_at: '2026-03-28T09:00:00Z',
  },
]

export const demoQuickStats = {
  today: { total_analyses: 42, tremor_count: 11, avg_severity: 1.6 },
  this_week: { total_analyses: 268, tremor_count: 74, avg_severity: 1.9 },
  this_month: { total_analyses: 1044, tremor_count: 261, avg_severity: 2.1 },
}

export const demoDoctorSummary = {
  patient_info: {
    username: demoUser.username,
    full_name: demoUser.full_name,
  },
  period: {
    start: '2026-04-11',
    end: '2026-04-18',
    days: 7,
  },
  summary: {
    total_monitoring_records: 268,
    tremor_episodes: 74,
    avg_severity: 1.9,
    max_severity: 3,
    severe_episodes: 6,
    severity_trend: 'stable' as const,
    frequency_trend: 'decreasing' as const,
  },
  comparison: {
    prev_period_tremors: 81,
    prev_period_avg_severity: 2.1,
    tremor_change_percent: -8.6,
    severity_change_percent: -9.5,
  },
  key_observations: [
    'Morning sessions show the most stable signal quality.',
    'High-severity episodes dropped after medication adherence improved.',
    'Resting tremor remains clustered in the 4.4-5.1 Hz range.',
  ],
  recommendations: [
    'Continue morning monitoring for another two weeks.',
    'Review medication timing against afternoon flare-ups.',
    'Maintain short guided dexterity practice after breakfast.',
  ],
}

export const demoGeneratedReport = {
  report_id: 'demo-report-001',
  report_type: 'weekly' as const,
  generated_at: now.toISOString(),
  summary: {
    period_start: '2026-04-11T00:00:00Z',
    period_end: '2026-04-18T00:00:00Z',
    total_sessions: 14,
    total_analyses: 268,
    tremor_detections: 74,
    detection_rate: 27.6,
    avg_severity: 1.9,
    max_severity: 3,
    total_duration_minutes: 214,
  },
  daily_breakdown: [
    { date: '2026-04-12', total: 38, tremors: 12, avg_severity: 2.0 },
    { date: '2026-04-13', total: 33, tremors: 8, avg_severity: 1.7 },
    { date: '2026-04-14', total: 41, tremors: 11, avg_severity: 2.1 },
    { date: '2026-04-15', total: 36, tremors: 10, avg_severity: 1.8 },
    { date: '2026-04-16', total: 37, tremors: 9, avg_severity: 1.9 },
    { date: '2026-04-17', total: 42, tremors: 13, avg_severity: 2.0 },
    { date: '2026-04-18', total: 41, tremors: 11, avg_severity: 1.8 },
  ],
  severity_distribution: { 0: 131, 1: 62, 2: 49, 3: 26, 4: 0 },
  hourly_pattern: Array.from({ length: 24 }, (_, hour) => ({
    hour,
    count: hour >= 7 && hour <= 20 ? 10 + (hour % 4) * 2 : 1,
    tremors: hour >= 9 && hour <= 18 ? 2 + (hour % 3) : 0,
  })),
  sessions: [
    {
      id: 101,
      start_time: '2026-04-18T08:45:00Z',
      end_time: '2026-04-18T09:02:00Z',
      duration_seconds: 1020,
      total_analyses: 24,
      tremor_count: 7,
      avg_severity: 1.8,
      max_severity: 3,
    },
    {
      id: 102,
      start_time: '2026-04-17T14:30:00Z',
      end_time: '2026-04-17T14:47:00Z',
      duration_seconds: 1020,
      total_analyses: 21,
      tremor_count: 4,
      avg_severity: 1.4,
      max_severity: 2,
    },
  ],
}

export const demoAiIntro: ChatMessage[] = [
  {
    role: 'assistant',
    content:
      'Hello, I am the Neuro Pulse assistant. I can summarize tremor trends, explain symptom patterns, and help draft clinician-ready notes.',
    timestamp: now.toISOString(),
  },
  {
    role: 'user',
    content: 'What stands out in my latest monitoring data?',
    timestamp: now.toISOString(),
  },
  {
    role: 'assistant',
    content:
      'Your latest demo data shows a stable average severity of 1.9 with fewer high-severity episodes than the previous week. Morning sessions remain the strongest window for baseline monitoring.',
    timestamp: now.toISOString(),
  },
]

export const demoAiResponse = {
  response:
    'The strongest signal cluster appears between 4.4 and 5.1 Hz, which is consistent with resting tremor behavior. The pattern is steady rather than rapidly worsening in this demo profile.',
  suggestions: [
    'How should I explain this to a clinician?',
    'What self-management steps help with resting tremor?',
    'How should I compare mornings vs afternoons?',
  ],
}

export const demoInsights = {
  insights: [
    'Morning sessions show the lowest variability.',
    'Late afternoon has the highest tremor detection rate.',
    'Severity remained stable after the latest medication schedule adjustment.',
  ],
  generated_at: now.toISOString(),
  period_days: 7,
}

export const demoHealthTips = {
  tips: [
    'Anchor one short monitoring session before breakfast.',
    'Pair medication logging with monitoring windows to see clearer trends.',
    'Use a short hand-stretch routine before fine-motor tasks.',
  ],
  personalized: true,
  generated_at: now.toISOString(),
}

export const demoDailyAnalysis: DailyAnalysis = {
  date: '2026-04-18',
  summary:
    'Signal quality remained stable with low-to-moderate tremor intensity and no prolonged severe episodes.',
  tremor_summary: {
    total_detections: 11,
    avg_severity: 1.6,
    max_severity: 3,
    trend: 'better',
    comparison_text: '比昨天更稳定',
  },
  key_observations: [
    '08:00-10:00 remains the steadiest monitoring window.',
    'Late afternoon still shows the highest tremor activity.',
    'No new sustained high-severity pattern appeared today.',
  ],
  concerns: [
    'The 15:00-17:00 window remains the most variable period.',
  ],
  positive_notes: [
    'No prolonged severe episode was recorded today.',
    'Morning baseline sessions kept a consistent waveform quality.',
  ],
  recommendations: [
    'Keep one short morning baseline session for another week.',
    'Log medication timing before the late-afternoon monitoring window.',
    'Share the trend summary with a clinician if afternoon variability grows.',
  ],
  medication_notes: 'The latest medication schedule appears to reduce high-severity spikes.',
  exercise_notes: 'Light dexterity practice after breakfast is correlating with steadier morning sessions.',
  generated_at: now.toISOString(),
}

export const demoPersonalizedAdvice: PersonalizedAdvice[] = [
  {
    advice_id: 'advice-1',
    title: 'Capture one early session',
    content: 'A short morning baseline session will make afternoon comparisons more reliable.',
    priority: 'medium',
    category: 'lifestyle',
    based_on: [
      'Morning sessions show the lowest variability in the last 7 days.',
      'Afternoon tremor activity remains the main comparison target.',
    ],
    action_items: [
      'Schedule a 5-minute check-in before breakfast.',
      'Repeat the same posture during afternoon follow-up sessions.',
    ],
    generated_at: now.toISOString(),
  },
  {
    advice_id: 'advice-2',
    title: 'Keep the wearable snug',
    content: 'Consistent strap fit improves waveform quality and confidence in severity scoring.',
    priority: 'low',
    category: 'exercise',
    based_on: [
      'Signal quality improves when strap tension is consistent.',
    ],
    action_items: [
      'Check strap fit before each monitoring session.',
      'Reposition the wearable if the waveform looks noisy.',
    ],
    generated_at: now.toISOString(),
  },
]

export const demoDoctorReport: DoctorVisitReport = {
  report_id: 'doctor-demo-001',
  generated_at: now.toISOString(),
  period: {
    start: '2026-03-19',
    end: '2026-04-18',
    days: 30,
  },
  patient_info: {
    name: demoUser.full_name || demoUser.username,
    age: 62,
    diagnosis_years: 4,
    hoehn_yahr_stage: 2,
  },
  summary: {
    executive_summary:
      'Over the last 30 days, the demo user showed a stable moderate tremor burden with fewer severe episodes in the last week.',
    key_metrics: [
      { metric: 'Average severity', value: '1.9 / 4', trend: 'Down from 2.1 last month' },
      { metric: 'Peak activity window', value: '15:00-17:00', trend: 'Unchanged' },
      { metric: 'High-severity episodes', value: '6', trend: 'Lower than prior period' },
    ],
  },
  tremor_analysis: {
    frequency_analysis:
      'Resting tremor remains clustered between 4.4 and 5.1 Hz, with afternoon variability still the most notable pattern.',
    severity_distribution: { 0: 131, 1: 62, 2: 49, 3: 26, 4: 0 },
    peak_times: ['09:00-10:00', '15:00-17:00'],
    notable_patterns: [
      'Morning sessions consistently produce the cleanest baselines.',
      'Late-afternoon variability increases when medication logging is incomplete.',
      'No evidence of sustained weekly worsening was observed in the demo profile.',
    ],
  },
  medication_analysis: {
    current_medications: ['Levodopa / Carbidopa', 'Evening dopamine agonist'],
    effectiveness_summary:
      'The current schedule appears to reduce severe spikes, though late-afternoon fluctuation remains present.',
    concerns: [
      'Medication timing is missing on several afternoon sessions.',
    ],
  },
  exercise_analysis: {
    compliance_rate: 82,
    favorite_exercises: ['Finger tapping sequence', 'Shoulder mobility flow'],
    observed_benefits: [
      'Morning dexterity sessions correlate with steadier baseline severity.',
      'Short mobility work appears to reduce setup-time stiffness.',
    ],
  },
  ai_observations: [
    'Average severity decreased from 2.1 to 1.9.',
    'Peak activity remains concentrated in late afternoon.',
    'No sustained escalation in episode duration was observed.',
  ],
  questions_for_doctor: [
    'Should afternoon medication timing be adjusted to reduce variability?',
    'Is the current monitoring cadence sufficient for follow-up visits?',
  ],
  data_appendix: {
    daily_summaries: [
      { date: '2026-04-12', detections: 12, avg_severity: 2.0 },
      { date: '2026-04-13', detections: 8, avg_severity: 1.7 },
      { date: '2026-04-14', detections: 11, avg_severity: 2.1 },
      { date: '2026-04-15', detections: 10, avg_severity: 1.8 },
      { date: '2026-04-16', detections: 9, avg_severity: 1.9 },
      { date: '2026-04-17', detections: 13, avg_severity: 2.0 },
      { date: '2026-04-18', detections: 11, avg_severity: 1.8 },
    ],
  },
}

export const demoSymptomCheck: SymptomCheckResponse = {
  assessment:
    'The current demo symptoms suggest a mild-to-moderate fluctuation pattern that should continue to be tracked, especially if afternoon episodes become more frequent.',
  possible_causes: [
    'Afternoon fatigue or stress',
    'Medication timing drift',
    'Reduced rest before fine-motor tasks',
  ],
  urgency_level: 'routine',
  recommendations: [
    'Keep monitoring symptom timing for the next 3 to 5 days.',
    'Note medication intake and activity level before symptom spikes.',
    'Seek clinical advice sooner if symptoms intensify or spread rapidly.',
  ],
  should_see_doctor: false,
  related_to_parkinsons_likelihood: 'medium',
}

export const demoRehabExercises = [
  {
    id: 1,
    name: 'Finger tapping sequence',
    category: 'coordination',
    difficulty: 'beginner',
    description: 'Alternating finger taps to support dexterity and rhythm.',
    instructions: 'Tap thumb to each fingertip for 60 seconds per hand.',
    video_url: '',
    image_url: '',
    duration_minutes: 6,
    calories: 12,
    is_active: true,
    created_at: '2026-04-01T00:00:00Z',
  },
  {
    id: 2,
    name: 'Shoulder mobility flow',
    category: 'stretching',
    difficulty: 'beginner',
    description: 'Gentle mobility flow to reduce stiffness before monitoring.',
    instructions: 'Complete 8 slow circles in each direction.',
    video_url: '',
    image_url: '',
    duration_minutes: 8,
    calories: 16,
    is_active: true,
    created_at: '2026-04-02T00:00:00Z',
  },
  {
    id: 3,
    name: 'Weight-shift balance drill',
    category: 'balance',
    difficulty: 'intermediate',
    description: 'Controlled lateral weight shifts to build confidence while standing.',
    instructions: 'Shift weight side to side for 3 sets of 45 seconds.',
    video_url: '',
    image_url: '',
    duration_minutes: 10,
    calories: 24,
    is_active: true,
    created_at: '2026-04-03T00:00:00Z',
  },
]

export const demoRehabPlan = {
  id: 1,
  user_id: demoUser.id,
  name: 'Morning steadiness plan',
  description: 'Short daily routine to prepare for steady movement and better monitoring baselines.',
  exercises: demoRehabExercises.map((exercise, index) => ({
    exercise_id: exercise.id,
    exercise,
    order: index + 1,
    sets: 1,
    duration_minutes: exercise.duration_minutes,
  })),
  schedule: {
    days_of_week: [1, 3, 5],
    time_of_day: '08:00',
  },
  is_active: true,
  created_at: '2026-04-05T00:00:00Z',
  updated_at: '2026-04-18T00:00:00Z',
}

export const demoTodayExercises = demoRehabPlan.exercises.map((entry, index) => ({
  exercise: entry.exercise,
  sets: entry.sets,
  reps: undefined,
  duration_minutes: entry.duration_minutes,
  completed: index === 0,
}))

export const demoRehabStats = {
  current_streak: 6,
  total_check_ins: 22,
  total_minutes: 214,
  avg_duration_minutes: 9.7,
  completion_rate: 82,
  weekly_minutes: [18, 26, 34, 28, 31, 42, 35],
  weekly_labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
}
