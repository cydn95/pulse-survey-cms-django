from django.contrib import admin
from .models import SHGroup, SHGroupUser, SHCategory, SHMapping, ProjectUser
from jet.admin import CompactInline

class SHGroupUserInline(admin.TabularInline):
    model = SHGroupUser
    extra = 0

class SHGroupAdmin(admin.ModelAdmin):
    fieldset = [
        (None, {'fields': ('SHGroupName', 'SHGroupAbbrev', 'project')})
    ]

    inlines = [SHGroupUserInline]

    list_display = ('SHGroupName', 'SHGroupAbbrev', 'project')


admin.site.register(SHGroup, SHGroupAdmin)
# Register your models here.
# admin.site.register(SHGroup)
admin.site.register(ProjectUser)
admin.site.register(SHGroupUser)
admin.site.register(SHCategory)
admin.site.register(SHMapping)