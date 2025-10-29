#!/usr/bin/env python
"""
Test the ai_analyze endpoint directly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from django.contrib.auth import get_user_model
from threat_intelligence.models import Threat
from threat_intelligence import ai_service

User = get_user_model()

print("\n" + "="*70)
print("TESTING AI ANALYZE ENDPOINT FLOW")
print("="*70 + "\n")

# Get user and create threat
user = User.objects.first()
print(f"👤 User: {user.username}")
print(f"🏢 Organization: {user.organization}\n")

# Create a test threat
print("Creating test threat...")
threat = Threat.objects.create(
    organization=user.organization,
    title="Suspicious Login Activity",
    description="Multiple failed login attempts from IP 192.168.1.100",
    threat_type="cyber",
    severity="high",
    status="new",
    created_by=user
)
print(f"✅ Created threat ID: {threat.id}\n")

# Test AI analysis
print("Running AI analysis...")
result = ai_service.analyze_threat(
    threat_description=threat.description,
    threat_type=threat.threat_type,
    source=threat.source
)

if result.get('success'):
    print("✅ AI Analysis successful\n")
    
    # Try to save the results to the threat
    print("Saving AI analysis to threat...")
    try:
        threat.ai_analyzed = True
        threat.ai_confidence = result['analysis'].get('confidence', 0.0)
        threat.ai_suggested_severity = result['analysis'].get('severity')
        threat.ai_analysis = result['analysis']
        threat.save()
        print(f"✅ Saved successfully!")
        print(f"   AI Analyzed: {threat.ai_analyzed}")
        print(f"   AI Confidence: {threat.ai_confidence}")
        print(f"   AI Suggested Severity: {threat.ai_suggested_severity}")
    except Exception as e:
        print(f"❌ ERROR saving: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ AI Analysis failed: {result.get('error')}")

# Cleanup
print(f"\n🧹 Cleaning up (deleting threat {threat.id})...")
threat.delete()

print("\n" + "="*70 + "\n")
