"""The plan's skeleton, decided by rules: which days, which movements, how many sets and reps.

The split depends on the days a week and experience (full body, upper/lower, push/pull/legs). Each day
lists movements in order of importance and keeps as many as fit the session length. Sets, reps and rest
follow the goal: heavy and long rests for strength, moderate for muscle, shorter rests for fat loss.
"""

from dataclasses import dataclass, field

from .exercises import BY_ID, Exercise, candidates
from .schemas import Profile

DAYS = {
    "full_a": ["squat", "push_h", "pull_h", "hinge", "push_v", "core", "biceps", "calves"],
    "full_b": ["hinge", "push_v", "pull_v", "lunge", "push_h", "core", "triceps", "shoulder_iso"],
    "full_c": ["lunge", "push_h", "pull_v", "squat", "pull_h", "core", "shoulder_iso", "hamstrings"],
    "upper_a": ["push_h", "pull_h", "push_v", "pull_v", "shoulder_iso", "biceps", "triceps", "core"],
    "upper_b": ["pull_v", "push_v", "pull_h", "push_h", "chest_iso", "triceps", "biceps", "shoulder_iso"],
    "lower_a": ["squat", "hinge", "lunge", "quads", "calves", "core", "hamstrings", "core"],
    "lower_b": ["hinge", "squat", "lunge", "hamstrings", "core", "calves", "quads", "core"],
    "push": ["push_h", "push_v", "push_h", "shoulder_iso", "triceps", "chest_iso", "core", "triceps"],
    "pull": ["pull_v", "pull_h", "pull_h", "shoulder_iso", "biceps", "hamstrings", "core", "biceps"],
    "legs": ["squat", "hinge", "lunge", "hamstrings", "quads", "calves", "core", "core"],
    "cardio": ["conditioning", "core", "core"],
}
EXERCISES_PER_SESSION = {30: 4, 45: 5, 60: 6, 75: 7, 90: 8}
COMPOUND = {"squat", "hinge", "lunge", "push_h", "push_v", "pull_h", "pull_v"}
# Lifts that suit heavy sets of 3-5 for strength; machines and cables stay in the 6-8 range.
HEAVY = {"back_squat", "front_squat", "leg_press", "deadlift", "romanian_deadlift", "hip_thrust", "bench_press",
         "db_bench_press", "incline_db_press", "overhead_press", "landmine_press", "barbell_row", "pull_up"}
# Where training days fall in a 7-day week, spread out so muscles get rest days between sessions.
SCHEDULE = {
    2: [1, 0, 0, 2, 0, 0, 0],
    3: [1, 0, 2, 0, 3, 0, 0],
    4: [1, 2, 0, 3, 4, 0, 0],
    5: [1, 2, 3, 0, 4, 5, 0],
    6: [1, 2, 3, 4, 5, 6, 0],
}


def split(profile: Profile) -> list[str]:
    days, level = profile.days_per_week, profile.level
    if profile.goal == "get_fitter":
        strength = ["full_a", "full_b", "full_c"][: min(days, 3)]
        return strength + ["cardio"] * (days - len(strength))
    if days == 2:
        return ["full_a", "full_b"]
    if days == 3:
        return ["push", "pull", "legs"] if level == "advanced" else ["full_a", "full_b", "full_c"]
    upper_lower = ["upper_a", "lower_a", "upper_b", "lower_b"]
    if days == 4:
        return upper_lower
    if level == "beginner":
        return upper_lower + ["cardio"] * (days - 4)  # beginners recover better with lighter extra days
    if days == 5:
        return ["upper_a", "lower_a", "push", "pull", "legs"]
    return ["push", "pull", "legs", "push", "pull", "legs"]


@dataclass
class Slot:
    pattern: str
    options: list[Exercise]
    position: int  # 0 for the first exercise of the day
    choice: Exercise | None = None


@dataclass
class Day:
    number: int
    template: str
    slots: list[Slot] = field(default_factory=list)

    @property
    def kind(self) -> str:
        return "cardio" if self.template == "cardio" else "strength"


def skeleton(profile: Profile) -> list[Day]:
    count = EXERCISES_PER_SESSION[profile.minutes]
    plan = []
    for number, template in enumerate(split(profile), 1):
        patterns = DAYS[template] if template == "cardio" else DAYS[template][:count]
        if template != "cardio" and profile.goal in ("lose_fat", "get_fitter") and profile.minutes >= 45:
            patterns = patterns[:-1] + ["conditioning"]  # finish with a short cardio block
        day = Day(number, template)
        for position, pattern in enumerate(patterns):
            options = candidates(pattern, profile.equipment, profile.injuries, profile.level)
            if options:  # e.g. no biceps exercise without equipment: the slot is simply left out
                day.slots.append(Slot(pattern, options, position))
        plan.append(day)
    return plan


def default_choices(days: list[Day]) -> None:
    """A sensible pick for every slot without AI: rotate through the options so the same movement on
    different days (or twice in one day) gets a different exercise."""
    used: dict[str, int] = {}
    for day in days:
        in_day: set[str] = set()
        for slot in day.slots:
            start = used.get(slot.pattern, 0)
            for offset in range(len(slot.options)):
                option = slot.options[(start + offset) % len(slot.options)]
                if option.id not in in_day:
                    slot.choice = option
                    break
            else:
                slot.choice = slot.options[0]
            in_day.add(slot.choice.id)
            used[slot.pattern] = start + 1


def prescription(profile: Profile, slot: Slot, exercise: Exercise | None = None) -> tuple[int, int, int, str, int]:
    """(sets, low, high, unit, rest in seconds) for an exercise in this slot (the chosen one by default).
    unit: reps, s or min."""
    goal, level = profile.goal, profile.level
    exercise = exercise or slot.choice or slot.options[0]
    if exercise.pattern == "conditioning":
        minutes = {"lose_fat": (10, 15), "get_fitter": (20, 30)}.get(goal, (8, 10))
        if slot.position == 0:  # a whole cardio day
            minutes = (25, 35) if goal == "get_fitter" else (20, 30)
        return 1, minutes[0], minutes[1], "min", 0
    if exercise.timed:
        low, high = (20, 30) if level == "beginner" else (30, 45)
        return 3, low, high, "s", 45
    main = slot.pattern in COMPOUND and slot.position < 2 and (goal != "get_stronger" or exercise.id in HEAVY)
    compound = slot.pattern in COMPOUND
    table = {
        "get_stronger": [(5, 3, 5, 180), (3, 6, 8, 120), (3, 8, 12, 90)],
        "build_muscle": [(4, 6, 10, 120), (3, 8, 12, 90), (3, 10, 15, 60)],
        "lose_fat": [(3, 8, 12, 90), (3, 10, 12, 75), (3, 12, 15, 45)],
        "get_fitter": [(3, 10, 12, 60), (3, 10, 12, 60), (2, 12, 15, 45)],
    }[goal]
    sets, low, high, rest = table[0] if main else table[1] if compound else table[2]
    if main and level == "beginner":
        sets = max(3, sets - 1)
    elif main and level == "advanced":
        sets = min(5, sets + 1)
    if exercise.needs == "bodyweight" and exercise.pattern in COMPOUND and goal == "get_stronger":
        low, high = 8, 15  # bodyweight moves are too light for 3-5 reps
    return sets, low, high, "reps", rest


def is_valid_choice(slot: Slot, exercise_id: str) -> bool:
    return exercise_id in BY_ID and any(o.id == exercise_id for o in slot.options)
