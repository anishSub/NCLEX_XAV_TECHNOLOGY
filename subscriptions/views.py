import base64
import hashlib
import hmac
import json
import uuid
from decimal import Decimal, InvalidOperation
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Subscription, PaymentTransaction, FeatureAccess
from django.contrib.auth import get_user_model

User = get_user_model()

PLAN_PRICING = {
    'MONTHLY': Decimal('999'),
    'QUARTERLY': Decimal('2499'),
    'YEARLY': Decimal('4999'),
    'LIFETIME': Decimal('4999'),
}


def _parse_amount(raw_amount):
    try:
        return Decimal(str(raw_amount))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _is_valid_plan(duration, amount):
    expected = PLAN_PRICING.get(duration)
    return expected is not None and amount == expected


def _generate_esewa_signature(secret_key, message):
    key = secret_key.encode('utf-8')
    msg = message.encode('utf-8')
    digest = hmac.new(key, msg, hashlib.sha256).digest()
    return base64.b64encode(digest).decode('utf-8')


def _decode_esewa_payload(encoded_payload):
    if not encoded_payload:
        return {}

    padding = "=" * (-len(encoded_payload) % 4)
    decoded = base64.b64decode(encoded_payload + padding).decode('utf-8')
    return json.loads(decoded)


def _post_json(url, payload, headers=None):
    req = urlrequest.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', **(headers or {})},
        method='POST',
    )
    with urlrequest.urlopen(req, timeout=20) as response:
        body = response.read().decode('utf-8')
        return response.getcode(), json.loads(body)


def _mark_transaction_failed(transaction, response_data=None):
    transaction.status = 'FAILED'
    if response_data is not None:
        transaction.gateway_response = response_data
    transaction.save(update_fields=['status', 'gateway_response', 'updated_at'])


def _mark_transaction_success(transaction, response_data=None):
    subscription, _ = Subscription.objects.get_or_create(user=transaction.user)
    subscription.activate_subscription(transaction.duration, transaction.amount)

    transaction.subscription = subscription
    transaction.status = 'SUCCESS'
    if response_data is not None:
        transaction.gateway_response = response_data
    transaction.save(update_fields=['subscription', 'status', 'gateway_response', 'updated_at'])
    return subscription


def pricing_page(request):
    """Display pricing plans."""
    return render(request, 'subscriptions/pricing.html')


@login_required
def checkout(request):
    """Checkout page for chosen plan."""
    duration = request.GET.get('duration')
    amount = _parse_amount(request.GET.get('amount'))
    
    if not duration or amount is None or not _is_valid_plan(duration, amount):
        messages.error(request, 'Please choose a valid subscription plan.')
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


@login_required
@require_POST
def start_payment(request):
    duration = request.POST.get('duration')
    amount = _parse_amount(request.POST.get('amount'))
    payment_method = request.POST.get('payment_method')

    if not duration or amount is None or not _is_valid_plan(duration, amount):
        messages.error(request, 'Invalid subscription plan selected.')
        return redirect('pricing')

    subscription, _ = Subscription.objects.get_or_create(user=request.user)
    transaction = PaymentTransaction.objects.create(
        user=request.user,
        subscription=subscription,
        transaction_id=f"SUB-{uuid.uuid4().hex[:18].upper()}",
        gateway=payment_method.upper() if payment_method else 'MANUAL',
        amount=amount,
        status='PENDING',
        duration=duration,
    )

    if payment_method == 'manual':
        _mark_transaction_success(transaction, {'mode': 'manual'})
        messages.success(request, 'Subscription activated successfully.')
        return redirect('subscription_dashboard')

    if payment_method == 'esewa':
        success_url = request.build_absolute_uri(reverse('esewa_success'))
        failure_url = request.build_absolute_uri(reverse('esewa_failure'))
        sign_message = (
            f"total_amount={amount},"
            f"transaction_uuid={transaction.transaction_id},"
            f"product_code={settings.ESEWA_PRODUCT_CODE}"
        )
        signature = _generate_esewa_signature(settings.ESEWA_SECRET_KEY, sign_message)

        context = {
            'esewa_url': settings.ESEWA_PAYMENT_URL,
            'amount': amount,
            'total_amount': amount,
            'transaction_uuid': transaction.transaction_id,
            'product_code': settings.ESEWA_PRODUCT_CODE,
            'signature': signature,
            'success_url': success_url,
            'failure_url': failure_url,
        }
        return render(request, 'subscriptions/esewa_redirect.html', context)

    if payment_method == 'khalti':
        callback_url = request.build_absolute_uri('/subscriptions/khalti/callback/')
        website_url = request.build_absolute_uri('/')
        payload = {
            "return_url": callback_url,
            "website_url": website_url,
            "amount": int(amount * 100),
            "purchase_order_id": transaction.transaction_id,
            "purchase_order_name": f"NCLEX XAV {duration} Plan",
            "customer_info": {
                "name": request.user.get_full_name() or request.user.email,
                "email": request.user.email,
                "phone": getattr(request.user, 'phone', '') or '9800000000',
            },
        }
        headers = {'Authorization': f'key {settings.KHALTI_SECRET_KEY}'}

        try:
            status_code, data = _post_json(
                f"{settings.KHALTI_BASE_URL}/epayment/initiate/",
                payload,
                headers=headers,
            )
        except (urlerror.URLError, TimeoutError, json.JSONDecodeError) as exc:
            _mark_transaction_failed(transaction, {'error': str(exc)})
            messages.error(request, 'Unable to connect to Khalti right now. Please try again.')
            return redirect(f"{reverse('checkout')}?duration={duration}&amount={amount}")

        transaction.gateway_response = data
        transaction.save(update_fields=['gateway_response', 'updated_at'])

        if status_code == 200 and data.get('payment_url'):
            return redirect(data['payment_url'])

        _mark_transaction_failed(transaction, data)
        messages.error(request, data.get('detail', 'Khalti initiation failed.'))
        return redirect(f"{reverse('checkout')}?duration={duration}&amount={amount}")

    transaction.delete()
    messages.error(request, 'Unsupported payment method selected.')
    return redirect('checkout')


@login_required
def esewa_success(request):
    encoded_data = request.GET.get('data')

    try:
        data = _decode_esewa_payload(encoded_data)
    except (json.JSONDecodeError, ValueError, TypeError):
        messages.error(request, 'Invalid eSewa response received.')
        return redirect('pricing')

    transaction_id = data.get('transaction_uuid')
    transaction = get_object_or_404(
        PaymentTransaction,
        transaction_id=transaction_id,
        user=request.user,
        gateway='ESEWA',
    )

    sign_message = (
        f"total_amount={data.get('total_amount')},"
        f"transaction_uuid={data.get('transaction_uuid')},"
        f"product_code={data.get('product_code')}"
    )
    expected_signature = _generate_esewa_signature(settings.ESEWA_SECRET_KEY, sign_message)

    if data.get('status') == 'COMPLETE' and data.get('signature') == expected_signature:
        _mark_transaction_success(transaction, data)
        messages.success(request, 'eSewa payment verified and subscription activated.')
        return redirect('subscription_dashboard')

    _mark_transaction_failed(transaction, data)
    messages.error(request, 'eSewa payment could not be verified.')
    return redirect('pricing')


@login_required
def esewa_failure(request):
    transaction_id = request.GET.get('transaction_uuid')
    if transaction_id:
        try:
            transaction = PaymentTransaction.objects.get(
                transaction_id=transaction_id,
                user=request.user,
                gateway='ESEWA',
            )
            _mark_transaction_failed(transaction, {'status': 'failure', 'query': request.GET.dict()})
        except PaymentTransaction.DoesNotExist:
            pass

    messages.error(request, 'eSewa payment was cancelled or failed.')
    return redirect('pricing')


@login_required
def khalti_callback(request):
    pidx = request.GET.get('pidx')
    purchase_order_id = request.GET.get('purchase_order_id')

    transaction = get_object_or_404(
        PaymentTransaction,
        transaction_id=purchase_order_id,
        user=request.user,
        gateway='KHALTI',
    )

    if not pidx:
        _mark_transaction_failed(transaction, {'error': 'Missing pidx', 'query': request.GET.dict()})
        messages.error(request, 'Khalti verification failed.')
        return redirect('pricing')

    headers = {'Authorization': f'key {settings.KHALTI_SECRET_KEY}'}
    try:
        _, lookup_data = _post_json(
            f"{settings.KHALTI_BASE_URL}/epayment/lookup/",
            {"pidx": pidx},
            headers=headers,
        )
    except (urlerror.URLError, TimeoutError, json.JSONDecodeError) as exc:
        _mark_transaction_failed(transaction, {'error': str(exc), 'pidx': pidx})
        messages.error(request, 'Unable to verify Khalti payment right now.')
        return redirect('pricing')

    combined_response = {'callback': request.GET.dict(), 'lookup': lookup_data}

    if lookup_data.get('status') == 'Completed':
        _mark_transaction_success(transaction, combined_response)
        messages.success(request, 'Khalti payment verified and subscription activated.')
        return redirect('subscription_dashboard')

    _mark_transaction_failed(transaction, combined_response)
    messages.error(request, 'Khalti payment was not completed.')
    return redirect('pricing')


# Helper function for access control
def check_premium_access(user):
    """Check if user has premium access."""
    try:
        return user.subscription.is_premium()
    except Subscription.DoesNotExist:
        # Create free tier subscription
        Subscription.objects.create(user=user, tier='FREE')
        return False
