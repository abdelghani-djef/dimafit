// Mirrors backend/app/schemas.py.

export type Lang = 'en' | 'fr' | 'ar'
export type Goal = 'lose_fat' | 'build_muscle' | 'get_stronger' | 'get_fitter'
export type Level = 'beginner' | 'intermediate' | 'advanced'
export type Equipment = 'gym' | 'dumbbells' | 'bodyweight'
export type Injury = 'knees' | 'back' | 'shoulders' | 'wrists'
export type Lifestyle = 'sedentary' | 'light' | 'active'

export interface Profile {
  goal: Goal
  sex: 'male' | 'female'
  age: number
  height_cm: number
  weight_kg: number
  waist_cm: number | null
  neck_cm: number | null
  hips_cm: number | null
  body_fat_pct: number | null
  level: Level
  days_per_week: number
  minutes: 30 | 45 | 60 | 75 | 90
  equipment: Equipment
  injuries: Injury[]
  lifestyle: Lifestyle
  notes: string
}

export interface Exercise {
  id: string
  name: string
  sets: number
  low: number
  high: number
  unit: 'reps' | 's' | 'min'
  rest_s: number
}

export interface Slot {
  exercise: Exercise
  alternatives: Exercise[]
  cue: string
}

export interface Day {
  number: number
  name: string
  kind: 'strength' | 'cardio'
  slots: Slot[]
}

export interface Plan {
  lang: Lang
  title: string
  summary: string
  schedule: number[]
  days: Day[]
  warmup: string[]
  progression: { week: number; focus: string; details: string }[]
  cardio: string
  tips: string[]
  ai: boolean
}

export interface Result {
  metrics: {
    bmi: number
    bmi_class: 'under' | 'healthy' | 'over' | 'obese'
    body_fat: number | null
    body_fat_source: 'measured' | 'given' | null
    waist_to_height: number | null
    lean_mass: number | null
    bmr: number
    tdee: number
  }
  nutrition: {
    calories: number
    protein: number
    fat: number
    carbs: number
    water_l: number
    weekly_change_pct: [number, number]
    adjusted_goal: string | null
  }
  plan: Plan
  warnings: string[]
}
