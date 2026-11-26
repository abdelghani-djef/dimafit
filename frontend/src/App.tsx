import { useEffect, useState } from 'react'
import { createPlan, PlanError } from './api'
import { EMPTY, Form } from './components/Form'
import { Logo } from './components/Icons'
import { PlanView } from './components/PlanView'
import { DICTS } from './i18n'
import type { Lang, Profile, Result } from './types'

// Everything stays in this browser: the answers, the last plan and the chosen language.
function load<T>(key: string): T | null {
  try {
    const raw = localStorage.getItem(`dimafit:${key}`)
    return raw ? (JSON.parse(raw) as T) : null
  } catch {
    return null
  }
}

function save(key: string, value: unknown) {
  try {
    if (value === null) localStorage.removeItem(`dimafit:${key}`)
    else localStorage.setItem(`dimafit:${key}`, JSON.stringify(value))
  } catch {
    // storage blocked: the plan just won't survive a reload
  }
}

function startLang(): Lang {
  const asked = new URLSearchParams(location.search).get('lang')
  if (asked === 'en' || asked === 'fr' || asked === 'ar') return asked
  const saved = load<Lang>('lang')
  if (saved) return saved
  const browser = navigator.language.toLowerCase()
  return browser.startsWith('ar') ? 'ar' : browser.startsWith('fr') ? 'fr' : 'en'
}

const LANGS: { value: Lang; label: string }[] = [
  { value: 'en', label: 'EN' },
  { value: 'fr', label: 'FR' },
  { value: 'ar', label: 'ع' },
]

export default function App() {
  const [lang, setLang] = useState<Lang>(startLang)
  const [profile, setProfile] = useState<Profile>(() => ({ ...EMPTY, ...(load<Profile>('profile') ?? {}) }))
  const [result, setResult] = useState<Result | null>(() => load<Result>('result'))
  const [editing, setEditing] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<PlanError | null>(null)
  const t = DICTS[lang]

  useEffect(() => {
    document.documentElement.lang = lang
    document.documentElement.dir = t.dir
    document.title = `DimaFit — ${t.tagline}`
    save('lang', lang)
  }, [lang, t])

  async function generate(next: Profile, planLang: Lang = lang) {
    setBusy(true)
    setError(null)
    setProfile(next)
    save('profile', next)
    try {
      const created = await createPlan(next, planLang)
      setResult(created)
      save('result', created)
      setEditing(false)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (err) {
      setError(err instanceof PlanError ? err : new PlanError('server'))
    } finally {
      setBusy(false)
    }
  }

  function swap(dayIndex: number, slotIndex: number) {
    if (!result) return
    const days = result.plan.days.map((day, d) =>
      d !== dayIndex ? day : {
        ...day,
        slots: day.slots.map((slot, s) => {
          if (s !== slotIndex || !slot.alternatives.length) return slot
          const [next, ...others] = slot.alternatives
          // The coaching cue was written for the old exercise, so it goes with it.
          return { exercise: next, alternatives: [...others, slot.exercise], cue: '' }
        }),
      })
    const updated = { ...result, plan: { ...result.plan, days } }
    setResult(updated)
    save('result', updated)
  }

  const showForm = !result || editing

  return (
    <div className="min-h-screen">
      <header className="no-print border-b border-line bg-paper/90">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
          <button type="button" onClick={() => result && setEditing(false)} className="flex items-center gap-2.5">
            <Logo className="h-8 w-8" />
            <span className="text-lg font-semibold tracking-tight" dir="ltr">DimaFit</span>
          </button>
          <div className="flex rounded-lg border border-line bg-card p-0.5" role="group" aria-label="Language">
            {LANGS.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setLang(option.value)}
                aria-pressed={lang === option.value}
                className={`rounded-md px-2.5 py-1 text-xs font-semibold ${lang === option.value ? 'bg-ink text-white' : 'text-muted hover:text-ink'}`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 pb-16 pt-8">
        {showForm ? (
          <>
            <div className="mx-auto max-w-2xl text-center">
              <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">{t.tagline}</h1>
              <p className="mt-3 text-muted">{t.intro}</p>
            </div>
            <div className="mx-auto mt-8 max-w-3xl">
              {error ? (
                <p className="mb-4 rounded-xl bg-bad-soft px-4 py-3 text-sm text-bad" role="alert">{t.errors[error.code]}</p>
              ) : null}
              <Form key={lang} t={t} initial={profile} busy={busy} badField={error?.field ?? null} onSubmit={(next) => generate(next)} />
              <p className="mt-6 text-center text-xs text-muted">{t.disclaimer}</p>
            </div>
          </>
        ) : result ? (
          <PlanView
            result={result}
            uiLang={lang}
            goal={profile.goal}
            weightKg={profile.weight_kg}
            busy={busy}
            onSwap={swap}
            onEdit={() => setEditing(true)}
            onRecreate={() => generate(profile, lang)}
          />
        ) : null}
        {!showForm && error ? <p className="no-print mt-4 rounded-xl bg-bad-soft px-4 py-3 text-sm text-bad">{t.errors[error.code]}</p> : null}
      </main>
    </div>
  )
}
