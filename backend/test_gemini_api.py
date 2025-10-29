#!/usr/bin/env python
"""
Test Gemini API configuration
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from django.conf import settings
import google.generativeai as genai

print("\n" + "="*70)
print("TESTING GEMINI API CONFIGURATION")
print("="*70 + "\n")

# Check API key
api_key = getattr(settings, 'GEMINI_API_KEY', None)
print(f"API Key configured: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API Key (first 10 chars): {api_key[:10]}...")
else:
    print("❌ ERROR: GEMINI_API_KEY not configured in settings!")
    exit(1)

# Try to configure Gemini
try:
    genai.configure(api_key=api_key)
    print("✅ Gemini API configured successfully\n")
except Exception as e:
    print(f"❌ Error configuring Gemini: {e}\n")
    exit(1)

# Test AI service
print("Testing threat analysis function...")
from threat_intelligence import ai_service

result = ai_service.analyze_threat(
    threat_description="Multiple failed login attempts from IP 192.168.1.100",
    threat_type="cyber",
    source="IDS System"
)

print("\n" + "-"*70)
if result.get('success'):
    print("✅ AI Analysis SUCCESS!")
    print(f"\nAnalysis:")
    import json
    print(json.dumps(result['analysis'], indent=2))
else:
    print("❌ AI Analysis FAILED!")
    print(f"Error: {result.get('error')}")
    if result.get('raw_response'):
        print(f"Raw response: {result['raw_response']}")

print("\n" + "="*70 + "\n")
