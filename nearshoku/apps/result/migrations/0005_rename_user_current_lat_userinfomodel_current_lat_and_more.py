# Generated by Django 5.0.3 on 2024-03-23 08:14

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("result", "0004_userinfomodel"),
    ]

    operations = [
        migrations.RenameField(
            model_name="userinfomodel",
            old_name="user_current_lat",
            new_name="current_lat",
        ),
        migrations.RenameField(
            model_name="userinfomodel",
            old_name="user_current_lng",
            new_name="current_lng",
        ),
        migrations.RenameField(
            model_name="userinfomodel",
            old_name="user_order",
            new_name="order",
        ),
        migrations.RenameField(
            model_name="userinfomodel",
            old_name="user_range",
            new_name="range",
        ),
        migrations.RenameField(
            model_name="userinfomodel",
            old_name="user_selected_lat",
            new_name="selected_lat",
        ),
        migrations.RenameField(
            model_name="userinfomodel",
            old_name="user_selected_lng",
            new_name="selected_lng",
        ),
    ]
