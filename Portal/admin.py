from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Profile)
admin.site.register(models.Application)
admin.site.register(models.AccessRequest)
admin.site.register(models.WorkflowHistory)
