from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import ExamSessions
from questions.models import Questions
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import ExamSessions
from .adaptive_engine import NCLEXAdaptiveEngine
from .selectors import get_next_question
from .scoring import NCLEXScoringService
from django.shortcuts import render
from django.http import JsonResponse
from .models import ExamSessions
from django.contrib.auth.decorators import login_required


@login_required
def start_exam_view(request):
    """
    Shows the exam launch screen and starts a new exam session on submit.
    """
    if request.method == 'POST':
        session = ExamSessions.objects.create(
            user=request.user,
            status='Ongoing',
            current_theta=0.0,
            total_information=0.01,
            standard_error=1.0
        )

        return render(request, 'exam_sessions/take_exam.html', {
            'session': session
        })

    previous_exam = ExamSessions.objects.filter(
        user=request.user,
        session_type='ADAPTIVE'
    ).order_by('-created_at').first()

    return render(request, 'exam_sessions/exam_start.html', {
        'question_bank_size': Questions.objects.filter(parent_scenario__isnull=True).count(),
        'case_study_count': Questions.objects.filter(parent_scenario__isnull=False).values('parent_scenario').distinct().count(),
        'previous_exam': previous_exam,
    })


@api_view(['GET'])
@login_required
def get_first_question_api(request, session_id):
    """
    Returns the first question for a newly created exam session.
    """
    try:
        session = ExamSessions.objects.get(id=session_id, user=request.user)
        
        # Get first question based on starting theta (0.0)
        question = get_next_question(session)
        
        if not question:
            return Response({
                'error': 'No questions available',
                'message': 'Please contact administrator to add questions to the database.'
            }, status=404)
        
        # Prepare question data
        response_data = {
            'question': {
                'id': question.id,
                'text': question.text,
                'type': question.type,
                'options': question.options,
                'is_case_study': bool(question.parent_scenario),
                'exhibit_updates': question.exhibit_updates,
                'scenario_question_number': question.scenario_question_number,
                'clinical_judgment_function': question.clinical_judgment_function,
            }
        }
        
        # If case study, include scenario data  
        if question.parent_scenario:
            response_data['question']['scenario'] = {
                'id': question.parent_scenario.id,
                'title': question.parent_scenario.title,
                'exhibits': question.parent_scenario.exhibits
            }
        
        return Response(response_data)
        
    except ExamSessions.DoesNotExist:
        return Response({'error': 'Session not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)



def get_performance_data(request, session_id):
    session = ExamSessions.objects.get(id=session_id)
    # Extract theta and SE history from your JSON question_history field
    # Assuming history is list of: {"theta": 0.5, "se": 0.4, "is_correct": True}
    return JsonResponse({
        "theta_history": [h['theta'] for h in session.question_history],
        "lower_bound": [h['theta'] - (1.96 * h['se']) for h in session.question_history],
        "upper_bound": [h['theta'] + (1.96 * h['se']) for h in session.question_history],
        "labels": [i+1 for i in range(len(session.question_history))]
    })


class SubmitMockAnswerAPI(APIView):
    def post(self, request, session_id):
        session = ExamSessions.objects.get(id=session_id)
        
        # 1. Check Time Limit (5 hours = 18,000 seconds)
        elapsed_time = (timezone.now() - session.created_at).total_seconds()
        if elapsed_time > 18000:
            session.status = 'FAIL' # Ran out of time
            session.save()
            return Response({"status": "EXPIRED", "message": "Time limit reached."})

        # 2. Get User Response and Correct Data
        user_data = request.data.get('user_answer')
        question_id = request.data.get('question_id')
        question = Questions.objects.get(id=question_id)
        
        # 3. Score the response (+/- or All-or-Nothing)
        raw_score = NCLEXScoringService.calculate_raw_score(
            question.type, user_data, question.correct_option_ids
        )
        is_correct = 1 if raw_score > 0 else 0

        # 4. Update Adaptive Stats (Theta & Standard Error)
        NCLEXAdaptiveEngine.update_student_ability(
            session, is_correct, question.difficulty_logit
        )

        # 5. Log History for Chart.js Graph
        session.question_history.append({
                    "question_id": question.id,  # Track which question was answered
                    "theta": session.current_theta,
                    "se": session.standard_error,
                    "is_correct": bool(is_correct),
                    # Use 'General' as default since Questions model doesn't have category field yet
                    "category": "General"
                })
        
        # CRITICAL: Save the session to persist question_history changes!
        session.save()

        # 6. Check Stopping Rules (95% Confidence or 150 Questions)
        decision = NCLEXAdaptiveEngine.check_stopping_rule(session)
        
        if decision in ['PASS', 'FAIL']:
            session.status = decision
            session.save()
            return Response({"status": "FINISHED", "result": decision})

        # 7. Fetch Next Question for the 5-hour loop
        next_q = get_next_question(session)
        
        # Build response with new fields
        next_question_data = {
            "id": next_q.id,
            "text": next_q.text,
            "type": next_q.type,
            "options": next_q.options,
            "is_case_study": bool(next_q.parent_scenario),
            "exhibit_updates": next_q.exhibit_updates,
            "scenario_question_number": next_q.scenario_question_number,
            "clinical_judgment_function": next_q.clinical_judgment_function,
        }
        
        # If case study, include scenario data
        if next_q.parent_scenario:
            next_question_data['scenario'] = {
                'id': next_q.parent_scenario.id,
                'title': next_q.parent_scenario.title,
                'exhibits': next_q.parent_scenario.exhibits
            }
        
        return Response({
            "status": "CONTINUE",
            "next_question": next_question_data
        })


def exam_results_view(request, session_id):
    """Renders the HTML results page."""
    session = ExamSessions.objects.get(id=session_id, user=request.user)
    return render(request, 'exam_sessions/results.html', {'session': session})



from django.utils import timezone
from django.db.models import Count, Avg
import statistics

def performance_data_api(request, session_id):
    try:
        session = ExamSessions.objects.get(id=session_id, user=request.user)
        
        # ========== EXISTING: Duration ==========
        duration_str = "N/A"
        total_seconds = 0
        if session.completed_at:
            diff = session.completed_at - session.created_at
            total_seconds = int(diff.total_seconds())
            minutes = total_seconds // 60
            hours = minutes // 60
            remaining_mins = minutes % 60
            
            if hours > 0:
                duration_str = f"{hours}h {remaining_mins}m"
            else:
                duration_str = f"{remaining_mins} mins"
        
        # ========== EXISTING: Category Breakdown ==========        
        breakdown = {}
        for entry in session.question_history:
            cat = entry.get('category', 'General')
            is_correct = entry.get('is_correct', False)
            
            if cat not in breakdown:
                breakdown[cat] = {'correct': 0, 'total': 0}
            
            breakdown[cat]['total'] += 1
            if is_correct:
                breakdown[cat]['correct'] += 1

        category_list = []
        for cat, stats in breakdown.items():
            percentage = round((stats['correct'] / stats['total']) * 100)
            category_list.append({
                'name': cat,
                'correct': stats['correct'],
                'total': stats['total'],
                'percentage': percentage
            })
        
        # ========== NEW: Ability Trend Over Time ==========
        # Get last 10 sessions for this user
        recent_sessions = ExamSessions.objects.filter(
            user=request.user,
            status__in=['PASS', 'FAIL']
        ).order_by('-created_at')[:10][::-1]  # Reverse to chronological order
        
        ability_trend = {
            'sessions': [s.id for s in recent_sessions],
            'theta_values': [float(s.current_theta) for s in recent_sessions],
            'dates': [s.created_at.strftime("%b %d") for s in recent_sessions]
        }
        
        # ========== NEW: Category Insights ==========
        if category_list:
            sorted_cats = sorted(category_list, key=lambda x: x['percentage'], reverse=True)
            strongest_cat = sorted_cats[0]['name'] if sorted_cats else "N/A"
            weakest_cat = sorted_cats[-1]['name'] if sorted_cats else "N/A"
            
            # Categories needing improvement (<70%)
            improvement_needed = [c['name'] for c in category_list if c['percentage'] < 70]
        else:
            strongest_cat = "N/A"
            weakest_cat = "N/A"
            improvement_needed = []
        
        category_insights = {
            'strongest': strongest_cat,
            'weakest': weakest_cat,
            'improvement_needed': improvement_needed
        }
        
        # ========== NEW: Time Analytics ==========
        avg_time_per_question = 0
        if session.question_history and total_seconds > 0:
            avg_time_per_question = total_seconds // len(session.question_history)
        
        # Time by category (estimate based on proportion of questions)
        time_by_category = {}
        total_questions = len(session.question_history)
        if total_questions > 0:
            for cat, stats in breakdown.items():
                proportion = stats['total'] / total_questions
                time_by_category[cat] = int(total_seconds * proportion // stats['total']) if stats['total'] > 0 else 0
        
        time_analytics = {
            'avg_time_per_question': avg_time_per_question,
            'total_duration': total_seconds,
            'time_by_category': time_by_category
        }
        
        # ========== NEW: Platform Comparison ==========
        # Calculate platform average theta for completed exams
        platform_avg_theta = ExamSessions.objects.filter(
            status__in=['PASS', 'FAIL']
        ).aggregate(Avg('current_theta'))['current_theta__avg'] or 0.0
        
        user_theta = float(session.current_theta)
        
        # Calculate percentile (simplified)
        all_thetas = list(ExamSessions.objects.filter(
            status__in=['PASS', 'FAIL']
        ).values_list('current_theta', flat=True))
        
        if all_thetas:
            percentile = sum(1 for t in all_thetas if t <= user_theta) / len(all_thetas) * 100
        else:
            percentile = 50  # Default
        
        comparison = {
            'user_theta': round(user_theta, 2),
            'platform_average': round(platform_avg_theta, 2),
            'percentile': int(percentile)
        }
        
        # ========== NEW: Personalized Recommendations ==========
        recommendations = []
        
        # Based on performance
        if user_theta > platform_avg_theta:
            recommendations.append(f"🎉 Excellent! You're performing above the platform average!")
        elif user_theta < platform_avg_theta:
            recommendations.append(f"📚 Keep practicing! You're {abs(round(user_theta - platform_avg_theta, 2))} points below average.")
        
        # Based on weak categories
        if improvement_needed:
            recommendations.append(f"🎯 Focus on: {', '.join(improvement_needed[:2])}")
        
        # Based on strong categories
        if strongest_cat != "N/A":
            recommendations.append(f"🏆 Great job in {strongest_cat}!")
        
        # Based on time
        if avg_time_per_question > 120:  # More than 2 minutes per question
            recommendations.append("⏱️ Try to pace yourself - aim for 1-2 minutes per question.")
        elif avg_time_per_question < 60:
            recommendations.append("👍 Good time management! You're answering efficiently.")
        
        # ========== RESPONSE DATA ==========
        data = {
            # Existing fields
            "student_name": f"{request.user.first_name} {request.user.last_name}",
            "duration": duration_str,
            "exam_date": session.created_at.strftime("%B %d, %Y"),
            "labels": [f"Q{i+1}" for i in range(len(session.question_history))],
            "theta_values": [h['theta'] for h in session.question_history],
            "lower_bound": [h['theta'] - (1.96 * h['se']) for h in session.question_history],
            "upper_bound": [h['theta'] + (1.96 * h['se']) for h in session.question_history],
            "pass_threshold": 0.0,
            "category_breakdown": category_list,
            
            # NEW: Analytics object
            "analytics": {
                "ability_trend": ability_trend,
                "category_insights": category_insights,
                "time_analytics": time_analytics,
                "comparison": comparison,
                "recommendations": recommendations
            }
        }
        return JsonResponse(data)
    except ExamSessions.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
