from django.contrib import admin

from .models import MentorshipRequest, StudentMentorshipTask, MentorshipHistory

@admin.register(StudentMentorshipTask)
class StudentMentorshipTasksAdmin(admin.ModelAdmin):
    list_display = ("student", "task", "state", "mentorship")

    @admin.display(description="Mentoría")
    def mentorship(self, obj):
        return obj.task.mentorship

@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "mentorship", "status", "date")

@admin.register(MentorshipHistory)
class MentorshipHistoryAdmin(admin.ModelAdmin):
    list_display = ("student", "mentorship", "state", "date")
