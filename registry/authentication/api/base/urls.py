from django.urls import path
from . import views

app_name = 'auth'
urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('verify-email/', views.VerifyEmail.as_view(), name='verify-email'),

    path(
        'token/refresh/', views.TokenRefreshAPIView.as_view(),
        name='token_refresh'),
    path('token/validate/', views.TokenVerifyAPIView.as_view(),
         name='token_validate'),

    path('change-password/', views.ChangePasswordView.as_view(),
         name='change_password'),

    path(
        'forget-password/', views.ForgetPasswordView.as_view(),
        name='forget_password'
    ),
    path(
        'update-password/', views.UpdatePasswordView.as_view(),
        name='update_password'
    ),
    path(
        'forget-password/', views.ForgetPasswordView.as_view(),
        name='forget_password'
    ),

    path(
        'user/', views.UserRetrieveView.as_view(),
        name='user-detail'
    ),
]
