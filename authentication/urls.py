
from django.urls import path
from .views import DoctorRegister, RegisterView, LoginAPIView, LogoutAPIView, Change_passwordAPIview, PaymentAPIView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # path('email-verify/', VerifyEmail.as_view(), name='email-verify'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('change-password/', Change_passwordAPIview.as_view(),
         name='change-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('doctor_register/', DoctorRegister.as_view(), name='doctor_register'),
    path('info_payment/', PaymentAPIView.as_view(), name='info_payment')
]
