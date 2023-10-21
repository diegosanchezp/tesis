# Generated by Django 4.2.6 on 2023-10-20 21:11

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
            name='Carreer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True, verbose_name='Nombre')),
            ],
        ),
        migrations.CreateModel(
            name='CarrerSpecialization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True, verbose_name='Nombre')),
                ('career', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='register.carreer', verbose_name='Carrer')),
            ],
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True, verbose_name='Nombre')),
            ],
        ),
        migrations.CreateModel(
            name='InterestTheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Nombre')),
            ],
        ),
        migrations.CreateModel(
            name='Mentor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('carreer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentors', to='register.carreer', verbose_name='Carrera')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('carreer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='register.carreer', verbose_name='Carrera')),
            ],
        ),
        migrations.CreateModel(
            name='StudentInterest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='register.interesttheme', verbose_name='Tema de interés')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='register.student', verbose_name='Estudiante')),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='interests',
            field=models.ManyToManyField(through='register.StudentInterest', to='register.interesttheme', verbose_name='Intereses'),
        ),
        migrations.AddField(
            model_name='student',
            name='specialization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='register.carrerspecialization', verbose_name='Especialización'),
        ),
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='MentorExperience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(help_text='Ej: Frontend developer', verbose_name='Nombre del cargo')),
                ('company', models.TextField(verbose_name='Compañía')),
                ('init_year', models.DateField(verbose_name='Año inicio')),
                ('end_year', models.DateField(blank=True, null=True, verbose_name='Año fin')),
                ('current', models.BooleanField(verbose_name='¿ Cargo actual ?')),
                ('description', models.TextField(verbose_name='Descripción del cargo')),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiences', to='register.mentor', verbose_name='Experiencie Mentor')),
            ],
        ),
        migrations.AddField(
            model_name='mentor',
            name='students',
            field=models.ManyToManyField(to='register.student', verbose_name='Estudiantes mentoreados'),
        ),
        migrations.AddField(
            model_name='mentor',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mentor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='carreer',
            name='faculty',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='carreers', to='register.faculty', verbose_name='faculty'),
        ),
        migrations.AddField(
            model_name='carreer',
            name='interest_themes',
            field=models.ManyToManyField(to='register.interesttheme', verbose_name='Temas de interés'),
        ),
    ]