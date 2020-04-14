from django.contrib import admin
from .models import Team
#from gremlin import deleteVertex

class TeamAdmin(admin.ModelAdmin):

    # Search
    search_fields = ['project', 'name']
    # Filter
    list_filter = ['project', 'name']
    # list
    list_display = ['project', 'name']
    # Edit
    # list_editable = ['project']

    model = Team
    # actions = ['delete_model']

    # def delete_model(self, request, obj):
    #     if obj.id is not None:
    #         id = 'team-{0}'.format(obj.id)
    #         deleteVertex(id)
    #     obj.delete()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, ** kwargs)
        project = form.base_fields['project']

        project.widget.can_add_related = False
        project.widget.can_change_related = False
        project.widget.can_delete_related = False

        return form

# Register your models here.
admin.site.register(Team, TeamAdmin)