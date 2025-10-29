"""
Script to create test data for Access Control Management
Run this with: python create_test_data.py
"""
import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from datetime import datetime, timedelta
from django.utils import timezone
import random
from access_control.models import AccessPoint, AccessLog, AccessSchedule, AccessPermission
from core.models import User, Organization

print("🚀 Creating test data for Access Control Management...")

# Get existing user by email
try:
    main_user = User.objects.get(email='nihedabdworks@gmail.com')
    org = main_user.organization
    print(f"✅ Using existing user: {main_user.username}")
    print(f"✅ Organization: {org.name}")
except User.DoesNotExist:
    print("❌ Error: User with email 'nihedabdworks@gmail.com' not found!")
    print("Please make sure you're logged in and have an account.")
    sys.exit(1)

if not org:
    print("❌ Error: User has no organization!")
    sys.exit(1)

# Create test users (including your main user)
users_data = [
    {'username': 'john.doe', 'email': 'john@test.com', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': 'jane.smith', 'email': 'jane@test.com', 'first_name': 'Jane', 'last_name': 'Smith'},
    {'username': 'mike.johnson', 'email': 'mike@test.com', 'first_name': 'Mike', 'last_name': 'Johnson'},
    {'username': 'sarah.williams', 'email': 'sarah@test.com', 'first_name': 'Sarah', 'last_name': 'Williams'},
    {'username': 'david.brown', 'email': 'david@test.com', 'first_name': 'David', 'last_name': 'Brown'},
]

# Start with your main user
users = [main_user]
print(f"✅ Main User: {main_user.get_full_name() or main_user.username}")

# Create additional test users
for data in users_data:
    user, created = User.objects.get_or_create(
        username=data['username'],
        defaults={
            'email': data['email'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'organization': org
        }
    )
    if created:
        user.set_password('Test123!')
        user.save()
    users.append(user)
    status = "✅ Created" if created else "ℹ️  Already exists"
    print(f"{status}: {user.get_full_name() or user.username}")

# Create access points
access_points_data = [
    {
        'name': 'Main Entrance Door',
        'point_type': 'door',
        'location': 'Building A - Ground Floor',
        'hardware_id': 'AP-001',
        'ip_address': '192.168.1.101',
        'description': 'Primary entrance to the building'
    },
    {
        'name': 'Server Room Gate',
        'point_type': 'gate',
        'location': 'Building A - Basement',
        'hardware_id': 'AP-002',
        'ip_address': '192.168.1.102',
        'description': 'Restricted access to server infrastructure'
    },
    {
        'name': 'Executive Floor Elevator',
        'point_type': 'elevator',
        'location': 'Building A - Elevator Bank',
        'hardware_id': 'AP-003',
        'ip_address': '192.168.1.103',
        'description': 'Access to executive offices on floor 10'
    },
    {
        'name': 'Parking Barrier',
        'point_type': 'parking',
        'location': 'Parking Lot - Main Entrance',
        'hardware_id': 'AP-004',
        'ip_address': '192.168.1.104',
        'description': 'Vehicle access control'
    },
    {
        'name': 'Reception Turnstile',
        'point_type': 'turnstile',
        'location': 'Building A - Reception',
        'hardware_id': 'AP-005',
        'ip_address': '192.168.1.105',
        'description': 'Main reception entry control'
    },
    {
        'name': 'Conference Room A',
        'point_type': 'door',
        'location': 'Building A - Floor 3',
        'hardware_id': 'AP-006',
        'ip_address': '192.168.1.106',
        'description': 'Meeting room access'
    },
    {
        'name': 'Lab Security Zone',
        'point_type': 'zone',
        'location': 'Building B - Floor 2',
        'hardware_id': 'AP-007',
        'ip_address': '192.168.1.107',
        'description': 'Research laboratory restricted zone'
    },
    {
        'name': 'Emergency Exit Door',
        'point_type': 'door',
        'location': 'Building A - Floor 1',
        'hardware_id': 'AP-008',
        'ip_address': '192.168.1.108',
        'description': 'Emergency exit with alarm'
    }
]

access_points = []
for data in access_points_data:
    point, created = AccessPoint.objects.get_or_create(
        hardware_id=data['hardware_id'],
        defaults={
            'organization': org,
            'name': data['name'],
            'point_type': data['point_type'],
            'location': data['location'],
            'ip_address': data['ip_address'],
            'description': data['description'],
            'status': 'active'
        }
    )
    access_points.append(point)
    status = "✅ Created" if created else "ℹ️  Already exists"
    print(f"{status}: {point.name} ({point.point_type})")

# Create access schedule
schedule, created = AccessSchedule.objects.get_or_create(
    organization=org,
    name='Business Hours',
    defaults={
        'description': 'Standard 9-5 weekday access',
        'days_of_week': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
        'start_time': '08:00:00',
        'end_time': '18:00:00',
        'is_active': True
    }
)
print(f"✅ Schedule: {schedule.name}")

# Create access logs (realistic patterns)
print("\n📝 Creating access logs...")

# Normal working pattern (John - Regular 9-5 worker)
now = timezone.now()
for day in range(7):  # Last 7 days
    date = now - timedelta(days=day)
    if date.weekday() < 5:  # Weekdays only
        # Morning entry
        morning = date.replace(hour=9, minute=random.randint(0, 15))
        AccessLog.objects.create(
            organization=org,
            access_point=access_points[0],  # Main Entrance
            user=users[0],  # John
            event_type='entry',
            is_granted=True,
            timestamp=morning,
            direction='in'
        )
        # Evening exit
        evening = date.replace(hour=17, minute=random.randint(0, 30))
        AccessLog.objects.create(
            organization=org,
            access_point=access_points[0],
            user=users[0],
            event_type='exit',
            is_granted=True,
            timestamp=evening,
            direction='out'
        )

# IT Admin pattern (Jane - Server room access)
for day in range(7):
    date = now - timedelta(days=day)
    if date.weekday() < 5:
        # Multiple server room visits
        for visit in range(random.randint(2, 4)):
            visit_time = date.replace(hour=random.randint(10, 16), minute=random.randint(0, 59))
            AccessLog.objects.create(
                organization=org,
                access_point=access_points[1],  # Server Room
                user=users[1],  # Jane
                event_type='entry',
                is_granted=True,
                timestamp=visit_time,
                direction='in'
            )

# Create ANOMALY: Late night server access
late_night = now - timedelta(days=1)
late_night = late_night.replace(hour=2, minute=30)
anomaly_log = AccessLog.objects.create(
    organization=org,
    access_point=access_points[1],  # Server Room
    user=users[1],  # Jane
    event_type='entry',
    is_granted=True,
    timestamp=late_night,
    direction='in',
    is_anomaly=True,  # Manually mark as anomaly for testing
    anomaly_score=0.89
)
print(f"🚨 Created ANOMALY: {users[1].username} accessed {access_points[1].name} at 2:30 AM")

# Create ANOMALY: Weekend access (unusual for David)
weekend = now - timedelta(days=2)  # 2 days ago
if weekend.weekday() >= 5:  # If it's a weekend
    weekend_time = weekend.replace(hour=20, minute=15)
    AccessLog.objects.create(
        organization=org,
        access_point=access_points[0],
        user=users[4],  # David
        event_type='entry',
        is_granted=True,
        timestamp=weekend_time,
        direction='in',
        is_anomaly=True,
        anomaly_score=0.72
    )
    print(f"🚨 Created ANOMALY: {users[4].username} accessed on weekend")

# Create denied access attempts
denied_reasons = ['no_permission', 'outside_schedule', 'invalid_credential', 'expired']
for i in range(5):
    denied_time = now - timedelta(hours=random.randint(1, 48))
    AccessLog.objects.create(
        organization=org,
        access_point=random.choice(access_points),
        user=random.choice(users),
        event_type='denied',
        is_granted=False,
        denial_reason=random.choice(denied_reasons),
        timestamp=denied_time
    )

# Create high traffic (parking lot)
for hour in [8, 9, 17, 18]:  # Rush hours
    for minute in range(0, 60, 5):  # Every 5 minutes
        access_time = now.replace(hour=hour, minute=minute)
        AccessLog.objects.create(
            organization=org,
            access_point=access_points[3],  # Parking
            user=random.choice(users),
            event_type='entry',
            is_granted=True,
            timestamp=access_time,
            direction='in'
        )

# Create rapid sequential access (suspicious)
rapid_time = now - timedelta(hours=3)
for i in range(4):
    AccessLog.objects.create(
        organization=org,
        access_point=access_points[i],
        user=users[2],  # Mike
        event_type='entry',
        is_granted=True,
        timestamp=rapid_time + timedelta(minutes=i*2),  # 2 minutes apart
        direction='in'
    )
print(f"🚨 Created ANOMALY: {users[2].username} rapid sequential access (4 points in 6 minutes)")

print("\n✨ Test data creation complete!")
print("\n📊 Summary:")
print(f"   - Organization: {org.name}")
print(f"   - Users: {len(users)}")
print(f"   - Access Points: {len(access_points)}")
print(f"   - Access Logs: {AccessLog.objects.filter(organization=org).count()}")
print(f"   - Anomalies: {AccessLog.objects.filter(organization=org, is_anomaly=True).count()}")

print("\n🧪 Test Scenarios Created:")
print("   1. ✅ Normal 9-5 work pattern (John)")
print("   2. ✅ IT admin server access pattern (Jane)")
print("   3. 🚨 Late night anomaly (Jane @ 2:30 AM)")
print("   4. 🚨 Weekend access anomaly (David)")
print("   5. 🚨 Rapid sequential access (Mike)")
print("   6. ❌ Multiple denied access attempts")
print("   7. 📈 Rush hour traffic simulation")

print("\n🔐 Test Credentials:")
print(f"   - Username: {main_user.username} | Email: {main_user.email} (Your account)")
for user in users[1:]:  # Skip main user since we already printed it
    print(f"   - Username: {user.username} | Password: Test123!")

print("\n🌐 Access the pages:")
print("   - Access Points: http://localhost:3000/access-points")
print("   - Login Events: http://localhost:3000/login-events")
print("\n💡 Login with your account (nihedabdworks@gmail.com) to see all data!")
