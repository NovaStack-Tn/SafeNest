#!/usr/bin/env python
"""
Initialize database with sample data for testing.
Run this after migrations: python init_db.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Organization, Role
from security.models import AnomalyRule
from django.db import connection

User = get_user_model()


def create_pgvector_extension():
    """Create pgvector extension if not exists."""
    print("📊 Creating pgvector extension...")
    with connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print("✅ pgvector extension created")


def create_roles():
    """Create default roles."""
    print("👥 Creating roles...")
    roles = [
        ('admin', 'Full system administrator access'),
        ('sec_officer', 'Security officer with incident management rights'),
        ('employee', 'Regular employee with limited access'),
        ('viewer', 'Read-only viewer access'),
    ]
    
    for role_name, description in roles:
        role, created = Role.objects.get_or_create(
            name=role_name,
            defaults={'description': description}
        )
        if created:
            print(f"  ✓ Created role: {role.get_name_display()}")
    
    print("✅ Roles created")


def create_organization():
    """Create demo organization."""
    print("🏢 Creating organization...")
    org, created = Organization.objects.get_or_create(
        slug='demo-org',
        defaults={
            'name': 'Demo Organization',
            'face_retention_days': 90,
            'consent_required': True,
            'data_residency': 'us-east-1',
        }
    )
    if created:
        print("  ✓ Created organization: Demo Organization")
    else:
        print("  ℹ Organization already exists")
    
    print("✅ Organization ready")
    return org


def create_users(org):
    """Create demo users."""
    print("👤 Creating users...")
    
    admin_role = Role.objects.get(name='admin')
    sec_role = Role.objects.get(name='sec_officer')
    emp_role = Role.objects.get(name='employee')
    
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@demo.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': admin_role,
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'security_officer',
            'email': 'security@demo.com',
            'password': 'security123',
            'first_name': 'Security',
            'last_name': 'Officer',
            'role': sec_role,
            'department': 'Security Operations',
        },
        {
            'username': 'employee',
            'email': 'employee@demo.com',
            'password': 'employee123',
            'first_name': 'John',
            'last_name': 'Employee',
            'role': emp_role,
            'department': 'Engineering',
        },
    ]
    
    for user_data in users_data:
        username = user_data.pop('username')
        password = user_data.pop('password')
        
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                password=password,
                organization=org,
                **user_data
            )
            print(f"  ✓ Created user: {username} (password: {password})")
        else:
            print(f"  ℹ User already exists: {username}")
    
    print("✅ Users created")


def create_anomaly_rules(org):
    """Create sample anomaly detection rules."""
    print("🔍 Creating anomaly rules...")
    
    admin = User.objects.filter(is_superuser=True).first()
    
    rules = [
        {
            'name': 'After Hours Login',
            'rule_type': 'time',
            'description': 'Detect logins outside business hours',
            'config': {'allowed_hours': [9, 10, 11, 12, 13, 14, 15, 16, 17]},
            'severity': 'medium',
        },
        {
            'name': 'Blocked Country Access',
            'rule_type': 'geo',
            'description': 'Detect logins from blocked countries',
            'config': {'blocked_countries': ['CN', 'RU', 'KP']},
            'severity': 'high',
        },
        {
            'name': 'New Device Login',
            'rule_type': 'device',
            'description': 'Detect logins from new devices',
            'config': {},
            'severity': 'low',
        },
        {
            'name': 'Impossible Travel',
            'rule_type': 'velocity',
            'description': 'Detect impossible travel patterns',
            'config': {'max_velocity_kmh': 900},
            'severity': 'critical',
        },
    ]
    
    for rule_data in rules:
        rule, created = AnomalyRule.objects.get_or_create(
            organization=org,
            name=rule_data['name'],
            defaults={
                **rule_data,
                'created_by': admin,
                'active': True,
            }
        )
        if created:
            print(f"  ✓ Created rule: {rule.name}")
    
    print("✅ Anomaly rules created")


def main():
    """Run all initialization tasks."""
    print("\n" + "="*50)
    print("🚀 SafeNest Database Initialization")
    print("="*50 + "\n")
    
    try:
        # Create pgvector extension
        create_pgvector_extension()
        
        # Create roles
        create_roles()
        
        # Create organization
        org = create_organization()
        
        # Create users
        create_users(org)
        
        # Create anomaly rules
        create_anomaly_rules(org)
        
        print("\n" + "="*50)
        print("✨ Database initialization complete!")
        print("="*50)
        print("\n📝 Login credentials:")
        print("   Admin: admin / admin123")
        print("   Security Officer: security_officer / security123")
        print("   Employee: employee / employee123")
        print("\n🌐 Access the platform:")
        print("   API: http://localhost:8000/api/")
        print("   Admin: http://localhost:8000/admin/")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
