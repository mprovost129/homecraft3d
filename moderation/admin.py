from django.contrib import admin
from .models import Report, DMCA, Flag, SecuritySetting

admin.site.register(Report)
admin.site.register(DMCA)
admin.site.register(Flag)
admin.site.register(SecuritySetting)
