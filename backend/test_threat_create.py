#!/usr/bin/env python
"""
Test threat creation to debug 500 error
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from django.contrib.auth import get_user_model
from threat_intelligence.models import Threat

User = get_user_model()

print("\n" + "="*70)
print("TESTING THREAT CREATION")
print("="*70 + "\n")

# Get first user
user = User.objects.first()
print(f"👤 User: {user.username}")
print(f"🏢 Organization: {user.organization}")
print(f"📧 Email: {user.email}\n")

if not user.organization:
    print("❌ ERROR: User has no organization!")
    exit(1)

# Try to create a threat
try:
    print("Creating test threat...")
    threat = Threat.objects.create(
        organization=user.organization,
        title="Test Threat",
        description="This is a test threat",
        threat_type="cyber",
        severity="high",
        status="new",
        created_by=user
    )
    print(f"✅ SUCCESS! Created threat ID: {threat.id}")
    print(f"   Title: {threat.title}")
    print(f"   Severity: {threat.severity}")
    print(f"   Created at: {threat.created_at}")
    print(f"   Updated at: {threat.updated_at}")
    
    # Clean up
    threat.delete()
    print("\n🧹 Test threat deleted (cleanup)")
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
