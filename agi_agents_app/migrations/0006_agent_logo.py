# Generated by Django 5.0.6 on 2024-09-06 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agi_agents_app', '0005_agent_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='logo',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]