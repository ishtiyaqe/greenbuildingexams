from django.conf import settings
from django.urls import include, path
from django.contrib import admin
# from home import models

from .models import *
from .views import *


urlpatterns = [
    path('signup/' , UserRegister.as_view() , name="signup"),
    path('login/' , UserLogin.as_view() , name="login"),
    path('otp' , otp , name="otp"),
    path('login-otp', login_otp , name="login_otp") ,
    path('resend-otp/<str:mobile>', resend_otp , name="resend_otp") ,
    path('accounts/', include('django.contrib.auth.urls')),
    path('user/', UserView.as_view(), name='user'),
    path('logout/', UserLogout.as_view(), name='user-logout'),
    
]
    
    
    
    
    
    
    
    
    
