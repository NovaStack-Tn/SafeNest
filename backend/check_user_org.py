from django.contrib.auth import get_user_model
from core.models import Organization
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

User = get_user_model()

# Check all users
users = User.objects.all()
print(f"Total users: {users.count()}")

for user in users:
    print(f"\n👤 User: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Organization: {user.organization}")
    print(f"   Org ID: {user.organization.id if user.organization else 'None'}")
    
    # Fix if no organization
    if user.organization is None:
        print(f"   ⚠️  No organization assigned!")
        org, created = Organization.objects.get_or_create(
            name="Default Organization",
            defaults={'description': 'Default organization for users'}
        )
        user.organization = org
        user.save()
        print(f"   ✅ Assigned to: {org.name} (ID: {org.id})")

print("\n✅ All users checked!")
