from django.contrib import admin
from .models import AMQuestion, AMQuestionSHGroup, AMResponse, AMResponseTopic, AMQuestionForm
from django.forms import CheckboxSelectMultiple
from django.contrib.admin.views.main import ChangeList

class AMQuestionList(ChangeList):

    def __init__(self, request, model, list_display,
        list_display_links, list_filter, date_hierarchy,
        search_fields, list_select_related, list_per_page,
        list_max_show_all, list_editable, model_admin):

        super(AMQuestionList, self).__init__(request, model,
            list_display, list_display_links, list_filter,
            date_hierarchy, search_fields, list_select_related,
            list_per_page, list_max_show_all, list_editable, 
            model_admin)

        # these need to be defined here, and not in MovieAdmin
        self.list_display = ['action_checkbox', 'driver', 'subdriver', 'questionText', 'controlType', 'sliderTextLeft', 'sliderTextRight', 'shGroup']
        self.list_display_links = ['questionText']
        self.list_editable = ['shGroup']


class AMQuestionAdmin(admin.ModelAdmin):
    def get_changelist(self, request, **kwargs):
        return AMQuestionList

    def get_changelist_form(self, request, **kwargs):
        return AMQuestionForm

    
admin.site.register(AMQuestion, AMQuestionAdmin)

# Register your models here.
# admin.site.register(AMQuestion)
admin.site.register(AMQuestionSHGroup)
admin.site.register(AMResponse)
admin.site.register(AMResponseTopic)