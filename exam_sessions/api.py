from rest_framework.views import APIView
from rest_framework.response import Response
from questions.models import Questions


class GetNextQuestionAPI(APIView):
    def get(self, request, session_id):
        # ... logic to pick the next question based on Theta ...
        question = QuestionSelector.get_next_question(session) #

        data = {
            "id": question.id,
            "text": question.text,
            "type": question.type,
            "options": question.options,
            "is_case_study": False
        }

        # Check for Parent-Child Relationship
        if question.parent_scenario:
            data["is_case_study"] = True
            data["scenario"] = {
                "title": question.parent_scenario.title,
                "exhibits": question.parent_scenario.exhibits # The JSONField with tabs
            }
        
        return Response(data)