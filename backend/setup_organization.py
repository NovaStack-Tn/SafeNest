"""
Quick script to create organization and assign user
Run: python setup_organization.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Organization

User = get_user_model()

# Get or create organization
org, created = Organization.objects.get_or_create(
    name='SafeNest HQ',
    defaults={
        'slug': 'safenest-hq',
        'is_active': True,
        'settings': {'description': 'Main organization'},
    }
)

if created:
    print(f"✅ Created organization: {org.name}")
else:
    print(f"✅ Organization already exists: {org.name}")

# Assign all users without organization
users_updated = 0
for user in User.objects.filter(organization__isnull=True):
    user.organization = org
    user.save()
    users_updated += 1
    print(f"✅ Assigned {user.username} to {org.name}")

print(f"\n🎉 Setup complete! {users_updated} user(s) assigned to organization.")
