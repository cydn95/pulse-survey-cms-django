from django.contrib import admin
from .models import AOQuestion, AOQuestionSHGroup, AOResponse, AOResponseTopic, AOPage, AOQuestionForm
from django.forms import CheckboxSelectMultiple
from django.contrib.admin.views.main import ChangeList

class AOQuestionList(ChangeList):

    def __init__(self, request, model, list_display,
        list_display_links, list_filter, date_hierarchy,
        search_fields, list_select_related, list_per_page,
        list_max_show_all, list_editable, model_admin):

        super(AOQuestionList, self).__init__(request, model,
            list_display, list_display_links, list_filter,
            date_hierarchy, search_fields, list_select_related,
            list_per_page, list_max_show_all, list_editable,
            model_admin)

        # these need to be defined here, and not in MovieAdmin
        self.list_display = ['action_checkbox', 'driver', 'subdriver', 'questionText', 'controlType', 'sliderTextLeft', 'sliderTextRight', 'shGroup']
        self.list_display_links = ['questionText']
        self.list_editable = ['shGroup']

class AOQuestionAdmin(admin.ModelAdmin):
    def get_changelist(self, request, **kwargs):
        return AOQuestionList
    
    def get_changelist_form(self, request, **kwargs):
        return AOQuestionForm

# Register your models here.
admin.site.register(AOQuestion, AOQuestionAdmin)
admin.site.register(AOQuestionSHGroup)
admin.site.register(AOResponse)
admin.site.register(AOResponseTopic)
admin.site.register(AOPage)