from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Subscription, PaymentTransaction, FeatureAccess
from django.contrib.auth import get_user_model

User = get_user_model()


def pricing_page(request):
    """Display pricing plans."""
    return render(request, 'subscriptions/pricing.html')


@login_required
def checkout(request):
    """Checkout page for chosen plan."""
    duration = request.GET.get('duration')
    amount = request.GET.get('amount')
    
    if not duration or not amount:
        return redirect('pricing')
    
    context = {
        'duration': duration,
        'amount': amount,
    }
    return render(request, 'subscriptions/checkout.html', context)


@login_required
def subscription_dashboard(request):
    """User subscription dashboard."""
    subscription, created = Subscription.objects.get_or_create(user=request.user)
   
    feature_access, _ = FeatureAccess.objects.get_or_create(user=request.user)
    
    context = {
        'subscription': subscription,
        'feature_access': feature_access,
        'is_premium': subscription.is_premium(),
        'days_remaining': subscription.days_remaining()
    }
    return render(request, 'subscriptions/dashboard.html', context)


@login_required
@require_POST
def activate_subscription(request):
    """Activate subscription after successful payment (for testing)."""
    import json
    data = json.loads(request.body)
    
    duration = data.get('duration')
    amount = data.get('amount')
    
    subscription, _ = Subscription.objects.get_or_create(user=request.user)
    subscription.activate_subscription(duration, float(amount))
    
    # Create payment record
    PaymentTransaction.objects.create(
        user=request.user,
        subscription=subscription,
        transaction_id=f"TEST-{request.user.id}-{timezone.now().timestamp()}",
        gateway='MANUAL',
        amount=amount,
        status='SUCCESS',
        duration=duration
    )
    
    return JsonResponse({'success': True, 'message': 'Subscription activated!'})


# Helper function for access control
def check_premium_access(user):
    """Check if user has premium access."""
    try:
        return user.subscription.is_premium()
    except Subscription.DoesNotExist:
        # Create free tier subscription
        Subscription.objects.create(user=user, tier='FREE')
        return False
