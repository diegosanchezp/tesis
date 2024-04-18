# Generated by Django 4.2.11 on 2024-03-09 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('register', '0005_themespecprocarreer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mentorship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nombre')),
                ('num_completed', models.PositiveIntegerField(default=0)),
                ('students_enrolled', models.PositiveIntegerField(default=0)),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentorships', to='register.mentor', verbose_name='Mentorías')),
            ],
            options={
                'unique_together': {('mentor', 'name')},
            },
        ),
        migrations.CreateModel(
            name='MentorshipTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nombre de la tarea', max_length=255, verbose_name='')),
                ('mentorship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='mentor.mentorship', verbose_name='Tarea')),
            ],
        ),
        migrations.CreateModel(
            name='StudentMentorshipTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('TODO', 'Por hacer'), ('IN_PROGRESS', 'En progreso'), ('COMPLETED', 'Completada')], default='TODO', max_length=250)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentorship_tasks', to='register.student', verbose_name='Mis tareas de Mentorías')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_tasks', to='mentor.mentorshiptask')),
            ],
            options={
                'unique_together': {('student', 'task')},
            },
        ),
        migrations.CreateModel(
            name='MentorshipRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('REQUESTED', 'Solicitado'), ('CANCELED', 'Cancelado'), ('REJECTED', 'Rechazado')], default='REQUESTED', max_length=255, verbose_name='Estado')),
                ('date', models.DateTimeField(auto_now=True, verbose_name='Fecha del estatus')),
                ('mentorship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentorship_requests', to='mentor.mentorship', verbose_name='Solicitudes')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentorship_requests', to='register.student', verbose_name='Solicitudes de mentorías')),
            ],
            options={
                'unique_together': {('student', 'mentorship')},
            },
        ),
    ]
