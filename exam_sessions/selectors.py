# exam_sessions/selectors.py
from questions.models import Questions

def get_next_question(session):
    """
    Selects a question within the student's difficulty window,
    excluding already answered questions.
    """
    target = session.current_theta
    
    # Extract answered question IDs from question_history
    answered_ids = [entry.get('question_id') for entry in session.question_history if 'question_id' in entry]
    
    print(f"🔍 get_next_question: target={target}, answered_ids={answered_ids}")
    
    # Query for questions within +/- 0.3 logit of the student's current ability
    question = Questions.objects.filter(
        difficulty_logit__range=(target - 0.3, target + 0.3)
    ).exclude(id__in=answered_ids).order_by('?').first()

    # Fallback: if no questions in that narrow range, widen the search
    if not question:
        question = Questions.objects.exclude(id__in=answered_ids).order_by('?').first()
    
    print(f"✅ Selected question ID: {question.id if question else 'None'}")
    
    return question