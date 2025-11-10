"""
Script to migrate interests data from business_name to interests field
Run this after migration 0004_profile_interests
"""
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import Profile

def migrate_interests():
    """Migrate interests from business_name to interests field"""
    profiles = Profile.objects.exclude(business_name='').exclude(business_name__isnull=True)
    
    migrated_count = 0
    for profile in profiles:
        try:
            # Try to parse business_name as JSON (if it contains interests)
            business_name = profile.business_name.strip()
            
            # Check if it looks like JSON array (starts with [ and ends with ])
            if business_name.startswith('[') and business_name.endswith(']'):
                try:
                    interests = json.loads(business_name)
                    # If it's a list of strings, it's likely interests
                    if isinstance(interests, list) and all(isinstance(item, str) for item in interests):
                        profile.interests = interests
                        # Clear business_name if it was only used for interests
                        # (You might want to keep it if it's actually a business name)
                        # profile.business_name = ''
                        profile.save(update_fields=['interests'])
                        migrated_count += 1
                        print(f"Migrated profile {profile.id}: {interests}")
                except json.JSONDecodeError:
                    # Not valid JSON, might be actual business name
                    pass
        except Exception as e:
            print(f"Error migrating profile {profile.id}: {e}")
    
    print(f"\nMigration complete! Migrated {migrated_count} profiles.")

if __name__ == '__main__':
    migrate_interests()





