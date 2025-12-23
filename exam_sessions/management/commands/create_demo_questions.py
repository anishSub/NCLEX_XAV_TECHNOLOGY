from django.core.management.base import BaseCommand
from questions.models import Questions
from scenarios.models import Scenarios


class Command(BaseCommand):
    help = 'Creates NCLEX-pattern questions across full difficulty spectrum (-3 to +3 logits)'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Creating NCLEX-pattern questions across difficulty levels...')
        
        # Clear existing questions
        Questions.objects.all().delete()
        Scenarios.objects.all().delete()
        
        created_count = 0
        
        # ========== VERY EASY (-3.0 to -2.0) ==========
        # Basic recall, fundamental nursing knowledge
        
        Questions.objects.create(
            text="What is the normal range for adult heart rate?",
            type="MCQ",
            options=[
                {"id": "A", "text": "40-60 beats per minute"},
                {"id": "B", "text": "60-100 beats per minute"},
                {"id": "C", "text": "100-120 beats per minute"},
                {"id": "D", "text": "120-140 beats per minute"}
            ],
            correct_option_ids=["B"],
            difficulty_logit=-3.0,
            rationale="Normal adult heart rate is 60-100 bpm. This is fundamental vital signs knowledge."
        )
        created_count += 1
        
        Questions.objects.create(
            text="A nurse is teaching handwashing. How long should the nurse scrub hands?",
            type="MCQ",
            options=[
                {"id": "A", "text": "5 seconds"},
                {"id": "B", "text": "10 seconds"},
                {"id": "C", "text": "20 seconds"},
                {"id": "D", "text": "60 seconds"}
            ],
            correct_option_ids=["C"],
            difficulty_logit=-2.5,
            rationale="CDC recommends 20 seconds of handwashing. Basic infection control."
        )
        created_count += 1
        
        # ========== EASY (-2.0 to -1.0) ==========
        # Simple application of basic concepts
        
        Questions.objects.create(
            text="A client has a blood pressure of 160/95 mmHg. The nurse should recognize this as:",
            type="MCQ",
            options=[
                {"id": "A", "text": "Normal blood pressure"},
                {"id": "B", "text": "Prehypertension"},
                {"id": "C", "text": "Stage 1 hypertension"},
                {"id": "D", "text": "Stage 2 hypertension"}
            ],
            correct_option_ids=["D"],
            difficulty_logit=-1.5,
            rationale="BP ≥160/100 is Stage 2 hypertension. Requires knowledge of BP classifications."
        )
        created_count += 1
        
        Questions.objects.create(
            text="Which vital sign should the nurse assess before administering digoxin?",
            type="MCQ",
            options=[
                {"id": "A", "text": "Temperature"},
                {"id": "B", "text": "Apical pulse"},
                {"id": "C", "text": "Respiratory rate"},
                {"id": "D", "text": "Blood pressure"}
            ],
            correct_option_ids=["B"],
            difficulty_logit=-1.0,
            rationale="Apical pulse must be >60 bpm before giving digoxin due to bradycardia risk."
        )
        created_count += 1
        
        # ========== BELOW AVERAGE (-1.0 to -0.5) ==========
        # Application with some critical thinking
        
        Questions.objects.create(
            text="A client with diabetes mellitus has a blood glucose of 45 mg/dL. Which action should the nurse take first?",
            type="MCQ",
            options=[
                {"id": "A", "text": "Administer regular insulin subcutaneously"},
                {"id": "B", "text": "Give 15 grams of simple carbohydrates"},
                {"id": "C", "text": "Notify the healthcare provider"},
                {"id": "D", "text": "Recheck blood glucose in 30 minutes"}
            ],
            correct_option_ids=["B"],
            difficulty_logit=-0.7,
            rationale="Hypoglycemia (<70 mg/dL) requires immediate treatment with 15g simple carbs (15-15 rule)."
        )
        created_count += 1
        
        Questions.objects.create(
            text="A nurse is caring for a postoperative client. Which assessment findings indicate possible hemorrhage? Select all that apply.",
            type="SATA",
            options=[
                {"id": "A", "text": "Increased blood pressure"},
                {"id": "B", "text": "Decreased blood pressure"},
                {"id": "C", "text": "Increased heart rate"},
                {"id": "D", "text": "Warm, flushed skin"},
                {"id": "E", "text": "Cool, clammy skin"}
            ],
            correct_option_ids=["B", "C", "E"],
            difficulty_logit=-0.5,
            rationale="Hemorrhage causes hypotension, tachycardia, and cool/clammy skin from hypovolemic shock."
        )
        created_count += 1
        
        # ========== AVERAGE (−0.5 to +0.5) ==========
        # Standard NCLEX difficulty - analysis and synthesis
        
        Questions.objects.create(
            text="A nurse is caring for a client with heart failure. Which dietary instruction should the nurse provide?",
            type="MCQ",
            options=[
                {"id": "A", "text": "Increase sodium intake to 4000 mg/day"},
                {"id": "B", "text": "Limit fluid intake to 2 liters per day"},
                {"id": "C", "text": "Eat large meals three times daily"},
                {"id": "D", "text": "Increase potassium-rich foods without restriction"}
            ],
            correct_option_ids=["B"],
            difficulty_logit=0.0,
            rationale="Fluid restriction (typically 2L/day) is standard for heart failure to prevent fluid overload."
        )
        created_count += 1
        
        Questions.objects.create(
            text="A nurse is preparing to administer a blood transfusion. Which actions should the nurse take? Select all that apply.",
            type="SATA",
            options=[
                {"id": "A", "text": "Verify blood type and Rh with another nurse"},
                {"id": "B", "text": "Use a 20-gauge or larger IV catheter"},
                {"id": "C", "text": "Prime tubing with normal saline"},
                {"id": "D", "text": "Remain with client for first 15 minutes"},
                {"id": "E", "text": "Infuse blood over 6 hours"}
            ],
            correct_option_ids=["A", "B", "C", "D"],
            difficulty_logit=0.3,
            rationale="All are correct except E - blood should be transfused within 4 hours, not 6."
        )
        created_count += 1
        
        Questions.objects.create(
            text="A client presents with confusion, increased thirst, and urinary frequency. Laboratory results show glucose 850 mg/dL. Which condition should the nurse suspect?",
            type="MCQ",
            options=[
                {"id": "A", "text": "Diabetic ketoacidosis (DKA)"},
                {"id": "B", "text": "Hyperosmolar hyperglycemic state (HHS)"},
                {"id": "C", "text": "Hypoglycemia"},
                {"id": "D", "text": "Insulin shock"}
            ],
            correct_option_ids=["B"],
            difficulty_logit=0.5,
            rationale="HHS presents with severe hyperglycemia (>600 mg/dL), confusion, and dehydration without significant ketosis."
        )
        created_count += 1
        
        # ========== ABOVE AVERAGE (+0.5 to +1.0) ==========
        # Requires deeper analysis and prioritization
        
        Questions.objects.create(
            text="A nurse receives report on four clients. Which client should the nurse assess first?",
            type="MCQ",
            options=[
                {"id": "A", "text": "Client with diabetes who has a blood glucose of 250 mg/dL"},
                {"id": "B", "text": "Client with chronic heart failure who has 2+ pitting edema"},
                {"id": "C", "text": "Client with asthma who has an oxygen saturation of 89% on room air"},
                {"id": "D", "text": "Client post-appendectomy who reports pain of 6/10"}
            ],
            correct_option_ids=["C"],
            difficulty_logit=0.7,
            rationale="O2 sat 89% requires immediate intervention (respiratory ABCs priority). Other conditions are concerning but not immediately life-threatening."
        )
        created_count += 1
        
        Questions.objects.create(
            text="A client is receiving IV heparin for deep vein thrombosis. Which laboratory value is most important for the nurse to monitor?",
            type="MCQ",
            options=[
                {"id": "A", "text": "Platelet count"},
                {"id": "B", "text": "Activated partial thromboplastin time (aPTT)"},
                {"id": "C", "text": "Prothrombin time (PT)"},
                {"id": "D", "text": "International normalized ratio (INR)"}
            ],
            correct_option_ids=["B"],
            difficulty_logit=0.8,
            rationale="aPTT monitors heparin therapy (goal: 1.5-2× control). PT/INR monitor warfarin, not heparin."
        )
        created_count += 1
        
        Questions.objects.create(
            text="A client with chronic kidney disease has the following laboratory values: K+ 6.2 mEq/L, BUN 85 mg/dL, Creatinine 4.5 mg/dL. Which ECG change should the nurse anticipate?",
            type="MCQ",
            options=[
                {"id": "A", "text": "Prolonged PR interval"},
                {"id": "B", "text": "Peaked T waves"},
                {"id": "C", "text": "Widened QRS complex"},
                {"id": "D", "text": "ST segment elevation"}
            ],
            correct_option_ids=["B"],
            difficulty_logit=1.0,
            rationale="Hyperkalemia (K+ >5.5) causes peaked T waves initially, then widened QRS, then cardiac arrest if untreated."
        )
        created_count += 1
        
        # ========== DIFFICULT (+1.0 to +2.0) ==========
        # Complex scenarios requiring advanced critical thinking
        
        Questions.objects.create(
            text="A client with acute respiratory distress syndrome (ARDS) on mechanical ventilation has the following arterial blood gas results: pH 7.28, PaCO2 55 mmHg, PaO2 58 mmHg, HCO3 24 mEq/L. Which ventilator adjustment should the nurse anticipate?",
            type="MCQ",
            options=[
                {"id": "A", "text": "Increase respiratory rate"},
                {"id": "B", "text": "Increase tidal volume"},
                {"id": "C", "text": "Increase PEEP (positive end-expiratory pressure)"},
                {"id": "D", "text": "Decrease FiO2"}
            ],
            correct_option_ids=["C"],
            difficulty_logit=1.3,
            rationale="ARDS with severe hypoxemia (PaO2 58) requires increased PEEP to improve oxygenation by recruiting collapsed alveoli. Respiratory acidosis is secondary."
        )
        created_count += 1
        
        Questions.objects.create(
            text="A nurse is caring for a client receiving chemotherapy who develops tumor lysis syndrome. Which interventions should the nurse implement? Select all that apply.",
            type="SATA",
            options=[
                {"id": "A", "text": "Administer allopurinol as prescribed"},
                {"id": "B", "text": "Restrict fluid intake"},
                {"id": "C", "text": "Monitor for cardiac dysrhythmias"},
                {"id": "D", "text": "Administer calcium gluconate as prescribed"},
                {"id": "E", "text": "Prepare for dialysis if indicated"}
            ],
            correct_option_ids=["A", "C", "D", "E"],
            difficulty_logit=1.5,
            rationale="Tumor lysis causes hyperuricemia (allopurinol), hyperkalemia (dysrhythmias), hypocalcemia (calcium), and may need dialysis. Fluids should be increased, not restricted."
        )
        created_count += 1
        
        Questions.objects.create(
            text="A client is diagnosed with syndrome of inappropriate antidiuretic hormone (SIADH). Which laboratory findings should the nurse expect? Select all that apply.",
            type="SATA",
            options=[
                {"id": "A", "text": "Serum sodium 118 mEq/L"},
                {"id": "B", "text": "Serum osmolality 260 mOsm/kg"},
                {"id": "C", "text": "Urine specific gravity 1.035"},
                {"id": "D", "text": "Serum sodium 155 mEq/L"},
                {"id": "E", "text": "Urine specific gravity 1.003"}
            ],
            correct_option_ids=["A", "B", "C"],
            difficulty_logit=1.7,
            rationale="SIADH causes excess ADH → water retention → dilutional hyponatremia, low serum osmolality, concentrated urine (high specific gravity). Opposite occurs in diabetes insipidus."
        )
        created_count += 1
        
        # ========== VERY DIFFICULT (+2.0 to +3.0) ==========
        # Expert-level, requires synthesis of multiple complex concepts
        
        Questions.objects.create(
            text="A client with myasthenia gravis is experiencing a crisis. How should the nurse differentiate between myasthenic crisis and cholinergic crisis?",
            type="MCQ",
            options=[
                {"id": "A", "text": "Myasthenic crisis improves with edrophonium; cholinergic crisis worsens"},
                {"id": "B", "text": "Myasthenic crisis causes muscle fasciculations; cholinergic crisis does not"},
                {"id": "C", "text": "Myasthenic crisis has no GI symptoms; cholinergic crisis causes diarrhea"},
                {"id": "D", "text": "Myasthenic crisis occurs in the morning; cholinergic crisis occurs at night"}
            ],
            correct_option_ids=["A"],
            difficulty_logit=2.0,
            rationale="Tensilon (edrophonium) test: improves myasthenic crisis (needs more anticholinesterase) but worsens cholinergic crisis (has too much). Both have respiratory failure but different causes."
        )
        created_count += 1
        
        Questions.objects.create(
            text="A newborn is diagnosed with transposition of the great arteries. Which intervention is priority until surgical correction?",
            type="MCQ",
            options=[
                {"id": "A", "text": "Administer oxygen at 100% FiO2"},
                {"id": "B", "text": "Initiate prostaglandin E1 infusion"},
                {"id": "C", "text": "Prepare for immediate intubation"},
                {"id": "D", "text": "Administer indomethacin IV"}
            ],
            correct_option_ids=["B"],
            difficulty_logit=2.3,
            rationale="TGA has parallel circulation (incompatible with life). PGE1 keeps ductus arteriosus open to allow mixing of oxygenated/deoxygenated blood until surgical switch. Indomethacin closes PDA (opposite)."
        )
        created_count += 1
        
        Questions.objects.create(
            text="A client develops autonomic dysreflexia after spinal cord injury at T4. Which interventions should the nurse implement immediately? Select all that apply.",
            type="SATA",
            options=[
                {"id": "A", "text": "Place client in high-Fowler's position"},
                {"id": "B", "text": "Check for bladder distention and catheterize if needed"},
                {"id": "C", "text": "Administer antihypertensive medication as prescribed"},
                {"id": "D", "text": "Lay client flat to improve cerebral perfusion"},
                {"id": "E", "text": "Check for fecal impaction"}
            ],
            correct_option_ids=["A", "B", "C", "E"],
            difficulty_logit=2.5,
            rationale="Autonomic dysreflexia is life-threatening hypertensive emergency (SCI above T6). Elevate HOB to lower BP, remove noxious stimuli (full bladder/bowel most common), give antihypertensives. Never lay flat (worsens BP)."
        )
        created_count += 1
        
        Questions.objects.create(
            text="A client with acute decompensated heart failure has the following hemodynamic values: PAWP 28 mmHg, cardiac index 1.8 L/min/m², SVR 1800 dynes. Which medication should the nurse anticipate?",
            type="MCQ",
            options=[
                {"id": "A", "text": "Dopamine to increase contractility"},
                {"id": "B", "text": "Norepinephrine to increase SVR"},
                {"id": "C", "text": "Nitroprusside to decrease afterload"},
                {"id": "D", "text": "Normal saline bolus to increase preload"}
            ],
            correct_option_ids=["C"],
            difficulty_logit=3.0,
            rationale="High PAWP (>18) = volume overload, low CI (<2.2) = poor output, high SVR (>1200) = high afterload. Need vasodilator (nitroprusside) to decrease afterload and improve cardiac output. Dopamine/fluids worsen volume overload; norepinephrine increases SVR."
        )
        created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} questions!')
        )
        
        # Show distribution
        self.stdout.write('\nDifficulty Distribution:')
        self.stdout.write('  Very Easy (-3.0 to -2.0): 2 questions')
        self.stdout.write('  Easy (-2.0 to -1.0): 2 questions')
        self.stdout.write('  Below Average (-1.0 to -0.5): 2 questions')
        self.stdout.write('  Average (-0.5 to +0.5): 3 questions')
        self.stdout.write('  Above Average (+0.5 to +1.0): 3 questions')
        self.stdout.write('  Difficult (+1.0 to +2.0): 3 questions')
        self.stdout.write('  Very Difficult (+2.0 to +3.0): 4 questions')
        self.stdout.write(f'\nTotal: {created_count} questions across full spectrum')
