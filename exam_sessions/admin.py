from django.contrib import admin
from .models import ExamSessions

@admin.register(ExamSessions)
class ExamSessionsAdmin(admin.ModelAdmin):
    # Columns to show: ID, User, Status, Current Skill Level (Theta), and Count
    list_display = ('id', 'user', 'status', 'current_theta', 'questions_answered_count')
    
    # Click ID or User to edit
    list_display_links = ('id', 'user')
    
    # Sidebar filter: See only 'completed' or 'in_progress' exams
    list_filter = ('status',)
    
    # Search by Student Username or Session ID
    search_fields = ('user__username', 'id')
    
    # Optimization: Loads the User data in one go (makes the admin faster)
    list_select_related = ('user',)
    
    # Pagination
    list_per_page = 25

    # --- CUSTOM LOGIC ---
    # This calculates the length of the JSON list to show progress
    def questions_answered_count(self, obj):
        return len(obj.question_history)
    
    questions_answered_count.short_description = "Questions Answered"