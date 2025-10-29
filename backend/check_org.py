#!/usr/bin/env python
"""Check and fix user organization issues"""

from django.contrib.auth import get_user_model
from core.models import Organization

User = get_user_model()

# Check all users
users = User.objects.all()
print(f"Total users: {users.count()}")

for user in users:
    print(f"\nUser: {user.username}")
    print(f"Email: {user.email}")
    print(f"Organization: {user.organization}")
    
    if user.organization is None:
        print("WARNING: No organization assigned!")
        org, created = Organization.objects.get_or_create(
            name="Default Organization",
            defaults={'description': 'Default organization'}
        )
        user.organization = org
        user.save()
        print(f"FIXED: Assigned to {org.name}")
    else:
        print(f"OK: Org ID {user.organization.id}")

print("\nDone!")
