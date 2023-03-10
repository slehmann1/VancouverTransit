# Generated by Django 4.1.6 on 2023-02-05 04:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("vancouver_transit_analyzer", "0002_alter_stop_stop_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataPoint",
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
                ("delay", models.IntegerField(null=True)),
                ("skipped", models.BooleanField(default=False)),
                (
                    "stop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="vancouver_transit_analyzer.stop",
                    ),
                ),
            ],
        ),
    ]
