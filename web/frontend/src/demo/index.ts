export const DEMO_TOKEN = 'neuro-pulse-demo-token'

export const demoUser = {
  id: 999,
  email: 'demo@neuropulse.ai',
  username: 'alex.demo',
  full_name: 'Alex Chen',
  role: 'user' as const,
  is_active: true,
  is_verified: true,
  created_at: '2026-04-18T00:00:00Z',
}

export function getDemoIntent(value: unknown): boolean | null {
  if (value === '1') {
    return true
  }

  if (value === '0') {
    return false
  }

  return null
}

interface DemoSessionController {
  enterDemo: () => void
  exitDemo: () => void
}

export function syncDemoModeFromLocation(
  sessionStore: DemoSessionController,
  search = typeof window !== 'undefined' ? window.location.search : ''
) {
  const params = new URLSearchParams(search)
  const intent = getDemoIntent(params.get('demo'))

  if (intent === true) {
    sessionStore.enterDemo()
  } else if (intent === false) {
    sessionStore.exitDemo()
  }

  return intent
}
