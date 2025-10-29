# Manual migration to add missing timestamp fields
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('threat_intelligence', '0003_auto_20251029_0717'),
    ]

    operations = [
        # Add created_at and updated_at to Threat if they don't exist
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'threat_intelligence_threat' 
                    AND column_name = 'created_at'
                ) THEN
                    ALTER TABLE threat_intelligence_threat 
                    ADD COLUMN created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'threat_intelligence_threat' 
                    AND column_name = 'updated_at'
                ) THEN
                    ALTER TABLE threat_intelligence_threat 
                    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                END IF;
            END $$;
            """,
            reverse_sql="""
            ALTER TABLE threat_intelligence_threat DROP COLUMN IF EXISTS created_at;
            ALTER TABLE threat_intelligence_threat DROP COLUMN IF EXISTS updated_at;
            """
        ),
        
        # Add created_at and updated_at to Alert if they don't exist
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'threat_intelligence_alert' 
                    AND column_name = 'created_at'
                ) THEN
                    ALTER TABLE threat_intelligence_alert 
                    ADD COLUMN created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'threat_intelligence_alert' 
                    AND column_name = 'updated_at'
                ) THEN
                    ALTER TABLE threat_intelligence_alert 
                    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                END IF;
            END $$;
            """,
            reverse_sql="""
            ALTER TABLE threat_intelligence_alert DROP COLUMN IF EXISTS created_at;
            ALTER TABLE threat_intelligence_alert DROP COLUMN IF EXISTS updated_at;
            """
        ),
        
        # Add created_at and updated_at to RiskAssessment if they don't exist
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'threat_intelligence_riskassessment' 
                    AND column_name = 'created_at'
                ) THEN
                    ALTER TABLE threat_intelligence_riskassessment 
                    ADD COLUMN created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'threat_intelligence_riskassessment' 
                    AND column_name = 'updated_at'
                ) THEN
                    ALTER TABLE threat_intelligence_riskassessment 
                    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                END IF;
            END $$;
            """,
            reverse_sql="""
            ALTER TABLE threat_intelligence_riskassessment DROP COLUMN IF EXISTS created_at;
            ALTER TABLE threat_intelligence_riskassessment DROP COLUMN IF EXISTS updated_at;
            """
        ),
        
        # Add created_at and updated_at to ThreatIndicator if they don't exist
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'threat_intelligence_threatindicator' 
                    AND column_name = 'created_at'
                ) THEN
                    ALTER TABLE threat_intelligence_threatindicator 
                    ADD COLUMN created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'threat_intelligence_threatindicator' 
                    AND column_name = 'updated_at'
                ) THEN
                    ALTER TABLE threat_intelligence_threatindicator 
                    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                END IF;
            END $$;
            """,
            reverse_sql="""
            ALTER TABLE threat_intelligence_threatindicator DROP COLUMN IF EXISTS created_at;
            ALTER TABLE threat_intelligence_threatindicator DROP COLUMN IF EXISTS updated_at;
            """
        ),
        
        # Add created_at and updated_at to Watchlist if they don't exist
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'threat_intelligence_watchlist' 
                    AND column_name = 'created_at'
                ) THEN
                    ALTER TABLE threat_intelligence_watchlist 
                    ADD COLUMN created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'threat_intelligence_watchlist' 
                    AND column_name = 'updated_at'
                ) THEN
                    ALTER TABLE threat_intelligence_watchlist 
                    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                END IF;
            END $$;
            """,
            reverse_sql="""
            ALTER TABLE threat_intelligence_watchlist DROP COLUMN IF EXISTS created_at;
            ALTER TABLE threat_intelligence_watchlist DROP COLUMN IF EXISTS updated_at;
            """
        ),
    ]
