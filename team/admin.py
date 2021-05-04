from django.contrib import admin
from .models import Team

class TeamAdmin(admin.ModelAdmin):

    search_fields = ['project__projectName', 'name']
    list_filter = ['project', 'name']
    list_display = ['project', 'name']

    model = Team
    list_per_page = 10

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, ** kwargs)
        project = form.base_fields['project']

        project.widget.can_add_related = False
        project.widget.can_change_related = False
        project.widget.can_delete_related = False

        return form

admin.site.register(Team, TeamAdmin)