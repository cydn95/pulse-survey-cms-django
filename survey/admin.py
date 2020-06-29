from django.contrib import admin, messages
from shgroup.models import ProjectUser, SHGroup, SHCategory
from aboutme.models import AMQuestion, AMQuestionSHGroup, AMQuestionOption, AMQuestionSkipOption
from aboutothers.models import AOQuestion, AOQuestionSHGroup, AOQuestionOption, AOQuestionSkipOption
from .models import Survey, Client, Project, Driver, ConfigPage, NikelMobilePage, ToolTipGuide
#from gremlin import deleteVertex
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django.utils.html import format_html
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from inline_actions.admin import InlineActionsMixin
from inline_actions.admin import InlineActionsModelAdminMixin
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import include, url
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core import serializers
from django import forms
from django.forms import widgets
from django.forms.models import BaseInlineFormSet
from django.contrib.admin.views.main import ChangeList
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.forms import ModelForm
from boolean_switch.admin import AdminBooleanMixin

class ProjectAdmin(admin.ModelAdmin):

    # Search
    search_fields = ['client', 'projectName']
    # Filter
    list_filter = ['client', 'projectName']
    # list
    list_display = ['client', 'projectName']
    # Edit
    #list_editable = ['projectName']
    list_per_page = 10

    model = Project
    # actions = ['delete_model']
        
class DriverAdmin(SortableAdminMixin, admin.ModelAdmin):
    search_fields = ['driverName']
    list_filter = ['survey']
    list_display = ['driverName', 'survey', 'iconPath']
    list_per_page = 10
    model = Driver

class ToolTipGuideAdmin(SortableAdminMixin, admin.ModelAdmin):
    search_fields = ['title', 'content']
    list_display = ['title', 'place', 'content']
    list_per_page = 10
    model = ToolTipGuide

class ProjectUserInline(InlineActionsMixin, admin.TabularInline):
    model = ProjectUser
    list_per_page = 10
    extra = 0

    #readonly_fields = ['invite_button']
    #fields = ('user', 'projectUserTitle', 'team', 'shGroup', 'invite_button')
    inline_actions = ['send_invite']

    def send_invite(self, request, obj, parent_obj=None):
        obj.save()
        messages.info(request, 'Email invitation has been sent.')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(ProjectUserInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        
        self_pub_id = request.resolver_match.args[0]
        self_proj_pub_id = Survey.objects.get(id=self_pub_id)
        if db_field.name in ['user', 'team', 'shGroup']:
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False

        if db_field.name == 'shGroup':
            if self_pub_id is not None:
                formfield.queryset = formfield.queryset.filter(survey_id=self_pub_id)
            else:
                formfield.queryset = formfield.queryset.none()
            
        if db_field.name == 'team':
            if self_proj_pub_id is not None:
                formfield.queryset = formfield.queryset.filter(project_id=self_proj_pub_id.project_id)
            else:
                formfield.queryset = formfield.queryset.none()

        return formfield

class DriverInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Driver
    extra = 0
    list_per_page = 10

    template = "admin/survey/edit_inline/driver_tabular.html"

# class InlineChangeList(object):
#     can_show_all = True
#     multi_page = True
#     get_query_string = ChangeList.__dict__['get_query_string']

#     def __init__(self, request, page_num, paginator):
#         self.show_all = 'all' in request.GET
#         self.page_num = page_num
#         self.paginator = paginator
#         self.result_count = paginator.count
#         self.params = dict(request.GET.items())
        
class AMQuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = AMQuestion
    ordering = ['driver', 'questionText']
    extra = 0
    exclude = ['isStandard']
    per_page = 10
    template = "admin/survey/edit_inline/amq_tabular.html"

    # def get_formset(self, request, obj=None, **kwargs):
    #     formset_class = super(AMQuestionInline, self).get_formset(request, obj, **kwargs)
    #     class AMQuestionFormSet(formset_class):
    #         def __init__(self, *args, **kwargs):
    #             super(AMQuestionFormSet, self).__init__(*args, **kwargs)

    #             qs = self.queryset
    #             paginator = Paginator(qs, self.per_page)
    #             try:
    #                 page_num = int(request.GET.get('p', '0'))
    #             except ValueError:
    #                 page_num = 0

    #             try:
    #                 page = paginator.page(page_num + 1)
    #             except (EmptyPage, InvalidPage):
    #                 page = paginator.page(paginator.num_pages)

    #             self.cl = InlineChangeList(request, page_num, paginator)
    #             self.paginator = paginator

    #             if self.cl.show_all:
    #                 self._queryset = qs
    #             else:
    #                 self._queryset = page.object_list

    #             print("Test")
    #             print(page.object_list)

    #     AMQuestionFormSet.per_page = self.per_page
        
    #     return AMQuestionFormSet

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(AMQuestionInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        
        self_pub_id = request.resolver_match.args[0]

        if db_field.name in ['driver', 'controlType', 'shGroup', 'option', 'skipOption']:
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False

        if db_field.name == 'driver':
            if self_pub_id is not None:
                formfield.queryset = formfield.queryset.filter(survey_id=self_pub_id)
            else:
                formfield.queryset = formfield.queryset.none()

        if db_field.name == 'shGroup':
            if self_pub_id is not None:
                formfield.queryset = formfield.queryset.filter(survey_id=self_pub_id)
            else:
                formfield.queryset = formfield.queryset.none()

        return formfield

class AOQuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = AOQuestion
    ordering = ['driver', 'questionText']
    extra = 0
    exclude = ['isStandard']
    list_per_page = 10

    template = "admin/survey/edit_inline/aoq_tabular.html"

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(AOQuestionInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        
        self_pub_id = request.resolver_match.args[0]

        if db_field.name in ['driver', 'controlType', 'shGroup', 'option', 'skipOption']:
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False

        if db_field.name == "driver":
            if self_pub_id is not None:
                formfield.queryset = formfield.queryset.filter(survey_id=self_pub_id)
            else:
                formfield.queryset = formfield.queryset.none()

        if db_field.name == 'shGroup':
            if self_pub_id is not None:
                formfield.queryset = formfield.queryset.filter(survey_id=self_pub_id)
            else:
                formfield.queryset = formfield.queryset.none()

        return formfield

class SHGroupInline(admin.TabularInline):
    model = SHGroup
    extra = 0
    list_per_page = 10

class SHCategoryInline(admin.TabularInline):
    model = SHCategory
    extra = 0
    list_per_page = 10

    template = "admin/survey/edit_inline/shcategory_tabular.html"

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(SHCategoryInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ['mapType']:
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False

        return formfield

class ConfigPageInline(admin.StackedInline):
    model = ConfigPage
    extra = 0
    list_per_page = 10

class AMDriverForm(forms.Form):
    am_driver = forms.ModelChoiceField(queryset=None)

class AODriverForm(forms.Form):
    ao_driver = forms.ModelChoiceField(queryset=None)

# class SurveyAdmin(InlineActionsModelAdminMixin, admin.ModelAdmin):
class SurveyAdmin(AdminBooleanMixin, admin.ModelAdmin):
    list_display = ['surveyTitle', 'get_client', 'project', 'isActive']
    search_fields = ['surveyTitle', 'project']
    list_filter = ['project']
    exclude = ['isStandard', 'isActive']
    list_per_page = 10
    # change_form_template = 'admin/survey/change_form.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra = extra_context or {}
        amform = AMDriverForm()
        amform.fields['am_driver'].queryset = Driver.objects.filter(survey_id=object_id)
        extra['am_driver'] = amform
        aoform = AODriverForm()
        aoform.fields['ao_driver'].queryset = Driver.objects.filter(survey_id=object_id)
        extra['ao_driver'] = aoform

        return super(SurveyAdmin, self).change_view(request, object_id, form_url, extra_context=extra)
        
    def get_form(self, request, obj=None, **kwargs):
        
        if obj:
            self.inlines = [
                ProjectUserInline,
                DriverInline,
                AMQuestionInline,
                AOQuestionInline,
                SHGroupInline,
                SHCategoryInline,
                ConfigPageInline
            ]
            context = {
                'object_id': obj.id
            }
        else:
            self.inlines = []

        return super(SurveyAdmin, self).get_form(request, obj, **kwargs)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'resetdriver/', self.reset_driver),
            url(r'resetamq/', self.reset_amq),
            url(r'resetamqlong/', self.reset_amq_long),
            url(r'resetamqshort/', self.reset_amq_short),
            url(r'resetaoq/', self.reset_aoq),
            url(r'resetaoqlong/', self.reset_aoq_long),
            url(r'resetaoqshort/', self.reset_aoq_short),
            url(r'resetshcategory/', self.reset_shcategory),
        ]
        return my_urls + urls

    def reset_shcategory(self, request):
        current_survey_id = request.GET['id']

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)

                if current_survey.id != std_survey.id:
                    SHCategory.objects.filter(survey_id=current_survey.id).delete()

                    try:
                        std_shcategory = SHCategory.objects.filter(survey_id=std_survey.id).values()

                        for i in range(len(std_shcategory)):
                            obj = SHCategory(survey_id=current_survey.id,
                                        SHCategoryName=std_shcategory[i]['SHCategoryName'],
                                        SHCategoryDesc=std_shcategory[i]['SHCategoryDesc'],
                                        mapType_id=std_shcategory[i]['mapType_id'],
                                        colour=std_shcategory[i]['colour'],
                                        icon=std_shcategory[i]['icon'])
                            obj.save()
                    except SHCategory.DoesNotExist:
                        messages.error(request, 'Standard SHCategory doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_5/")
                else:
                    messages.info(request, 'This is the standard SHCategory.')
                    return HttpResponseRedirect("../#/tab/inline_5/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_5/")

        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_5/")

        messages.success(request, 'SHCategory has been reset.')
        return HttpResponseRedirect("../#/tab/inline_5/")

    def reset_driver(self, request):
        current_survey_id = request.GET['id']

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)

                if current_survey.id != std_survey.id:
                    AMQuestion.objects.filter(survey_id=current_survey.id, isStandard=True).delete()
                    AOQuestion.objects.filter(survey_id=current_survey.id, isStandard=True).delete()
                    Driver.objects.filter(survey_id=current_survey.id).delete()
                    
                    try:
                        std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                        
                        for i in range(len(std_driver)):
                            obj = Driver(driverName=std_driver[i]['driverName'],
                                    iconPath=std_driver[i]['iconPath'],
                                    driveOrder=std_driver[i]['driveOrder'],
                                    survey_id=current_survey.id)
                            obj.save()

                            driver_id = obj.id

                            std_amq = AMQuestion.objects.filter(survey_id=std_survey.id, driver_id=std_driver[i]['id'])

                            for j in range(len(std_amq)):
                                amq_obj = AMQuestion(survey=current_survey, driver=obj, 
                                                subdriver=std_amq[j].subdriver,
                                                questionText=std_amq[j].questionText,
                                                controlType_id=std_amq[j].controlType_id,
                                                questionSequence=std_amq[j].questionSequence,
                                                sliderTextLeft=std_amq[j].sliderTextLeft,
                                                sliderTextRight=std_amq[j].sliderTextRight,
                                                skipOptionYN=std_amq[j].skipOptionYN,
                                                topicPrompt=std_amq[j].topicPrompt,
                                                commentPrompt=std_amq[j].commentPrompt,
                                                #shGroup=std_amq[j].shGroup,
                                                #option=std_amq[j].option,
                                                #skipOption=std_amq[j].skipOption,
                                                amqOrder=std_amq[j].amqOrder,
                                                shortForm=std_amq[j].shortForm,
                                                longForm=std_amq[j].longForm,
                                                isStandard=True)
                                amq_obj.save()
                                stdamq_shgroup = std_amq[j].shGroup.all()
                                for a in range(len(stdamq_shgroup)):
                                    amq_obj.shGroup.add(stdamq_shgroup[a])
                                stdamq_option = std_amq[j].option.all()
                                for b in range(len(stdamq_option)):
                                    amq_obj.option.add(stdamq_option[b])
                                stdamq_skipoption = std_amq[j].skipOption.all()
                                for c in range(len(stdamq_skipoption)):
                                    amq_obj.skipOption.add(stdamq_skipoption[c])

                            std_aoq = AOQuestion.objects.filter(survey_id=std_survey.id, driver_id=std_driver[i]['id'])
                            for k in range(len(std_aoq)):
                                aoq_obj = AOQuestion(survey=current_survey, driver=obj, 
                                                subdriver=std_aoq[k].subdriver,
                                                questionText=std_aoq[k].questionText,
                                                controlType_id=std_aoq[k].controlType_id,
                                                questionSequence=std_aoq[k].questionSequence,
                                                sliderTextLeft=std_aoq[k].sliderTextLeft,
                                                sliderTextRight=std_aoq[k].sliderTextRight,
                                                skipOptionYN=std_aoq[k].skipOptionYN,
                                                topicPrompt=std_aoq[k].topicPrompt,
                                                commentPrompt=std_aoq[k].commentPrompt,
                                                aoqOrder=std_aoq[k].aoqOrder,
                                                shortForm=std_aoq[k].shortForm,
                                                longForm=std_aoq[k].longForm,
                                                isStandard=True)
                                aoq_obj.save()
                                stdaoq_shgroup = std_aoq[k].shGroup.all()
                                for a in range(len(stdaoq_shgroup)):
                                    aoq_obj.shGroup.add(stdaoq_shgroup[a])
                                stdaoq_option = std_aoq[k].option.all()
                                for b in range(len(stdaoq_option)):
                                    aoq_obj.option.add(stdaoq_option[b])
                                stdaoq_skipoption = std_aoq[k].skipOption.all()
                                for c in range(len(stdaoq_skipoption)):
                                    aoq_obj.skipOption.add(stdaoq_skipoption[c])
                

                    except Driver.DoesNotExist:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_1/")
                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_1/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_1/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_1/")

        messages.success(request, 'Driver has been reset.')
        return HttpResponseRedirect("../#/tab/inline_1/")

    def reset_amq(self, request):
        current_survey_id = request.GET['id']
        reset = int(request.GET['reset'])
        print("RESET")
        print(reset)
        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)
                
                if current_survey.id != std_survey.id:
                    AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    # AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    if reset == 1:
                        print(reset)
                        Driver.objects.filter(survey_id=current_survey.id).delete()
                    
                    try:
                        std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                        print(std_driver)
                        for i in range(len(std_driver)):
                            obj = None
                            try:
                                obj = Driver.objects.get(driverName=std_driver[i]['driverName'],
                                                    iconPath=std_driver[i]['iconPath'],
                                                    driveOrder=std_driver[i]['driveOrder'],
                                                    survey=current_survey)
                            except Driver.DoesNotExist:
                                obj = Driver(driverName=std_driver[i]['driverName'],
                                        iconPath=std_driver[i]['iconPath'],
                                        driveOrder=std_driver[i]['driveOrder'],
                                        survey_id=current_survey.id)
                                obj.save()

                            driver_id = obj.id

                            std_amq = AMQuestion.objects.filter(survey_id=std_survey.id, driver_id=std_driver[i]['id'])

                            for j in range(len(std_amq)):
                                amq_obj = AMQuestion(survey=current_survey, driver=obj, 
                                                subdriver=std_amq[j].subdriver,
                                                questionText=std_amq[j].questionText,
                                                controlType_id=std_amq[j].controlType_id,
                                                questionSequence=std_amq[j].questionSequence,
                                                sliderTextLeft=std_amq[j].sliderTextLeft,
                                                sliderTextRight=std_amq[j].sliderTextRight,
                                                skipOptionYN=std_amq[j].skipOptionYN,
                                                topicPrompt=std_amq[j].topicPrompt,
                                                commentPrompt=std_amq[j].commentPrompt,
                                                #shGroup=std_amq[j].shGroup,
                                                #option=std_amq[j].option,
                                                #skipOption=std_amq[j].skipOption,
                                                amqOrder=std_amq[j].amqOrder,
                                                shortForm=std_amq[j].shortForm,
                                                longForm=std_amq[j].longForm,
                                                isStandard=True)
                                amq_obj.save()
                                stdamq_shgroup = std_amq[j].shGroup.all()
                                for a in range(len(stdamq_shgroup)):
                                    amq_obj.shGroup.add(stdamq_shgroup[a])
                                stdamq_option = std_amq[j].option.all()
                                for b in range(len(stdamq_option)):
                                    amq_obj.option.add(stdamq_option[b])
                                stdamq_skipoption = std_amq[j].skipOption.all()
                                for c in range(len(stdamq_skipoption)):
                                    amq_obj.skipOption.add(stdamq_skipoption[c])

                    except Driver.DoesNotExist:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_1/")
                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_2/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_1/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_1/")

        messages.success(request, 'AM Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_2/")

    def reset_amq_long(self, request):
        current_survey_id = request.GET['id']
        reset = int(request.GET['reset'])

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)
                
                if current_survey.id != std_survey.id:
                    AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    # AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    if reset == 1:
                        Driver.objects.filter(survey_id=current_survey.id).delete()
                    
                    try:
                        std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                        print(std_driver)
                        for i in range(len(std_driver)):
                            obj = None
                            try:
                                obj = Driver.objects.get(driverName=std_driver[i]['driverName'],
                                                    iconPath=std_driver[i]['iconPath'],
                                                    driveOrder=std_driver[i]['driveOrder'],
                                                    survey=current_survey)
                            except Driver.DoesNotExist:
                                obj = Driver(driverName=std_driver[i]['driverName'],
                                        iconPath=std_driver[i]['iconPath'],
                                        driveOrder=std_driver[i]['driveOrder'],
                                        survey_id=current_survey.id)
                                obj.save()

                            driver_id = obj.id

                            std_amq = AMQuestion.objects.filter(survey_id=std_survey.id, driver_id=std_driver[i]['id'])

                            for j in range(len(std_amq)):
                                amq_obj = AMQuestion(survey=current_survey, driver=obj, 
                                                subdriver=std_amq[j].subdriver,
                                                questionText=std_amq[j].questionText,
                                                controlType_id=std_amq[j].controlType_id,
                                                questionSequence=std_amq[j].questionSequence,
                                                sliderTextLeft=std_amq[j].sliderTextLeft,
                                                sliderTextRight=std_amq[j].sliderTextRight,
                                                skipOptionYN=std_amq[j].skipOptionYN,
                                                topicPrompt=std_amq[j].topicPrompt,
                                                commentPrompt=std_amq[j].commentPrompt,
                                                #shGroup=std_amq[j].shGroup,
                                                #option=std_amq[j].option,
                                                #skipOption=std_amq[j].skipOption,
                                                amqOrder=std_amq[j].amqOrder,
                                                shortForm=False,
                                                longForm=True,
                                                isStandard=True)
                                amq_obj.save()
                                stdamq_shgroup = std_amq[j].shGroup.all()
                                for a in range(len(stdamq_shgroup)):
                                    amq_obj.shGroup.add(stdamq_shgroup[a])
                                stdamq_option = std_amq[j].option.all()
                                for b in range(len(stdamq_option)):
                                    amq_obj.option.add(stdamq_option[b])
                                stdamq_skipoption = std_amq[j].skipOption.all()
                                for c in range(len(stdamq_skipoption)):
                                    amq_obj.skipOption.add(stdamq_skipoption[c])

                    except Driver.DoesNotExist:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_1/")
                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_2/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_1/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_1/")

        messages.success(request, 'AM Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_2/")

    def reset_amq_short(self, request):
        current_survey_id = request.GET['id']
        reset = int(request.GET['reset'])

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)
                
                if current_survey.id != std_survey.id:
                    AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    # AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    if reset == 1:
                        Driver.objects.filter(survey_id=current_survey.id).delete()
                    
                    try:
                        std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                        print(std_driver)
                        for i in range(len(std_driver)):
                            obj = None
                            try:
                                obj = Driver.objects.get(driverName=std_driver[i]['driverName'],
                                                    iconPath=std_driver[i]['iconPath'],
                                                    driveOrder=std_driver[i]['driveOrder'],
                                                    survey=current_survey)
                            except Driver.DoesNotExist:
                                obj = Driver(driverName=std_driver[i]['driverName'],
                                        iconPath=std_driver[i]['iconPath'],
                                        driveOrder=std_driver[i]['driveOrder'],
                                        survey_id=current_survey.id)
                                obj.save()

                            driver_id = obj.id

                            std_amq = AMQuestion.objects.filter(survey_id=std_survey.id, driver_id=std_driver[i]['id'])

                            for j in range(len(std_amq)):
                                amq_obj = AMQuestion(survey=current_survey, driver=obj, 
                                                subdriver=std_amq[j].subdriver,
                                                questionText=std_amq[j].questionText,
                                                controlType_id=std_amq[j].controlType_id,
                                                questionSequence=std_amq[j].questionSequence,
                                                sliderTextLeft=std_amq[j].sliderTextLeft,
                                                sliderTextRight=std_amq[j].sliderTextRight,
                                                skipOptionYN=std_amq[j].skipOptionYN,
                                                topicPrompt=std_amq[j].topicPrompt,
                                                commentPrompt=std_amq[j].commentPrompt,
                                                #shGroup=std_amq[j].shGroup,
                                                #option=std_amq[j].option,
                                                #skipOption=std_amq[j].skipOption,
                                                amqOrder=std_amq[j].amqOrder,
                                                shortForm=True,
                                                longForm=False,
                                                isStandard=True)
                                amq_obj.save()
                                stdamq_shgroup = std_amq[j].shGroup.all()
                                for a in range(len(stdamq_shgroup)):
                                    amq_obj.shGroup.add(stdamq_shgroup[a])
                                stdamq_option = std_amq[j].option.all()
                                for b in range(len(stdamq_option)):
                                    amq_obj.option.add(stdamq_option[b])
                                stdamq_skipoption = std_amq[j].skipOption.all()
                                for c in range(len(stdamq_skipoption)):
                                    amq_obj.skipOption.add(stdamq_skipoption[c])

                    except Driver.DoesNotExist:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_1/")
                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_2/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_1/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_1/")

        messages.success(request, 'AM Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_2/")

    def reset_aoq(self, request):
        current_survey_id = request.GET['id']
        reset = int(request.GET['reset'])

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)

                if current_survey.id != std_survey.id:
                    # AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    if reset == 1:
                        Driver.objects.filter(survey_id=current_survey.id).delete()
                    
                    try:
                        std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                        print(std_driver)
                        for i in range(len(std_driver)):
                            obj = None
                            try:
                                obj = Driver.objects.get(driverName=std_driver[i]['driverName'],
                                                    iconPath=std_driver[i]['iconPath'],
                                                    driveOrder=std_driver[i]['driveOrder'],
                                                    survey=current_survey)
                            except Driver.DoesNotExist:
                                obj = Driver(driverName=std_driver[i]['driverName'],
                                        iconPath=std_driver[i]['iconPath'],
                                        driveOrder=std_driver[i]['driveOrder'],
                                        survey_id=current_survey.id)
                                obj.save()

                            driver_id = obj.id
                            
                            std_aoq = AOQuestion.objects.filter(survey_id=std_survey.id, driver_id=std_driver[i]['id'])
                            for k in range(len(std_aoq)):
                                aoq_obj = AOQuestion(survey=current_survey, driver=obj, 
                                                subdriver=std_aoq[k].subdriver,
                                                questionText=std_aoq[k].questionText,
                                                controlType_id=std_aoq[k].controlType_id,
                                                questionSequence=std_aoq[k].questionSequence,
                                                sliderTextLeft=std_aoq[k].sliderTextLeft,
                                                sliderTextRight=std_aoq[k].sliderTextRight,
                                                skipOptionYN=std_aoq[k].skipOptionYN,
                                                topicPrompt=std_aoq[k].topicPrompt,
                                                commentPrompt=std_aoq[k].commentPrompt,
                                                aoqOrder=std_aoq[k].aoqOrder,
                                                shortForm=std_aoq[k].shortForm,
                                                longForm=std_aoq[k].longForm,
                                                isStandard=True)
                                aoq_obj.save()
                                stdaoq_shgroup = std_aoq[k].shGroup.all()
                                for a in range(len(stdaoq_shgroup)):
                                    aoq_obj.shGroup.add(stdaoq_shgroup[a])
                                stdaoq_option = std_aoq[k].option.all()
                                for b in range(len(stdaoq_option)):
                                    aoq_obj.option.add(stdaoq_option[b])
                                stdaoq_skipoption = std_aoq[k].skipOption.all()
                                for c in range(len(stdaoq_skipoption)):
                                    aoq_obj.skipOption.add(stdaoq_skipoption[c])

                    except Driver.DoesNotExist:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_1/")
                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_3/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_1/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_1/")

        messages.success(request, 'AO Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_3/")

    def reset_aoq_long(self, request):
        current_survey_id = request.GET['id']
        reset = int(request.GET['reset'])

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)

                if current_survey.id != std_survey.id:
                    # AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    if reset == 1:
                        Driver.objects.filter(survey_id=current_survey.id).delete()
                    
                    try:
                        std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                        print(std_driver)
                        for i in range(len(std_driver)):
                            obj = None
                            try:
                                obj = Driver.objects.get(driverName=std_driver[i]['driverName'],
                                                    iconPath=std_driver[i]['iconPath'],
                                                    driveOrder=std_driver[i]['driveOrder'],
                                                    survey=current_survey)
                            except Driver.DoesNotExist:
                                obj = Driver(driverName=std_driver[i]['driverName'],
                                        iconPath=std_driver[i]['iconPath'],
                                        driveOrder=std_driver[i]['driveOrder'],
                                        survey_id=current_survey.id)
                                obj.save()

                            driver_id = obj.id
                            
                            std_aoq = AOQuestion.objects.filter(survey_id=std_survey.id, driver_id=std_driver[i]['id'])
                            for k in range(len(std_aoq)):
                                aoq_obj = AOQuestion(survey=current_survey, driver=obj, 
                                                subdriver=std_aoq[k].subdriver,
                                                questionText=std_aoq[k].questionText,
                                                controlType_id=std_aoq[k].controlType_id,
                                                questionSequence=std_aoq[k].questionSequence,
                                                sliderTextLeft=std_aoq[k].sliderTextLeft,
                                                sliderTextRight=std_aoq[k].sliderTextRight,
                                                skipOptionYN=std_aoq[k].skipOptionYN,
                                                topicPrompt=std_aoq[k].topicPrompt,
                                                commentPrompt=std_aoq[k].commentPrompt,
                                                aoqOrder=std_aoq[k].aoqOrder,
                                                shortForm=False,
                                                longForm=True,
                                                isStandard=True)
                                aoq_obj.save()
                                stdaoq_shgroup = std_aoq[k].shGroup.all()
                                for a in range(len(stdaoq_shgroup)):
                                    aoq_obj.shGroup.add(stdaoq_shgroup[a])
                                stdaoq_option = std_aoq[k].option.all()
                                for b in range(len(stdaoq_option)):
                                    aoq_obj.option.add(stdaoq_option[b])
                                stdaoq_skipoption = std_aoq[k].skipOption.all()
                                for c in range(len(stdaoq_skipoption)):
                                    aoq_obj.skipOption.add(stdaoq_skipoption[c])

                    except Driver.DoesNotExist:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_1/")
                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_3/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_1/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_1/")

        messages.success(request, 'AO Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_3/")

    def reset_aoq_short(self, request):
        current_survey_id = request.GET['id']
        reset = int(request.GET['reset'])

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)

                if current_survey.id != std_survey.id:
                    # AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    if reset == 1:
                        Driver.objects.filter(survey_id=current_survey.id).delete()
                    
                    try:
                        std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                        print(std_driver)
                        for i in range(len(std_driver)):
                            obj = None
                            try:
                                obj = Driver.objects.get(driverName=std_driver[i]['driverName'],
                                                    iconPath=std_driver[i]['iconPath'],
                                                    driveOrder=std_driver[i]['driveOrder'],
                                                    survey=current_survey)
                            except Driver.DoesNotExist:
                                obj = Driver(driverName=std_driver[i]['driverName'],
                                        iconPath=std_driver[i]['iconPath'],
                                        driveOrder=std_driver[i]['driveOrder'],
                                        survey_id=current_survey.id)
                                obj.save()

                            driver_id = obj.id
                            
                            std_aoq = AOQuestion.objects.filter(survey_id=std_survey.id, driver_id=std_driver[i]['id'])
                            for k in range(len(std_aoq)):
                                aoq_obj = AOQuestion(survey=current_survey, driver=obj, 
                                                subdriver=std_aoq[k].subdriver,
                                                questionText=std_aoq[k].questionText,
                                                controlType_id=std_aoq[k].controlType_id,
                                                questionSequence=std_aoq[k].questionSequence,
                                                sliderTextLeft=std_aoq[k].sliderTextLeft,
                                                sliderTextRight=std_aoq[k].sliderTextRight,
                                                skipOptionYN=std_aoq[k].skipOptionYN,
                                                topicPrompt=std_aoq[k].topicPrompt,
                                                commentPrompt=std_aoq[k].commentPrompt,
                                                aoqOrder=std_aoq[k].aoqOrder,
                                                shortForm=True,
                                                longForm=False,
                                                isStandard=True)
                                aoq_obj.save()
                                stdaoq_shgroup = std_aoq[k].shGroup.all()
                                for a in range(len(stdaoq_shgroup)):
                                    aoq_obj.shGroup.add(stdaoq_shgroup[a])
                                stdaoq_option = std_aoq[k].option.all()
                                for b in range(len(stdaoq_option)):
                                    aoq_obj.option.add(stdaoq_option[b])
                                stdaoq_skipoption = std_aoq[k].skipOption.all()
                                for c in range(len(stdaoq_skipoption)):
                                    aoq_obj.skipOption.add(stdaoq_skipoption[c])

                    except Driver.DoesNotExist:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_1/")
                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_3/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_1/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_1/")

        messages.success(request, 'AO Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_3/")

    def get_client(self, obj):
        return obj.project.client
    get_client.short_description = 'Client'
    get_client.admin_order_field = 'project__client'

    

class ClientAdmin(admin.ModelAdmin):
    #list_display = ['clientName', 'client_actions']
    list_display = ['clientName']
    model = Client
    list_per_page = 10

    # def get_queryset(self, request):
    #     self.full_path = request.get_full_path()
    #     return super(ClientAdmin, self).get_queryset(request)

    # def client_actions(self, obj):
    #     return format_html(
    #         mark_safe('<a class="button" href="{}add">Add Project</a><a class="button" href="{}"></a>'.format(self.full_path)),
    #     )
    #     client_actions.short_description = 'Client Actions'
    #     client_actions.allow_tags = True

class NikelMobilePageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['pageOrder', 'survey', 'pageName', 'pageText', 'img']
    list_display_links = ['pageName']
    model = NikelMobilePage
    list_per_page = 10

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        survey = form.base_fields['survey']

        survey.widget.can_add_related = False
        survey.widget.can_change_related = False
        survey.widget.can_delete_related = False

        return form

# Register your models here.
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(ConfigPage)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(ToolTipGuide, ToolTipGuideAdmin)
admin.site.register(NikelMobilePage, NikelMobilePageAdmin)