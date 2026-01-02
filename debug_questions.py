import os
import django
import sys

# Setup Django environment
sys.path.append('/Users/macm2/Desktop/NCLEX_XAV_TECHNOLOGY')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nclex_core.settings')
django.setup()

from questions.models import Questions
from scenarios.models import Scenarios

try:
    scenario = Scenarios.objects.get(title__icontains="Case Study 101")
    print(f"Scenario: {scenario.title} (ID: {scenario.id})")
    
    questions = Questions.objects.filter(parent_scenario=scenario).order_by('scenario_question_number')
    
    print(f"{'ID':<5} {'Seq':<5} {'Type':<25} {'Text':<50}")
    print("-" * 90)
    
    for q in questions:
        q_type = q.question_type.code if q.question_type else q.type
        print(f"{q.id:<5} {q.scenario_question_number:<5} {q_type:<25} {q.text[:48]}...")

except Scenarios.DoesNotExist:
    print("Scenario 'Case Study 101' not found.")
except Exception as e:
    print(f"Error: {e}")
