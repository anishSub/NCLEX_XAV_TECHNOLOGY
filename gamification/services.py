"""
Gamification service layer - handles all business logic.
Optimized for performance with minimal database queries.
"""

from django.db import transaction
from django.core.cache import cache
from .models import UserGameProfile, UserBadge, DailyActivity
from .badges import BADGE_DEFINITIONS, get_badge_info
from django.utils import timezone


class GamificationService:
    """
    Main service for gamification operations.
    All methods are optimized to minimize database hits.
    """
    
    @staticmethod
    def get_or_create_profile(user):
        """Get or create user game profile (cached)"""
        profile, created = UserGameProfile.objects.get_or_create(user=user)
        if created:
            # Award first login badge
            GamificationService.check_and_award_badge(user, 'BASE_CAMP')
        return profile
    
    @staticmethod
    @transaction.atomic
    def award_points(user, points, reason=""):
        """
        Award points to user and update stats.
        Uses transaction for data consistency.
        """
        profile = GamificationService.get_or_create_profile(user)
        profile.add_points(points, reason)
        
        # Update daily activity
        today = timezone.now().date()
        activity, _ = DailyActivity.objects.get_or_create(
            user=user,
            date=today,
            defaults={'points_earned': 0, 'questions_answered': 0}
        )
        activity.points_earned += points
        activity.save(update_fields=['points_earned'])
        
        # Invalidate cache
        cache.delete(f'profile_{user.id}')
        
        return profile
    
    @staticmethod
    @transaction.atomic
    def record_question_attempt(user, is_correct):
        """
        Record a question attempt and award points.
        Also checks for question-based badges.
        """
        profile = GamificationService.get_or_create_profile(user)
        
        # Update stats
        profile.total_questions_answered += 1
        if is_correct:
            profile.correct_answers += 1
            points = 10
        else:
            points = 2  # Consolation points for trying
        
        profile.add_points(points, "Question answered")
        
        # Update daily activity
        today = timezone.now().date()
        activity, _ = DailyActivity.objects.get_or_create(
            user=user,
            date=today,
            defaults={'points_earned': 0, 'questions_answered': 0}
        )
        activity.questions_answered += 1
        activity.save(update_fields=['questions_answered'])
        
        # Check for badges (optimized - batch check)
        newly_earned = GamificationService.check_question_badges(user, profile)
        
        return profile, newly_earned
    
    @staticmethod
    def check_and_award_badge(user, badge_code, force=False):
        """
        Check if user qualifies for a badge and award it.
        Returns badge instance if awarded, None otherwise.
        """
        # Check if already earned (unless forced)
        if not force and UserBadge.objects.filter(user=user, badge_code=badge_code).exists():
            return None
        
        badge_info = get_badge_info(badge_code)
        if not badge_info:
            return None
        
        # Check condition
        profile = GamificationService.get_or_create_profile(user)
        if badge_info['condition'](profile, user):
            # Award badge
            user_badge, created = UserBadge.objects.get_or_create(
                user=user,
                badge_code=badge_code,
                defaults={'points_awarded': badge_info['points']}
            )
            
            if created:
                # Award bonus points
                profile.add_points(badge_info['points'], f"Badge: {badge_code}")
                return user_badge
        
        return None
    
    @staticmethod
    def check_question_badges(user, profile):
        """
        Check all question-related badges efficiently.
        Returns list of newly earned badges.
        """
        question_badges = ['EXPLORER', 'CLIMBER', 'SHERPA', 'PEAK_MASTER', 'SAGARMATHA']
        
        # Get already earned badges in one query
        earned_codes = set(UserBadge.objects.filter(
            user=user,
            badge_code__in=question_badges
        ).values_list('badge_code', flat=True))
        
        newly_earned = []
        for badge_code in question_badges:
            if badge_code not in earned_codes:
                badge = GamificationService.check_and_award_badge(user, badge_code)
                if badge:
                    newly_earned.append(badge)
        
        return newly_earned
    
    @staticmethod
    def check_streak_badges(user, profile):
        """
        Check streak-related badges.
        Returns list of newly earned badges.
        """
        streak_badges = ['BASE_CAMP', 'TRAIL_BLAZER', 'SUMMIT_PUSH', 'ANNAPURNA', 'EVEREST']
        
        earned_codes = set(UserBadge.objects.filter(
            user=user,
            badge_code__in=streak_badges
        ).values_list('badge_code', flat=True))
        
        newly_earned = []
        for badge_code in streak_badges:
            if badge_code not in earned_codes:
                badge = GamificationService.check_and_award_badge(user, badge_code)
                if badge:
                    newly_earned.append(badge)
        
        return newly_earned
    
    @staticmethod
    def check_performance_badges(user, profile):
        """Check performance-based badges"""
        perf_badges = ['RISING_STAR', 'SUMMIT_VIEW', 'PEAK_POWER', 'EVEREST_LEVEL']
        
        earned_codes = set(UserBadge.objects.filter(
            user=user,
            badge_code__in=perf_badges
        ).values_list('badge_code', flat=True))
        
        newly_earned = []
        for badge_code in perf_badges:
            if badge_code not in earned_codes:
                badge = GamificationService.check_and_award_badge(user, badge_code)
                if badge:
                    newly_earned.append(badge)
        
        return newly_earned
    
    @staticmethod
    def update_user_streak(user):
        """
        Update user's daily streak.
        Should be called on login.
        Returns True if streak was updated.
        """
        profile = GamificationService.get_or_create_profile(user)
        updated = profile.update_streak()
        
        if updated:
            # Check streak badges
            GamificationService.check_streak_badges(user, profile)
        
        return updated
    
    @staticmethod
    def get_leaderboard(limit=100):
        """
        Get top users by points (cached for 1 hour).
        Optimized with select_related.
        """
        cache_key = f'leaderboard_{limit}'
        leaderboard = cache.get(cache_key)
        
        if not leaderboard:
            leaderboard = UserGameProfile.objects.select_related('user').order_by('-total_points')[:limit]
            cache.set(cache_key, leaderboard, 3600)  # Cache for 1 hour
        
        return leaderboard
    
    @staticmethod
    def get_user_rank(user):
        """Get user's rank in leaderboard (cached)"""
        cache_key = f'rank_{user.id}'
        rank = cache.get(cache_key)
        
        if not rank:
            profile = GamificationService.get_or_create_profile(user)
            rank = UserGameProfile.objects.filter(total_points__gt=profile.total_points).count() + 1
            cache.set(cache_key, rank, 1800)  # Cache for 30 min
        
        return rank
    
    @staticmethod
    def get_user_badges(user):
        """Get all badges earned by user (cached)"""
        cache_key = f'badges_{user.id}'
        badges = cache.get(cache_key)
        
        if badges is None:
            badges = list(UserBadge.objects.filter(user=user).order_by('-earned_date'))
            cache.set(cache_key, badges, 300)  # Cache for 5 min
        
        return badges
    
    @staticmethod
    def invalidate_user_cache(user):
        """Invalidate all cache for a user"""
        cache.delete(f'profile_{user.id}')
        cache.delete(f'badges_{user.id}')
        cache.delete(f'rank_{user.id}')
