from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from httpx import request
from .models import *
from .serializers import *
import random
import http.client
from django.conf import settings
from django.contrib.auth import authenticate, login, authenticate
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.contrib.auth.forms import AuthenticationForm
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status, permissions, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import permission_classes, authentication_classes
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .validations import *

def send_otp(email, otp):
    # Sender email credentials
    sender_email = "aicamerdotcom@gmail.com"
    sender_password = "tjek zyiu unls jmhn"

    # Recipient email
    recipient_email = email

    # SMTP server configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # For Gmail

    # Create a secure SSL context
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Email content
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = "Your OTP"
        message.attach(MIMEText(f"Aicamer.com\nYour OTP is: {otp}", 'plain'))

        # Send email
        server.sendmail(sender_email, recipient_email, message.as_string())
        print("OTP email sent successfully")
    except Exception as e:
        print(f"Error sending OTP email: {e}")
    finally:
        server.quit()



class UserRegister(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        clean_data = custom_validation(request.data)
        serializer = UserRegisterSerializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)

            # Create a custom user instance
            custom_user = CustomUser(user=user, username=user.username, phone=user.username)
            custom_user.save()

            # Generate a random OTP
            # otp = str(randint(1000, 9999))
            otp = str('1234')

            # Create a Profile instance
            # profile = Profile(user=user, email=user.email, otp=otp)
            # profile.save()

            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)

def login_attempt(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        
        # user = Profile.objects.filter(mobile = mobile).first()
        
        # if user is None:
        user = User(usename=usename,email = email, password =  password)
        user.save()
        kalaa = User.objects.get(email = email)
        profile = Profile(user = kalaa , mobile=email , otp = otp) 
        profile.save()
        # send_otp(email, otp)
        # request.session['mobile'] = email
        return JsonResponse({'Message': 'Register successful'}, status=status.HTTP_200_OK)
        
        # otp = str(random.randint(1000 , 9999))
        # user.otp = otp
        # user.save()
        # send_otp(mobile , otp)
        # request.session['mobile'] = mobile
        # return redirect('login_otp')        
    return JsonResponse({'Message': 'Something went wrong please, try again '}, status=status.HTTP_200_OK)





def login_otp(request):
    mobile = request.session['mobile']
    context = {'mobile':mobile}
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Profile.objects.filter(mobile=mobile).first()
        
        if otp == profile.otp:
            user = User.objects.get(id = profile.user.id)
            login(request , user)
            return redirect('home')
        else:
            context = {'message' : 'Wrong OTP' , 'class' : 'danger','mobile':mobile }
            return render(request,'account/login_otp.html' , context)
    
    return render(request,'account/login_otp.html' , context)
    
def resend_otp(request, mobile):
    print("called data!")
    mobile = mobile
    otp = str(random.randint(1000 , 9999))
    user = Profile.objects.filter(mobile = mobile).first()
    user.otp = otp
    print(user.otp)
    user.save()
    send_otp(mobile , otp)
   
    
    return redirect('login_otp') 
    
    

def otp(request):
    mobile = request.session['mobile']
    context = {'mobile':mobile}
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Profile.objects.filter(mobile=mobile).first()
        
        if otp == profile.otp:
            return redirect('home')
        else:
            
            context = {'message' : 'Wrong OTP' , 'class' : 'danger','mobile':mobile }
            return render(request,'account/otp.html' , context)
            
        
    return render(request,'account/otp.html' , context)

class UserView(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	authentication_classes = (SessionAuthentication,)
	##
	def get(self, request):
		serializer = UserSerializer(request.user)
		return Response({'user': serializer.data}, status=status.HTTP_200_OK)
    
class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        print(request)
        data = request.data
        username = data.get('username')
        password = data.get('password')
        serializer = UserLoginSerializer(data=data)
        if not username or not password:
            return Response({'error': 'Invalid input data'}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.check_user(data)

        if user is not None:
            login(request, user)
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            error_message = 'User not found'
            return JsonResponse({'error': error_message}, status=404)


class UserLogout(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = ()
	def post(self, request):
		logout(request)
		return Response(status=status.HTTP_200_OK)