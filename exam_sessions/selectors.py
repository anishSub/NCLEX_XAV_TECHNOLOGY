# exam_sessions/selectors.py
from questions.models import Questions

def get_next_question(session):
    """
    Selects the next question for the student.
    
    PRIORITY 1: If the previous question was part of a scenario, continue with
                the next sequential question in that scenario (enforces 6-question sequence).
    
    PRIORITY 2: Otherwise, use adaptive selection based on student's current ability.
    
    This ensures NCLEX NGN scenarios are delivered as unfolding case studies.
    """
    target = session.current_theta
    
    # Extract answered question IDs from question_history
    answered_ids = [entry.get('question_id') for entry in session.question_history if 'question_id' in entry]
    
    print(f"🔍 get_next_question: target={target}, answered_ids={answered_ids}")
    
    # ========== SCENARIO SEQUENCING LOGIC ==========
    # Check if we're in the middle of a scenario
    if answered_ids:
        last_question_id = answered_ids[-1]
        try:
            last_question = Questions.objects.get(id=last_question_id)
            
            # If last question was part of a scenario, check for next question in sequence
            if last_question.parent_scenario and last_question.scenario_question_number:
                next_scenario_question = Questions.objects.filter(
                    parent_scenario=last_question.parent_scenario,
                    scenario_question_number=last_question.scenario_question_number + 1
                ).first()
                
                if next_scenario_question:
                    print(f"📚 SCENARIO CONTINUATION: Returning Q{next_scenario_question.scenario_question_number} of scenario '{last_question.parent_scenario.title}'")
                    return next_scenario_question
                else:
                    print(f"✅ SCENARIO COMPLETE: Finished all questions for '{last_question.parent_scenario.title}', returning to adaptive selection")
        except Questions.DoesNotExist:
            print(f"⚠️ Warning: Last question ID {last_question_id} not found")
    
    # ========== ADAPTIVE SELECTION LOGIC ==========
    # No active scenario, use normal adaptive selection
    print(f"🎯 ADAPTIVE SELECTION: Selecting question near theta={target}")
    
    # Query for questions within +/- 0.3 logit of the student's current ability
    question = Questions.objects.filter(
        difficulty_logit__range=(target - 0.3, target + 0.3)
    ).exclude(id__in=answered_ids).order_by('?').first()

    # Fallback: if no questions in that narrow range, widen the search
    if not question:
        question = Questions.objects.exclude(id__in=answered_ids).order_by('?').first()
    
    if question:
        if question.parent_scenario:
            print(f"✅ Selected NEW SCENARIO: '{question.parent_scenario.title}' Q{question.scenario_question_number}")
        else:
            print(f"✅ Selected standalone question ID: {question.id}")
    else:
        print(f"❌ No questions available")
    
    return question