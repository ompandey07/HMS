from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Hotel
import json
import re
import base64
import random
import string
from datetime import datetime, timedelta

# Rate limiting storage (use Redis/Cache in production)
login_attempts = {}

# OTP storage (use Redis/Cache in production)
otp_storage = {}


def get_lockout_time(attempts):
    """Get lockout time in minutes based on failed attempts"""
    if attempts < 5:
        return 0
    elif attempts < 10:
        return 2
    elif attempts < 15:
        return 3
    elif attempts < 20:
        return 5
    else:
        return 10


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_otp(length=6):
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))


def send_welcome_email(user, hotel, password):
    """Send welcome email to newly registered hotel"""
    try:
        subject = '🎉 Welcome to Bookly - Your Hotel Management Journey Begins!'
        
        context = {
            'hotel_name': hotel.hotel_name,
            'email': user.email,
            'password': password,
            'mobile_number': hotel.mobile_number,
            'login_url': getattr(settings, 'SITE_URL', 'http://localhost:8000') + '/accounts/login/',
            'current_year': datetime.now().year,
        }
        
        html_content = render_to_string('accounts/welcome_email.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email]
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        return True
    except Exception as e:
        print(f"Welcome email error: {str(e)}")
        return False


def send_otp_email(email, otp, hotel_name=None):
    """Send OTP email for password reset"""
    try:
        subject = '🔐 Your Bookly Password Reset OTP'
        
        context = {
            'otp': otp,
            'hotel_name': hotel_name or 'User',
            'email': email,
            'expiry_minutes': 10,
            'current_year': datetime.now().year,
        }
        
        html_content = render_to_string('accounts/otp_email.html', context)
        text_content = strip_tags(html_content)
        
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[email]
        )
        
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send(fail_silently=False)
        
        return True
    except Exception as e:
        print(f"OTP email error: {str(e)}")
        return False


def send_password_changed_email(user, hotel_name):
    """Send password changed confirmation email"""
    try:
        subject = '✅ Your Bookly Password Has Been Changed'
        
        context = {
            'hotel_name': hotel_name,
            'email': user.email,
            'changed_at': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            'login_url': getattr(settings, 'SITE_URL', 'http://localhost:8000') + '/accounts/login/',
            'current_year': datetime.now().year,
        }
        
        html_content = render_to_string('accounts/password_changed_email.html', context)
        text_content = strip_tags(html_content)
        
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email]
        )
        
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send(fail_silently=False)
        
        return True
    except Exception as e:
        print(f"Password changed email error: {str(e)}")
        return False


# #############################################################
# LOGIN VIEW
# #############################################################
@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """Handle login page and authentication - Email only"""
    
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'accounts/login.html')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            client_ip = get_client_ip(request)
            current_time = datetime.now()
            
            # Check rate limiting
            if client_ip in login_attempts:
                attempt_data = login_attempts[client_ip]
                lockout_minutes = get_lockout_time(attempt_data['count'])
                
                if lockout_minutes > 0:
                    lockout_until = attempt_data['last_attempt'] + timedelta(minutes=lockout_minutes)
                    if current_time < lockout_until:
                        remaining = int((lockout_until - current_time).total_seconds())
                        mins = remaining // 60
                        secs = remaining % 60
                        return JsonResponse({
                            'success': False,
                            'message': f'Too many failed attempts. Please wait {mins}m {secs}s.',
                            'lockout': True,
                            'remaining_seconds': remaining
                        }, status=429)
            
            # Validate email
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email address is required.'
                }, status=400)
            
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter a valid email address.'
                }, status=400)
            
            if not password:
                return JsonResponse({
                    'success': False,
                    'message': 'Password is required.'
                }, status=400)
            
            # Find user by email
            try:
                user_obj = User.objects.get(email__iexact=email)
                username_to_auth = user_obj.username
            except User.DoesNotExist:
                if client_ip not in login_attempts:
                    login_attempts[client_ip] = {'count': 0, 'last_attempt': current_time}
                
                login_attempts[client_ip]['count'] += 1
                login_attempts[client_ip]['last_attempt'] = current_time
                
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid email or password.'
                }, status=401)
            
            # Authenticate user
            user = authenticate(request, username=username_to_auth, password=password)
            
            if user is not None:
                if not user.is_active:
                    return JsonResponse({
                        'success': False,
                        'message': 'Your account has been deactivated. Please contact support.'
                    }, status=403)
                
                if not hasattr(user, 'hotel'):
                    return JsonResponse({
                        'success': False,
                        'message': 'No hotel profile found. Please contact support.'
                    }, status=403)
                
                login(request, user)
                
                if client_ip in login_attempts:
                    del login_attempts[client_ip]
                
                return JsonResponse({
                    'success': True,
                    'message': 'Login successful! Redirecting...',
                    'redirect': '/dashboard/'
                })
            else:
                if client_ip not in login_attempts:
                    login_attempts[client_ip] = {'count': 0, 'last_attempt': current_time}
                
                login_attempts[client_ip]['count'] += 1
                login_attempts[client_ip]['last_attempt'] = current_time
                
                attempts_count = login_attempts[client_ip]['count']
                attempts_until_lockout = 5 - (attempts_count % 5)
                if attempts_until_lockout == 0:
                    attempts_until_lockout = 5
                
                next_lockout_time = get_lockout_time(attempts_count + attempts_until_lockout)
                
                message = 'Invalid email or password.'
                if attempts_until_lockout <= 3:
                    message += f' {attempts_until_lockout} attempt(s) remaining before {next_lockout_time}m lockout.'
                
                return JsonResponse({
                    'success': False,
                    'message': message
                }, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request format.'
            }, status=400)
        except Exception as e:
            print(f"Login error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again.'
            }, status=500)


# #############################################################
# REGISTER VIEW
# #############################################################
@csrf_protect
@require_http_methods(["GET", "POST"])
def register_view(request):
    """Handle registration page and user/hotel creation"""
    
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'accounts/register.html')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            hotel_logo_data = data.get('hotel_logo', '')
            hotel_name = data.get('hotel_name', '').strip()
            email = data.get('email', '').strip().lower()
            mobile_number = data.get('mobile_number', '').strip()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            
            # ===== HOTEL NAME VALIDATION =====
            if not hotel_name:
                return JsonResponse({
                    'success': False,
                    'message': 'Hotel name is required.'
                }, status=400)
            
            if len(hotel_name) < 2:
                return JsonResponse({
                    'success': False,
                    'message': 'Hotel name must be at least 2 characters.'
                }, status=400)
            
            if len(hotel_name) > 200:
                return JsonResponse({
                    'success': False,
                    'message': 'Hotel name is too long (max 200 characters).'
                }, status=400)
            
            if not re.match(r'^[a-zA-Z0-9\s&\'\-\.]+$', hotel_name):
                return JsonResponse({
                    'success': False,
                    'message': 'Hotel name contains invalid characters.'
                }, status=400)
            
            # ===== EMAIL VALIDATION =====
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email address is required.'
                }, status=400)
            
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter a valid email address.'
                }, status=400)
            
            if len(email) > 254:
                return JsonResponse({
                    'success': False,
                    'message': 'Email address is too long.'
                }, status=400)
            
            if User.objects.filter(email__iexact=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'An account with this email already exists.'
                }, status=400)
            
            # ===== MOBILE NUMBER VALIDATION =====
            if not mobile_number:
                return JsonResponse({
                    'success': False,
                    'message': 'Mobile number is required.'
                }, status=400)
            
            cleaned_mobile = re.sub(r'[\s\-\(\)\+]', '', mobile_number)
            
            if not cleaned_mobile.isdigit():
                return JsonResponse({
                    'success': False,
                    'message': 'Mobile number should contain only digits.'
                }, status=400)
            
            if len(cleaned_mobile) < 10:
                return JsonResponse({
                    'success': False,
                    'message': 'Mobile number must be at least 10 digits.'
                }, status=400)
            
            if len(cleaned_mobile) > 15:
                return JsonResponse({
                    'success': False,
                    'message': 'Mobile number is too long (max 15 digits).'
                }, status=400)
            
            if len(set(cleaned_mobile)) == 1:
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter a valid mobile number.'
                }, status=400)
            
            sequential_patterns = ['1234567890', '0987654321', '0123456789']
            for pattern in sequential_patterns:
                if cleaned_mobile in pattern or pattern in cleaned_mobile:
                    return JsonResponse({
                        'success': False,
                        'message': 'Please enter a valid mobile number.'
                    }, status=400)
            
            # ===== PASSWORD VALIDATION =====
            if not password:
                return JsonResponse({
                    'success': False,
                    'message': 'Password is required.'
                }, status=400)
            
            if len(password) < 8:
                return JsonResponse({
                    'success': False,
                    'message': 'Password must be at least 8 characters long.'
                }, status=400)
            
            if len(password) > 128:
                return JsonResponse({
                    'success': False,
                    'message': 'Password is too long (max 128 characters).'
                }, status=400)
            
            if not re.search(r'[A-Z]', password):
                return JsonResponse({
                    'success': False,
                    'message': 'Password must contain at least one uppercase letter (A-Z).'
                }, status=400)
            
            if not re.search(r'[a-z]', password):
                return JsonResponse({
                    'success': False,
                    'message': 'Password must contain at least one lowercase letter (a-z).'
                }, status=400)
            
            if not re.search(r'[0-9]', password):
                return JsonResponse({
                    'success': False,
                    'message': 'Password must contain at least one number (0-9).'
                }, status=400)
            
            if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', password):
                return JsonResponse({
                    'success': False,
                    'message': 'Password must contain at least one special character (!@#$%^&* etc.).'
                }, status=400)
            
            common_passwords = [
                'password', 'password1', 'password123', '12345678', 'qwerty123',
                'letmein', 'welcome', 'admin123', 'abc123', 'monkey123',
                'Password1', 'Password123', 'Qwerty123', 'Welcome1', 'Admin123',
                'Hotel123', 'Booking1', 'Manager1'
            ]
            
            if password.lower() in [p.lower() for p in common_passwords]:
                return JsonResponse({
                    'success': False,
                    'message': 'This password is too common. Please choose a stronger password.'
                }, status=400)
            
            if hotel_name.lower().replace(' ', '') in password.lower():
                return JsonResponse({
                    'success': False,
                    'message': 'Password should not contain hotel name.'
                }, status=400)
            
            # ===== CONFIRM PASSWORD =====
            if not confirm_password:
                return JsonResponse({
                    'success': False,
                    'message': 'Please confirm your password.'
                }, status=400)
            
            if password != confirm_password:
                return JsonResponse({
                    'success': False,
                    'message': 'Passwords do not match.'
                }, status=400)
            
            # ===== LOGO VALIDATION (Optional) =====
            logo_file = None
            if hotel_logo_data:
                try:
                    if 'base64,' in hotel_logo_data:
                        format_part, imgstr = hotel_logo_data.split('base64,')
                        
                        if 'png' in format_part:
                            ext = 'png'
                        elif 'jpeg' in format_part or 'jpg' in format_part:
                            ext = 'jpg'
                        elif 'gif' in format_part:
                            ext = 'gif'
                        elif 'webp' in format_part:
                            ext = 'webp'
                        else:
                            return JsonResponse({
                                'success': False,
                                'message': 'Invalid logo format. Please use PNG, JPG, GIF, or WEBP.'
                            }, status=400)
                        
                        decoded_file = base64.b64decode(imgstr)
                        if len(decoded_file) > 2 * 1024 * 1024:
                            return JsonResponse({
                                'success': False,
                                'message': 'Logo file is too large. Maximum size is 2MB.'
                            }, status=400)
                        
                        logo_file = ContentFile(decoded_file, name=f'logo.{ext}')
                        
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid logo file. Please try again.'
                    }, status=400)
            
            # ===== CREATE USER =====
            email_username = email.split('@')[0]
            base_username = email_username
            username = base_username
            counter = 1
            
            while User.objects.filter(username__iexact=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=hotel_name[:30],
                last_name=''
            )
            
            # ===== CREATE HOTEL =====
            hotel = Hotel.objects.create(
                user=user,
                hotel_name=hotel_name,
                mobile_number=mobile_number
            )
            
            if logo_file:
                hotel.hotel_logo.save(logo_file.name, logo_file, save=True)
            
            # ===== SEND WELCOME EMAIL =====
            email_sent = send_welcome_email(user, hotel, password)
            
            if email_sent:
                return JsonResponse({
                    'success': True,
                    'message': 'Registration successful! Check your email for login details.',
                    'redirect': '/accounts/login/'
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'Registration successful! Please login to continue.',
                    'redirect': '/accounts/login/'
                })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request format.'
            }, status=400)
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'An error occurred during registration. Please try again.'
            }, status=500)


# #############################################################
# FORGOT PASSWORD VIEW
# #############################################################
@csrf_protect
@require_http_methods(["GET", "POST"])
def forgot_password_view(request):
    """Handle forgot password page and OTP verification"""
    
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'accounts/forgot_password.html')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action', '')
            
            # ===== STEP 1: SEND OTP =====
            if action == 'send_otp':
                email = data.get('email', '').strip().lower()
                
                # Validate email
                if not email:
                    return JsonResponse({
                        'success': False,
                        'message': 'Email address is required.'
                    }, status=400)
                
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, email):
                    return JsonResponse({
                        'success': False,
                        'message': 'Please enter a valid email address.'
                    }, status=400)
                
                # Check if user exists
                try:
                    user = User.objects.get(email__iexact=email)
                    hotel_name = user.hotel.hotel_name if hasattr(user, 'hotel') else None
                except User.DoesNotExist:
                    # Don't reveal if email exists or not for security
                    return JsonResponse({
                        'success': True,
                        'message': 'If an account exists with this email, you will receive an OTP shortly.'
                    })
                
                # Check rate limiting for OTP
                client_ip = get_client_ip(request)
                otp_key = f"otp_{email}"
                
                if otp_key in otp_storage:
                    last_sent = otp_storage[otp_key].get('last_sent')
                    if last_sent and (datetime.now() - last_sent).total_seconds() < 60:
                        remaining = 60 - int((datetime.now() - last_sent).total_seconds())
                        return JsonResponse({
                            'success': False,
                            'message': f'Please wait {remaining} seconds before requesting a new OTP.'
                        }, status=429)
                
                # Generate and store OTP
                otp = generate_otp(6)
                otp_storage[otp_key] = {
                    'otp': otp,
                    'email': email,
                    'created_at': datetime.now(),
                    'last_sent': datetime.now(),
                    'attempts': 0,
                    'verified': False
                }
                
                # Send OTP email
                email_sent = send_otp_email(email, otp, hotel_name)
                
                if email_sent:
                    return JsonResponse({
                        'success': True,
                        'message': 'OTP sent successfully! Please check your email.'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Failed to send OTP. Please try again.'
                    }, status=500)
            
            # ===== STEP 2: VERIFY OTP =====
            elif action == 'verify_otp':
                email = data.get('email', '').strip().lower()
                otp = data.get('otp', '').strip()
                
                if not email or not otp:
                    return JsonResponse({
                        'success': False,
                        'message': 'Email and OTP are required.'
                    }, status=400)
                
                otp_key = f"otp_{email}"
                
                if otp_key not in otp_storage:
                    return JsonResponse({
                        'success': False,
                        'message': 'OTP has expired. Please request a new one.'
                    }, status=400)
                
                otp_data = otp_storage[otp_key]
                
                # Check if OTP is expired (10 minutes)
                if (datetime.now() - otp_data['created_at']).total_seconds() > 600:
                    del otp_storage[otp_key]
                    return JsonResponse({
                        'success': False,
                        'message': 'OTP has expired. Please request a new one.'
                    }, status=400)
                
                # Check attempts
                if otp_data['attempts'] >= 5:
                    del otp_storage[otp_key]
                    return JsonResponse({
                        'success': False,
                        'message': 'Too many failed attempts. Please request a new OTP.'
                    }, status=429)
                
                # Verify OTP
                if otp_data['otp'] != otp:
                    otp_storage[otp_key]['attempts'] += 1
                    remaining_attempts = 5 - otp_storage[otp_key]['attempts']
                    return JsonResponse({
                        'success': False,
                        'message': f'Invalid OTP. {remaining_attempts} attempt(s) remaining.'
                    }, status=400)
                
                # Mark as verified
                otp_storage[otp_key]['verified'] = True
                
                return JsonResponse({
                    'success': True,
                    'message': 'OTP verified successfully!'
                })
            
            # ===== STEP 3: RESET PASSWORD =====
            elif action == 'reset_password':
                email = data.get('email', '').strip().lower()
                otp = data.get('otp', '').strip()
                new_password = data.get('new_password', '')
                confirm_password = data.get('confirm_password', '')
                
                # Validate inputs
                if not email or not otp:
                    return JsonResponse({
                        'success': False,
                        'message': 'Session expired. Please start over.'
                    }, status=400)
                
                otp_key = f"otp_{email}"
                
                # Verify OTP session
                if otp_key not in otp_storage:
                    return JsonResponse({
                        'success': False,
                        'message': 'Session expired. Please start over.'
                    }, status=400)
                
                otp_data = otp_storage[otp_key]
                
                if not otp_data.get('verified'):
                    return JsonResponse({
                        'success': False,
                        'message': 'OTP not verified. Please verify your OTP first.'
                    }, status=400)
                
                if otp_data['otp'] != otp:
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid session. Please start over.'
                    }, status=400)
                
                # Validate password
                if not new_password:
                    return JsonResponse({
                        'success': False,
                        'message': 'New password is required.'
                    }, status=400)
                
                if len(new_password) < 8:
                    return JsonResponse({
                        'success': False,
                        'message': 'Password must be at least 8 characters long.'
                    }, status=400)
                
                if len(new_password) > 128:
                    return JsonResponse({
                        'success': False,
                        'message': 'Password is too long (max 128 characters).'
                    }, status=400)
                
                if not re.search(r'[A-Z]', new_password):
                    return JsonResponse({
                        'success': False,
                        'message': 'Password must contain at least one uppercase letter (A-Z).'
                    }, status=400)
                
                if not re.search(r'[a-z]', new_password):
                    return JsonResponse({
                        'success': False,
                        'message': 'Password must contain at least one lowercase letter (a-z).'
                    }, status=400)
                
                if not re.search(r'[0-9]', new_password):
                    return JsonResponse({
                        'success': False,
                        'message': 'Password must contain at least one number (0-9).'
                    }, status=400)
                
                if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', new_password):
                    return JsonResponse({
                        'success': False,
                        'message': 'Password must contain at least one special character (!@#$%^&* etc.).'
                    }, status=400)
                
                if not confirm_password:
                    return JsonResponse({
                        'success': False,
                        'message': 'Please confirm your password.'
                    }, status=400)
                
                if new_password != confirm_password:
                    return JsonResponse({
                        'success': False,
                        'message': 'Passwords do not match.'
                    }, status=400)
                
                # Get user and update password
                try:
                    user = User.objects.get(email__iexact=email)
                    hotel_name = user.hotel.hotel_name if hasattr(user, 'hotel') else 'User'
                except User.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'User not found.'
                    }, status=404)
                
                # Set new password
                user.set_password(new_password)
                user.save()
                
                # Clean up OTP storage
                del otp_storage[otp_key]
                
                # Send password changed email
                send_password_changed_email(user, hotel_name)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Password changed successfully! Please login with your new password.',
                    'redirect': '/accounts/login/'
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid action.'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request format.'
            }, status=400)
        except Exception as e:
            print(f"Forgot password error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again.'
            }, status=500)


# #############################################################
# RESEND OTP VIEW
# #############################################################
@csrf_protect
@require_http_methods(["POST"])
def resend_otp_view(request):
    """Resend OTP for password reset"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'Email address is required.'
            }, status=400)
        
        # Check if user exists
        try:
            user = User.objects.get(email__iexact=email)
            hotel_name = user.hotel.hotel_name if hasattr(user, 'hotel') else None
        except User.DoesNotExist:
            return JsonResponse({
                'success': True,
                'message': 'If an account exists with this email, you will receive an OTP shortly.'
            })
        
        # Check rate limiting
        otp_key = f"otp_{email}"
        
        if otp_key in otp_storage:
            last_sent = otp_storage[otp_key].get('last_sent')
            if last_sent and (datetime.now() - last_sent).total_seconds() < 60:
                remaining = 60 - int((datetime.now() - last_sent).total_seconds())
                return JsonResponse({
                    'success': False,
                    'message': f'Please wait {remaining} seconds before requesting a new OTP.'
                }, status=429)
        
        # Generate new OTP
        otp = generate_otp(6)
        otp_storage[otp_key] = {
            'otp': otp,
            'email': email,
            'created_at': datetime.now(),
            'last_sent': datetime.now(),
            'attempts': 0,
            'verified': False
        }
        
        # Send OTP email
        email_sent = send_otp_email(email, otp, hotel_name)
        
        if email_sent:
            return JsonResponse({
                'success': True,
                'message': 'New OTP sent successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to send OTP. Please try again.'
            }, status=500)
            
    except Exception as e:
        print(f"Resend OTP error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }, status=500)


# #############################################################
# LOGOUT VIEW
# #############################################################
def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('login')



# ===== UPDATE PROFILE VIEW =====
@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def update_profile_view(request):
    """Handle profile update page and updates"""
    
    user = request.user
    hotel = user.hotel
    
    if request.method == 'GET':
        # Return profile data for template
        context = {
            'hotel': hotel,
            'user': user,
        }
        return render(request, 'accounts/update_profile.html', context)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action', 'update_profile')
            
            # Track what was updated for email notification
            updated_fields = []
            old_values = {}
            new_values = {}
            
            # ===== UPDATE BASIC PROFILE =====
            if action == 'update_profile':
                hotel_logo_data = data.get('hotel_logo', '')
                hotel_name = data.get('hotel_name', '').strip()
                mobile_number = data.get('mobile_number', '').strip()
                remove_logo = data.get('remove_logo', False)
                
                # ===== HOTEL NAME VALIDATION =====
                if hotel_name:
                    if len(hotel_name) < 2:
                        return JsonResponse({
                            'success': False,
                            'message': 'Hotel name must be at least 2 characters.'
                        }, status=400)
                    
                    if len(hotel_name) > 200:
                        return JsonResponse({
                            'success': False,
                            'message': 'Hotel name is too long (max 200 characters).'
                        }, status=400)
                    
                    if not re.match(r'^[a-zA-Z0-9\s&\'\-\.]+$', hotel_name):
                        return JsonResponse({
                            'success': False,
                            'message': 'Hotel name contains invalid characters.'
                        }, status=400)
                    
                    if hotel.hotel_name != hotel_name:
                        old_values['hotel_name'] = hotel.hotel_name
                        new_values['hotel_name'] = hotel_name
                        hotel.hotel_name = hotel_name
                        user.first_name = hotel_name[:30]
                        updated_fields.append('Hotel Name')
                
                # ===== MOBILE NUMBER VALIDATION =====
                if mobile_number:
                    cleaned_mobile = re.sub(r'[\s\-\(\)\+]', '', mobile_number)
                    
                    if not cleaned_mobile.isdigit():
                        return JsonResponse({
                            'success': False,
                            'message': 'Mobile number should contain only digits.'
                        }, status=400)
                    
                    if len(cleaned_mobile) < 10:
                        return JsonResponse({
                            'success': False,
                            'message': 'Mobile number must be at least 10 digits.'
                        }, status=400)
                    
                    if len(cleaned_mobile) > 15:
                        return JsonResponse({
                            'success': False,
                            'message': 'Mobile number is too long (max 15 digits).'
                        }, status=400)
                    
                    if len(set(cleaned_mobile)) == 1:
                        return JsonResponse({
                            'success': False,
                            'message': 'Please enter a valid mobile number.'
                        }, status=400)
                    
                    sequential_patterns = ['1234567890', '0987654321', '0123456789']
                    for pattern in sequential_patterns:
                        if cleaned_mobile in pattern or pattern in cleaned_mobile:
                            return JsonResponse({
                                'success': False,
                                'message': 'Please enter a valid mobile number.'
                            }, status=400)
                    
                    if hotel.mobile_number != mobile_number:
                        old_values['mobile_number'] = hotel.mobile_number
                        new_values['mobile_number'] = mobile_number
                        hotel.mobile_number = mobile_number
                        updated_fields.append('Mobile Number')
                
                # ===== LOGO HANDLING =====
                if remove_logo and hotel.hotel_logo:
                    old_values['hotel_logo'] = 'Previous Logo'
                    new_values['hotel_logo'] = 'Removed'
                    hotel.hotel_logo.delete(save=False)
                    updated_fields.append('Hotel Logo (Removed)')
                
                elif hotel_logo_data:
                    try:
                        if 'base64,' in hotel_logo_data:
                            format_part, imgstr = hotel_logo_data.split('base64,')
                            
                            if 'png' in format_part:
                                ext = 'png'
                            elif 'jpeg' in format_part or 'jpg' in format_part:
                                ext = 'jpg'
                            elif 'gif' in format_part:
                                ext = 'gif'
                            elif 'webp' in format_part:
                                ext = 'webp'
                            else:
                                return JsonResponse({
                                    'success': False,
                                    'message': 'Invalid logo format. Please use PNG, JPG, GIF, or WEBP.'
                                }, status=400)
                            
                            decoded_file = base64.b64decode(imgstr)
                            if len(decoded_file) > 2 * 1024 * 1024:
                                return JsonResponse({
                                    'success': False,
                                    'message': 'Logo file is too large. Maximum size is 2MB.'
                                }, status=400)
                            
                            # Delete old logo if exists
                            if hotel.hotel_logo:
                                hotel.hotel_logo.delete(save=False)
                            
                            logo_file = ContentFile(decoded_file, name=f'logo_{user.id}.{ext}')
                            hotel.hotel_logo.save(logo_file.name, logo_file, save=False)
                            
                            old_values['hotel_logo'] = 'Previous Logo' if hotel.hotel_logo else 'No Logo'
                            new_values['hotel_logo'] = 'New Logo Uploaded'
                            updated_fields.append('Hotel Logo')
                            
                    except Exception as e:
                        return JsonResponse({
                            'success': False,
                            'message': 'Invalid logo file. Please try again.'
                        }, status=400)
                
                # Save changes
                if updated_fields:
                    hotel.save()
                    user.save()
                    
                    # Send email notification
                    send_profile_updated_email(user, hotel.hotel_name, updated_fields, old_values, new_values)
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Profile updated successfully! Updated: {", ".join(updated_fields)}'
                    })
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'No changes were made.'
                    })
            
            # ===== UPDATE EMAIL =====
            elif action == 'update_email':
                new_email = data.get('new_email', '').strip().lower()
                password = data.get('password', '')
                
                # Validate password first
                if not password:
                    return JsonResponse({
                        'success': False,
                        'message': 'Current password is required to change email.'
                    }, status=400)
                
                if not user.check_password(password):
                    return JsonResponse({
                        'success': False,
                        'message': 'Incorrect password.'
                    }, status=401)
                
                # Validate new email
                if not new_email:
                    return JsonResponse({
                        'success': False,
                        'message': 'New email address is required.'
                    }, status=400)
                
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, new_email):
                    return JsonResponse({
                        'success': False,
                        'message': 'Please enter a valid email address.'
                    }, status=400)
                
                if len(new_email) > 254:
                    return JsonResponse({
                        'success': False,
                        'message': 'Email address is too long.'
                    }, status=400)
                
                if new_email == user.email.lower():
                    return JsonResponse({
                        'success': False,
                        'message': 'New email is same as current email.'
                    }, status=400)
                
                if User.objects.filter(email__iexact=new_email).exclude(id=user.id).exists():
                    return JsonResponse({
                        'success': False,
                        'message': 'An account with this email already exists.'
                    }, status=400)
                
                old_email = user.email
                user.email = new_email
                user.save()
                
                # Send notification to both old and new email
                send_email_changed_notification(user, hotel.hotel_name, old_email, new_email)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Email updated successfully!'
                })
            
            # ===== UPDATE PASSWORD =====
            elif action == 'update_password':
                current_password = data.get('current_password', '')
                new_password = data.get('new_password', '')
                confirm_password = data.get('confirm_password', '')
                
                # Validate current password
                if not current_password:
                    return JsonResponse({
                        'success': False,
                        'message': 'Current password is required.'
                    }, status=400)
                
                if not user.check_password(current_password):
                    return JsonResponse({
                        'success': False,
                        'message': 'Current password is incorrect.'
                    }, status=401)
                
                # Validate new password
                if not new_password:
                    return JsonResponse({
                        'success': False,
                        'message': 'New password is required.'
                    }, status=400)
                
                if len(new_password) < 8:
                    return JsonResponse({
                        'success': False,
                        'message': 'Password must be at least 8 characters long.'
                    }, status=400)
                
                if len(new_password) > 128:
                    return JsonResponse({
                        'success': False,
                        'message': 'Password is too long (max 128 characters).'
                    }, status=400)
                
                if not re.search(r'[A-Z]', new_password):
                    return JsonResponse({
                        'success': False,
                        'message': 'Password must contain at least one uppercase letter (A-Z).'
                    }, status=400)
                
                if not re.search(r'[a-z]', new_password):
                    return JsonResponse({
                        'success': False,
                        'message': 'Password must contain at least one lowercase letter (a-z).'
                    }, status=400)
                
                if not re.search(r'[0-9]', new_password):
                    return JsonResponse({
                        'success': False,
                        'message': 'Password must contain at least one number (0-9).'
                    }, status=400)
                
                if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', new_password):
                    return JsonResponse({
                        'success': False,
                        'message': 'Password must contain at least one special character (!@#$%^&* etc.).'
                    }, status=400)
                
                common_passwords = [
                    'password', 'password1', 'password123', '12345678', 'qwerty123',
                    'letmein', 'welcome', 'admin123', 'abc123', 'monkey123',
                    'Password1', 'Password123', 'Qwerty123', 'Welcome1', 'Admin123',
                    'Hotel123', 'Booking1', 'Manager1'
                ]
                
                if new_password.lower() in [p.lower() for p in common_passwords]:
                    return JsonResponse({
                        'success': False,
                        'message': 'This password is too common. Please choose a stronger password.'
                    }, status=400)
                
                if hotel.hotel_name.lower().replace(' ', '') in new_password.lower():
                    return JsonResponse({
                        'success': False,
                        'message': 'Password should not contain hotel name.'
                    }, status=400)
                
                if current_password == new_password:
                    return JsonResponse({
                        'success': False,
                        'message': 'New password must be different from current password.'
                    }, status=400)
                
                if not confirm_password:
                    return JsonResponse({
                        'success': False,
                        'message': 'Please confirm your new password.'
                    }, status=400)
                
                if new_password != confirm_password:
                    return JsonResponse({
                        'success': False,
                        'message': 'Passwords do not match.'
                    }, status=400)
                
                # Update password
                user.set_password(new_password)
                user.save()
                
                # Send notification
                send_password_changed_email(user, hotel.hotel_name)
                
                # Log user out and redirect to login
                logout(request)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Password changed successfully! Please login with your new password.',
                    'redirect': '/accounts/login/'
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid action.'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request format.'
            }, status=400)
        except Exception as e:
            print(f"Update profile error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again.'
            }, status=500)


def send_profile_updated_email(user, hotel_name, updated_fields, old_values, new_values):
    """Send profile updated email notification"""
    try:
        subject = '✅ Your Bookly Profile Has Been Updated'
        
        context = {
            'hotel_name': hotel_name,
            'email': user.email,
            'updated_fields': updated_fields,
            'old_values': old_values,
            'new_values': new_values,
            'updated_at': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            'login_url': getattr(settings, 'SITE_URL', 'http://localhost:8000') + '/accounts/login/',
            'current_year': datetime.now().year,
        }
        
        html_content = render_to_string('accounts/profile_updated_email.html', context)
        text_content = strip_tags(html_content)
        
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email]
        )
        
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send(fail_silently=False)
        
        return True
    except Exception as e:
        print(f"Profile updated email error: {str(e)}")
        return False


def send_email_changed_notification(user, hotel_name, old_email, new_email):
    """Send email changed notification to both old and new email"""
    try:
        subject = '📧 Your Bookly Email Address Has Been Changed'
        
        context = {
            'hotel_name': hotel_name,
            'old_email': old_email,
            'new_email': new_email,
            'changed_at': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            'login_url': getattr(settings, 'SITE_URL', 'http://localhost:8000') + '/accounts/login/',
            'current_year': datetime.now().year,
        }
        
        html_content = render_to_string('accounts/email_changed_notification.html', context)
        text_content = strip_tags(html_content)
        
        # Send to new email
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[new_email]
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send(fail_silently=False)
        
        # Send to old email as security notification
        context['is_old_email'] = True
        html_content_old = render_to_string('accounts/email_changed_notification.html', context)
        text_content_old = strip_tags(html_content_old)
        
        email_msg_old = EmailMultiAlternatives(
            subject='⚠️ Your Bookly Email Address Was Changed',
            body=text_content_old,
            from_email=settings.EMAIL_HOST_USER,
            to=[old_email]
        )
        email_msg_old.attach_alternative(html_content_old, "text/html")
        email_msg_old.send(fail_silently=False)
        
        return True
    except Exception as e:
        print(f"Email changed notification error: {str(e)}")
        return False