from django.urls import path
from . import views

urlpatterns = [
    path('pricing/', views.pricing_page, name='pricing'),
    path('checkout/', views.checkout, name='checkout'),
    path('dashboard/', views.subscription_dashboard, name='subscription_dashboard'),
    path('api/activate/', views.activate_subscription, name='activate_subscription'),
    path('pay/', views.start_payment, name='start_subscription_payment'),
    path('esewa/success/', views.esewa_success, name='esewa_success'),
    path('esewa/failure/', views.esewa_failure, name='esewa_failure'),
    path('khalti/callback/', views.khalti_callback, name='khalti_callback'),
]
