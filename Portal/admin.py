from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import AccessRequest, Application, Profile, WorkflowHistory


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Application)
admin.site.register(AccessRequest)
admin.site.register(WorkflowHistory)
