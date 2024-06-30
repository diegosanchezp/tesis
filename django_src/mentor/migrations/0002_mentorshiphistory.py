# Generated by Django 5.0.6 on 2024-06-28 18:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mentor", "0001_initial"),
        ("register", "0006_alter_registerapprovals_date"),
    ]

    operations = [
        migrations.CreateModel(
            name="MentorshipHistory",
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
                (
                    "state",
                    models.CharField(
                        choices=[("ACCEPTED", "Aceptado"), ("COMPLETED", "Completado")],
                        default="ACCEPTED",
                    ),
                ),
                ("date", models.DateTimeField()),
                (
                    "mentorship",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="history",
                        to="mentor.mentorship",
                        verbose_name="Mentoría",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mentorship_history",
                        to="register.student",
                        verbose_name="Estudiante",
                    ),
                ),
            ],
        ),
    ]
