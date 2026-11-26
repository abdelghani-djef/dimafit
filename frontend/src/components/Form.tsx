import { useState, type ReactNode } from 'react'
import { type Dict } from '../i18n'
import type { Equipment, Goal, Injury, Level, Lifestyle, Profile } from '../types'
import { BarbellIcon, DumbbellIcon, FlameIcon, HeartIcon } from './Icons'

const GOAL_ICONS = { lose_fat: FlameIcon, build_muscle: DumbbellIcon, get_stronger: BarbellIcon, get_fitter: HeartIcon }

export const EMPTY: Profile = {
  goal: 'build_muscle',
  sex: 'male',
  age: 28,
  height_cm: 175,
  weight_kg: 75,
  waist_cm: null,
  neck_cm: null,
  hips_cm: null,
  body_fat_pct: null,
  level: 'beginner',
  days_per_week: 3,
  minutes: 60,
  equipment: 'gym',
  injuries: [],
  lifestyle: 'light',
  notes: '',
}

interface Props {
  t: Dict
  initial: Profile
  busy: boolean
  badField: string | null
  onSubmit: (profile: Profile) => void
}

function Section({ title, hint, children }: { title: string; hint?: string; children: ReactNode }) {
  return (
    <section className="rounded-2xl border border-line bg-card p-5 sm:p-6">
      <h2 className="text-lg font-semibold">
        {title}
        {hint ? <span className="ms-2 text-sm font-normal text-muted">({hint})</span> : null}
      </h2>
      <div className="mt-4">{children}</div>
    </section>
  )
}

function Choice({ active, onClick, children, className = '' }: { active: boolean; onClick: () => void; children: ReactNode; className?: string }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`rounded-xl border px-3 py-2.5 text-start text-sm transition ${
        active ? 'border-accent bg-accent-soft font-semibold ring-1 ring-accent' : 'border-line bg-card hover:border-ink'
      } ${className}`}
    >
      {children}
    </button>
  )
}

function NumberField({ label, unit, value, onChange, min, max, step = 1, required = false, bad = false, help }: {
  label: string
  unit: string
  value: number | null
  onChange: (value: number | null) => void
  min: number
  max: number
  step?: number
  required?: boolean
  bad?: boolean
  help?: string
}) {
  return (
    <label className="block text-sm font-medium">
      {label}
      <span className="relative mt-1 block">
        <input
          type="number"
          inputMode="decimal"
          min={min}
          max={max}
          step={step}
          required={required}
          value={value ?? ''}
          onChange={(e) => onChange(e.target.value === '' ? null : Number(e.target.value))}
          className={`w-full rounded-lg border bg-paper py-2.5 pe-12 ps-3 text-base outline-none transition focus:bg-card focus:ring-2 focus:ring-accent/20 ${
            bad ? 'border-bad' : 'border-line focus:border-accent'
          }`}
        />
        <span className="pointer-events-none absolute inset-y-0 end-3 flex items-center text-sm text-muted">{unit}</span>
      </span>
      {help ? <span className="mt-1 block text-xs font-normal text-muted">{help}</span> : null}
    </label>
  )
}

export function Form({ t, initial, busy, badField, onSubmit }: Props) {
  const [p, setP] = useState<Profile>(initial)
  const set = <K extends keyof Profile>(key: K, value: Profile[K]) => setP((current) => ({ ...current, [key]: value }))
  const toggleInjury = (injury: Injury) =>
    set('injuries', p.injuries.includes(injury) ? p.injuries.filter((i) => i !== injury) : [...p.injuries, injury])

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit({ ...p, notes: p.notes.trim(), hips_cm: p.sex === 'female' ? p.hips_cm : null })
      }}
      className="space-y-5"
    >
      <Section title={t.goalTitle}>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {(Object.keys(t.goals) as Goal[]).map((goal) => {
            const Icon = GOAL_ICONS[goal]
            return (
            <Choice key={goal} active={p.goal === goal} onClick={() => set('goal', goal)} className="py-3">
              <Icon className={`h-6 w-6 ${p.goal === goal ? 'text-accent' : 'text-muted'}`} />
              <span className="mt-1 block font-semibold">{t.goals[goal][0]}</span>
              <span className="block text-xs font-normal text-muted">{t.goals[goal][1]}</span>
            </Choice>
            )
          })}
        </div>
      </Section>

      <Section title={t.aboutTitle}>
        <div className="grid gap-4 sm:grid-cols-4">
          <div className="text-sm font-medium">
            {t.sex}
            <div className="mt-1 grid grid-cols-2 gap-2">
              <Choice active={p.sex === 'male'} onClick={() => set('sex', 'male')} className="text-center">{t.male}</Choice>
              <Choice active={p.sex === 'female'} onClick={() => set('sex', 'female')} className="text-center">{t.female}</Choice>
            </div>
          </div>
          <NumberField label={t.age} unit={t.years} value={p.age} onChange={(v) => set('age', v ?? 0)} min={16} max={80} required bad={badField === 'age'} />
          <NumberField label={t.height} unit={t.cm} value={p.height_cm} onChange={(v) => set('height_cm', v ?? 0)} min={130} max={230} required bad={badField === 'height_cm'} />
          <NumberField label={t.weight} unit={t.kg} value={p.weight_kg} onChange={(v) => set('weight_kg', v ?? 0)} min={35} max={250} step={0.1} required bad={badField === 'weight_kg'} />
        </div>
      </Section>

      <Section title={t.measuresTitle} hint={t.optional}>
        <p className="-mt-2 mb-4 text-sm text-muted">{t.measuresHelp}</p>
        <div className="grid gap-4 sm:grid-cols-2">
          <NumberField label={t.waist} unit={t.cm} value={p.waist_cm} onChange={(v) => set('waist_cm', v)} min={45} max={200} step={0.5} bad={badField === 'waist_cm'} />
          <NumberField label={t.neck} unit={t.cm} value={p.neck_cm} onChange={(v) => set('neck_cm', v)} min={25} max={70} step={0.5} bad={badField === 'neck_cm'} />
          {p.sex === 'female' ? (
            <NumberField label={t.hips} unit={t.cm} value={p.hips_cm} onChange={(v) => set('hips_cm', v)} min={60} max={200} step={0.5} help={t.hipsHelp} bad={badField === 'hips_cm'} />
          ) : null}
          <NumberField label={t.bodyFat} unit="%" value={p.body_fat_pct} onChange={(v) => set('body_fat_pct', v)} min={3} max={60} step={0.5} bad={badField === 'body_fat_pct'} />
        </div>
      </Section>

      <Section title={t.trainingTitle}>
        <div className="space-y-5">
          <fieldset>
            <legend className="text-sm font-medium">{t.level}</legend>
            <div className="mt-1 grid gap-2 sm:grid-cols-3">
              {(Object.keys(t.levels) as Level[]).map((level) => (
                <Choice key={level} active={p.level === level} onClick={() => set('level', level)}>
                  <span className="block font-semibold">{t.levels[level][0]}</span>
                  <span className="block text-xs font-normal text-muted">{t.levels[level][1]}</span>
                </Choice>
              ))}
            </div>
          </fieldset>
          <div className="grid gap-5 sm:grid-cols-2">
            <fieldset>
              <legend className="text-sm font-medium">{t.days}</legend>
              <div className="mt-1 grid grid-cols-5 gap-2">
                {[2, 3, 4, 5, 6].map((n) => (
                  <Choice key={n} active={p.days_per_week === n} onClick={() => set('days_per_week', n)} className="text-center tabular-nums">{n}</Choice>
                ))}
              </div>
            </fieldset>
            <fieldset>
              <legend className="text-sm font-medium">{t.minutes}</legend>
              <div className="mt-1 grid grid-cols-5 gap-2">
                {([30, 45, 60, 75, 90] as const).map((n) => (
                  <Choice key={n} active={p.minutes === n} onClick={() => set('minutes', n)} className="text-center tabular-nums">{n}</Choice>
                ))}
              </div>
            </fieldset>
          </div>
          <fieldset>
            <legend className="text-sm font-medium">{t.equipment}</legend>
            <div className="mt-1 grid gap-2 sm:grid-cols-3">
              {(Object.keys(t.equipments) as Equipment[]).map((equipment) => (
                <Choice key={equipment} active={p.equipment === equipment} onClick={() => set('equipment', equipment)}>{t.equipments[equipment]}</Choice>
              ))}
            </div>
          </fieldset>
          <fieldset>
            <legend className="text-sm font-medium">{t.injuries} <span className="font-normal text-muted">({t.optional})</span></legend>
            <div className="mt-1 grid grid-cols-2 gap-2 sm:grid-cols-4">
              {(Object.keys(t.injuryNames) as Injury[]).map((injury) => (
                <Choice key={injury} active={p.injuries.includes(injury)} onClick={() => toggleInjury(injury)}>{t.injuryNames[injury]}</Choice>
              ))}
            </div>
          </fieldset>
          <fieldset>
            <legend className="text-sm font-medium">{t.lifestyle}</legend>
            <div className="mt-1 grid gap-2 sm:grid-cols-3">
              {(Object.keys(t.lifestyles) as Lifestyle[]).map((lifestyle) => (
                <Choice key={lifestyle} active={p.lifestyle === lifestyle} onClick={() => set('lifestyle', lifestyle)}>{t.lifestyles[lifestyle]}</Choice>
              ))}
            </div>
          </fieldset>
          <label className="block text-sm font-medium">
            {t.notes} <span className="font-normal text-muted">({t.optional})</span>
            <input
              type="text"
              maxLength={200}
              value={p.notes}
              onChange={(e) => set('notes', e.target.value)}
              placeholder={t.notesPlaceholder}
              className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2.5 text-base outline-none focus:border-accent focus:bg-card"
            />
          </label>
        </div>
      </Section>

      <button
        type="submit"
        disabled={busy}
        className="flex w-full items-center justify-center gap-2 rounded-xl bg-ink px-5 py-4 text-base font-semibold text-white transition hover:bg-ink/90 disabled:opacity-60"
      >
        {busy ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-r-transparent" aria-hidden="true" /> : null}
        {busy ? t.creating : t.create}
      </button>
      <p className="text-center text-xs text-muted">{t.privacy}</p>
    </form>
  )
}
