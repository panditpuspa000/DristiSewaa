from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse

import random
from .models import OTPModel, Document


# HOME
def home(request):
    return render(request, 'students_app/home.html')


# REGISTER (SEND OTP ONLY)
def register(request):

    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')

        # GENERATE OTP
        otp = str(random.randint(100000, 999999))

        # STORE SESSION TEMP DATA
        request.session['first_name'] = first_name
        request.session['last_name'] = last_name
        request.session['email'] = email
        request.session['password'] = password

        # REMOVE OLD OTP
        OTPModel.objects.filter(email=email).delete()

        # SAVE OTP
        OTPModel.objects.create(email=email, otp=otp)

        # SEND EMAIL
        send_mail(
            'OTP Verification',
            f'Your OTP is {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        messages.success(request, "OTP sent to your email")
        return redirect('verify_otp')

    return render(request, 'students_app/register.html')


# VERIFY OTP (CREATE USER HERE)
def verify_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get('otp')
        email = request.session.get('email')

        if not email:
            messages.error(request, "Session expired. Please register again.")
            return redirect('register')

        try:
            otp_obj = OTPModel.objects.get(email=email, is_verified=False)

            if otp_obj.is_expired():
                messages.error(request, "OTP expired")
                return redirect('register')

            if otp_obj.otp == entered_otp:

                otp_obj.is_verified = True
                otp_obj.save()

                # CREATE USER
                User.objects.create_user(
                    username=email,
                    email=email,
                    password=request.session.get('password'),
                    first_name=request.session.get('first_name'),
                    last_name=request.session.get('last_name')
                )

                # CLEAR SESSION
                request.session.flush()

                messages.success(request, "Account created successfully!")
                return redirect('login')

            else:
                messages.error(request, "Invalid OTP")
                return redirect('verify_otp')

        except OTPModel.DoesNotExist:
            messages.error(request, "OTP not found")
            return redirect('register')

    return render(request, 'students_app/otp_verification.html')


# LOGIN
def login_view(request):

    if request.method == "POST":

        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, "Invalid credentials")
        return redirect('login')

    return render(request, 'students_app/login.html')


# DASHBOARD
@login_required
def dashboard(request):
    return render(request, 'students_app/dashboard.html')


# UPLOAD DOCUMENTS
@login_required
def upload_docs(request):

    if request.method == "POST":

        name = request.POST.get('document_name')
        file = request.FILES.get('document_file')

        if file:
            Document.objects.create(
                user=request.user,
                document_name=name,
                document_file=file,
                status="Pending"
            )

            messages.success(request, "Document uploaded successfully!")

        return redirect('app_status')

    return render(request, 'students_app/upload_docs.html')


# STATUS (IMPORTANT FIX - USER-WISE DATA)
@login_required
def app_status(request):

    docs = Document.objects.filter(user=request.user)

    return render(request, 'students_app/status.html', {
        'documents': docs
    })


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('home')


# TEST EMAIL
def test_email(request):
    send_mail(
        'Test Email',
        'Hello from Django',
        settings.EMAIL_HOST_USER,
        ['receiver@gmail.com'],
        fail_silently=False,
    )
    return HttpResponse("Email sent!")