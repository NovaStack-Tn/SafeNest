"""Quick script to display all users in the database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from core.models import User

print("\n" + "="*60)
print("👥 SafeNest Users")
print("="*60 + "\n")

users = User.objects.all()

for user in users:
    print(f"📌 Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Full Name: {user.get_full_name() or 'N/A'}")
    print(f"   Role: {user.role}")
    print(f"   Organization: {user.organization}")
    print(f"   Is Active: {user.is_active}")
    print(f"   Is Staff: {user.is_staff}")
    print(f"   Date Joined: {user.date_joined}")
    print("-" * 60)

print(f"\n✅ Total Users: {users.count()}\n")
