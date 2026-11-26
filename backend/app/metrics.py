"""Body measurements to numbers: BMI, body fat, energy needs and nutrition targets.

Plain, well-known formulas, computed here rather than by the AI so the numbers are always the same
for the same person:
- BMI = weight / height².
- Body fat from a tape measure: the U.S. Navy method (waist and neck, plus hips for women).
- Resting energy (BMR): Mifflin-St Jeor. Daily energy (TDEE): BMR × an activity factor.
- Calories by goal: about 20 % below TDEE to lose fat, 10 % above to build muscle.
- Protein 1.6-2.2 g per kg (per kg of a healthy reference weight for people with a high BMI).
"""

import math
from dataclasses import dataclass

from .schemas import Profile

LIFESTYLE = {"sedentary": 1.2, "light": 1.3, "active": 1.45}  # job and daily life, before training
TRAINING_DAY = 0.035  # added to the factor for each training day a week

CALORIE_CHANGE = {"lose_fat": -0.20, "build_muscle": 0.10, "get_stronger": 0.05, "get_fitter": 0.0}
PROTEIN_PER_KG = {"lose_fat": 2.0, "build_muscle": 1.8, "get_stronger": 1.8, "get_fitter": 1.5}
MIN_CALORIES = {"male": 1500, "female": 1200}
WEEKLY_CHANGE = {"lose_fat": (-0.7, -0.4), "build_muscle": (0.2, 0.4), "get_stronger": (0.0, 0.3), "get_fitter": (0.0, 0.0)}


@dataclass
class Metrics:
    bmi: float
    bmi_class: str  # under, healthy, over, obese
    body_fat: float | None  # %
    body_fat_source: str | None  # measured (tape), given (typed in), or None
    waist_to_height: float | None
    lean_mass: float | None  # kg
    bmr: int
    tdee: int


@dataclass
class Nutrition:
    calories: int
    protein: int  # g a day
    fat: int
    carbs: int
    water_l: float
    weekly_change_pct: tuple[float, float]  # expected body-weight change per week, % (min, max)
    adjusted_goal: str | None  # set when the goal had to be changed for safety


def bmi_class(bmi: float) -> str:
    if bmi < 18.5:
        return "under"
    if bmi < 25:
        return "healthy"
    if bmi < 30:
        return "over"
    return "obese"


def navy_body_fat(sex: str, height: float, waist: float, neck: float, hips: float | None) -> float | None:
    """U.S. Navy circumference method, all measures in cm. None when the measures can't be used."""
    try:
        if sex == "male":
            if waist <= neck:
                return None
            value = 495 / (1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(height)) - 450
        else:
            if hips is None or waist + hips <= neck:
                return None
            value = 495 / (1.29579 - 0.35004 * math.log10(waist + hips - neck) + 0.22100 * math.log10(height)) - 450
    except (ValueError, ZeroDivisionError):
        return None
    return round(value, 1) if 3 <= value <= 60 else None


def compute(profile: Profile) -> Metrics:
    height_m = profile.height_cm / 100
    bmi = profile.weight_kg / height_m**2
    if profile.body_fat_pct is not None:
        body_fat, source = profile.body_fat_pct, "given"
    elif profile.waist_cm and profile.neck_cm:
        body_fat = navy_body_fat(profile.sex, profile.height_cm, profile.waist_cm, profile.neck_cm, profile.hips_cm)
        source = "measured" if body_fat is not None else None
    else:
        body_fat, source = None, None
    bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age + (5 if profile.sex == "male" else -161)
    factor = LIFESTYLE[profile.lifestyle] + TRAINING_DAY * profile.days_per_week
    return Metrics(
        bmi=round(bmi, 1), bmi_class=bmi_class(bmi), body_fat=body_fat, body_fat_source=source,
        waist_to_height=round(profile.waist_cm / profile.height_cm, 2) if profile.waist_cm else None,
        lean_mass=round(profile.weight_kg * (1 - body_fat / 100), 1) if body_fat is not None else None,
        bmr=round(bmr), tdee=round(bmr * factor),
    )


def nutrition(profile: Profile, metrics: Metrics) -> Nutrition:
    goal = profile.goal
    adjusted = None
    if goal == "lose_fat" and metrics.bmi < 18.5:
        goal, adjusted = "get_fitter", "underweight"  # no calorie deficit for an underweight person
    calories = metrics.tdee * (1 + CALORIE_CHANGE[goal])
    if goal == "lose_fat":
        # Never below the floor, and never more than 1,000 kcal under maintenance.
        calories = max(calories, MIN_CALORIES[profile.sex], metrics.tdee - 1000)
    calories = round(calories / 10) * 10

    # Protein per kg of a reference weight: actual weight, or the weight at BMI 25 when BMI is above 30,
    # so a 130 kg person isn't told to eat 260 g a day.
    height_m = profile.height_cm / 100
    reference = profile.weight_kg if metrics.bmi <= 30 else 25 * height_m**2
    protein = round(PROTEIN_PER_KG[goal] * reference)
    fat = round(max(0.6 * profile.weight_kg, calories * 0.27 / 9))
    carbs = max(0, round((calories - protein * 4 - fat * 9) / 4))
    return Nutrition(
        calories=int(calories), protein=protein, fat=fat, carbs=carbs,
        water_l=round(0.035 * profile.weight_kg + 0.4 * profile.days_per_week / 7, 1),
        weekly_change_pct=WEEKLY_CHANGE[goal], adjusted_goal=adjusted,
    )
