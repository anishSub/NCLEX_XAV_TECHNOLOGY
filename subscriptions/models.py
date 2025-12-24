from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Subscription(models.Model):
    """User subscription model."""
    
    TIER_CHOICES = [
        ('FREE', 'Free'),
        ('PREMIUM', 'Premium'),
    ]
    
    DURATION_CHOICES = [
        ('MONTHLY', '1 Month'),
        ('QUARTERLY', '3 Months'),
        ('YEARLY', '1 Year'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='FREE')
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, null=True, blank=True)
    
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)
    
    # Pricing info
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='NPR')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.tier} - {self.duration if self.duration else 'N/A'}"
    
    def is_premium(self):
        """Check if user has active premium subscription."""
        if self.tier != 'PREMIUM':
            return False
        if not self.end_date:
            return False
        return self.end_date > timezone.now() and self.is_active
    
    def days_remaining(self):
        """Calculate days remaining in subscription."""
        if not self.end_date:
            return 0
        delta = self.end_date - timezone.now()
        return max(0, delta.days)
    
    def activate_subscription(self, duration, amount):
        """Activate premium subscription."""
        self.tier = 'PREMIUM'
        self.duration = duration
        self.amount_paid = amount
        self.start_date = timezone.now()
        
        # Calculate end date based on duration
        if duration == 'MONTHLY':
            self.end_date = self.start_date + timedelta(days=30)
        elif duration == 'QUARTERLY':
            self.end_date = self.start_date + timedelta(days=90)
        elif duration == 'YEARLY':
            self.end_date = self.start_date + timedelta(days=365)
        
        self.is_active = True
        self.save()


class PaymentTransaction(models.Model):
    """Payment transaction records."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    GATEWAY_CHOICES = [
        ('ESEWA', 'eSewa'),
        ('KHALTI', 'Khalti'),
        ('STRIPE', 'Stripe'),
        ('MANUAL', 'Manual'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    
    transaction_id = models.CharField(max_length=255, unique=True)
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NPR')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Gateway specific data
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Subscription details
    duration = models.CharField(max_length=20, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency} - {self.status}"


class FeatureAccess(models.Model):
    """Track feature usage for access control."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='feature_access')
    
    # Free tier limits
    daily_questions_used = models.IntegerField(default=0)
    last_reset_date = models.DateField(auto_now_add=True)
    
    # CAT exam attempts (premium only)
    cat_exams_taken = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - Questions: {self.daily_questions_used}"
    
    def reset_daily_limits(self):
        """Reset daily question count."""
        today = timezone.now().date()
        if self.last_reset_date < today:
            self.daily_questions_used = 0
            self.last_reset_date = today
            self.save()
    
    def can_take_cat_exam(self):
        """Check if user can take adaptive CAT exam."""
        return self.user.subscription.is_premium()
