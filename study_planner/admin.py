from django.contrib import admin
from .models import StudyPlan, StudyTask, StudySession


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam_date', 'daily_study_hours', 'study_streak', 'created_at']
    list_filter = ['exam_date', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['study_streak', 'last_study_date', 'created_at', 'updated_at']


@admin.register(StudyTask)
class StudyTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'study_plan', 'task_type', 'scheduled_date', 'priority', 'status', 'completed_at']
    list_filter = ['task_type', 'priority', 'status', 'scheduled_date']
    search_fields = ['title', 'description', 'study_plan__user__email']
    readonly_fields = ['completed_at', 'created_at', 'updated_at']
    date_hierarchy = 'scheduled_date'


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['study_plan', 'session_date', 'total_minutes', 'tasks_completed']
    list_filter = ['session_date']
    search_fields = ['study_plan__user__email', 'notes']
    readonly_fields = ['created_at']
    date_hierarchy = 'session_date'
