from typing import Literal

from pydantic import BaseModel, Field, model_validator

Goal = Literal["lose_fat", "build_muscle", "get_stronger", "get_fitter"]
Level = Literal["beginner", "intermediate", "advanced"]
Equipment = Literal["gym", "dumbbells", "bodyweight"]
Injury = Literal["knees", "back", "shoulders", "wrists"]
Lang = Literal["en", "fr", "ar"]


class Profile(BaseModel):
    goal: Goal
    sex: Literal["male", "female"]
    age: int = Field(ge=16, le=80)
    height_cm: float = Field(ge=130, le=230)
    weight_kg: float = Field(ge=35, le=250)
    waist_cm: float | None = Field(default=None, ge=45, le=200)
    neck_cm: float | None = Field(default=None, ge=25, le=70)
    hips_cm: float | None = Field(default=None, ge=60, le=200)
    body_fat_pct: float | None = Field(default=None, ge=3, le=60)
    level: Level
    days_per_week: int = Field(ge=2, le=6)
    minutes: Literal[30, 45, 60, 75, 90]
    equipment: Equipment
    injuries: list[Injury] = Field(default_factory=list, max_length=4)
    lifestyle: Literal["sedentary", "light", "active"] = "light"
    notes: str = Field(default="", max_length=200)

    @model_validator(mode="after")
    def unique_injuries(self) -> "Profile":
        self.injuries = sorted(set(self.injuries))
        self.notes = " ".join(self.notes.split())
        return self


class PlanRequest(BaseModel):
    profile: Profile
    lang: Lang = "en"


class ExerciseOut(BaseModel):
    """An exercise with its own sets and reps (a plank is timed, a crunch is counted)."""
    id: str
    name: str
    sets: int
    low: int
    high: int
    unit: Literal["reps", "s", "min"]
    rest_s: int


class SlotOut(BaseModel):
    exercise: ExerciseOut
    alternatives: list[ExerciseOut]  # for the swap button
    cue: str  # about the chosen exercise


class DayOut(BaseModel):
    number: int
    name: str
    kind: str  # strength, cardio
    slots: list[SlotOut]


class WeekOut(BaseModel):
    week: int
    focus: str
    details: str


class PlanOut(BaseModel):
    lang: Lang
    title: str
    summary: str
    schedule: list[int]  # 7 entries: the training day number on that day of the week, 0 for rest
    days: list[DayOut]
    warmup: list[str]
    progression: list[WeekOut]
    cardio: str
    tips: list[str]
    ai: bool  # False when the AI was unavailable and the plan was built from the rules only


class MetricsOut(BaseModel):
    bmi: float
    bmi_class: str
    body_fat: float | None
    body_fat_source: str | None
    waist_to_height: float | None
    lean_mass: float | None
    bmr: int
    tdee: int


class NutritionOut(BaseModel):
    calories: int
    protein: int
    fat: int
    carbs: int
    water_l: float
    weekly_change_pct: tuple[float, float]
    adjusted_goal: str | None


class PlanResponse(BaseModel):
    metrics: MetricsOut
    nutrition: NutritionOut
    plan: PlanOut
    warnings: list[str]  # codes the app shows as notices: see_doctor, underweight, ...
