#!/usr/bin/env python
"""
Reset threat_intelligence app - drop all tables and reapply migrations
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from django.db import connection

print("\n" + "="*70)
print("RESETTING THREAT INTELLIGENCE TABLES")
print("="*70 + "\n")

tables_to_drop = [
    'threat_intelligence_threatindicator',
    'threat_intelligence_watchlist',
    'threat_intelligence_alert',
    'threat_intelligence_riskassessment',
    'threat_intelligence_threat',
]

with connection.cursor() as cursor:
    for table in tables_to_drop:
        try:
            print(f"Dropping {table}...")
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            print(f"  ✅ Dropped")
        except Exception as e:
            print(f"  ❌ Error: {e}")

print("\n✅ All tables dropped!")
print("\nNow run:")
print("  python manage.py migrate threat_intelligence")
print("\n" + "="*70 + "\n")
