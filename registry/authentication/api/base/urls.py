from django.urls import path
# from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'auth'
urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/validate/', views.TokenVerifyAPIView.as_view(),
         name='token_validate'),

    # Path for changing user password
    path('user/setpassword/', views.SetPasswordView.as_view(),
         name='set_password'),
    path('user/changePassword/', views.ChangePasswordView.as_view(),
         name='change_password'),
    path('user/phone/update/<int:id>/',
         views.PhoneUpdateAPIView.as_view(), name='update_phone'),
    path('user/phone/list/', views.PhoneListAPIView.as_view(), name='list_phone'),
    path('user/phone/create/',
         views.PhoneCreateAPIView.as_view(), name='create_phone'),

    # Relationships
    path('user/relationship/create/',
         views.RelationshipCreateAPIView.as_view(), name='create_relationship'),

    # Get user verify token for email verification
    path('user/email-token/generate/',
         views.GenerateTokenView.as_view(), name='gen_token'),
    path('user/email-token/validate/',
         views.ValidateTokenView.as_view(), name='validate_token'),

    # Path for generating otp
    path('util/generate_otp/', views.GenerateOtpView.as_view(), name='gen_otp'),

    # Paths for getting and finding user informations
    path('user/', views.UserListView.as_view(), name='user_list'),
    path('user/detail/<int:id>/',
         views.UserAPIView.as_view(), name='user_data'),

]
