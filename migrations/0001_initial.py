# Generated by Django 4.1.6 on 2023-02-04 21:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="StopType",
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
                ("name", models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name="Stop",
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
                ("stop_id", models.IntegerField()),
                ("stop_code", models.IntegerField()),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("stop_name", models.CharField(max_length=60)),
                (
                    "stop_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="vancouver_transit_analyzer.stoptype",
                    ),
                ),
            ],
        ),
    ]
