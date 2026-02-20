from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('update-profile/', views.update_profile_view, name='update_profile'),
]