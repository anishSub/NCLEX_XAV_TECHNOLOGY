from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .services import GamificationService
from .badges import BADGE_DEFINITIONS, get_badge_info


@login_required
def leaderboard_view(request):
    """Display the global leaderboard"""
    top_users = GamificationService.get_leaderboard(limit=100)
    user_rank = GamificationService.get_user_rank(request.user)
    user_profile = GamificationService.get_or_create_profile(request.user)
    
    context = {
        'top_users': top_users,
        'user_rank': user_rank,
        'user_profile': user_profile,
    }
    return render(request, 'gamification/leaderboard.html', context)


@login_required
def badges_view(request):
    """Display user's badges and available badges"""
    user_badges = GamificationService.get_user_badges(request.user)
    user_profile = GamificationService.get_or_create_profile(request.user)
    
    # Get earned badge codes
    earned_codes = {badge.badge_code for badge in user_badges}
    
    # Prepare badge info with earned status
    all_badges = []
    for code, info in BADGE_DEFINITIONS.items():
        all_badges.append({
            'code': code,
            'earned': code in earned_codes,
            'info': info,
            'earned_date': next((b.earned_date for b in user_badges if b.badge_code == code), None)
        })
    
    # Sort: earned first, then by points
    all_badges.sort(key=lambda x: (not x['earned'], -x['info']['points']))
    
    context = {
        'user_badges': user_badges,
        'all_badges': all_badges,
        'user_profile': user_profile,
        'total_badges': len(BADGE_DEFINITIONS),
        'earned_count': len(earned_codes),
    }
    return render(request, 'gamification/badges.html', context)


@login_required
def profile_stats_api(request):
    """API endpoint for gamification stats (for AJAX)"""
    profile = GamificationService.get_or_create_profile(request.user)
    badges = GamificationService.get_user_badges(request.user)
    rank = GamificationService.get_user_rank(request.user)
    
    return JsonResponse({
        'success': True,
        'profile': {
            'level': profile.level,
            'total_points': profile.total_points,
            'current_streak': profile.current_streak,
            'longest_streak': profile.longest_streak,
            'total_questions': profile.total_questions_answered,
            'average_score': profile.average_score,
            'points_to_next_level': profile.points_to_next_level,
        },
        'badges_count': len(badges),
        'rank': rank,
    })
