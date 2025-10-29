#!/usr/bin/env python
"""
Verify threat intelligence database tables have all required columns
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from django.db import connection

def check_table_columns(table_name):
    """Check columns in a table"""
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        return cursor.fetchall()

print("\n" + "="*70)
print("THREAT INTELLIGENCE TABLES - COLUMN VERIFICATION")
print("="*70 + "\n")

tables = [
    'threat_intelligence_threat',
    'threat_intelligence_alert',
    'threat_intelligence_riskassessment',
    'threat_intelligence_threatindicator',
    'threat_intelligence_watchlist'
]

all_good = True

for table in tables:
    print(f"📋 Table: {table}")
    columns = check_table_columns(table)
    
    # Check for required columns
    column_names = [col[0] for col in columns]
    
    required = ['id', 'organization_id', 'created_at', 'updated_at']
    missing = [col for col in required if col not in column_names]
    
    if missing:
        print(f"   ❌ MISSING: {', '.join(missing)}")
        all_good = False
    else:
        print(f"   ✅ Has: id, organization_id, created_at, updated_at")
    
    print(f"   Total columns: {len(columns)}")
    print()

print("="*70)
if all_good:
    print("✅ ALL TABLES VERIFIED - Ready to use!")
else:
    print("❌ SOME TABLES MISSING COLUMNS - Run migrations!")
print("="*70 + "\n")
