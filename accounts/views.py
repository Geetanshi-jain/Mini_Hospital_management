from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import User, Doctor, Patient
from django.db import transaction

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        full_name = request.POST.get('full_name')
        
        # Additional fields
        specialization = request.POST.get('specialization')
        phone = request.POST.get('phone')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('signup')
            
        try:            # partial user creation in not allowed 
            with transaction.atomic():
                user = User.objects.create_user(email=email, password=password, role=role)
                
                if role == 'doctor':
                    Doctor.objects.create(user=user, full_name=full_name, specialization=specialization)
                else: # patient
                    Patient.objects.create(user=user, full_name=full_name, phone=phone)
                
                login(request, user)
                if role == 'doctor':
                    return redirect('doctor_dashboard')
                return redirect('patient_dashboard')
                
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('signup')
            
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)  # inbuilt auth medthod also match hash password
        if user is not None:
            login(request, user)
            if user.role == 'doctor':
                return redirect('doctor_dashboard')
            return redirect('patient_dashboard')
        else:
            messages.error(request, 'Invalid email or password')
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
