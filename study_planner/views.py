from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
from .models import StudyPlan, StudyTask, StudySession
from categories.models import Categories
import json


@login_required
def planner_dashboard(request):
    """Main study planner dashboard."""
    try:
        study_plan = StudyPlan.objects.get(user=request.user)
    except StudyPlan.DoesNotExist:
        # Redirect to setup if no plan exists
        return redirect('setup_study_plan')
    
    # Get today's tasks grouped by status
    today = timezone.now().date()
    todays_tasks_todo = study_plan.tasks.filter(scheduled_date=today, status='TODO')
    todays_tasks_in_progress = study_plan.tasks.filter(scheduled_date=today, status='IN_PROGRESS')
    todays_tasks_completed = study_plan.tasks.filter(scheduled_date=today, status='COMPLETED')
    
    upcoming_tasks = study_plan.tasks.filter(scheduled_date__gt=today).exclude(status='COMPLETED')[:5]
    
    # Calculate stats
    days_until_exam = (study_plan.exam_date - today).days
    total_tasks = study_plan.tasks.count()
    completed_tasks = study_plan.tasks.filter(status='COMPLETED').count()
    completion_rate = round((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    
    context = {
        'study_plan': study_plan,
        'todays_tasks_todo': todays_tasks_todo,
        'todays_tasks_in_progress': todays_tasks_in_progress,
        'todays_tasks_completed': todays_tasks_completed,
        'upcoming_tasks': upcoming_tasks,
        'days_until_exam': days_until_exam,
        'completion_rate': completion_rate,
        'today': today,  # For the add task modal date input
    }
    return render(request, 'study_planner/dashboard.html', context)


@login_required
def setup_study_plan(request):
    """Setup or edit study plan."""
    try:
        study_plan = StudyPlan.objects.get(user=request.user)
    except StudyPlan.DoesNotExist:
        study_plan = None
    
    if request.method == 'POST':
        exam_date = request.POST.get('exam_date')
        daily_hours = request.POST.get('daily_study_hours', 2)
        
        if study_plan:
            study_plan.exam_date = exam_date
            study_plan.daily_study_hours = daily_hours
            study_plan.save()
        else:
            study_plan = StudyPlan.objects.create(
                user=request.user,
                exam_date=exam_date,
                daily_study_hours=daily_hours
            )
        
        return redirect('study_planner')
    
    return render(request, 'study_planner/setup.html', {'study_plan': study_plan})


@login_required
@require_POST
def create_task(request):
    """Create a new study task."""
    try:
        data = json.loads(request.body)
        
        # Check if user has a study plan
        try:
            study_plan = request.user.study_plan
        except StudyPlan.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Please set up your study plan first!'
            }, status=400)
        
        task = StudyTask.objects.create(
            study_plan=study_plan,
            title=data.get('title'),
            description=data.get('description', ''),
            task_type=data.get('task_type', 'CUSTOM'),
            category_id=data.get('category_id'),
            scheduled_date=data.get('scheduled_date'),
            estimated_minutes=data.get('estimated_minutes', 30),
            priority=data.get('priority', 'MEDIUM')
        )
        
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'scheduled_date': str(task.scheduled_date),
                'status': task.status  # Changed from 'completed'
            }
        })
    except Exception as e:
        import traceback
        print(f"Error creating task: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def complete_task(request, task_id):
    """Mark a task as complete."""
    task = get_object_or_404(StudyTask, id=task_id, study_plan__user=request.user)
    
    data = json.loads(request.body)
    actual_minutes = data.get('actual_minutes')
    
    task.mark_complete(actual_minutes=actual_minutes)
    
    return JsonResponse({
        'success': True,
        'study_streak': task.study_plan.study_streak
    })


@login_required
@require_http_methods(["DELETE"])
def delete_task(request, task_id):
    """Delete a task."""
    task = get_object_or_404(StudyTask, id=task_id, study_plan__user=request.user)
    task.delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def update_task_status(request, task_id):
    """Update task status (TODO / IN_PROGRESS / COMPLETED)."""
    task = get_object_or_404(StudyTask, id=task_id, study_plan__user=request.user)
    
    data = json.loads(request.body)
    new_status = data.get('status')
    
    if new_status in ['TODO', 'IN_PROGRESS', 'COMPLETED']:
        if new_status == 'COMPLETED':
            task.mark_complete(actual_minutes=data.get('actual_minutes'))
        elif new_status == 'IN_PROGRESS':
            task.mark_in_progress()
        else:  # TODO
            task.mark_todo()
        
        return JsonResponse({
            'success': True,
            'study_streak': task.study_plan.study_streak
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)



@login_required
def get_calendar_tasks(request, view_type):
    """Get tasks for calendar view (day/week/month)."""
    study_plan = request.user.study_plan
    today = timezone.now().date()
    
    if view_type == 'day':
        date_param = request.GET.get('date', today)
        tasks = study_plan.tasks.filter(scheduled_date=date_param)
    elif view_type == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        tasks = study_plan.tasks.filter(scheduled_date__range=[start_date, end_date])
    elif view_type == 'month':
        start_date = today.replace(day=1)
        next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_date = next_month - timedelta(days=1)
        tasks = study_plan.tasks.filter(scheduled_date__range=[start_date, end_date])
    else:
        tasks = study_plan.tasks.all()
    
    tasks_data = []
    for task in tasks:
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'date': str(task.scheduled_date),
            'completed': task.completed,
            'priority': task.priority,
            'task_type': task.task_type,
            'estimated_minutes': task.estimated_minutes
        })
    
    return JsonResponse({'tasks': tasks_data})


@login_required
def get_study_stats(request):
    """Get study statistics."""
    study_plan = request.user.study_plan
    today = timezone.now().date()
    
    # This week stats
    week_start = today - timedelta(days=today.weekday())
    week_tasks = study_plan.tasks.filter(scheduled_date__gte=week_start, scheduled_date__lte=today)
    week_completed = week_tasks.filter(completed=True)
    
    stats = {
        'study_streak': study_plan.study_streak,
        'total_tasks': study_plan.tasks.count(),
        'completed_tasks': study_plan.tasks.filter(status='COMPLETED').count(),
        'in_progress_tasks': study_plan.tasks.filter(status='IN_PROGRESS').count(),
        'todo_tasks': study_plan.tasks.filter(status='TODO').count(),
        'week_completed': week_completed.count(),
        'week_total': week_tasks.count(),
        'days_until_exam': (study_plan.exam_date - today).days
    }
    
    return JsonResponse(stats)


# ==================== SMART RECOMMENDATIONS ====================

@login_required
def get_recommendations(request):
    """Get personalized study recommendations based on exam performance."""
    from .utils import analyze_user_performance
    
    try:
        recommendations = analyze_user_performance(request.user)
        return JsonResponse({'recommendations': recommendations})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def create_recommendation_task(request):
    """Auto-create practice task from recommendation."""
    from .utils import calculate_estimated_time
    
    try:
        data = json.loads(request.body)
        category_id = data.get('category_id')
        category_name = data.get('category_name')
        num_questions = data.get('num_questions', 20)
        
        # Check if user has study plan
        try:
            study_plan = request.user.study_plan
        except StudyPlan.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Please set up your study plan first!'
            }, status=400)
        
        # Check for duplicate task
        tomorrow = timezone.now().date() + timedelta(days=1)
        existing_task = StudyTask.objects.filter(
            study_plan=study_plan,
            category_id=category_id,
            task_type='PRACTICE',
            scheduled_date=tomorrow,
            status='TODO'
        ).exists()
        
        if existing_task:
            return JsonResponse({
                'success': False,
                'error': 'Practice task already exists for this category!'
            })
        
        # Create practice task
        estimated_minutes = int(calculate_estimated_time(num_questions))
        
        task = StudyTask.objects.create(
            study_plan=study_plan,
            title=f"Practice {category_name} (Recommended)",
            description=f"Focus on {category_name} - identified as a weak area",
            task_type='PRACTICE',
            category_id=category_id,
            scheduled_date=tomorrow,
            estimated_minutes=estimated_minutes,
            priority='HIGH'
        )
        
        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'message': f'Practice task created for tomorrow!'
        })
        
    except Exception as e:
        import traceback
        print(f"Error creating recommendation task: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

