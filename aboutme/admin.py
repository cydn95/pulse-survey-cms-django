from django.contrib import admin
from .models import AMQuestion, AMQuestionSHGroup, AMQuestionOption, AMQuestionSkipOption, AMResponse, AMResponseTopic, AMQuestionForm
from django.forms import CheckboxSelectMultiple
from django.contrib.admin.views.main import ChangeList
from import_export.admin import ImportExportModelAdmin

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

        # currently commented the action_checkbox
        # self.list_display = ['action_checkbox', 'driver', 'subdriver', 'questionText', 'controlType', 'sliderTextLeft', 'sliderTextRight', 'shGroup']
        self.list_display = ['action_checkbox', 'questionText', 'driver', 'subdriver', 'controlType', 'sliderTextLeft', 'sliderTextRight', 'shGroup']
        self.list_display_links = ['questionText']
        self.list_editable = ['shGroup', 'option', 'skipOption']


class AMQuestionAdmin(admin.ModelAdmin):
    def get_changelist(self, request, **kwargs):
        return AMQuestionList

    def get_changelist_form(self, request, **kwargs):
        return AMQuestionForm

class AMResponseAdmin(ImportExportModelAdmin):
    list_display = ['amQuestion', 'user', 'subjectUser', 'survey', 'topicValue', 'commentValue', 'skipValue']
    readonly_fields = ['user', 'subjectUser', 'survey', 'project', 'amQuestion', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']
    model = AMResponse

    def has_add_permission(self, request):
        return False
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Don't allow adding new Item
        """
        form = super(AMResponseAdmin, self).get_form(request, obj, **kwargs)
        # form.base_fields['survey'].widget.can_add_related = False
        # form.base_fields['survey'].widget.can_change_related = False
        # form.base_fields['survey'].widget.can_delete_related = False
        # form.base_fields['user'].widget.can_add_related = False
        # form.base_fields['user'].widget.can_change_related = False
        # form.base_fields['user'].widget.can_delete_related = False
        # form.base_fields['subjectUser'].widget.can_add_related = False
        # form.base_fields['subjectUser'].widget.can_change_related = False
        # form.base_fields['subjectUser'].widget.can_delete_related = False
        # form.base_fields['project'].widget.can_add_related = False
        # form.base_fields['project'].widget.can_change_related = False
        # form.base_fields['project'].widget.can_delete_related = False
        # form.base_fields['amQuestion'].widget.can_add_related = False
        # form.base_fields['amQuestion'].widget.can_change_related = False
        # form.base_fields['amQuestion'].widget.can_delete_related = False

        return form

admin.site.register(AMQuestion, AMQuestionAdmin)
admin.site.register(AMQuestionSHGroup)
admin.site.register(AMQuestionOption)
admin.site.register(AMQuestionSkipOption)
admin.site.register(AMResponse, AMResponseAdmin)
admin.site.register(AMResponseTopic)
