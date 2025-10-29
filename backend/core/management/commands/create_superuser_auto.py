"""
Management command to automatically create a superuser from environment variables.
This is useful for deployments where shell access is not available.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Automatically create a superuser from environment variables'

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@safenest.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD','admin123')
        
        if not password:
            self.stdout.write(
                self.style.WARNING(
                    'Skipping superuser creation: DJANGO_SUPERUSER_PASSWORD not set'
                )
            )
            return
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" already exists')
            )
            return
        
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" created successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )
