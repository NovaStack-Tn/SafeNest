"""
Signals for core app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from security.models import LoginEvent

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Handle post-user creation tasks."""
    if created:
        # Log user creation
        from core.models import AuditLog
        AuditLog.objects.create(
            user=instance,
            organization=instance.organization,
            action='create',
            model_name='User',
            object_id=str(instance.id),
        )
