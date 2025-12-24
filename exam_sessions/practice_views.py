from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import ExamSessions
from questions.models import Questions
from categories.models import Categories
from django.utils import timezone
import random
import json


# ==================== PRACTICE MODE VIEWS ====================

@login_required
def practice_categories_view(request):
    """Display category selection page for practice mode."""
    categories = Categories.objects.filter(type='NCLEX_CATEGORY').order_by('name')
    return render(request, 'exam_sessions/practice_categories.html', {
        'categories': categories
    })


@login_required
@require_POST
def start_practice_session(request):
    """Create a practice session with selected categories."""
    try:
        # Get selected category IDs from POST data
        category_ids = request.POST.getlist('categories')  # List of category IDs
        num_questions = int(request.POST.get('num_questions', 20))
        
        if not category_ids:
            return JsonResponse({'error': 'Please select at least one category'}, status=400)
        
        # Create practice session
        session = ExamSessions.objects.create(
            user=request.user,
            session_type='PRACTICE',
            status='Ongoing',
            selected_categories=[int(cid) for cid in category_ids],
            total_questions=num_questions,
            current_theta=0.0,  # Not used in practice but kept for consistency
            total_information=0.01,
            standard_error=1.0
        )
        
        return redirect('take_practice_exam', session_id=session.id)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def take_practice_exam(request, session_id):
    """Render the practice exam interface."""
    session = get_object_or_404(ExamSessions, id=session_id, user=request.user, session_type='PRACTICE')
    
    # Get category names for display
    category_names = Categories.objects.filter(
        id__in=session.selected_categories
    ).values_list('name', flat=True)
    
    return render(request, 'exam_sessions/take_practice.html', {
        'session': session,
        'category_names': ', '.join(category_names)
    })


@login_required
def get_practice_first_question(request, session_id):
    """Get the first question for practice mode."""
    try:
        session = ExamSessions.objects.get(id=session_id, user=request.user, session_type='PRACTICE')
        
        # Get random question from selected categories
        questions = Questions.objects.filter(
            category_ids__id__in=session.selected_categories
        ).distinct()
        
        if not questions.exists():
            return JsonResponse({
                'error': 'No questions available',
                'message': 'No questions found for selected categories. Please contact administrator.'
            }, status=404)
        
        # Select a random question
        question = random.choice(questions)
        
        # Prepare response
        response_data = {
            'question': {
                'id': question.id,
                'text': question.text,
                'type': question.type,
                'options': question.options,
                'is_case_study': bool(question.parent_scenario),
            }
        }
        
        # Include scenario if it's a case study
        if question.parent_scenario:
            response_data['question']['scenario'] = {
                'id': question.parent_scenario.id,
                'title': question.parent_scenario.title,
                'exhibits': question.parent_scenario.exhibits
            }
        
        return JsonResponse(response_data)
        
    except ExamSessions.DoesNotExist:
        return JsonResponse({'error': 'Practice session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def submit_practice_answer(request, session_id):
    """Submit answer for practice mode (no adaptive logic)."""
    try:
        session = ExamSessions.objects.get(id=session_id, user=request.user, session_type='PRACTICE')
        
        # Parse request data
        data = json.loads(request.body)
        user_answer = data.get('user_answer')
        question_id = data.get('question_id')
        
        question = Questions.objects.get(id=question_id)
        
        # Simple scoring (1 or 0)
        from .scoring import NCLEXScoringService
        raw_score = NCLEXScoringService.calculate_raw_score(
            question.type, user_answer, question.correct_option_ids
        )
        is_correct = 1 if raw_score > 0 else 0
        
        # Get question categories
        question_categories = question.category_ids.all().values_list('name', flat=True)
        category_name = question_categories[0] if question_categories else 'General'
        
        # Log to history (no theta/SE updates)
        session.question_history.append({
            'question_id': question.id,
            'is_correct': bool(is_correct),
            'category': category_name,
            'user_answer': user_answer,
            'correct_answer': question.correct_option_ids
        })
        session.save()
        
        # Check if practice is complete
        answered_count = len(session.question_history)
        if answered_count >= session.total_questions:
            session.status = 'COMPLETED'
            session.completed_at = timezone.now()
            session.save()
            return JsonResponse({'status': 'FINISHED'})
        
        # Get next random question (excluding already answered)
        answered_ids = [h['question_id'] for h in session.question_history]
        next_question = Questions.objects.filter(
            category_ids__id__in=session.selected_categories
        ).exclude(id__in=answered_ids).distinct().order_by('?').first()
        
        if not next_question:
            # No more questions available
            session.status = 'COMPLETED'
            session.completed_at = timezone.now()
            session.save()
            return JsonResponse({'status': 'FINISHED'})
        
        # Return next question
        response_data = {
            'status': 'CONTINUE',
            'next_question': {
                'id': next_question.id,
                'text': next_question.text,
                'type': next_question.type,
                'options': next_question.options,
                'is_case_study': bool(next_question.parent_scenario)
            }
        }
        
        if next_question.parent_scenario:
            response_data['next_question']['scenario'] = {
                'id': next_question.parent_scenario.id,
                'title': next_question.parent_scenario.title,
                'exhibits': next_question.parent_scenario.exhibits
            }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def practice_results_view(request, session_id):
    """Display results for practice mode."""
    session = get_object_or_404(ExamSessions, id=session_id, user=request.user, session_type='PRACTICE')
    
    # Calculate stats
    total_questions = len(session.question_history)
    correct_count = sum(1 for h in session.question_history if h['is_correct'])
    incorrect_count = total_questions - correct_count
    score_percentage = round((correct_count / total_questions) * 100) if total_questions > 0 else 0
    
    # Category breakdown
    category_stats = {}
    for entry in session.question_history:
        cat = entry.get('category', 'General')
        if cat not in category_stats:
            category_stats[cat] = {'correct': 0, 'total': 0}
        category_stats[cat]['total'] += 1
        if entry['is_correct']:
            category_stats[cat]['correct'] += 1
    
    # Format category data
    category_list = []
    for cat, stats in category_stats.items():
        percentage = round((stats['correct'] / stats['total']) * 100)
        category_list.append({
            'name': cat,
            'correct': stats['correct'],
            'total': stats['total'],
            'percentage': percentage
        })
    
    context = {
        'session': session,
        'total_questions': total_questions,
        'correct_count': correct_count,
        'incorrect_count': incorrect_count,
        'score_percentage': score_percentage,
        'category_breakdown': category_list
    }
    
    return render(request, 'exam_sessions/practice_results.html', context)
