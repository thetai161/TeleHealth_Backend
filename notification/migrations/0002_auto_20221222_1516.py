# Generated by Django 3.2.13 on 2022-12-22 08:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('content', models.CharField(blank=True, max_length=100, null=True)),
                ('linkId', models.CharField(blank=True, max_length=50, null=True)),
                ('read', models.BooleanField(blank=True, default=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'notification',
                'ordering': ['-created_at'],
            },
        ),
        migrations.DeleteModel(
            name='Company',
        ),
    ]
