from django.contrib import admin, messages
from shgroup.models import ProjectUser, SHGroup, SHCategory
from aboutme.models import AMQuestion, AMQuestionSHGroup, AMQuestionOption, AMQuestionSkipOption
from aboutothers.models import AOQuestion, AOQuestionSHGroup, AOQuestionOption, AOQuestionSkipOption
from .models import Survey, Client, Project, Driver, ConfigPage, NikelMobilePage, ToolTipGuide
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
from django.db.models import Q

class ProjectAdmin(admin.ModelAdmin):

    search_fields = ['client__clientName', 'projectName']
    list_filter = ['client', 'projectName']
    list_display = ['client', 'projectName']
    list_per_page = 10

    model = Project
        
class DriverAdmin(SortableAdminMixin, admin.ModelAdmin):
    search_fields = ['driverName']
    list_filter = ['survey']
    list_display = ['driverName', 'survey', 'iconPath']
    exclude = ['isStandard']
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

    inline_actions = ['send_invite']

    def send_invite(self, request, obj, parent_obj=None):
        # temporary commented 2021-03-24
        print("Send Invite Test")
        print(self)
        # obj.save()
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
    exclude = ['isStandard']
    template = "admin/survey/edit_inline/driver_tabular.html"
      
class AMQuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = AMQuestion
    ordering = ['driver', 'questionText']
    extra = 0
    exclude = ['isStandard']
    per_page = 10
    template = "admin/survey/edit_inline/amq_tabular.html"

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(AMQuestionInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        
        self_pub_id = request.resolver_match.args[0]

        if db_field.name in ['driver', 'controlType', 'shGroup', 'skipOption']:
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

        if db_field.name == 'option':
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

        if db_field.name in ['driver', 'controlType', 'shGroup', 'skipOption']:
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

        if db_field.name == 'option':
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

class NikelMobilePageInline(admin.StackedInline):
    model = NikelMobilePage
    extra = 0
    list_per_page = 10

class AMDriverForm(forms.Form):
    am_driver = forms.ModelChoiceField(queryset=None)

class AODriverForm(forms.Form):
    ao_driver = forms.ModelChoiceField(queryset=None)

class SurveyAdmin(admin.ModelAdmin):
    list_display = ['surveyTitle', 'get_client', 'project', 'survey_status']
    search_fields = ['surveyTitle', 'project__projectName']
    list_filter = ['project']
    exclude = ['isStandard', 'isActive']
    list_per_page = 10
    
    def survey_status(self, obj):
        if obj.isActive:
            return '<a onclick="activeSurvey(%s, 0)"><label class="switch"><input type="checkbox" name="project_%s" checked><span class="slider round"></span></label></a>' % (obj.id, obj.project_id)
        else:
            return '<a onclick="activeSurvey(%s, 1)"><label class="switch"><input type="checkbox" name="project_%s"><span class="slider round"></span></label></a>' % (obj.id, obj.project_id)
    survey_status.allow_tags = True
    survey_status.short_description = 'Survey Status'

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
                SHGroupInline,
                ProjectUserInline,
                DriverInline,
                AMQuestionInline,
                AOQuestionInline,
                SHCategoryInline,
                ConfigPageInline,
                NikelMobilePageInline,
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
            url(r'activesurvey/', self.active_survey),
        ]
        return my_urls + urls

    def active_survey(self, request):
        current_survey_id = request.GET['id']
        status = request.GET['status']

        project_id = Survey.objects.get(pk=current_survey_id).project_id
        
        if status == "1":
            Survey.objects.filter(pk=current_survey_id).update(isActive=True)
        elif status == "0":
            Survey.objects.filter(pk=current_survey_id).update(isActive=False)

        Survey.objects.filter(~Q(pk=current_survey_id), project_id=project_id).update(isActive=False)
        if request.is_ajax():
            message = "Yes, AJAX!"
        else:
            message = "Not Ajax"
        return HttpResponse(message)

    def reset_shcategory(self, request):
        current_survey_id = request.GET['id']

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)

                if current_survey.id != std_survey.id:
                    SHCategory.objects.filter(survey_id=current_survey.id).delete()

                    
                    std_shcategory = SHCategory.objects.filter(survey_id=std_survey.id).values()

                    if std_shcategory.count() == 0:
                        messages.error(request, 'Standard SHCategory doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_5/")

                    for i in range(len(std_shcategory)):
                        obj = SHCategory(survey_id=current_survey.id,
                                    SHCategoryName=std_shcategory[i]['SHCategoryName'],
                                    SHCategoryDesc=std_shcategory[i]['SHCategoryDesc'],
                                    mapType_id=std_shcategory[i]['mapType_id'],
                                    colour=std_shcategory[i]['colour'],
                                    icon=std_shcategory[i]['icon'])
                        obj.save()
                        
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
                    
                    
                    std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                    
                    if std_driver.count() == 0:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_2/")

                    for i in range(len(std_driver)):
                        obj = Driver(driverName=std_driver[i]['driverName'],
                                iconPath=std_driver[i]['iconPath'],
                                driveOrder=std_driver[i]['driveOrder'],
                                survey_id=current_survey.id,
                                isStandard=True)
                        obj.save()
                        
                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_2/")
            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_2/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_2/")

        messages.success(request, 'Driver has been reset.')
        return HttpResponseRedirect("../#/tab/inline_2/")

    def reset_amq(self, request):
        current_survey_id = request.GET['id']
        reset = int(request.GET['reset'])
        
        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)
                
                if current_survey.id != std_survey.id:
                    AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    
                    if reset == 1:
                        Driver.objects.filter(survey_id=current_survey.id, isStandard=False).delete()
                    
                    std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                    if std_driver.count() == 0:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_3/")

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
                                    survey_id=current_survey.id, isStandard=True)
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

                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_3/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_3/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_3/")

        messages.success(request, 'AM Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_3/")

    def reset_amq_long(self, request):
        current_survey_id = request.GET['id']
        reset = int(request.GET['reset'])

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)
                
                if current_survey.id != std_survey.id:
                    AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    if reset == 1:
                        Driver.objects.filter(survey_id=current_survey.id, isStandard=False).delete()

                    std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                    if std_driver.count() == 0:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_3/")
                    
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
                                    survey_id=current_survey.id, isStandard=True)
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

                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_3/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_3/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_3/")

        messages.success(request, 'AM Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_3/")

    def reset_amq_short(self, request):
        current_survey_id = request.GET['id']
        reset = int(request.GET['reset'])

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)
                
                if current_survey.id != std_survey.id:
                    AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    if reset == 1:
                        Driver.objects.filter(survey_id=current_survey.id, isStandard=False).delete()
                    
                    std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                    if std_driver.count() == 0:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_3/")

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
                                    survey_id=current_survey.id, isStandard=True)
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
  
                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_3/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_3/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_3/")

        messages.success(request, 'AM Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_3/")

    def reset_aoq(self, request):
        current_survey_id = request.GET['id']
        reset = int(request.GET['reset'])

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)

                if current_survey.id != std_survey.id:
                    AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    if reset == 1:
                        Driver.objects.filter(survey_id=current_survey.id, isStandard=False).delete()

                    std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                    if std_driver.count() == 0:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_4/")

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
                                    survey_id=current_survey.id, isStandard=True)
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
 
                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_4/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_4/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_4/")

        messages.success(request, 'AO Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_4/")

    def reset_aoq_long(self, request):
        current_survey_id = request.GET['id']
        reset = int(request.GET['reset'])

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)

                if current_survey.id != std_survey.id:
                    AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    if reset == 1:
                        Driver.objects.filter(survey_id=current_survey.id, isStandard=False).delete()
                    
                    std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                    if std_driver.count() == 0:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_4/")

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
                                    survey_id=current_survey.id, isStandard=True)
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
 
                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_4/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_4/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_4/")

        messages.success(request, 'AO Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_4/")

    def reset_aoq_short(self, request):
        current_survey_id = request.GET['id']
        reset = int(request.GET['reset'])

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)

                if current_survey.id != std_survey.id:
                    AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    if reset == 1:
                        Driver.objects.filter(survey_id=current_survey.id, isStandard=False).delete()
                    
                    std_driver = Driver.objects.filter(survey_id=std_survey.id).values()
                    if std_driver.count() == 0:
                        messages.error(request, 'Standard Driver doesn\'t exist.')
                        return HttpResponseRedirect("../#/tab/inline_4/")

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
                                    survey_id=current_survey.id, isStandard=True)
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

                else:
                    messages.info(request, 'This is the standard survey.')
                    return HttpResponseRedirect("../#/tab/inline_4/")

            except Survey.DoesNotExist:
                messages.error(request, 'Unknown errors. Please try again.')
                return HttpResponseRedirect("../#/tab/inline_4/")
        except Survey.DoesNotExist:
            messages.error(request, 'Unknown errors. Please try again.')
            return HttpResponseRedirect("../#/tab/inline_4/")

        messages.success(request, 'AO Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_4/")

    def get_client(self, obj):
        return obj.project.client
    get_client.short_description = 'Client'
    get_client.admin_order_field = 'project__client'

    

class ClientAdmin(admin.ModelAdmin):
    list_display = ['clientName']
    model = Client
    list_per_page = 10

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
