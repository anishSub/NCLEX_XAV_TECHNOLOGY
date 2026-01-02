
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nclex_core.settings')
django.setup()

from questions.models import Questions
from exam_sessions.models import ExamSessions
from categories.models import Categories

def check_integrity():
    print("=== DATABASE INTEGRITY CHECK ===")
    
    # 1. Check Scenario Questions for Categories
    scenario_questions = Questions.objects.filter(parent_scenario__isnull=False)
    print(f"\n[Scenario Questions]")
    print(f"Total Questions belonging to scenarios: {scenario_questions.count()}")
    
    orphans = []
    for q in scenario_questions:
        cat_count = q.category_ids.count()
        if cat_count == 0:
            orphans.append(q.id)
            
    print(f"Scenario Questions WITHOUT Categories: {len(orphans)}")
    if orphans:
        print(f"⚠️  IDs without categories: {orphans}")
    else:
        print("✅ All scenario questions have at least one category.")

    # 2. Check a recent session
    try:
        last_session = ExamSessions.objects.filter(session_type='PRACTICE').last()
        if last_session:
            print(f"\n[Last Practice Session ID: {last_session.id}]")
            print(f"Total Questions Expected: {last_session.total_questions}")
            print(f"Selected Categories: {last_session.selected_categories}")
            print(f"History Length: {len(last_session.question_history)}")
            
            # Simulate the query
            answered_ids = [h['question_id'] for h in last_session.question_history]
            candidates = Questions.objects.filter(
                category_ids__id__in=last_session.selected_categories
            ).exclude(id__in=answered_ids).distinct()
            
            print(f"Actual Remaining Candidates in DB: {candidates.count()}")
            
            if candidates.count() == 0 and len(last_session.question_history) < last_session.total_questions:
                print("🚨 BUG CONFIRMED: Query returns 0 but session is not full.")
        else:
            print("\nNo practice sessions found.")
            
    except Exception as e:
        print(f"Error checking session: {e}")

if __name__ == "__main__":
    check_integrity()
