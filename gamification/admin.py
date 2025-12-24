from django.contrib import admin
from .models import UserGameProfile, UserBadge, DailyActivity


@admin.register(UserGameProfile)
class UserGameProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'total_points', 'current_streak', 'longest_streak', 'total_questions_answered', 'average_score']
    list_filter = ['level', 'current_streak']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-total_points']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Points & Level', {
            'fields': ('total_points', 'level')
        }),
        ('Streaks', {
            'fields': ('current_streak', 'longest_streak', 'last_active_date')
        }),
        ('Statistics', {
            'fields': ('total_questions_answered', 'correct_answers')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge_code', 'earned_date', 'points_awarded']
    list_filter = ['badge_code', 'earned_date']
    search_fields = ['user__username', 'badge_code']
    date_hierarchy = 'earned_date'
    ordering = ['-earned_date']


@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'questions_answered', 'points_earned', 'active']
    list_filter = ['date', 'active']
    search_fields = ['user__username']
    date_hierarchy = 'date'
    ordering = ['-date']
