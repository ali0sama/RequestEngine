from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import AccessRequest, Application, Profile, Role, WorkflowHistory


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "manager":
            kwargs["queryset"] = User.objects.filter(profile__role=Role.MANAGER)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Application)
admin.site.register(AccessRequest)
admin.site.register(WorkflowHistory)
