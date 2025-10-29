"""
Management command to check and fix user organization assignments
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Organization

User = get_user_model()


class Command(BaseCommand):
    help = 'Check and fix user organization assignments'

    def handle(self, *args, **options):
        users = User.objects.all()
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"Checking {users.count()} user(s)...")
        self.stdout.write(f"{'='*60}\n")
        
        users_without_org = []
        
        for user in users:
            self.stdout.write(f"\n👤 User: {user.username}")
            self.stdout.write(f"   Email: {user.email}")
            
            if user.organization:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"   ✅ Organization: {user.organization.name} (ID: {user.organization.id})"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"   ❌ No organization assigned!"
                    )
                )
                users_without_org.append(user)
        
        if users_without_org:
            self.stdout.write(f"\n{'-'*60}")
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  Found {len(users_without_org)} user(s) without organization"
                )
            )
            
            # Auto-fix
            self.stdout.write("\n🔧 Creating/assigning default organization...\n")
            
            org, created = Organization.objects.get_or_create(
                name="Main Organization",
                defaults={
                    'description': 'Default organization for SafeNest users'
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Created organization: {org.name}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Using existing organization: {org.name}")
                )
            
            for user in users_without_org:
                user.organization = org
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"   ✅ Assigned {user.username} to {org.name}")
                )
            
            self.stdout.write(
                self.style.SUCCESS(f"\n✅ All users now have organizations!\n")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n✅ All users have organizations assigned!\n")
            )
        
        self.stdout.write(f"{'='*60}\n")
