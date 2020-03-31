from django.contrib import admin
from .models import AOQuestion, AOQuestionSHGroup, AOQuestionOption, AOQuestionSkipOption, AOResponse, AOResponseTopic, AOPage, AOQuestionForm
from django.forms import CheckboxSelectMultiple
from django.contrib.admin.views.main import ChangeList
from import_export.admin import ImportExportModelAdmin

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
        self.list_display = ['action_checkbox', 'questionText', 'driver', 'subdriver', 'controlType', 'sliderTextLeft', 'sliderTextRight', 'shGroup']
        self.list_display_links = ['questionText']
        self.list_editable = ['shGroup', 'option', 'skipOption']

class AOQuestionAdmin(admin.ModelAdmin):
    def get_changelist(self, request, **kwargs):
        return AOQuestionList
    
    def get_changelist_form(self, request, **kwargs):
        return AOQuestionForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        controlType = form.base_fields['controlType']

        controlType.widget.can_add_related = False
        controlType.widget.can_change_related = False
        controlType.widget.can_delete_related = False

        return form

#class AOResponseAdmin(admin.ModelAdmin):
class AOResponseAdmin(ImportExportModelAdmin):
    list_display = ['aoQuestion', 'user', 'subjectUser', 'survey', 'topicValue', 'commentValue', 'skipValue']
    fileds = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']
    readonly_fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']
    
    model = AOResponse

    def has_add_permission(self, request):
        return False
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(AOResponseAdmin, self).get_form(request, obj, **kwargs)

        controlType = getattr(obj, 'controlType')
        skipValue = getattr(obj, 'skipValue')
        if controlType == 'TEXT':
            if skipValue != '':
                self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'skipValue']
            else:
                self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
        elif controlType == 'SLIDER':
            if skipValue != '':
                self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'skipValue']
            else:
                self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'integerValue', 'commentValue']
        elif controlType == 'TWO_OPTIONS':
            if skipValue != '':
                self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'skipValue']
            else:
                self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
        elif controlType == 'MULTI_OPTIONS':
            if skipValue != '':
                self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'skipValue']
            else:
                self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
        elif controlType == 'MULTI_TOPICS':
            if skipValue != '':
                self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'skipValue']
            else:
                self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
        elif controlType == 'SMART_TEXT':
            if skipValue != '':
                self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'skipValue']
            else:
                self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
        else:
            self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']

        return form

# Register your models here.
admin.site.register(AOQuestion, AOQuestionAdmin)
admin.site.register(AOQuestionSHGroup)
admin.site.register(AOQuestionOption)
admin.site.register(AOQuestionSkipOption)
admin.site.register(AOResponse, AOResponseAdmin)
admin.site.register(AOResponseTopic)
admin.site.register(AOPage)