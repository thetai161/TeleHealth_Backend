# Generated by Django 3.2.13 on 2023-07-21 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetingguest',
            name='conclusion',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='conclusion',
            field=models.TextField(null=True),
        ),
    ]
