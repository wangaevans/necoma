from django.urls import path
from django.contrib.auth import views as auth_views
from .views import logout_admin, network_admin_login, network_admin_signup

urlpatterns = [
    path('signup/', network_admin_signup, name='signup'),
    path('login/', network_admin_login, name='login'),
    path('logout/', logout_admin, name='logout'),

    # Password reset views
    path('reset-password/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset-password-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]
