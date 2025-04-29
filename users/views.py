import random
import string
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import CustomUser
from .forms import SignupStep1Form, SignupStep2Form, OTPVerificationForm, LoginForm

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    """Send OTP to user's email"""
    subject = 'Your OTP for Authentication'
    message = f'Your OTP is: {otp}. It is valid for 10 minutes.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def index(request):
    """Home page view"""
    return render(request, 'users/index.html')

def signup_step1(request):
    """First step of signup process - collect basic information"""
    if request.method == 'POST':
        form = SignupStep1Form(request.POST)
        if form.is_valid():
            # Save form data to session
            request.session['signup_step1_data'] = form.cleaned_data
            return redirect('signup_step2')
    else:
        form = SignupStep1Form()
    
    return render(request, 'users/signup_step1.html', {'form': form})

def signup_step2(request):
    """Second step of signup process - email verification"""
    # Check if step 1 was completed
    if 'signup_step1_data' not in request.session:
        return redirect('signup_step1')
    
    if request.method == 'POST':
        form = SignupStep2Form(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if email already exists
            if CustomUser.objects.filter(email=email).exists():
                form.add_error('email', 'This email is already registered.')
                return render(request, 'users/signup_step2.html', {'form': form})
            
            # Generate and send OTP
            otp = generate_otp()
            request.session['signup_email'] = email
            request.session['signup_otp'] = otp
            request.session['signup_otp_created_at'] = timezone.now().isoformat()
            
            # Send OTP to email
            send_otp_email(email, otp)
            
            return redirect('verify_signup_otp')
    else:
        form = SignupStep2Form()
    
    return render(request, 'users/signup_step2.html', {'form': form})

def verify_signup_otp(request):
    """Verify OTP for signup"""
    # Check if previous steps were completed
    if 'signup_step1_data' not in request.session or 'signup_email' not in request.session:
        return redirect('signup_step1')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            stored_otp = request.session.get('signup_otp')
            otp_created_at = datetime.fromisoformat(request.session.get('signup_otp_created_at'))
            
            # Check if OTP is expired (10 minutes)
            if timezone.now() > otp_created_at + timedelta(minutes=10):
                form.add_error('otp', 'OTP has expired. Please request a new one.')
                return render(request, 'users/verify_otp.html', {'form': form})
            
            # Verify OTP
            if entered_otp == stored_otp:
                # Create user
                step1_data = request.session['signup_step1_data']
                email = request.session['signup_email']
                
                # Generate a random username if not provided
                username = email.split('@')[0] + ''.join(random.choices(string.digits, k=4))
                
                # Create user with random password (since we're using OTP)
                random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=random_password,
                    first_name=step1_data['first_name'],
                    last_name=step1_data['last_name'],
                    age=step1_data['age'],
                    profession=step1_data['profession'],
                    profession_detail=step1_data['profession_detail'],
                    bio=step1_data['bio'],
                    hobbies=step1_data['hobbies'],
                    is_email_verified=True
                )
                
                # Clean up session
                for key in ['signup_step1_data', 'signup_email', 'signup_otp', 'signup_otp_created_at']:
                    if key in request.session:
                        del request.session[key]
                
                # Log in the user
                login(request, user)
                messages.success(request, 'Registration successful!')
                return redirect('welcome')
            else:
                form.add_error('otp', 'Invalid OTP. Please try again.')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'users/verify_otp.html', {'form': form, 'purpose': 'signup'})

def login_view(request):
    """Login view"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if user exists
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                form.add_error('email', 'No account found with this email.')
                return render(request, 'users/login.html', {'form': form})
            
            # Generate and send OTP
            otp = generate_otp()
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            
            # Send OTP to email
            send_otp_email(email, otp)
            
            # Store email in session for verification
            request.session['login_email'] = email
            
            return redirect('verify_login_otp')
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})

def verify_login_otp(request):
    """Verify OTP for login"""
    if 'login_email' not in request.session:
        return redirect('login')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            email = request.session['login_email']
            
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return redirect('login')
            
            # Check if OTP is expired (10 minutes)
            if not user.otp_created_at or timezone.now() > user.otp_created_at + timedelta(minutes=10):
                form.add_error('otp', 'OTP has expired. Please request a new one.')
                return render(request, 'users/verify_otp.html', {'form': form})
            
            # Verify OTP
            if entered_otp == user.otp:
                # Clear OTP
                user.otp = None
                user.otp_created_at = None
                user.save()
                
                # Clean up session
                if 'login_email' in request.session:
                    del request.session['login_email']
                
                # Log in the user
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('welcome')
            else:
                form.add_error('otp', 'Invalid OTP. Please try again.')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'users/verify_otp.html', {'form': form, 'purpose': 'login'})

def welcome(request):
    """Welcome page after login"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render(request, 'users/welcome.html')

def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('index')

def demo(request):
    return render(request, 'demo.html')