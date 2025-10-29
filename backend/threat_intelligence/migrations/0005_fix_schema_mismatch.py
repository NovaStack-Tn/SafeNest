# Fix schema mismatch - remove/modify columns that don't exist in model
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('threat_intelligence', '0004_add_timestamps'),
    ]

    operations = [
        # Drop columns that don't exist in the model
        migrations.RunSQL(
            sql="""
            -- Threat table fixes
            ALTER TABLE threat_intelligence_threat 
                DROP COLUMN IF EXISTS risk_score,
                DROP COLUMN IF EXISTS confidence_score,
                DROP COLUMN IF EXISTS external_ref,
                DROP COLUMN IF EXISTS latitude,
                DROP COLUMN IF EXISTS longitude,
                DROP COLUMN IF EXISTS location_name,
                DROP COLUMN IF EXISTS attack_vector,
                DROP COLUMN IF EXISTS impact_analysis,
                DROP COLUMN IF EXISTS last_seen_at,
                DROP COLUMN IF EXISTS resolved_at,
                ALTER COLUMN first_detected DROP NOT NULL,
                ALTER COLUMN source DROP NOT NULL,
                ALTER COLUMN tags SET DEFAULT '[]'::jsonb,
                ALTER COLUMN metadata SET DEFAULT '{}'::jsonb;
            """,
            reverse_sql="SELECT 1;"
        ),
    ]
