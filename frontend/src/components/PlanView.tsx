import type { ReactNode } from 'react'
import { DICTS, number, type Dict } from '../i18n'
import type { Exercise, Goal, Lang, Result } from '../types'
import { AlertIcon, EditIcon, PrintIcon, SwapIcon } from './Icons'

interface Props {
  result: Result
  uiLang: Lang
  goal: Goal
  weightKg: number
  onSwap: (day: number, slot: number) => void
  onEdit: () => void
  onRecreate: () => void
  busy: boolean
}

function rest(seconds: number, d: Dict): string {
  if (seconds < 60) return `${seconds} ${d.sec}`
  const minutes = Math.floor(seconds / 60)
  const extra = seconds % 60
  return extra ? `${minutes} ${d.min} ${extra} ${d.sec}` : `${minutes} ${d.min}`
}

function dose(exercise: Exercise, d: Dict): string {
  const range = exercise.low === exercise.high ? `${exercise.low}` : `${exercise.low}–${exercise.high}`
  if (exercise.unit === 'min') return `${range} ${d.min}`
  const unit = d.units[exercise.unit]
  return d.sets(exercise.sets, unit ? `${range} ${unit}` : range)
}

function Card({ title, children, className = '' }: { title: string; children: ReactNode; className?: string }) {
  return (
    <section className={`print-card rounded-2xl border border-line bg-card p-5 sm:p-6 ${className}`}>
      <h3 className="text-lg font-semibold">{title}</h3>
      <div className="mt-3">{children}</div>
    </section>
  )
}

export function PlanView({ result, uiLang, goal, weightKg, onSwap, onEdit, onRecreate, busy }: Props) {
  const { plan, metrics, nutrition, warnings } = result
  const d = DICTS[plan.lang] // the plan, its labels and its printout stay in the language it was written in
  const ui = DICTS[uiLang]
  const n = (value: number, digits = 0) => number(value, plan.lang, digits)
  const [lowPct, highPct] = nutrition.weekly_change_pct
  const kgLow = n(Math.abs((weightKg * Math.min(Math.abs(lowPct), Math.abs(highPct))) / 100), 1)
  const kgHigh = n(Math.abs((weightKg * Math.max(Math.abs(lowPct), Math.abs(highPct))) / 100), 1)
  const macroTotal = nutrition.protein * 4 + nutrition.carbs * 4 + nutrition.fat * 9

  return (
    <div className="space-y-5">
      <div className="no-print flex flex-wrap items-center gap-2">
        <button type="button" onClick={() => window.print()} className="inline-flex items-center gap-2 rounded-lg bg-ink px-4 py-2.5 text-sm font-semibold text-white hover:bg-ink/90">
          <PrintIcon className="h-4 w-4" /> {ui.print}
        </button>
        <button type="button" onClick={onEdit} className="inline-flex items-center gap-2 rounded-lg border border-line bg-card px-4 py-2.5 text-sm font-semibold hover:border-ink">
          <EditIcon className="h-4 w-4" /> {ui.edit}
        </button>
      </div>

      {plan.lang !== uiLang ? (
        <div className="no-print flex flex-wrap items-center justify-between gap-3 rounded-xl bg-accent-soft px-4 py-3 text-sm">
          <span>{ui.otherLanguage(ui.langNames[plan.lang])}</span>
          <button type="button" disabled={busy} onClick={onRecreate} className="font-semibold text-accent underline-offset-2 hover:underline disabled:opacity-50">
            {busy ? ui.creating : ui.recreate}
          </button>
        </div>
      ) : null}

      <div dir={d.dir} lang={plan.lang} className="space-y-5">
        <header className="print-card rounded-2xl bg-ink p-6 text-white sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-widest text-[#ff8a5c]">{d.goals[goal][0]}</p>
          <h2 className="mt-2 text-2xl font-semibold leading-tight sm:text-3xl">{plan.title}</h2>
          <p className="mt-3 max-w-3xl text-sm leading-relaxed text-white/80 sm:text-base">{plan.summary}</p>
        </header>

        {warnings.length ? (
          <div className="space-y-2">
            {warnings.map((code) => d.warnings[code] ? (
              <p key={code} className={`print-card flex gap-2 rounded-xl px-4 py-3 text-sm ${code === 'ai_offline' ? 'no-print bg-paper text-muted ring-1 ring-line' : 'bg-warn-soft text-warn'}`}>
                <AlertIcon className="mt-0.5 h-4 w-4 shrink-0" /> {d.warnings[code]}
              </p>
            ) : null)}
          </div>
        ) : null}

        <div className="grid gap-5 lg:grid-cols-2">
          <Card title={d.numbersTitle}>
            <dl className="grid grid-cols-2 gap-3">
              <div className="rounded-xl bg-paper p-3">
                <dt className="text-xs text-muted">{d.bmi}</dt>
                <dd className="text-2xl font-semibold tabular-nums">{n(metrics.bmi, 1)}</dd>
                <dd className="text-xs text-muted">{d.bmiClass[metrics.bmi_class]}</dd>
              </div>
              <div className="rounded-xl bg-paper p-3">
                <dt className="text-xs text-muted">{d.bodyFatLabel}</dt>
                <dd className="text-2xl font-semibold tabular-nums" dir="ltr">{metrics.body_fat != null ? `${n(metrics.body_fat, 1)}${plan.lang === 'fr' ? ' %' : '%'}` : '—'}</dd>
                <dd className="text-xs text-muted">{metrics.body_fat_source ? d[metrics.body_fat_source] : d.unknown}</dd>
              </div>
              <div className="rounded-xl bg-paper p-3">
                <dt className="text-xs text-muted">{d.maintenance}</dt>
                <dd className="text-2xl font-semibold tabular-nums">{n(metrics.tdee)}</dd>
                <dd className="text-xs text-muted">{d.kcalDay}</dd>
              </div>
              {metrics.waist_to_height != null ? (
                <div className="rounded-xl bg-paper p-3">
                  <dt className="text-xs text-muted">{d.waistRatio}</dt>
                  <dd className={`text-2xl font-semibold tabular-nums ${metrics.waist_to_height >= 0.5 ? 'text-warn' : ''}`}>{n(metrics.waist_to_height, 2)}</dd>
                  <dd className="text-xs text-muted">&lt; {n(0.5, 1)}</dd>
                </div>
              ) : null}
            </dl>
          </Card>

          <Card title={d.nutritionTitle}>
            <div className="flex items-end gap-2">
              <span className="text-4xl font-semibold tabular-nums text-food">{n(nutrition.calories)}</span>
              <span className="pb-1 text-sm text-muted">{d.kcalDay}</span>
            </div>
            <div className="mt-3 flex h-2.5 overflow-hidden rounded-full bg-paper" aria-hidden="true">
              <span className="bg-food" style={{ width: `${(nutrition.protein * 400) / macroTotal}%` }} />
              <span className="bg-[#5eb8ad]" style={{ width: `${(nutrition.carbs * 400) / macroTotal}%` }} />
              <span className="bg-[#b7dcd6]" style={{ width: `${(nutrition.fat * 900) / macroTotal}%` }} />
            </div>
            <dl className="mt-3 grid grid-cols-4 gap-2 text-center">
              {([[d.protein, nutrition.protein, d.g, 'bg-food'], [d.carbs, nutrition.carbs, d.g, 'bg-[#5eb8ad]'], [d.fat, nutrition.fat, d.g, 'bg-[#b7dcd6]'], [d.water, nutrition.water_l, d.l, '']] as const).map(([label, value, unit, dot]) => (
                <div key={label} className="rounded-xl bg-paper px-1 py-2">
                  <dt className="flex items-center justify-center gap-1.5 text-xs text-muted">
                    {dot ? <i className={`h-2 w-2 rounded-full ${dot}`} /> : null}{label}
                  </dt>
                  <dd className="text-lg font-semibold tabular-nums">{n(value, 1)} <span className="text-xs font-normal text-muted">{unit}</span></dd>
                </div>
              ))}
            </dl>
            <p className="mt-3 text-sm text-muted">{d.change(kgLow, kgHigh, nutrition.adjusted_goal ? 'get_fitter' : goal)}</p>
          </Card>
        </div>

        <Card title={d.weekTitle}>
          <ol className="grid grid-cols-7 gap-1.5">
            {plan.schedule.map((day, i) => {
              const info = plan.days.find((x) => x.number === day)
              return (
                <li key={i} title={day ? `${d.dayN(day)} · ${info?.name ?? ''}` : d.rest}
                  className={`rounded-lg px-1 py-2 text-center text-xs ${day ? 'bg-ink text-white' : 'bg-paper text-muted'}`}>
                  <span className="block text-base font-semibold tabular-nums">{i + 1}</span>
                  <span className="mt-0.5 hidden truncate sm:block">{day ? d.dayN(day) : d.rest}</span>
                  <span className="mt-0.5 block sm:hidden" aria-hidden="true">{day ? '●' : '–'}</span>
                </li>
              )
            })}
          </ol>
          <p className="mt-2 text-xs text-muted">{d.weekHint}</p>
        </Card>

        <div className="grid gap-5 lg:grid-cols-2">
          {plan.days.map((day, dayIndex) => (
            <section key={day.number} className="print-card rounded-2xl border border-line bg-card">
              <div className="flex items-baseline justify-between gap-3 border-b border-line px-5 py-4">
                <h3 className="font-semibold">
                  <span className="text-accent">{d.dayN(day.number)}</span> · {day.name}
                </h3>
                <span className="shrink-0 text-xs text-muted">{d.perSession(day.slots.length)}</span>
              </div>
              <ol className="divide-y divide-line">
                {day.slots.map((slot, slotIndex) => (
                  <li key={slotIndex} className="flex gap-3 px-5 py-3.5">
                    <span className="mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-full bg-paper text-xs font-semibold tabular-nums text-muted">{slotIndex + 1}</span>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
                        <p className="font-medium">{slot.exercise.name}</p>
                        <p className="text-sm font-semibold tabular-nums" dir="ltr">{dose(slot.exercise, d)}</p>
                      </div>
                      {slot.cue ? <p className="mt-0.5 text-sm text-muted">{slot.cue}</p> : null}
                      <div className="mt-1 flex items-center justify-between gap-3">
                        <p className="text-xs text-muted">{slot.exercise.rest_s ? d.restFor(rest(slot.exercise.rest_s, d)) : ''}</p>
                        {slot.alternatives.length ? (
                          <button type="button" onClick={() => onSwap(dayIndex, slotIndex)} title={d.swapTitle}
                            className="no-print inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-semibold text-muted hover:bg-paper hover:text-accent">
                            <SwapIcon className="h-3.5 w-3.5" /> {d.swap}
                          </button>
                        ) : null}
                      </div>
                    </div>
                  </li>
                ))}
              </ol>
            </section>
          ))}
        </div>

        <div className="grid gap-5 lg:grid-cols-2">
          <Card title={d.warmupTitle}>
            <ol className="list-decimal space-y-1.5 ps-5 text-sm">{plan.warmup.map((step) => <li key={step}>{step}</li>)}</ol>
          </Card>
          <Card title={d.cardioTitle}>
            <p className="text-sm leading-relaxed">{plan.cardio}</p>
          </Card>
        </div>

        <Card title={d.progressionTitle}>
          <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {plan.progression.map((week) => (
              <li key={week.week} className="rounded-xl bg-paper p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-accent">{d.weekN(week.week)}</p>
                <p className="mt-1 font-semibold">{week.focus}</p>
                <p className="mt-1 text-sm text-muted">{week.details}</p>
              </li>
            ))}
          </ol>
        </Card>

        <Card title={d.tipsTitle}>
          <ul className="space-y-1.5 text-sm">{plan.tips.map((tip) => <li key={tip} className="flex gap-2"><span className="text-accent">•</span>{tip}</li>)}</ul>
        </Card>

        <p className="text-center text-xs text-muted">{d.disclaimer}</p>
        <p className="hidden text-center text-xs text-muted print:block">{d.newPlan} · dimafit.35-180-91-97.sslip.io</p>
      </div>
    </div>
  )
}
