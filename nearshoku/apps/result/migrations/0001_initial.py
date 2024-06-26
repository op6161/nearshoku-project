# Generated by Django 5.0.3 on 2024-03-22 13:42

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ShopInfoModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("shop_list_number", models.IntegerField()),
                ("shop_id", models.CharField(max_length=20)),
                ("shop_name", models.CharField(max_length=100)),
                ("shop_kana", models.CharField(max_length=100)),
                ("shop_access", models.CharField(max_length=100)),
                ("shop_thumbnail", models.ImageField(upload_to="")),
            ],
        ),
    ]
