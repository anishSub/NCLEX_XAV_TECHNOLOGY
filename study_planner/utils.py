"""
Utility functions for Study Planner
"""
from exam_sessions.models import ExamSessions
from categories.models import Categories
from datetime import date, timedelta


def analyze_user_performance(user):
    """
    Analyze user's exam performance by category and identify weak areas.
    
    Args:
        user: User object
        
    Returns:
        List of dictionaries with category performance data
    """
    # Get all completed exam sessions for user
    completed_sessions = ExamSessions.objects.filter(
        user=user,
        status__in=['PASS', 'FAIL', 'COMPLETED']
    )
    
    if not completed_sessions.exists():
        return []
    
    # Aggregate all question history
    category_stats = {}
    
    for session in completed_sessions:
        for question in session.question_history:
            category = question.get('category', 'General')
            is_correct = question.get('is_correct', False)
            
            if category not in category_stats:
                category_stats[category] = {
                    'total': 0,
                    'correct': 0
                }
            
            category_stats[category]['total'] += 1
            if is_correct:
                category_stats[category]['correct'] += 1
    
    # Calculate percentages and create recommendations
    recommendations = []
    
    for category_name, stats in category_stats.items():
        if stats['total'] < 5:  # Need at least 5 questions to make recommendation
            continue
            
        percentage = round((stats['correct'] / stats['total']) * 100)
        
        # Determine status and priority
        if percentage < 70:
            status = 'weak'
            priority = 'HIGH'
            icon = '🔴'
        elif percentage < 80:
            status = 'needs_work'
            priority = 'MEDIUM'
            icon = '🟡'
        else:
            status = 'strong'
            priority = 'LOW'
            icon = '🟢'
        
        # Suggest practice question count based on performance
        if percentage < 50:
            recommended_practice = 30
        elif percentage < 70:
            recommended_practice = 20
        else:
            recommended_practice = 10
        
        # Get category object
        try:
            category_obj = Categories.objects.get(name=category_name)
            category_id = category_obj.id
        except Categories.DoesNotExist:
            category_id = None
        
        recommendations.append({
            'category_id': category_id,
            'category_name': category_name,
            'total_questions': stats['total'],
            'correct_answers': stats['correct'],
            'percentage': percentage,
            'status': status,
            'priority': priority,
            'icon': icon,
            'recommended_practice': recommended_practice
        })
    
    # Sort by percentage (weakest first)
    recommendations.sort(key=lambda x: x['percentage'])
    
    return recommendations


def get_weak_areas_only(user):
    """Get only weak areas (< 70%) for focused practice."""
    all_recommendations = analyze_user_performance(user)
    return [rec for rec in all_recommendations if rec['percentage'] < 70]


def calculate_estimated_time(num_questions):
    """Calculate estimated time in minutes for practice questions."""
    # Average 1.5 minutes per question
    return num_questions * 1.5
