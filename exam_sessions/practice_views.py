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
        
        # Count available questions in selected categories
        available_count = Questions.objects.filter(
            category_ids__id__in=category_ids
        ).distinct().count()
        
        # Use available count or user-specified, whichever is smaller
        num_questions = int(request.POST.get('num_questions', available_count))
        num_questions = min(num_questions, available_count) if available_count > 0 else 0
        
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
                'type': question.question_type.code if question.question_type else 'MCQ',
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
                'type': next_question.question_type.code if next_question.question_type else 'MCQ',
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


import re

def format_answer_display(answer, q_type, question_obj=None):
    """
    Helper to format complex JSON answers into a human-readable list of strings.
    """
    if not answer:
        return ["No Answer"]

    # 1. Drag & Drop (Dict: {'well1': 'Text'})
    if isinstance(answer, dict):
        return [str(v) for k, v in answer.items() if v]

    # 2. Matrix (List of Dicts: [{'finding': 'F', 'diagnosis': 'D'}])
    if isinstance(answer, list) and len(answer) > 0 and isinstance(answer[0], dict):
        lines = []
        for item in answer:
            # Try to find consistent keys for matrix
            # Usually {'row_label': 'X', 'col_label': 'Y'} or {'finding': 'X', 'diagnosis': 'Y'}
            # We'll just join the values to be generic but usually finding/diagnosis
            vals = [str(v) for k, v in item.items() if k != 'id'] 
            lines.append(" → ".join(vals))
        return lines

    # 3. Highlight Text (List of IDs: ['h1', 'h3'])
    # We need to map IDs back to text from question_obj.options['formatted_text']
    if q_type == 'HIGHLIGHT_TEXT' and isinstance(answer, list) and question_obj:
        try:
            formatted_text = question_obj.options.get('formatted_text', '')
            # Regex to find id='ID'...>Content</span>
            # Matches <span ... id='h1' ... >Content</span>
            # This is a simple regex assumption, might need robustness
            readable_answers = []
            for ans_id in answer:
                # Find the content inside the span with this ID
                pattern = re.compile(f"id=['\"]{ans_id}['\"].*?>(.*?)</span>", re.IGNORECASE | re.DOTALL)
                match = pattern.search(formatted_text)
                if match:
                    # Strip any nested tags if simple text is wanted
                    text = re.sub('<[^<]+?>', '', match.group(1)).strip()
                    readable_answers.append(text)
                else:
                    readable_answers.append(str(ans_id)) # Fallback
            return readable_answers
        except:
            return [str(a) for a in answer]

    # 4. Standard List (MCQ/SATA: ['Option A', 'Option B'])
    if isinstance(answer, list):
        return [str(a) for a in answer]

    return [str(answer)]

@login_required
def practice_results_view(request, session_id):
    """Display results for practice mode."""
    session = get_object_or_404(ExamSessions, id=session_id, user=request.user, session_type='PRACTICE')
    
    # Calculate stats
    total_questions = len(session.question_history)
    correct_count = sum(1 for h in session.question_history if h['is_correct'])
    incorrect_count = total_questions - correct_count
    score_percentage = round((correct_count / total_questions) * 100) if total_questions > 0 else 0
    
    # Statistics containers
    category_stats = {}
    type_stats = {}
    detailed_review = []
    
    # Pre-fetch all questions to get details like text/rationale
    # We need to preserve order, so we'll map them
    q_ids = [entry['question_id'] for entry in session.question_history]
    questions_map = {q.id: q for q in Questions.objects.filter(id__in=q_ids)}

    for entry in session.question_history:
        # --- Category Stats ---
        cat = entry.get('category', 'General')
        if cat not in category_stats:
            category_stats[cat] = {'correct': 0, 'total': 0}
        category_stats[cat]['total'] += 1
        if entry['is_correct']:
            category_stats[cat]['correct'] += 1
            
        # --- Question Type Stats ---
        # Get question type from the pre-fetched object
        question_obj = questions_map.get(entry['question_id'])
        q_type = question_obj.question_type.display_name if question_obj and question_obj.question_type else 'Unknown'
        q_code = question_obj.question_type.code if question_obj and question_obj.question_type else 'MCQ'
        
        if q_type not in type_stats:
            type_stats[q_type] = {'correct': 0, 'total': 0}
        type_stats[q_type]['total'] += 1
        if entry['is_correct']:
            type_stats[q_type]['correct'] += 1
            
        # --- Detailed Review Data ---
        if question_obj:
            user_ans_raw = entry.get('user_answer')
            # Correct answer might need normalization if it's just IDs in DB but we want text
            # For simplicity, if correct_answer is missing in history, use question_obj.correct_option_ids
            # usage: format_answer_display uses question_obj to lookup text if needed
            
            # Note: entry['correct_answer'] is what was saved during submission. 
            # If it's just ids, we might want to resolve them. 
            # Ideally the submission logic saved the *ids*. 
            
            detailed_review.append({
                'id': question_obj.id,
                'num': len(detailed_review) + 1,
                'text': question_obj.text,
                'user_answer': format_answer_display(user_ans_raw, q_code, question_obj),
                'correct_answer': format_answer_display(entry.get('correct_answer'), q_code, question_obj),
                'rationale': question_obj.rationale,
                'is_correct': entry['is_correct'],
                'type': q_type
            })
    
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
        
    # Format type data
    type_list = []
    for qtype, stats in type_stats.items():
        percentage = round((stats['correct'] / stats['total']) * 100)
        type_list.append({
            'name': qtype,
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
        'category_breakdown': category_list,
        'type_breakdown': type_list,
        'detailed_review': detailed_review
    }
    
    return render(request, 'exam_sessions/practice_results.html', context)
