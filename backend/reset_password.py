"""
Quick password reset script for SafeNest users.
Usage: python reset_password.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def reset_password():
    print("\n🔐 SafeNest Password Reset Tool")
    print("=" * 50)
    
    # Show all users
    users = User.objects.all()
    print(f"\n📋 Available users ({users.count()}):")
    for i, user in enumerate(users, 1):
        print(f"  {i}. {user.username} ({user.email}) - {user.role}")
    
    # Get username
    print("\n" + "=" * 50)
    username = input("Enter username to reset: ").strip()
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found!")
        return
    
    # Get new password
    new_password = input("Enter new password (min 8 chars): ").strip()
    
    if len(new_password) < 8:
        print("❌ Password must be at least 8 characters!")
        return
    
    # Confirm
    confirm = input(f"Reset password for '{username}'? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        user.set_password(new_password)
        user.save()
        print(f"\n✅ Password reset successfully for '{username}'!")
        print(f"📝 Username: {username}")
        print(f"🔑 New password: {new_password}")
    else:
        print("❌ Password reset cancelled.")

if __name__ == '__main__':
    reset_password()
