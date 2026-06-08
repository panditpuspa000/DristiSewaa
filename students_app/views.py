# students_app/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse

import random
from decimal import Decimal, InvalidOperation
from .models import OTPModel, Document
from apps.accounts.models import StudentProfile

User = get_user_model()


# 1. HOME
def home(request):
    return render(request, 'students_app/home.html')


# 2. REGISTER
def register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not first_name or not last_name or not email or not password:
            messages.error(request, "All registration fields are required.")
            return render(request, 'students_app/register.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'students_app/register.html')

        # Check for account existence first and redirect them away cleanly
        if User.objects.filter(username=email).exists():
            messages.warning(request, "This email is already fully registered. Please log in directly.")
            return redirect('students:login')

        # Generate 6-digit verification code
        otp = str(random.randint(100000, 999999))

        request.session['first_name'] = first_name
        request.session['last_name'] = last_name
        request.session['email'] = email
        request.session['password'] = password

        # Clear any old/active verification tokens before issuing a new one
        OTPModel.objects.filter(email=email).delete()
        OTPModel.objects.create(email=email, otp=otp)

        try:
            send_mail(
                'OTP Verification Code',
                f'Your DristiSewa registration OTP verification code is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            messages.success(request, "An OTP has been sent to your email address.")
            return redirect('students:verify_otp')
        except Exception as e:
            messages.error(request, f"Failed to deliver email: {str(e)}")
            return render(request, 'students_app/register.html')

    return render(request, 'students_app/register.html')


# 3. VERIFY OTP
def verify_otp(request):
    email = request.session.get('email')
    
    if not email:
        messages.error(request, "Registration session not found. Please try submitting your credentials again.")
        return redirect('students:register')

    if request.method == "POST":
        entered_otp = request.POST.get('otp', '').strip()

        # Use .filter().first() instead of .get() to prevent sequence issues
        otp_obj = OTPModel.objects.filter(email=email, is_verified=False).order_by('-created_at').first()

        if not otp_obj:
            messages.error(request, "No active OTP verification sequence found for this email. Please register again.")
            return redirect('students:register')

        if otp_obj.is_expired():
            messages.error(request, "This OTP has expired. Please register again to receive a fresh token.")
            return redirect('students:register')

        if otp_obj.otp == entered_otp:
            otp_obj.is_verified = True
            otp_obj.save()

            # Double-check right before creation that another process didn't save it while user was typing
            if User.objects.filter(username=email).exists():
                messages.warning(request, "This account was completed during submission. You can now log in.")
                return redirect('students:login')

            # 1. Create the secure custom User record
            user = User.objects.create_user(
                username=email,
                email=email,
                password=request.session.get('password'),
                first_name=request.session.get('first_name'),
                last_name=request.session.get('last_name'),
                role='student'
            )

            # 2. Database Creation safe-assert
            StudentProfile.objects.get_or_create(user=user)

            # Instantly clear out temporary registration secrets from session memories
            keys_to_clear = ['first_name', 'last_name', 'password', 'email']
            for key in keys_to_clear:
                if key in request.session:
                    del request.session[key]

            # Flash confirmation and route them explicitly to the login view page
            messages.success(request, "Your account has been verified and registered successfully! Please log in to your account.")
            return redirect('students:login')

        else:
            messages.error(request, "Invalid OTP code entered. Please try again.")
            return render(request, 'students_app/otp_verification.html')

    return render(request, 'students_app/otp_verification.html')


# 4. LOGIN
def login_view(request):
    if request.user.is_authenticated and request.user.role == 'student':
        return redirect('students:dashboard')

    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user:
            if user.role == 'student':
                login(request, user)
                return redirect('students:dashboard')
            else:
                messages.error(request, "This login workspace is explicitly reserved for students.")
                return render(request, 'students_app/login.html')

        messages.error(request, "Invalid credentials entered.")
        return render(request, 'students_app/login.html')

    return render(request, 'students_app/login.html')


# 5. DASHBOARD
@login_required(login_url='students:login')
def dashboard(request):
    if request.user.role != 'student':
        logout(request)
        messages.error(request, "Unauthorized view access to student resources.")
        return redirect('students:login')
        
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        dob = request.POST.get('date_of_birth')
        college = request.POST.get('college_name', '').strip()
        year = request.POST.get('passed_year')
        gpa_val = request.POST.get('gpa')
        test_type = request.POST.get('test_type')
        score_val = request.POST.get('test_score')
        country = request.POST.get('preferred_country')

        # Map form metrics securely back into the profile instance
        profile.date_of_birth = dob if dob else None
        profile.college_name = college if college else None
        profile.passed_year = int(year) if year and year.isdigit() else None
        profile.test_type = test_type if test_type else None
        profile.preferred_country = country if country else None

        try:
            profile.gpa = Decimal(gpa_val) if gpa_val else None
        except (InvalidOperation, ValueError, TypeError):
            profile.gpa = None

        try:
            profile.test_score = Decimal(score_val) if score_val else None
        except (InvalidOperation, ValueError, TypeError):
            profile.test_score = None
        
        # Commit profiles straight to the relational database tables
        profile.save()
        messages.success(request, "Academic application metrics saved successfully!")
        
        # FIXED: Pattern name updated from 'upload_docs' to match 'upload-documents' from routing metrics
        return redirect('students:upload_docs')

    return render(request, 'students_app/dashboard.html', {'profile': profile})


# 6. UPLOAD DOCUMENTS
@login_required(login_url='students:login')
def upload_docs(request):
    if request.user.role != 'student':
        logout(request)
        messages.error(request, "Unauthorized workspace access.")
        return redirect('students:login')

    if request.method == "POST":
        name = request.POST.get('document_name', '').strip()
        file = request.FILES.get('document_file')

        if file:
            Document.objects.create(
                user=request.user,
                document_name=name if name else "Uploaded Document",
                document_file=file,
                status="Pending"
            )
            messages.success(request, "Document entry dispatched successfully!")
            
            # FIXED: Pattern name updated from 'app_status' to match 'application-status' from server traces
            return redirect('students:app_status')
        else:
            messages.error(request, "Please attach a valid file block to submit.")

    return render(request, 'students_app/upload_docs.html')


# 7. STATUS
@login_required(login_url='students:login')
def app_status(request):
    if request.user.role != 'student':
        logout(request)
        messages.error(request, "Access unauthorized.")
        return redirect('students:login')

    docs = Document.objects.filter(user=request.user)
    return render(request, 'students_app/status.html', {
        'documents': docs
    })


# 8. LOGOUT
def logout_view(request):
    logout(request)
    return redirect('students:home')


# 9. DIAGNOSTIC MAIL TESTER
def test_email(request):
    try:
        send_mail(
            'System Connectivity Diagnostics',
            'Automated SMTP email communication interface check successful.',
            settings.EMAIL_HOST_USER,
            ['receiver@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse("Diagnostic SMTP test mail delivered successfully.")
    except Exception as e:
        return HttpResponse(f"SMTP Server Connection Failure Diagnostic Error Stack: {str(e)}")