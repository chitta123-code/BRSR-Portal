from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('SUBMIT', 'Submit'), ('REVIEW', 'Review'), ('APPROVE', 'Approve'), ('REJECT', 'Reject'), ('VERIFY', 'Verify Evidence'), ('IMPORT', 'Import Data'), ('EXPORT', 'Export'), ('DELETE', 'Delete'), ('OTHER', 'Other')], db_index=True, default='OTHER', max_length=20)),
                ('target_model', models.CharField(max_length=100)),
                ('object_pk', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField()),
                ('changes', models.JSONField(blank=True, default=dict)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='brsr_audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Audit Trail Entry',
                'verbose_name_plural': 'Audit Trail Entries',
                'ordering': ['-timestamp'],
            },
        ),
    ]
