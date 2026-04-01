from django.core.management.base import BaseCommand
from questions.models import Questions, QuestionType
from categories.models import Categories


def opt(a, b, c, d):
    return [
        {'id': 'A', 'text': a},
        {'id': 'B', 'text': b},
        {'id': 'C', 'text': c},
        {'id': 'D', 'text': d},
    ]


# 10 questions × 8 categories = 80 questions
# Format: (text, options, correct_letter, category_id)
QUESTIONS = [
    # ── Category 1: Management of Care ──────────────────────────────────────
    ("A nurse is delegating tasks to a UAP. Which task is MOST appropriate to delegate?",
     opt("Assessing a patient's pain level", "Ambulating a stable post-op patient",
         "Teaching a diabetic patient about insulin", "Interpreting lab results"), 'B', 1),

    ("The nurse uses SBAR communication. What does the 'R' stand for?",
     opt("Report", "Recommendation", "Review", "Reason"), 'B', 1),

    ("Which action demonstrates the nurse's advocacy role?",
     opt("Administering medication without checking allergies",
         "Questioning a medication order that seems unsafe",
         "Ignoring a patient's refusal of treatment",
         "Documenting care after the shift ends"), 'B', 1),

    ("A nurse discovers a medication error made by a colleague. What is the FIRST action?",
     opt("Report the colleague to administration", "Assess the patient for adverse effects",
         "Document the error in the chart", "Notify the patient immediately"), 'B', 1),

    ("Which principle describes giving only the information needed to perform a task?",
     opt("Confidentiality", "Need-to-know basis", "Informed consent", "Autonomy"), 'B', 1),

    ("Restraints may be applied without a physician order in which situation?",
     opt("When a patient is confused", "In an emergency to prevent immediate harm",
         "When family requests them", "When the patient is uncooperative"), 'B', 1),

    ("The charge nurse prioritizes patient assignments. A nurse with a heavy load asks for help. What is BEST?",
     opt("Tell the nurse to manage their own workload",
         "Redistribute tasks among team members",
         "Ask the patient to wait", "Call the physician"), 'B', 1),

    ("Which statement about informed consent is TRUE?",
     opt("The nurse is responsible for obtaining informed consent",
         "The physician must explain risks and alternatives before obtaining consent",
         "A signed consent form alone is sufficient",
         "Informed consent is not required for minor procedures"), 'B', 1),

    ("A patient with dementia pulls at their IV. What is the MOST appropriate nursing action?",
     opt("Apply wrist restraints immediately",
         "Reorient the patient, use mitts, and notify the physician",
         "Ignore the behavior", "Ask family to restrain the patient"), 'B', 1),

    ("Which is an example of an intentional tort?",
     opt("Failing to prevent a fall", "Battery — touching a patient without consent",
         "Giving the wrong dose accidentally", "Delegating inappropriately"), 'B', 1),

    # ── Category 2: Safety and Infection Control ─────────────────────────────
    ("A patient is placed on Contact Precautions. Which PPE is required FIRST when entering the room?",
     opt("N95 respirator", "Gloves and gown", "Face shield only", "Surgical mask"), 'B', 2),

    ("The nurse is caring for a patient with active pulmonary TB. Which precaution is required?",
     opt("Standard Precautions only", "Airborne Precautions with N95",
         "Droplet Precautions with surgical mask", "Contact Precautions with gown"), 'B', 2),

    ("Which hand hygiene method is MOST effective against C. difficile?",
     opt("Alcohol-based hand rub", "Soap and water", "Antiseptic wipes", "Glove use alone"), 'B', 2),

    ("A nurse finds a patient on the floor. What is the FIRST action?",
     opt("Call the physician", "Assess the patient for injuries",
         "Help the patient back to bed", "Complete an incident report"), 'B', 2),

    ("Which patient is at HIGHEST risk for a fall?",
     opt("25-year-old post appendectomy", "70-year-old on diuretics and sedatives",
         "40-year-old with a fractured arm", "55-year-old post colonoscopy"), 'B', 2),

    ("The five rights of medication administration include all EXCEPT:",
     opt("Right drug", "Right assessment", "Right dose", "Right route"), 'B', 2),

    ("A nurse recaps a needle after giving an injection. What is the SAFEST method?",
     opt("Two-handed recapping", "One-handed scoop technique",
         "Asking a colleague to hold the cap", "Disposing uncapped into sharps container"), 'D', 2),

    ("Standard Precautions apply to:",
     opt("Blood only", "All body fluids, secretions, and non-intact skin",
         "Patients with known infections only", "Airborne pathogens only"), 'B', 2),

    ("Which room assignment is MOST appropriate for a patient with MRSA?",
     opt("Semi-private room", "Private room with contact precautions",
         "Any available room", "Shared room with another MRSA patient only"), 'B', 2),

    ("A nurse is teaching a patient about fire safety (RACE). What does 'A' stand for?",
     opt("Alert", "Activate the alarm", "Assess", "Assist"), 'B', 2),

    # ── Category 3: Health Promotion and Maintenance ─────────────────────────
    ("At what age should routine colorectal cancer screening BEGIN for average-risk adults?",
     opt("40 years", "45 years", "50 years", "60 years"), 'B', 3),

    ("A nurse is teaching a pregnant client about folic acid. When should supplementation BEGIN?",
     opt("After the first trimester", "At least one month before conception",
         "Only after a positive pregnancy test", "During the third trimester"), 'B', 3),

    ("Which immunization is recommended annually for all adults?",
     opt("MMR", "Influenza vaccine", "Hepatitis B", "Varicella"), 'B', 3),

    ("A nurse teaches a patient about breast self-examination. When is the BEST time to perform it?",
     opt("First day of the menstrual cycle",
         "7–10 days after the start of the menstrual period",
         "During menstruation", "Any consistent day each month for post-menopausal women"), 'D', 3),

    ("Which behavior indicates a client understands Healthy People goals?",
     opt("Smoking one pack per day", "Walking 30 minutes five days per week",
         "Eating fast food daily", "Sleeping only 4 hours per night"), 'B', 3),

    ("A 2-year-old should achieve which developmental milestone?",
     opt("Riding a bike", "Speaking in 2–3 word phrases",
         "Reading simple words", "Tying shoelaces"), 'B', 3),

    ("Which BMI range is classified as obese?",
     opt("18.5–24.9", "25–29.9", "30 and above", "Below 18.5"), 'C', 3),

    ("A nurse counsels a smoker wanting to quit. Which is the MOST evidence-based first step?",
     opt("Recommend nicotine replacement therapy immediately",
         "Set a firm quit date and discuss cessation strategies",
         "Tell the patient to stop cold turkey", "Refer directly to surgery"), 'B', 3),

    ("The nurse is teaching a new mother about safe sleep for her infant. Which is CORRECT?",
     opt("Place infant prone to prevent flat head",
         "Place infant supine on a firm, flat surface",
         "Co-sleep with the baby for bonding", "Use soft bedding and pillows"), 'B', 3),

    ("Which lab value indicates a patient is at risk for osteoporosis?",
     opt("Elevated serum calcium", "Low bone mineral density on DEXA scan",
         "High vitamin D level", "Elevated phosphorus"), 'B', 3),

    # ── Category 4: Psychosocial Integrity ───────────────────────────────────
    ("A patient states, 'I want to kill myself.' What is the nurse's FIRST action?",
     opt("Call the physician", "Ask directly about a plan",
         "Leave and get help", "Document the statement"), 'B', 4),

    ("Which response by the nurse demonstrates therapeutic communication?",
     opt("'You shouldn't feel that way.'", "'Tell me more about what you're experiencing.'",
         "'Everything will be fine.'", "'I understand exactly how you feel.'"), 'B', 4),

    ("A patient with schizophrenia says, 'The TV is sending me messages.' This is a:",
     opt("Hallucination", "Delusion of reference", "Illusion", "Confabulation"), 'B', 4),

    ("Maslow's hierarchy: which need must be met BEFORE safety needs?",
     opt("Love and belonging", "Self-esteem", "Physiological needs", "Self-actualization"), 'C', 4),

    ("A patient is in the bargaining stage of grief. Which statement reflects this?",
     opt("'I don't believe this is happening.'",
         "'If I get better, I promise I'll change my ways.'",
         "'I am so angry at everyone.'",
         "'There's no point in anything anymore.'"), 'B', 4),

    ("Which action demonstrates respect for patient autonomy?",
     opt("Giving medication without explaining side effects",
         "Allowing a competent patient to refuse treatment",
         "Restraining a confused patient without an order",
         "Making decisions for a patient who can decide"), 'B', 4),

    ("A patient with alcohol use disorder is experiencing tremors 24 hours after admission. The nurse should FIRST:",
     opt("Offer oral fluids", "Assess for signs of delirium tremens and notify the physician",
         "Give a mild anxiolytic without an order", "Apply restraints"), 'B', 4),

    ("Which is a positive symptom of schizophrenia?",
     opt("Flat affect", "Auditory hallucinations", "Social withdrawal", "Alogia"), 'B', 4),

    ("A nurse uses active listening. Which behavior demonstrates this?",
     opt("Interrupting to give advice", "Maintaining eye contact and nodding",
         "Looking at the chart while the patient speaks", "Finishing the patient's sentences"), 'B', 4),

    ("The nurse is caring for a patient in denial about a terminal diagnosis. The BEST response is:",
     opt("Confront the patient with the truth immediately",
         "Sit with the patient and allow them to express feelings",
         "Ask the family to tell the patient", "Avoid discussing it"), 'B', 4),

    # ── Category 5: Basic Care and Comfort ───────────────────────────────────
    ("A patient is NPO after midnight. Surgery is at 0800. At 0600 the patient asks for water. The nurse should:",
     opt("Allow sips of water only", "Explain NPO rationale and offer mouth care",
         "Give ice chips", "Allow clear liquids"), 'B', 5),

    ("Which position is BEST for a patient with dyspnea?",
     opt("Supine", "High Fowler's (90°)", "Prone", "Left lateral Sims'"), 'B', 5),

    ("A patient rates pain 8/10 thirty minutes after IV morphine. The nurse FIRST:",
     opt("Document the response and wait another hour",
         "Reassess pain characteristics and notify the physician",
         "Give another dose immediately without an order",
         "Tell the patient to use relaxation techniques"), 'B', 5),

    ("Which intervention helps prevent pressure injuries in a bedridden patient?",
     opt("Keep head of bed above 60° at all times",
         "Reposition every 2 hours and use pressure-relief mattress",
         "Massage bony prominences vigorously", "Apply tight bandages"), 'B', 5),

    ("A Stage 2 pressure injury is characterized by:",
     opt("Intact skin with non-blanchable redness",
         "Shallow open ulcer with pink/red wound bed",
         "Full-thickness tissue loss with visible bone",
         "Deep tissue purple discoloration"), 'B', 5),

    ("Which action prevents aspiration during enteral feeding?",
     opt("Place patient supine", "Elevate head of bed 30–45° during and after feeding",
         "Give feeding rapidly to save time", "Check residuals only once daily"), 'B', 5),

    ("A patient with urinary incontinence should be offered voiding every:",
     opt("30 minutes", "2 hours", "4 hours", "Only when requested"), 'B', 5),

    ("Which sleep hygiene tip is CORRECT?",
     opt("Drink coffee before bed", "Avoid caffeine/screens before sleep and keep a regular schedule",
         "Nap as much as possible during the day", "Exercise vigorously right before bed"), 'B', 5),

    ("A patient has dry, cracked lips. The nurse's BEST intervention is:",
     opt("Apply petroleum jelly and increase fluid intake",
         "Wipe lips with dry gauze", "Apply alcohol-based mouthwash", "Give IV fluids only"), 'A', 5),

    ("When performing passive range of motion, the nurse should:",
     opt("Move joints rapidly through full range", "Support the joint and move slowly within pain-free range",
         "Push past resistance to increase flexibility", "Avoid moving inflamed joints"), 'B', 5),

    # ── Category 6: Pharmacological and Parenteral Therapies ─────────────────
    ("A patient's apical pulse is 52 bpm before digoxin. The nurse should:",
     opt("Administer the drug as scheduled", "Hold the dose and notify the physician",
         "Give half the dose", "Give the dose and recheck in 1 hour"), 'B', 6),

    ("Which antidote is used for acetaminophen overdose?",
     opt("Naloxone", "N-acetylcysteine", "Flumazenil", "Protamine sulfate"), 'B', 6),

    ("A patient on warfarin has an INR of 5.8. The nurse anticipates administering:",
     opt("Heparin", "Vitamin K", "Aspirin", "Protamine sulfate"), 'B', 6),

    ("Heparin is ordered 5,000 units subcutaneously. The nurse should inject at:",
     opt("90° angle into the deltoid", "45–90° angle into abdominal fat avoiding 2 inches around umbilicus",
         "15° angle into the forearm", "Any available muscle site"), 'B', 6),

    ("A patient develops sudden urticaria, wheezing, and hypotension after IV ampicillin. The FIRST drug to give is:",
     opt("Diphenhydramine IV", "Epinephrine 1:1000 IM",
         "Methylprednisolone IV", "Normal saline bolus"), 'B', 6),

    ("Which electrolyte imbalance is a common adverse effect of loop diuretics?",
     opt("Hyperkalemia", "Hypokalemia", "Hypernatremia", "Hypercalcemia"), 'B', 6),

    ("A patient on lithium has a level of 2.1 mEq/L. The nurse anticipates:",
     opt("Continue therapy, level is therapeutic", "Hold the dose, notify the physician — level is toxic",
         "Double the dose", "Switch to another mood stabilizer"), 'B', 6),

    ("Which medication requires teaching about avoiding tyramine-rich foods?",
     opt("SSRIs", "MAOIs", "Beta-blockers", "Atypical antipsychotics"), 'B', 6),

    ("Before giving metformin, the nurse verifies the patient's:",
     opt("INR", "Serum creatinine and eGFR", "Thyroid function", "Platelet count"), 'B', 6),

    ("A patient is prescribed morphine PCA. The nurse's PRIORITY assessment is:",
     opt("Pain score", "Respiratory rate and sedation level",
         "Blood pressure", "Heart rate"), 'B', 6),

    # ── Category 7: Reduction of Risk Potential ──────────────────────────────
    ("A post-op patient has urine output of 20 mL/hr for 2 hours. The nurse FIRST:",
     opt("Document and reassess in another hour",
         "Assess fluid balance and notify the physician",
         "Increase IV rate without an order",
         "Insert a larger Foley catheter"), 'B', 7),

    ("Which lab value indicates acute kidney injury?",
     opt("Serum creatinine 0.9 mg/dL", "BUN 8 mg/dL",
         "Serum creatinine rising from 0.9 to 2.1 within 48 hours",
         "Urine output 60 mL/hr"), 'C', 7),

    ("A patient post-thyroidectomy reports tingling around the mouth and muscle cramps. The nurse suspects:",
     opt("Hyperkalemia", "Hypocalcemia", "Hyponatremia", "Hypoglycemia"), 'B', 7),

    ("Which finding after a lumbar puncture requires IMMEDIATE nursing action?",
     opt("Mild headache in supine position", "Sudden lower limb weakness and loss of bladder control",
         "Mild back soreness at puncture site", "Thirst"), 'B', 7),

    ("A patient is post-coronary angiography via right femoral artery. The nurse checks for:",
     opt("Hematoma and loss of pedal pulse in the right leg",
         "Hematoma at the left elbow", "Urine output only", "Blood glucose"), 'A', 7),

    ("A chest tube with water-seal drainage shows continuous bubbling in the water-seal chamber. This indicates:",
     opt("Normal tidaling", "Air leak — clamp and notify physician",
         "Tube blockage", "Normal drainage"), 'B', 7),

    ("A patient with COPD has SpO₂ of 88%. The target SpO₂ for a COPD patient is:",
     opt("98–100%", "88–92%", "80–85%", "95–98%"), 'B', 7),

    ("Which ABG result indicates respiratory acidosis?",
     opt("pH 7.48, PaCO₂ 30, HCO₃ 22", "pH 7.30, PaCO₂ 55, HCO₃ 24",
         "pH 7.35, PaCO₂ 40, HCO₃ 22", "pH 7.50, PaCO₂ 40, HCO₃ 30"), 'B', 7),

    ("A patient's blood pressure drops from 130/80 to 90/60 after standing. This is called:",
     opt("Essential hypertension", "Orthostatic hypotension",
         "Hypertensive urgency", "White coat syndrome"), 'B', 7),

    ("A post-op patient has a temperature of 38.8°C on day 1. The most likely cause is:",
     opt("Wound infection", "Atelectasis",
         "Deep vein thrombosis", "Urinary tract infection"), 'B', 7),

    # ── Category 8: Physiological Adaptation ─────────────────────────────────
    ("A patient with DKA is MOST likely to present with:",
     opt("Bradycardia and hypertension",
         "Kussmaul breathing, fruity breath, and polyuria",
         "Bradypnea and hypoglycemia",
         "Hypothermia and diaphoresis"), 'B', 8),

    ("The nurse is caring for a patient in hypovolemic shock. The FIRST intervention is:",
     opt("Administer vasopressors", "Establish IV access and give fluid resuscitation",
         "Prepare for surgery", "Give blood immediately"), 'B', 8),

    ("A patient with acute MI receives thrombolytics. The nurse monitors for:",
     opt("Hypertension", "Bleeding and signs of intracranial hemorrhage",
         "Hyperkalemia", "Fluid overload"), 'B', 8),

    ("Which finding indicates increased intracranial pressure?",
     opt("Tachycardia, hypotension, and rapid respirations",
         "Cushing's triad: bradycardia, hypertension, and irregular respirations",
         "Hypotension, tachycardia, and fever",
         "Normal LOC with severe headache only"), 'B', 8),

    ("A patient with SIADH will likely have:",
     opt("Hypernatremia and polyuria",
         "Hyponatremia and decreased urine output",
         "Hyperkalemia and polydipsia",
         "Normal sodium and concentrated urine"), 'B', 8),

    ("Which is the earliest sign of hypoxia?",
     opt("Cyanosis", "Restlessness and confusion", "Bradycardia", "Hypotension"), 'B', 8),

    ("A patient with cirrhosis develops asterixis. This is a sign of:",
     opt("Hypoglycemia", "Hepatic encephalopathy",
         "Alcohol withdrawal", "Electrolyte imbalance"), 'B', 8),

    ("A patient post-kidney transplant is started on cyclosporine. The nurse monitors for:",
     opt("Hypoglycemia", "Nephrotoxicity and signs of infection",
         "Bradycardia", "Hemorrhage"), 'B', 8),

    ("Normal serum potassium range is:",
     opt("1.5–2.5 mEq/L", "3.5–5.0 mEq/L", "5.5–7.0 mEq/L", "7.5–9.0 mEq/L"), 'B', 8),

    ("A burn patient receives the Parkland formula. Which fluid is used in the first 24 hours?",
     opt("D5W", "Lactated Ringer's", "Normal saline 0.45%", "Albumin"), 'B', 8),
]


class Command(BaseCommand):
    help = 'Seeds 80 NCLEX MCQ questions across all 8 game categories'

    def handle(self, *args, **options):
        # Get or create MCQ question type
        mcq_type, _ = QuestionType.objects.get_or_create(
            code='MCQ',
            defaults={
                'display_name': 'Multiple Choice Question',
                'description': 'Standard 4-option multiple choice',
                'is_active': True,
            }
        )

        created = 0
        skipped = 0

        for text, options, correct_letter, cat_id in QUESTIONS:
            try:
                category = Categories.objects.get(id=cat_id)
            except Categories.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Category {cat_id} not found, skipping.'))
                skipped += 1
                continue

            # Skip if this exact question text already exists
            if Questions.objects.filter(text=text).exists():
                skipped += 1
                continue

            q = Questions.objects.create(
                text=text,
                question_type=mcq_type,
                type='MCQ',
                options=options,
                correct_option_ids=[correct_letter],
                difficulty_logit=0.0,
            )
            q.category_ids.add(category)
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Done! Created {created} questions, skipped {skipped} duplicates.'
        ))

        # Summary by category
        self.stdout.write('\n📊 Questions per category:')
        for cat in Categories.objects.all().order_by('id'):
            count = Questions.objects.filter(
                category_ids=cat,
                options__isnull=False,
            ).count()
            self.stdout.write(f'  [{cat.id}] {cat.name}: {count}')
