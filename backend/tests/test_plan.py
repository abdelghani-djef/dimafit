import asyncio

import pytest
from fastapi.testclient import TestClient

from app import coach, groq, main, metrics
from app.exercises import BY_ID, LIBRARY, candidates
from app.program import default_choices, prescription, skeleton, split
from app.schemas import Profile

HEADERS = {"X-Requested-With": "dimafit"}


def person(**changes) -> Profile:
    values = dict(goal="build_muscle", sex="male", age=30, height_cm=180, weight_kg=80, level="intermediate",
                  days_per_week=4, minutes=60, equipment="gym", injuries=[], lifestyle="light")
    values.update(changes)
    return Profile(**values)


# ---------- numbers ----------


def test_bmi_and_navy_body_fat():
    m = metrics.compute(person(waist_cm=85, neck_cm=38))
    assert m.bmi == 24.7 and m.bmi_class == "healthy"
    assert 15 < m.body_fat < 20 and m.body_fat_source == "measured"
    women = metrics.compute(person(sex="female", height_cm=165, weight_kg=60, waist_cm=72, neck_cm=32, hips_cm=98))
    assert 24 < women.body_fat < 32
    assert metrics.compute(person(sex="female", waist_cm=72, neck_cm=32)).body_fat is None  # hips needed


def test_mifflin_st_jeor_and_activity():
    m = metrics.compute(person(lifestyle="sedentary", days_per_week=4))
    assert m.bmr == round(10 * 80 + 6.25 * 180 - 5 * 30 + 5)
    assert m.tdee == round(m.bmr * (1.2 + 4 * 0.035))


def test_fat_loss_deficit_has_a_floor():
    small = person(goal="lose_fat", sex="female", age=60, height_cm=150, weight_kg=50, lifestyle="sedentary")
    food = metrics.nutrition(small, metrics.compute(small))
    assert food.calories >= 1200


def test_no_deficit_when_underweight():
    thin = person(goal="lose_fat", weight_kg=55)
    food = metrics.nutrition(thin, metrics.compute(thin))
    assert food.adjusted_goal == "underweight"
    assert food.calories >= metrics.compute(thin).tdee - 10


def test_protein_uses_a_reference_weight_for_high_bmi():
    heavy = person(goal="lose_fat", weight_kg=140)
    food = metrics.nutrition(heavy, metrics.compute(heavy))
    assert food.protein == round(2.0 * 25 * 1.8**2)  # BMI-25 weight, not 140 kg
    assert food.protein * 4 + food.fat * 9 + food.carbs * 4 == pytest.approx(food.calories, abs=10)


# ---------- program rules ----------


def test_splits():
    assert split(person(days_per_week=3)) == ["full_a", "full_b", "full_c"]
    assert split(person(days_per_week=3, level="advanced")) == ["push", "pull", "legs"]
    assert split(person(days_per_week=6, level="beginner")) == ["upper_a", "lower_a", "upper_b", "lower_b", "cardio", "cardio"]
    assert split(person(goal="get_fitter", days_per_week=5)) == ["full_a", "full_b", "full_c", "cardio", "cardio"]


def test_equipment_injuries_and_level_filter_the_options():
    home = candidates("squat", "bodyweight", [], "beginner")
    assert home and all(e.needs == "bodyweight" for e in home)
    knees = candidates("squat", "gym", ["knees"], "advanced")
    assert all("knees" not in e.avoid for e in knees) and "back_squat" not in {e.id for e in knees}
    assert all(e.level == 1 for e in candidates("pull_v", "gym", [], "beginner"))


def test_every_library_exercise_has_three_names():
    for exercise in LIBRARY:
        assert exercise.en and exercise.fr and exercise.ar, exercise.id
        assert any("؀" <= c <= "ۿ" for c in exercise.ar), exercise.id


def test_session_length_sets_exercise_count_and_no_repeats_in_a_day():
    days = skeleton(person(minutes=45))
    default_choices(days)
    for day in days:
        assert len(day.slots) <= 5
        ids = [s.choice.id for s in day.slots]
        assert len(ids) == len(set(ids))


def test_fat_loss_days_end_with_cardio():
    days = skeleton(person(goal="lose_fat"))
    assert all(day.slots[-1].pattern == "conditioning" for day in days)


def test_strength_prescription():
    p = person(goal="get_stronger", days_per_week=3)
    days = skeleton(p)
    default_choices(days)
    first = days[0].slots[0]
    assert first.choice.id in ("back_squat", "leg_press")
    sets, low, high, unit, rest = prescription(p, first)
    assert (low, high, unit) == (3, 5, "reps") and rest >= 150
    plank = BY_ID["plank"]
    assert prescription(p, days[0].slots[-1], plank)[3] == "s"


# ---------- AI merge ----------


def fake(answer_for):
    async def call(model, messages, schema, max_tokens, user=""):
        return answer_for(messages)
    return call


def test_ai_choices_are_validated(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test")
    p = person(days_per_week=2, equipment="bodyweight")

    def answer(_):
        return {
            "title": "Home plan", "summary": "Short summary.",
            "days": [{"slots": [{"exercise_id": "back_squat", "cue": "not allowed at home"},
                                {"exercise_id": "push_up", "cue": "Body straight."},
                                {"exercise_id": "push_up", "cue": "repeated"}]}],
            "warmup": ["Walk"], "progression": [{"focus": "a", "details": "b"}], "cardio": "Walk daily.", "tips": ["Sleep"],
        }

    monkeypatch.setattr(groq, "call", fake(answer))
    m = metrics.compute(p)
    plan = asyncio.run(coach.build(p, m, metrics.nutrition(p, m), "en"))
    first_day = plan.days[0].slots
    names = [s.exercise.id for s in first_day]
    assert "back_squat" not in names  # not an option without equipment
    assert names.count("push_up") == 1
    assert next(s for s in first_day if s.exercise.id == "push_up").cue == "Body straight."
    assert plan.title == "Home plan" and plan.ai
    assert len(plan.progression) == 4 and plan.progression[0].focus != "a"  # incomplete: fixed texts used


def test_plan_without_ai_uses_the_fixed_texts(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    p = person()
    m = metrics.compute(p)
    plan = asyncio.run(coach.build(p, m, metrics.nutrition(p, m), "ar"))
    assert not plan.ai and "برنامج" in plan.title
    assert all(s.exercise.name for d in plan.days for s in d.slots)


def test_arabic_texts_in_another_language_are_rejected():
    assert coach._text("This is English", 100, "ar") is None
    assert coach._text("هذا نص عربي", 100, "ar") == "هذا نص عربي"


# ---------- API ----------


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    main._recent.clear()
    return TestClient(main.app, headers=HEADERS)


BODY = {"lang": "fr", "profile": {"goal": "lose_fat", "sex": "female", "age": 35, "height_cm": 163, "weight_kg": 74,
                                  "waist_cm": 88, "neck_cm": 33, "hips_cm": 104, "level": "beginner", "days_per_week": 3,
                                  "minutes": 45, "equipment": "dumbbells", "injuries": ["back"], "lifestyle": "sedentary"}}


def test_plan_endpoint(client):
    response = client.post("/api/plan", json=BODY)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["plan"]["lang"] == "fr" and len(data["plan"]["days"]) == 3
    assert data["plan"]["schedule"] == [1, 0, 2, 0, 3, 0, 0]
    assert {"see_doctor", "waist_risk", "ai_offline"} <= set(data["warnings"])
    used = {s["exercise"]["id"] for d in data["plan"]["days"] for s in d["slots"]}
    assert not any("back" in BY_ID[i].avoid for i in used)


def test_validation_and_csrf(client):
    bad = {**BODY, "profile": {**BODY["profile"], "age": 12}}
    assert client.post("/api/plan", json=bad).status_code == 422
    assert TestClient(main.app).post("/api/plan", json=BODY).status_code == 403


def test_rate_limit(client):
    for _ in range(main.PLANS_PER_HOUR):
        assert client.post("/api/plan", json=BODY).status_code == 200
    assert client.post("/api/plan", json=BODY).status_code == 429
