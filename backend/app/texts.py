"""Fixed texts in the three languages: day names, and the plan texts used when the AI is unavailable."""

DAY_NAMES = {
    "full_a": {"en": "Full body A", "fr": "Corps entier A", "ar": "الجسم كامل أ"},
    "full_b": {"en": "Full body B", "fr": "Corps entier B", "ar": "الجسم كامل ب"},
    "full_c": {"en": "Full body C", "fr": "Corps entier C", "ar": "الجسم كامل ج"},
    "upper_a": {"en": "Upper body A", "fr": "Haut du corps A", "ar": "الجزء العلوي أ"},
    "upper_b": {"en": "Upper body B", "fr": "Haut du corps B", "ar": "الجزء العلوي ب"},
    "lower_a": {"en": "Lower body A", "fr": "Bas du corps A", "ar": "الجزء السفلي أ"},
    "lower_b": {"en": "Lower body B", "fr": "Bas du corps B", "ar": "الجزء السفلي ب"},
    "push": {"en": "Push (chest, shoulders, triceps)", "fr": "Poussée (pectoraux, épaules, triceps)", "ar": "الدفع (صدر، أكتاف، ترايسبس)"},
    "pull": {"en": "Pull (back, biceps)", "fr": "Tirage (dos, biceps)", "ar": "السحب (ظهر، بايسبس)"},
    "legs": {"en": "Legs", "fr": "Jambes", "ar": "الأرجل"},
    "cardio": {"en": "Cardio and core", "fr": "Cardio et gainage", "ar": "كارديو وعضلات الجذع"},
}

GOALS = {
    "lose_fat": {"en": "Fat loss", "fr": "Perte de gras", "ar": "خسارة الدهون"},
    "build_muscle": {"en": "Muscle building", "fr": "Prise de muscle", "ar": "بناء العضلات"},
    "get_stronger": {"en": "Strength", "fr": "Force", "ar": "القوة"},
    "get_fitter": {"en": "Fitness", "fr": "Forme physique", "ar": "اللياقة البدنية"},
}

FALLBACK = {
    "en": {
        "title": "{goal} plan, {days} days a week",
        "summary": "A {days}-day plan built around your goal and level. Aim for about {calories} kcal and {protein} g of protein a day, and add a little weight or a rep or two each week while keeping good form.",
        "warmup": ["5 minutes of easy cardio (bike, brisk walk or rowing).", "Arm circles, hip circles and leg swings, 10 each side.", "1–2 light sets of the first exercise before the working sets."],
        "progression": [
            ("Learn the movements", "Use a weight you could lift 3 more times. Note the weights you use."),
            ("Add repetitions", "Do 1–2 more reps per set than last week with the same weights."),
            ("Add weight", "When you reach the top of the rep range, add the smallest weight step and start again at the bottom."),
            ("Lighter week", "Do half the sets with the same weights to recover, then start the next 4 weeks a little heavier."),
        ],
        "cardio": {
            "lose_fat": "Walk 8,000–10,000 steps a day and add 2–3 sessions of 20–30 minutes of easy cardio.",
            "build_muscle": "Keep 1–2 short sessions of easy cardio a week for your heart, without tiring your legs before leg days.",
            "get_stronger": "1–2 sessions of 20 minutes of easy cardio a week help recovery between heavy sessions.",
            "get_fitter": "Build up to 150 minutes of moderate cardio a week, with one session of short intervals.",
        },
        "tips": ["Sleep 7–9 hours: it is when your body recovers and adapts.", "Spread your protein over 3–4 meals a day.", "Stop any exercise that causes sharp pain, and ask a professional.", "Consistency beats intensity: never miss two sessions in a row."],
    },
    "fr": {
        "title": "Programme {goal}, {days} jours par semaine",
        "summary": "Un programme de {days} jours construit selon votre objectif et votre niveau. Visez environ {calories} kcal et {protein} g de protéines par jour, et ajoutez un peu de charge ou une à deux répétitions chaque semaine en gardant une bonne technique.",
        "warmup": ["5 minutes de cardio léger (vélo, marche rapide ou rameur).", "Cercles de bras, de hanches et balancements de jambes, 10 de chaque côté.", "1 à 2 séries légères du premier exercice avant les séries de travail."],
        "progression": [
            ("Apprendre les mouvements", "Prenez une charge que vous pourriez soulever 3 fois de plus. Notez vos charges."),
            ("Ajouter des répétitions", "Faites 1 à 2 répétitions de plus par série que la semaine précédente, avec la même charge."),
            ("Ajouter de la charge", "Quand vous atteignez le haut de la fourchette, ajoutez le plus petit palier de charge et repartez du bas."),
            ("Semaine allégée", "Faites la moitié des séries avec les mêmes charges pour récupérer, puis reprenez 4 semaines un peu plus lourd."),
        ],
        "cardio": {
            "lose_fat": "Marchez 8 000 à 10 000 pas par jour et ajoutez 2 à 3 séances de 20 à 30 minutes de cardio léger.",
            "build_muscle": "Gardez 1 à 2 courtes séances de cardio léger par semaine pour le cœur, sans fatiguer les jambes avant les séances de jambes.",
            "get_stronger": "1 à 2 séances de 20 minutes de cardio léger par semaine aident à récupérer entre les séances lourdes.",
            "get_fitter": "Montez progressivement à 150 minutes de cardio modéré par semaine, dont une séance de fractionné court.",
        },
        "tips": ["Dormez 7 à 9 heures : c'est là que le corps récupère et progresse.", "Répartissez vos protéines sur 3 à 4 repas par jour.", "Arrêtez tout exercice qui provoque une douleur vive et demandez conseil à un professionnel.", "La régularité compte plus que l'intensité : ne manquez jamais deux séances de suite."],
    },
    "ar": {
        "title": "برنامج {goal}، {days} أيام في الأسبوع",
        "summary": "برنامج من {days} أيام مبني على هدفك ومستواك. احرص على نحو {calories} سعرة حرارية و{protein} غرامًا من البروتين يوميًا، وأضف قليلًا من الوزن أو تكرارًا أو اثنين كل أسبوع مع الحفاظ على الأداء الصحيح.",
        "warmup": ["5 دقائق من الكارديو الخفيف (دراجة أو مشي سريع أو آلة التجديف).", "دوائر بالذراعين والوركين وتأرجح الساقين، 10 مرات لكل جهة.", "مجموعة أو مجموعتان خفيفتان من التمرين الأول قبل مجموعات العمل."],
        "progression": [
            ("تعلّم الحركات", "استخدم وزنًا يمكنك رفعه 3 مرات إضافية. سجّل الأوزان التي تستعملها."),
            ("زيادة التكرارات", "أدِّ تكرارًا أو اثنين أكثر في كل مجموعة مقارنة بالأسبوع الماضي بنفس الوزن."),
            ("زيادة الوزن", "عندما تصل إلى أعلى نطاق التكرارات، أضف أصغر زيادة في الوزن وابدأ من جديد من أسفل النطاق."),
            ("أسبوع خفيف", "أدِّ نصف المجموعات بنفس الأوزان للتعافي، ثم ابدأ الأسابيع الأربعة التالية بوزن أثقل قليلًا."),
        ],
        "cardio": {
            "lose_fat": "امشِ من 8000 إلى 10000 خطوة يوميًا وأضف 2 إلى 3 حصص من الكارديو الخفيف لمدة 20 إلى 30 دقيقة.",
            "build_muscle": "حافظ على حصة أو حصتين قصيرتين من الكارديو الخفيف أسبوعيًا لصحة القلب، دون إرهاق الساقين قبل أيام الأرجل.",
            "get_stronger": "حصة أو حصتان من الكارديو الخفيف لمدة 20 دقيقة أسبوعيًا تساعدان على التعافي بين الحصص الثقيلة.",
            "get_fitter": "ارفع المدة تدريجيًا إلى 150 دقيقة من الكارديو المعتدل أسبوعيًا، مع حصة واحدة من التمارين المتقطعة القصيرة.",
        },
        "tips": ["نم من 7 إلى 9 ساعات: ففي النوم يتعافى الجسم ويتطور.", "وزّع البروتين على 3 إلى 4 وجبات في اليوم.", "أوقف أي تمرين يسبب ألمًا حادًا واستشر مختصًا.", "الاستمرارية أهم من الشدة: لا تفوّت حصتين متتاليتين."],
    },
}
