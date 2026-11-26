"""The exercise library. The AI may only choose from it, so every plan uses real, well-known exercises,
fits the equipment the person has, and leaves out movements that strain an injured joint.

`needs` is the least equipment required: bodyweight < dumbbells (with a bench or chair at home) < gym.
`avoid` lists the injuries the exercise is unsuitable for. `level` 1 suits beginners, 3 needs experience.
"""

from dataclasses import dataclass

EQUIPMENT_RANK = {"bodyweight": 0, "dumbbells": 1, "gym": 2}
TIMED = {"plank", "side_plank", "dead_bug", "pallof_press", "farmer_carry", "wall_sit"}


@dataclass(frozen=True)
class Exercise:
    id: str
    pattern: str
    needs: str
    level: int
    avoid: frozenset[str]
    en: str
    fr: str
    ar: str

    @property
    def timed(self) -> bool:
        """Done for a time (plank, carry, cardio) rather than for a number of repetitions."""
        return self.id in TIMED or self.pattern == "conditioning"

    def name(self, lang: str) -> str:
        return getattr(self, lang)


def _x(id, pattern, needs, level, avoid, en, fr, ar) -> Exercise:
    return Exercise(id, pattern, needs, level, frozenset(avoid.split()) if avoid else frozenset(), en, fr, ar)


LIBRARY: list[Exercise] = [
    # squat
    _x("back_squat", "squat", "gym", 2, "knees back", "Barbell back squat", "Squat à la barre", "سكوات بالبار"),
    _x("front_squat", "squat", "gym", 3, "knees wrists back", "Barbell front squat", "Squat avant à la barre", "سكوات أمامي بالبار"),
    _x("leg_press", "squat", "gym", 1, "", "Leg press", "Presse à cuisses", "مكبس الأرجل"),
    _x("goblet_squat", "squat", "dumbbells", 1, "knees", "Dumbbell goblet squat", "Squat goblet à l'haltère", "سكوات الكأس بالدمبل"),
    _x("box_squat", "squat", "bodyweight", 1, "", "Squat to a chair or box", "Squat jusqu'à une chaise", "سكوات حتى الكرسي"),
    _x("bodyweight_squat", "squat", "bodyweight", 1, "knees", "Bodyweight squat", "Squat au poids du corps", "سكوات بوزن الجسم"),
    # hinge
    _x("deadlift", "hinge", "gym", 2, "back", "Barbell deadlift", "Soulevé de terre", "الرفعة الميتة بالبار"),
    _x("romanian_deadlift", "hinge", "gym", 2, "back", "Barbell Romanian deadlift", "Soulevé de terre roumain", "الرفعة الرومانية بالبار"),
    _x("db_romanian_deadlift", "hinge", "dumbbells", 1, "back", "Dumbbell Romanian deadlift", "Soulevé de terre roumain aux haltères", "الرفعة الرومانية بالدمبل"),
    _x("hip_thrust", "hinge", "gym", 1, "", "Barbell hip thrust", "Hip thrust à la barre", "رفع الحوض بالبار"),
    _x("db_hip_thrust", "hinge", "dumbbells", 1, "", "Dumbbell hip thrust", "Hip thrust à l'haltère", "رفع الحوض بالدمبل"),
    _x("glute_bridge", "hinge", "bodyweight", 1, "", "Glute bridge", "Pont fessier", "جسر الأرداف"),
    # single leg
    _x("walking_lunge", "lunge", "dumbbells", 1, "knees", "Dumbbell walking lunge", "Fentes marchées aux haltères", "الطعنات المتحركة بالدمبل"),
    _x("bulgarian_split_squat", "lunge", "dumbbells", 2, "knees", "Bulgarian split squat", "Squat bulgare", "السكوات البلغاري"),
    _x("step_up", "lunge", "dumbbells", 1, "", "Dumbbell step-up", "Montée sur banc aux haltères", "الصعود على المقعد بالدمبل"),
    _x("reverse_lunge", "lunge", "bodyweight", 1, "knees", "Reverse lunge", "Fente arrière", "الطعن الخلفي"),
    _x("bodyweight_step_up", "lunge", "bodyweight", 1, "", "Step-up on a stair or box", "Montée sur une marche", "الصعود على درجة"),
    # horizontal push
    _x("bench_press", "push_h", "gym", 2, "shoulders", "Barbell bench press", "Développé couché à la barre", "ضغط البنش بالبار"),
    _x("db_bench_press", "push_h", "gym", 1, "", "Dumbbell bench press", "Développé couché aux haltères", "ضغط البنش بالدمبل"),
    _x("incline_db_press", "push_h", "gym", 1, "", "Incline dumbbell press", "Développé incliné aux haltères", "ضغط الدمبل على المقعد المائل"),
    _x("machine_chest_press", "push_h", "gym", 1, "", "Machine chest press", "Développé poitrine à la machine", "ضغط الصدر بالآلة"),
    _x("db_floor_press", "push_h", "dumbbells", 1, "", "Dumbbell floor press", "Développé au sol aux haltères", "ضغط الدمبل على الأرض"),
    _x("push_up", "push_h", "bodyweight", 1, "wrists", "Push-up", "Pompes", "تمرين الضغط"),
    _x("incline_push_up", "push_h", "bodyweight", 1, "wrists", "Incline push-up (hands on a bench)", "Pompes inclinées (mains sur un banc)", "الضغط المائل (اليدان على مقعد)"),
    # vertical push
    _x("overhead_press", "push_v", "gym", 2, "shoulders back", "Standing barbell overhead press", "Développé militaire debout", "الضغط العسكري واقفًا بالبار"),
    _x("landmine_press", "push_v", "gym", 2, "", "Landmine press", "Développé landmine", "ضغط اللاندماين"),
    _x("machine_shoulder_press", "push_v", "gym", 1, "shoulders", "Machine shoulder press", "Développé épaules à la machine", "ضغط الأكتاف بالآلة"),
    _x("db_shoulder_press", "push_v", "dumbbells", 1, "shoulders", "Seated dumbbell shoulder press", "Développé épaules assis aux haltères", "ضغط الأكتاف بالدمبل جالسًا"),
    _x("pike_push_up", "push_v", "bodyweight", 2, "shoulders wrists", "Pike push-up", "Pompes en pike", "الضغط بوضعية الهرم"),
    # horizontal pull
    _x("barbell_row", "pull_h", "gym", 2, "back", "Barbell bent-over row", "Rowing barre buste penché", "التجديف بالبار منحنيًا"),
    _x("seated_cable_row", "pull_h", "gym", 1, "", "Seated cable row", "Tirage horizontal à la poulie", "التجديف بالكابل جالسًا"),
    _x("chest_supported_row", "pull_h", "gym", 1, "", "Chest-supported dumbbell row", "Rowing haltères poitrine appuyée", "التجديف بالدمبل مع إسناد الصدر"),
    _x("db_row", "pull_h", "dumbbells", 1, "", "One-arm dumbbell row", "Rowing unilatéral à l'haltère", "التجديف بالدمبل بذراع واحدة"),
    _x("inverted_row", "pull_h", "bodyweight", 2, "", "Inverted row (under a sturdy table)", "Rowing inversé (sous une table solide)", "التجديف المقلوب (تحت طاولة متينة)"),
    _x("towel_row", "pull_h", "bodyweight", 1, "", "Door-frame towel row", "Rowing à la serviette (cadre de porte)", "التجديف بالمنشفة على إطار الباب"),
    # vertical pull
    _x("pull_up", "pull_v", "gym", 3, "shoulders", "Pull-up", "Traction", "العقلة"),
    _x("assisted_pull_up", "pull_v", "gym", 2, "", "Assisted pull-up (machine or band)", "Traction assistée (machine ou élastique)", "العقلة بالمساعدة (آلة أو مطاط)"),
    _x("lat_pulldown", "pull_v", "gym", 1, "", "Lat pulldown", "Tirage vertical à la poulie", "السحب العلوي بالكابل"),
    _x("db_pullover", "pull_v", "dumbbells", 1, "shoulders", "Dumbbell pullover", "Pull-over à l'haltère", "البول أوفر بالدمبل"),
    _x("prone_w_raise", "pull_v", "bodyweight", 1, "", "Lying W-raise", "Élévations en W allongé", "رفع الذراعين بوضعية W مستلقيًا"),
    # shoulders and chest isolation
    _x("lateral_raise", "shoulder_iso", "dumbbells", 1, "", "Dumbbell lateral raise", "Élévations latérales aux haltères", "الرفرفة الجانبية بالدمبل"),
    _x("face_pull", "shoulder_iso", "gym", 1, "", "Cable face pull", "Face pull à la poulie", "سحب الحبل نحو الوجه"),
    _x("rear_delt_fly", "shoulder_iso", "dumbbells", 1, "", "Dumbbell rear-delt fly", "Oiseau aux haltères", "الرفرفة الخلفية بالدمبل"),
    _x("cable_fly", "chest_iso", "gym", 1, "", "Cable chest fly", "Écarté à la poulie", "التفتيح بالكابل"),
    _x("db_fly", "chest_iso", "dumbbells", 1, "shoulders", "Dumbbell fly", "Écarté aux haltères", "التفتيح بالدمبل"),
    # arms
    _x("cable_curl", "biceps", "gym", 1, "", "Cable biceps curl", "Curl biceps à la poulie", "تمرين البايسبس بالكابل"),
    _x("db_curl", "biceps", "dumbbells", 1, "", "Dumbbell biceps curl", "Curl biceps aux haltères", "تمرين البايسبس بالدمبل"),
    _x("hammer_curl", "biceps", "dumbbells", 1, "", "Hammer curl", "Curl marteau", "تمرين المطرقة بالدمبل"),
    _x("triceps_pushdown", "triceps", "gym", 1, "", "Cable triceps pushdown", "Extension triceps à la poulie", "دفع الترايسبس بالكابل"),
    _x("overhead_extension", "triceps", "dumbbells", 1, "shoulders", "Overhead dumbbell triceps extension", "Extension triceps au-dessus de la tête", "تمديد الترايسبس فوق الرأس بالدمبل"),
    _x("close_push_up", "triceps", "bodyweight", 2, "wrists", "Close-grip push-up", "Pompes mains serrées", "الضغط بقبضة ضيقة"),
    _x("bench_dip", "triceps", "bodyweight", 1, "shoulders wrists", "Bench dip", "Dips sur banc", "الغطس على المقعد"),
    # leg isolation
    _x("leg_curl", "hamstrings", "gym", 1, "", "Lying leg curl", "Leg curl allongé", "ثني الأرجل بالآلة"),
    _x("single_leg_bridge", "hamstrings", "bodyweight", 1, "", "Single-leg glute bridge", "Pont fessier sur une jambe", "جسر الأرداف على رجل واحدة"),
    _x("leg_extension", "quads", "gym", 1, "knees", "Leg extension", "Leg extension", "تمديد الأرجل بالآلة"),
    _x("wall_sit", "quads", "bodyweight", 1, "knees", "Wall sit", "Chaise contre le mur", "الجلوس على الحائط"),
    _x("seated_calf_raise", "calves", "gym", 1, "", "Seated calf raise", "Mollets assis à la machine", "رفع السمانة جالسًا"),
    _x("calf_raise", "calves", "bodyweight", 1, "", "Standing calf raise", "Mollets debout", "رفع السمانة واقفًا"),
    # core
    _x("plank", "core", "bodyweight", 1, "", "Plank", "Gainage (planche)", "البلانك"),
    _x("side_plank", "core", "bodyweight", 1, "", "Side plank", "Gainage latéral", "البلانك الجانبي"),
    _x("dead_bug", "core", "bodyweight", 1, "", "Dead bug", "Dead bug", "تمرين الحشرة الميتة"),
    _x("pallof_press", "core", "gym", 1, "", "Cable Pallof press", "Pallof press à la poulie", "ضغط بالوف بالكابل"),
    _x("hanging_knee_raise", "core", "gym", 2, "shoulders", "Hanging knee raise", "Relevés de genoux suspendu", "رفع الركبتين معلقًا"),
    _x("farmer_carry", "core", "dumbbells", 1, "", "Farmer's carry", "Marche du fermier", "مشية المزارع"),
    # conditioning
    _x("incline_walk", "conditioning", "gym", 1, "", "Incline treadmill walk", "Marche inclinée sur tapis", "المشي المائل على جهاز المشي"),
    _x("bike_intervals", "conditioning", "gym", 1, "", "Stationary bike intervals", "Intervalles sur vélo", "فترات على الدراجة الثابتة"),
    _x("rower_intervals", "conditioning", "gym", 2, "back", "Rowing machine intervals", "Intervalles au rameur", "فترات على آلة التجديف"),
    _x("brisk_walk", "conditioning", "bodyweight", 1, "", "Brisk walk", "Marche rapide", "المشي السريع"),
    _x("mountain_climbers", "conditioning", "bodyweight", 1, "wrists", "Mountain climbers", "Mountain climbers", "تسلق الجبل"),
    _x("jumping_jacks", "conditioning", "bodyweight", 1, "knees", "Jumping jacks", "Jumping jacks", "القفز مع فتح الذراعين"),
    _x("burpees", "conditioning", "bodyweight", 2, "knees wrists back", "Burpees", "Burpees", "البيربي"),
]

BY_ID = {e.id: e for e in LIBRARY}


def candidates(pattern: str, equipment: str, injuries: list[str], level: str) -> list[Exercise]:
    """Exercises that fit: right movement, available equipment, no injured joint, not too advanced.
    The best fit first: most equipment-specific, then easiest for beginners."""
    max_level = {"beginner": 1, "intermediate": 2, "advanced": 3}[level]
    rank = EQUIPMENT_RANK[equipment]
    fits = [e for e in LIBRARY if e.pattern == pattern and EQUIPMENT_RANK[e.needs] <= rank
            and not e.avoid & set(injuries) and e.level <= max_level]
    # Prefer what the person's setting is made for: barbells and machines in a gym, dumbbells at home.
    return sorted(fits, key=lambda e: (-EQUIPMENT_RANK[e.needs], e.level if level == "beginner" else abs(e.level - 2)))
