from django.contrib import admin
from .models import UserResponses

@admin.register(UserResponses)
class UserResponsesAdmin(admin.ModelAdmin):
    # Columns: Show which student (via session), which question, correctness, and speed
    list_display = ('id', 'get_student', 'question_preview', 'is_correct', 'time_taken')
    
    # Click ID to edit
    list_display_links = ('id',)
    
    # Filter: Quickly see all wrong answers (False) to spot difficult questions
    list_filter = ('is_correct',)
    
    # Search: Find responses by Student Name or Question Text
    search_fields = ('session__user__username', 'question__text')
    
    # PERFORMANCE KEY: Instead of loading a dropdown of 1000s of questions, 
    # this creates a search box to find the session/question.
    # (Requires search_fields to be set on ExamSessions and Questions admin)
    autocomplete_fields = ['session', 'question']
    
    # Optimization: Loads related data in one query
    list_select_related = ('session', 'session__user', 'question')
    
    list_per_page = 25

    # Helper to show student name instead of just "Session Object 1"
    def get_student(self, obj):
        return obj.session.user.username
    get_student.short_description = "Student"

    # Helper to show a snippet of the question
    def question_preview(self, obj):
        return obj.question.text[:50] + "..."
    question_preview.short_description = "Question"