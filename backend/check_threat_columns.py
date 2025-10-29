#!/usr/bin/env python
"""
Check all columns in threat_intelligence_threat table
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT 
            column_name, 
            data_type, 
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = 'threat_intelligence_threat'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()

print("\n" + "="*100)
print("THREAT TABLE COLUMNS")
print("="*100)
print(f"{'Column Name':<30} {'Type':<20} {'Nullable':<10} {'Default':<30}")
print("-"*100)

for col_name, data_type, nullable, default in columns:
    default_str = str(default)[:28] if default else ""
    print(f"{col_name:<30} {data_type:<20} {nullable:<10} {default_str:<30}")

print("="*100)
print(f"Total columns: {len(columns)}\n")
