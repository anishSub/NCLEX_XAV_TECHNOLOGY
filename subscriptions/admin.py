from django.contrib import admin
from .models import Subscription, PaymentTransaction, FeatureAccess


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'tier', 'duration', 'start_date', 'end_date', 'is_active', 'days_remaining_display']
    list_filter = ['tier', 'duration', 'is_active']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def days_remaining_display(self, obj):
        if obj.tier == 'FREE':
            return 'N/A'
        return f"{obj.days_remaining()} days"
    days_remaining_display.short_description = 'Days Remaining'


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_id', 'amount', 'currency', 'gateway', 'status', 'created_at']
    list_filter = ['status', 'gateway', 'created_at']
    search_fields = ['user__email', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at', 'gateway_response']


@admin.register(FeatureAccess)
class FeatureAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'daily_questions_used', 'last_reset_date', 'cat_exams_taken']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']
