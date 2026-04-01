from django.urls import path
from . import views

urlpatterns = [
    path('pricing/', views.pricing_page, name='pricing'),
    path('checkout/', views.checkout, name='checkout'),
    path('dashboard/', views.subscription_dashboard, name='subscription_dashboard'),
    path('api/activate/', views.activate_subscription, name='activate_subscription'),
]
