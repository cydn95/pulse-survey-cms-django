from django.contrib import admin
from .models import Team
from gremlin import deleteVertex

class TeamAdmin(admin.ModelAdmin):
    # Exclude
    # exclude = ['name']

    # Order
    fields = ['name', 'organization']

    # Search
    search_fields = ['name', 'organization']

    # Filter
    list_filter = ['name', 'organization']

    # list
    list_display = ['name', 'organization']

    # Edit
    list_editable = ['organization']

    model = Team
    actions = ['delete_model']

    def delete_model(self, request, obj):
        if obj.id is not None:
            id = 'team-{0}'.format(obj.id)
            deleteVertex(id)
        obj.delete()
        
    # Custom template
    # change_list_template = "admin/team/team_change_list.html"

# Register your models here.
admin.site.register(Team, TeamAdmin)