# Generated migration for incident management enhancements

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('incidents', '0001_initial'),
    ]

    operations = [
        # Create IncidentCategory model
        migrations.CreateModel(
            name='IncidentCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('color', models.CharField(default='#6b7280', max_length=7)),
                ('icon', models.CharField(blank=True, max_length=50)),
                ('severity_default', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incident_categories', to='core.organization')),
            ],
            options={
                'verbose_name': 'Incident Category',
                'verbose_name_plural': 'Incident Categories',
                'ordering': ['name'],
            },
        ),
        
        # Add unique constraint
        migrations.AddConstraint(
            model_name='incidentcategory',
            constraint=models.UniqueConstraint(fields=['organization', 'name'], name='unique_org_category_name'),
        ),
        
        # Add new fields to Incident model
        migrations.AddField(
            model_name='incident',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incidents', to='incidents.incidentcategory'),
        ),
        migrations.AddField(
            model_name='incident',
            name='ai_generated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='incident',
            name='ai_confidence',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incident',
            name='extracted_entities',
            field=models.JSONField(blank=True, default=dict),
        ),
        
        # Create IncidentResolution model
        migrations.CreateModel(
            name='IncidentResolution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resolution_type', models.CharField(choices=[('resolved', 'Resolved'), ('false_positive', 'False Positive'), ('duplicate', 'Duplicate'), ('mitigated', 'Mitigated'), ('escalated', 'Escalated'), ('cannot_fix', 'Cannot Fix')], max_length=20)),
                ('summary', models.TextField()),
                ('actions_taken', models.TextField()),
                ('root_cause', models.TextField(blank=True)),
                ('preventive_measures', models.TextField(blank=True)),
                ('resolved_at', models.DateTimeField(auto_now_add=True)),
                ('time_to_detect', models.DurationField(blank=True, null=True)),
                ('time_to_resolve', models.DurationField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('incident', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='resolution', to='incidents.incident')),
                ('related_incidents', models.ManyToManyField(blank=True, related_name='related_resolutions', to='incidents.incident')),
                ('resolved_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_incidents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Incident Resolution',
                'verbose_name_plural': 'Incident Resolutions',
                'ordering': ['-resolved_at'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='incident',
            index=models.Index(fields=['category', '-opened_at'], name='incidents_i_categor_idx'),
        ),
        migrations.AddIndex(
            model_name='incident',
            index=models.Index(fields=['ai_generated', '-opened_at'], name='incidents_i_ai_gene_idx'),
        ),
    ]
