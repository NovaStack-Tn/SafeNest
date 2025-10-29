"""
Comprehensive test data generator for Access Control with AI testing
Creates varied patterns, anomalies, and realistic scenarios
Run: python create_comprehensive_test_data.py
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')
django.setup()

from django.utils import timezone
from access_control.models import AccessPoint, AccessLog, AccessAnomaly
from core.models import User, Organization

print("🚀 Creating comprehensive test data for AI testing...")

# Get existing user
try:
    main_user = User.objects.get(email='nihedabdworks@gmail.com')
    org = main_user.organization
    print(f"✅ Using organization: {org.name}")
except User.DoesNotExist:
    print("❌ User not found! Please login first.")
    sys.exit(1)

# Create diverse users
users_data = [
    {'username': 'alice.johnson', 'email': 'alice@company.com', 'first_name': 'Alice', 'last_name': 'Johnson', 'role': 'IT Admin'},
    {'username': 'bob.smith', 'email': 'bob@company.com', 'first_name': 'Bob', 'last_name': 'Smith', 'role': 'Security Officer'},
    {'username': 'charlie.brown', 'email': 'charlie@company.com', 'first_name': 'Charlie', 'last_name': 'Brown', 'role': 'Employee'},
    {'username': 'diana.prince', 'email': 'diana@company.com', 'first_name': 'Diana', 'last_name': 'Prince', 'role': 'Manager'},
    {'username': 'eve.martinez', 'email': 'eve@company.com', 'first_name': 'Eve', 'last_name': 'Martinez', 'role': 'Employee'},
    {'username': 'frank.white', 'email': 'frank@company.com', 'first_name': 'Frank', 'last_name': 'White', 'role': 'Contractor'},
    {'username': 'grace.lee', 'email': 'grace@company.com', 'first_name': 'Grace', 'last_name': 'Lee', 'role': 'Employee'},
]

users = [main_user]
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
    status = "✅ Created" if created else "ℹ️  Exists"
    print(f"{status}: {user.get_full_name()} ({data['role']})")

# Create access points
access_points_data = [
    {'name': 'Main Entrance', 'type': 'door', 'location': 'Building A - Ground Floor', 'hw_id': 'AP-001', 'ip': '192.168.1.101'},
    {'name': 'Server Room', 'type': 'door', 'location': 'Building A - Basement', 'hw_id': 'AP-002', 'ip': '192.168.1.102'},
    {'name': 'Executive Suite', 'type': 'door', 'location': 'Building A - 10th Floor', 'hw_id': 'AP-003', 'ip': '192.168.1.103'},
    {'name': 'Parking Gate', 'type': 'parking', 'location': 'Parking Lot', 'hw_id': 'AP-004', 'ip': '192.168.1.104'},
    {'name': 'Reception Turnstile', 'type': 'turnstile', 'location': 'Lobby', 'hw_id': 'AP-005', 'ip': '192.168.1.105'},
    {'name': 'Conference Room A', 'type': 'door', 'location': 'Floor 3', 'hw_id': 'AP-006', 'ip': '192.168.1.106'},
    {'name': 'R&D Lab', 'type': 'zone', 'location': 'Building B', 'hw_id': 'AP-007', 'ip': '192.168.1.107'},
    {'name': 'Emergency Exit', 'type': 'door', 'location': 'All Floors', 'hw_id': 'AP-008', 'ip': '192.168.1.108'},
    {'name': 'Data Center', 'type': 'zone', 'location': 'Basement Level 2', 'hw_id': 'AP-009', 'ip': '192.168.1.109'},
    {'name': 'Rooftop Access', 'type': 'door', 'location': 'Roof', 'hw_id': 'AP-010', 'ip': '192.168.1.110'},
]

access_points = []
for data in access_points_data:
    point, created = AccessPoint.objects.get_or_create(
        hardware_id=data['hw_id'],
        defaults={
            'organization': org,
            'name': data['name'],
            'point_type': data['type'],
            'location': data['location'],
            'ip_address': data['ip'],
            'status': 'active'
        }
    )
    access_points.append(point)
    status = "✅" if created else "ℹ️"
    print(f"{status} {point.name}")

print("\n📊 Generating realistic access patterns...")

now = timezone.now()
total_logs = 0

# Pattern 1: Normal 9-5 workers (Alice, Charlie, Grace)
normal_workers = [users[1], users[3], users[7]]  # Alice, Charlie, Grace
for user in normal_workers:
    for day in range(30):  # Last 30 days
        date = now - timedelta(days=day)
        if date.weekday() < 5:  # Weekdays only
            # Morning arrival (8-9 AM)
            morning = date.replace(hour=random.randint(8, 9), minute=random.randint(0, 30), second=0, microsecond=0)
            AccessLog.objects.create(
                organization=org,
                access_point=access_points[0],  # Main Entrance
                user=user,
                event_type='entry',
                is_granted=True,
                timestamp=morning,
                direction='in'
            )
            total_logs += 1
            
            # Lunch break (12-1 PM)
            if random.random() > 0.3:  # 70% go out for lunch
                lunch_out = date.replace(hour=12, minute=random.randint(0, 30), second=0, microsecond=0)
                AccessLog.objects.create(
                    organization=org,
                    access_point=access_points[0],
                    user=user,
                    event_type='exit',
                    is_granted=True,
                    timestamp=lunch_out,
                    direction='out'
                )
                lunch_in = lunch_out + timedelta(minutes=random.randint(30, 60))
                AccessLog.objects.create(
                    organization=org,
                    access_point=access_points[0],
                    user=user,
                    event_type='entry',
                    is_granted=True,
                    timestamp=lunch_in,
                    direction='in'
                )
                total_logs += 2
            
            # Evening departure (5-6 PM)
            evening = date.replace(hour=random.randint(17, 18), minute=random.randint(0, 45), second=0, microsecond=0)
            AccessLog.objects.create(
                organization=org,
                access_point=access_points[0],
                user=user,
                event_type='exit',
                is_granted=True,
                timestamp=evening,
                direction='out'
            )
            total_logs += 1

# Pattern 2: IT Admin with server room access (Bob)
bob = users[2]
for day in range(30):
    date = now - timedelta(days=day)
    if date.weekday() < 5:
        # Regular entry
        morning = date.replace(hour=random.randint(8, 9), minute=random.randint(0, 45), second=0, microsecond=0)
        AccessLog.objects.create(
            organization=org,
            access_point=access_points[0],
            user=bob,
            event_type='entry',
            is_granted=True,
            timestamp=morning,
            direction='in'
        )
        total_logs += 1
        
        # Multiple server room visits throughout the day
        for _ in range(random.randint(3, 6)):
            hour = random.randint(9, 17)
            server_access = date.replace(hour=hour, minute=random.randint(0, 59), second=0, microsecond=0)
            AccessLog.objects.create(
                organization=org,
                access_point=access_points[1],  # Server Room
                user=bob,
                event_type='entry',
                is_granted=True,
                timestamp=server_access,
                direction='in'
            )
            total_logs += 1

# Pattern 3: Manager with executive access (Diana)
diana = users[4]
for day in range(30):
    date = now - timedelta(days=day)
    if date.weekday() < 5:
        morning = date.replace(hour=random.randint(8, 10), minute=random.randint(0, 45), second=0, microsecond=0)
        AccessLog.objects.create(
            organization=org,
            access_point=access_points[0],
            user=diana,
            event_type='entry',
            is_granted=True,
            timestamp=morning,
            direction='in'
        )
        
        # Executive suite access
        exec_time = date.replace(hour=random.randint(10, 16), minute=random.randint(0, 59), second=0, microsecond=0)
        AccessLog.objects.create(
            organization=org,
            access_point=access_points[2],  # Executive Suite
            user=diana,
            event_type='entry',
            is_granted=True,
            timestamp=exec_time,
            direction='in'
        )
        total_logs += 2

# Pattern 4: Contractor with limited access (Frank)
frank = users[6]
for day in range(15):  # Only last 15 days (new contractor)
    date = now - timedelta(days=day)
    if date.weekday() < 5:
        morning = date.replace(hour=random.randint(9, 10), minute=random.randint(0, 45), second=0, microsecond=0)
        AccessLog.objects.create(
            organization=org,
            access_point=access_points[0],
            user=frank,
            event_type='entry',
            is_granted=True,
            timestamp=morning,
            direction='in'
        )
        total_logs += 1

# 🚨 ANOMALY 1: Late night server room access
print("\n🚨 Creating anomalies for AI detection...")
late_night = now - timedelta(days=1)
late_night = late_night.replace(hour=2, minute=45, second=0, microsecond=0)
anomaly_log_1 = AccessLog.objects.create(
    organization=org,
    access_point=access_points[1],  # Server Room
    user=bob,
    event_type='entry',
    is_granted=True,
    timestamp=late_night,
    direction='in',
    is_anomaly=True,
    anomaly_score=0.92
)
AccessAnomaly.objects.create(
    organization=org,
    access_log=anomaly_log_1,
    user=bob,
    anomaly_type='unusual_time',
    severity='high',
    confidence_score=0.92,
    description=f'{bob.get_full_name()} accessed Server Room at 2:45 AM - highly unusual time',
    baseline_pattern={'typical_hours': [9, 10, 11, 12, 13, 14, 15, 16, 17]},
    detected_pattern={'access_hour': 2}
)
print(f"   ⚡ Unusual time: {bob.username} @ 2:45 AM")
total_logs += 1

# 🚨 ANOMALY 2: Weekend access
weekend = now - timedelta(days=2)
while weekend.weekday() < 5:
    weekend = weekend - timedelta(days=1)
weekend = weekend.replace(hour=22, minute=15, second=0, microsecond=0)
charlie = users[3]
anomaly_log_2 = AccessLog.objects.create(
    organization=org,
    access_point=access_points[0],
    user=charlie,
    event_type='entry',
    is_granted=True,
    timestamp=weekend,
    direction='in',
    is_anomaly=True,
    anomaly_score=0.78
)
AccessAnomaly.objects.create(
    organization=org,
    access_log=anomaly_log_2,
    user=charlie,
    anomaly_type='pattern_break',
    severity='medium',
    confidence_score=0.78,
    description=f'{charlie.get_full_name()} accessed on weekend - pattern break detected',
    baseline_pattern={'weekend_access_rate': 0.0},
    detected_pattern={'is_weekend': True}
)
print(f"   ⚡ Weekend access: {charlie.username} on {weekend.strftime('%A')}")
total_logs += 1

# 🚨 ANOMALY 3: Rapid sequential access (badge sharing suspicion)
rapid_time = now - timedelta(hours=5)
for i, point in enumerate(access_points[:5]):
    AccessLog.objects.create(
        organization=org,
        access_point=point,
        user=frank,
        event_type='entry',
        is_granted=True,
        timestamp=rapid_time + timedelta(minutes=i*2),
        direction='in'
    )
    total_logs += 1
last_rapid = AccessLog.objects.filter(user=frank, timestamp__gte=rapid_time).last()
last_rapid.is_anomaly = True
last_rapid.anomaly_score = 0.85
last_rapid.save()
AccessAnomaly.objects.create(
    organization=org,
    access_log=last_rapid,
    user=frank,
    anomaly_type='rapid_sequence',
    severity='high',
    confidence_score=0.85,
    description=f'{frank.get_full_name()} accessed 5 points in 8 minutes - suspicious rapid movement',
    baseline_pattern={'avg_points_per_hour': 1.2},
    detected_pattern={'points_accessed': 5, 'time_window_minutes': 8}
)
print(f"   ⚡ Rapid access: {frank.username} - 5 points in 8 min")

# 🚨 ANOMALY 4: Unusual location access
unusual_loc_time = now - timedelta(days=3)
unusual_loc_time = unusual_loc_time.replace(hour=14, minute=30, second=0, microsecond=0)
anomaly_log_4 = AccessLog.objects.create(
    organization=org,
    access_point=access_points[8],  # Data Center (never accessed before)
    user=charlie,
    event_type='entry',
    is_granted=True,
    timestamp=unusual_loc_time,
    direction='in',
    is_anomaly=True,
    anomaly_score=0.81
)
AccessAnomaly.objects.create(
    organization=org,
    access_log=anomaly_log_4,
    user=charlie,
    anomaly_type='unusual_location',
    severity='medium',
    confidence_score=0.81,
    description=f'{charlie.get_full_name()} accessed Data Center - first time access to this location',
    baseline_pattern={'usual_locations': ['Main Entrance', 'Conference Room A']},
    detected_pattern={'new_location': 'Data Center'}
)
print(f"   ⚡ Unusual location: {charlie.username} @ Data Center")
total_logs += 1

# ❌ Create denied access attempts
print("\n❌ Creating denied access attempts...")
denial_reasons = ['no_permission', 'outside_schedule', 'invalid_credential', 'expired']

# Regular denied attempts spread across time
for i in range(50):
    denied_time = now - timedelta(hours=random.randint(1, 168))  # Last week
    AccessLog.objects.create(
        organization=org,
        access_point=random.choice(access_points),
        user=random.choice(users),
        event_type='denied',
        is_granted=False,
        denial_reason=random.choice(denial_reasons),
        timestamp=denied_time
    )
    total_logs += 1

# Cluster of denials at server room (security concern)
for i in range(15):
    denied_time = now - timedelta(hours=random.randint(1, 48))
    AccessLog.objects.create(
        organization=org,
        access_point=access_points[1],  # Server Room
        user=random.choice([frank, users[5]]),  # Contractors with no access
        event_type='denied',
        is_granted=False,
        denial_reason='no_permission',
        timestamp=denied_time
    )
    total_logs += 1

# Failed badge attempts (expired credentials)
for i in range(10):
    denied_time = now - timedelta(hours=random.randint(1, 24))
    AccessLog.objects.create(
        organization=org,
        access_point=random.choice(access_points),
        user=random.choice(users),
        event_type='denied',
        is_granted=False,
        denial_reason='expired',
        timestamp=denied_time
    )
    total_logs += 1

print(f"   Created 75 denied access attempts (various scenarios)")

# 🚗 High traffic at parking (rush hours)
print("\n🚗 Simulating rush hour traffic...")
for day in range(7):
    date = now - timedelta(days=day)
    if date.weekday() < 5:
        # Morning rush (7:30-9:00 AM)
        for minute in range(0, 90, 3):  # Every 3 minutes
            rush_time = date.replace(hour=7, minute=30, second=0, microsecond=0) + timedelta(minutes=minute)
            AccessLog.objects.create(
                organization=org,
                access_point=access_points[3],  # Parking
                user=random.choice(users),
                event_type='entry',
                is_granted=True,
                timestamp=rush_time,
                direction='in'
            )
            total_logs += 1
        
        # Evening rush (5:00-6:30 PM)
        for minute in range(0, 90, 3):
            rush_time = date.replace(hour=17, minute=0, second=0, microsecond=0) + timedelta(minutes=minute)
            AccessLog.objects.create(
                organization=org,
                access_point=access_points[3],
                user=random.choice(users),
                event_type='exit',
                is_granted=True,
                timestamp=rush_time,
                direction='out'
            )
            total_logs += 1

print(f"   Created rush hour traffic patterns")

# 📋 Conference room usage
print("\n📋 Simulating meeting patterns...")
for day in range(14):
    date = now - timedelta(days=day)
    if date.weekday() < 5:
        # Morning meetings (9-11 AM)
        for _ in range(random.randint(2, 4)):
            meeting_time = date.replace(hour=random.randint(9, 11), minute=0, second=0, microsecond=0)
            AccessLog.objects.create(
                organization=org,
                access_point=access_points[5],  # Conference Room
                user=random.choice(users),
                event_type='entry',
                is_granted=True,
                timestamp=meeting_time,
                direction='in'
            )
            total_logs += 1

print("\n" + "="*60)
print("✨ TEST DATA GENERATION COMPLETE!")
print("="*60)
print(f"\n📊 Statistics:")
print(f"   - Users: {len(users)}")
print(f"   - Access Points: {len(access_points)}")
print(f"   - Total Logs: {total_logs}")
print(f"   - Anomalies: {AccessAnomaly.objects.filter(organization=org).count()}")
print(f"   - Denied Attempts: {AccessLog.objects.filter(organization=org, is_granted=False).count()}")
print(f"   - Time Range: Last 30 days")

print(f"\n🎯 AI Testing Scenarios Created:")
print(f"   1. ✅ Normal 9-5 patterns (multiple users)")
print(f"   2. ✅ IT admin server access patterns")
print(f"   3. ✅ Executive suite usage")
print(f"   4. ✅ Contractor limited access")
print(f"   5. 🚨 Late night anomaly (2 AM access)")
print(f"   6. 🚨 Weekend access anomaly")
print(f"   7. 🚨 Rapid sequential access (badge sharing)")
print(f"   8. 🚨 Unusual location access")
print(f"   9. ❌ Denied access attempts")
print(f"   10. 🚗 Rush hour traffic patterns")
print(f"   11. 📋 Meeting room usage")

print(f"\n🌐 Next Steps:")
print(f"   1. Restart backend: python manage.py runserver")
print(f"   2. Open frontend: http://localhost:3000/access-points")
print(f"   3. View AI suggestions (Gemini-powered)")
print(f"   4. Check login events: http://localhost:3000/login-events")
print(f"   5. See security alerts and anomalies")

print(f"\n✨ Gemini AI will analyze this data and provide:")
print(f"   - Security threat detection")
print(f"   - Traffic optimization suggestions")
print(f"   - Anomaly pattern insights")
print(f"   - Operational efficiency recommendations")
