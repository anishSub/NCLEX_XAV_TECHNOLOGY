import json
from questions.models import Questions
from scenarios.models import Scenarios

def run_import(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    for item in data:
        # 1. Create the Parent Scenario
        scenario = Scenarios.objects.create(
            title=item['scenario_title'],
            exhibits=item['exhibits']
        )
        print(f"Created Scenario: {scenario.title}")

        # 2. Create the Child Questions linked to this Scenario
        for q in item['questions']:
            Questions.objects.create(
                parent_scenario=scenario, # This is the Parent-Child link
                text=q['text'],
                type=q['type'],
                difficulty_logit=q['difficulty'],
                options=q['options'],
                correct_option_ids=q['correct']
            )
        print(f"--- Imported {len(item['questions'])} questions for this case.")

# To run: run_import('nclex_data.json')