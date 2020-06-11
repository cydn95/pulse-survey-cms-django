from django.contrib import admin, messages
from shgroup.models import ProjectUser, SHGroup, SHCategory
from aboutme.models import AMQuestion, AMQuestionSHGroup, AMQuestionOption, AMQuestionSkipOption
from aboutothers.models import AOQuestion, AOQuestionSHGroup, AOQuestionOption, AOQuestionSkipOption
from .models import Survey, Client, Project, Driver, ConfigPage, NikelMobilePage
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

class ProjectAdmin(admin.ModelAdmin):

    # Search
    search_fields = ['client', 'projectName']
    # Filter
    list_filter = ['client', 'projectName']
    # list
    list_display = ['client', 'projectName']
    # Edit
    #list_editable = ['projectName']

    model = Project
    # actions = ['delete_model']
        
class DriverAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass

class ProjectUserInline(InlineActionsMixin, admin.TabularInline):
    model = ProjectUser
    extra = 0

    #readonly_fields = ['invite_button']
    #fields = ('user', 'projectUserTitle', 'team', 'shGroup', 'invite_button')
    inline_actions = ['send_invite']

    def send_invite(self, request, obj, parent_obj=None):
        obj.save()
        messages.info(request, 'Email invitation has been sent.')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(ProjectUserInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ['user', 'team', 'shGroup']:
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False

        return formfield

class DriverInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Driver
    extra = 0

    template = "admin/survey/edit_inline/driver_tabular.html"

class AMQuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = AMQuestion
    extra = 0

    template = "admin/survey/edit_inline/amq_tabular.html"

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(AMQuestionInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ['driver', 'controlType', 'shGroup', 'option', 'skipOption']:
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False

        return formfield

class AOQuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = AOQuestion
    extra = 0

    template = "admin/survey/edit_inline/aoq_tabular.html"

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(AOQuestionInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ['driver', 'controlType', 'shGroup', 'option', 'skipOption']:
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False

        return formfield

class SHGroupInline(admin.TabularInline):
    model = SHGroup
    extra = 0

class SHCategoryInline(admin.TabularInline):
    model = SHCategory
    extra = 0

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

class SurveyAdmin(InlineActionsModelAdminMixin, admin.ModelAdmin):
    list_display = ['id', 'surveyTitle', 'get_client', 'project']
    search_fields = ['surveyTitle', 'project']
    list_filter = ['project', 'surveyTitle']
    exclude = ['isStandard']
    object_id = None

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.object_id = obj.id
            self.inlines = [
                ProjectUserInline,
                DriverInline,
                AMQuestionInline,
                AOQuestionInline,
                SHGroupInline,
                SHCategoryInline,
                ConfigPageInline
            ]
        return super(SurveyAdmin, self).get_form(request, obj, **kwargs)

    # def change_view(self, request, object_id, form_url='', extra_context=None):

    #     # self.object_id = object_id
    #     self.inlines = [
    #         ProjectUserInline,
    #         DriverInline,
    #         AMQuestionInline,
    #         AOQuestionInline,
    #         SHGroupInline,
    #         SHCategoryInline,
    #         ConfigPageInline
    #     ]

    #     return super(SurveyAdmin, self).change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = []
        return super(SurveyAdmin, self).add_view(request)

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
        ]
        return my_urls + urls

    def reset_driver(self, request):
        current_survey_id = self.object_id

        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)

                if current_survey.id != std_survey.id:
                    AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    AOQuestion.objects.filter(survey_id=current_survey.id).delete()
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
                                                longForm=std_amq[j].longForm)
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
                                                longForm=std_aoq[k].longForm)
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
        current_survey_id = self.object_id
        
        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)
                
                if current_survey.id != std_survey.id:
                    AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    # AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    # Driver.objects.filter(survey_id=current_survey.id).delete()
                    
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
                                                longForm=std_amq[j].longForm)
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
        current_survey_id = self.object_id
        
        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)
                
                if current_survey.id != std_survey.id:
                    AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    # AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    # Driver.objects.filter(survey_id=current_survey.id).delete()
                    
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
                                                longForm=True)
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
        current_survey_id = self.object_id
        
        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)
                
                if current_survey.id != std_survey.id:
                    AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    # AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    # Driver.objects.filter(survey_id=current_survey.id).delete()
                    
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
                                                longForm=False)
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
        current_survey_id = self.object_id
        
        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)

                if current_survey.id != std_survey.id:
                    # AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    # Driver.objects.filter(survey_id=current_survey.id).delete()
                    
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
                                                longForm=std_aoq[k].longForm)
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
        current_survey_id = self.object_id
        
        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)

                if current_survey.id != std_survey.id:
                    # AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    # Driver.objects.filter(survey_id=current_survey.id).delete()
                    
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
                                                longForm=True)
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
        current_survey_id = self.object_id
        
        try:
            current_survey = Survey.objects.get(id=current_survey_id)
            try:
                std_survey = Survey.objects.get(isStandard=True)

                if current_survey.id != std_survey.id:
                    # AMQuestion.objects.filter(survey_id=current_survey.id).delete()
                    AOQuestion.objects.filter(survey_id=current_survey.id).delete()
                    # Driver.objects.filter(survey_id=current_survey.id).delete()
                    
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
                                                longForm=False)
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
admin.site.register(NikelMobilePage, NikelMobilePageAdmin)