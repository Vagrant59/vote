from django.contrib import admin

from polls.models import Subject, Teacher, User


class SubjectModelAdmin(admin.ModelAdmin):
    list_display = ('no', 'name', 'intro', 'is_hot')
    search_fields = ('name', )
    ordering = ('no', 'name', 'intro', 'is_hot', )


class TeacherModelAdmin(admin.ModelAdmin):
    list_display = ('no', 'name', 'sex', 'birth', 'good_count', 'bad_count', 'subject')
    search_fields = ('name', )
    ordering = ('no', 'name', 'sex', 'birth', 'good_count', 'bad_count', 'subject', )


class UserAdmin(admin.ModelAdmin):
    list_display = ('no', 'username', 'tel', 'reg_date', 'last_visit')
    search_fields = ('username', )
    ordering = ('no', 'username', 'tel', 'reg_date', 'last_visit', )


admin.site.register(Subject, SubjectModelAdmin)
admin.site.register(Teacher, TeacherModelAdmin)
admin.site.register(User, UserAdmin)
