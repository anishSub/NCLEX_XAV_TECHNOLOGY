from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Users, StudentProfile

# Define an inline admin descriptor for StudentProfile
# This lets you edit the Profile INSIDE the User page
class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'

@admin.register(Users)
class UsersAdmin(BaseUserAdmin):
    # Use 'email' for the admin list view
    list_display = ('email', 'username', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('email',)

    # Add the profile inline
    inlines = (StudentProfileInline,)

    # Update fieldsets to separate Auth info from Role info
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Make sure 'email' is required when adding a user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password', 'role'),
        }),
    )