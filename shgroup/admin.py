from django.contrib import admin
from .models import SHGroup, SHCategory, SHMapping, ProjectUser, MapType
from jet.admin import CompactInline


class SHGroupAdmin(admin.ModelAdmin):
    fieldset = [
        (None, {'fields': ('SHGroupName', 'SHGroupAbbrev', 'project')})
    ]

    list_display = ('SHGroupName', 'SHGroupAbbrev', 'project')


admin.site.register(SHGroup, SHGroupAdmin)
# Register your models here.
# admin.site.register(SHGroup)
admin.site.register(ProjectUser)
admin.site.register(SHCategory)
admin.site.register(SHMapping)
admin.site.register(MapType)