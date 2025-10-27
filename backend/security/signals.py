"""
Signals for security events.
"""
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import LoginEvent
from .utils import get_ip_geolocation, parse_user_agent

User = get_user_model()


@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):
    """Log successful login attempts."""
    from .tasks import process_login_event
    
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Create login event
    event = LoginEvent.objects.create(
        user=user,
        username=user.username,
        success=True,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    # Process asynchronously with Celery
    process_login_event.delay(event.id)


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log failed login attempts."""
    from .tasks import process_login_event
    
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    username = credentials.get('username', 'unknown')
    
    # Create login event
    event = LoginEvent.objects.create(
        user=None,
        username=username,
        success=False,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    # Process asynchronously
    process_login_event.delay(event.id)


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
