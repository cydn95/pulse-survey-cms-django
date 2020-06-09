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

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.object_id = object_id
        return super(SurveyAdmin, self).change_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'resetdriver/', self.reset_driver),
            url(r'resetamq/', self.reset_amq),
            url(r'resetaoq/', self.reset_aoq),
        ]
        return my_urls + urls

    def reset_driver(self, request):
        print(self.object_id)

        # get superuser ids
        superusers = User.objects.filter(is_superuser=True).values('id')
        survey_ids = []

        for i in range(len(superusers)):
            items = ProjectUser.objects.filter(user_id=superusers[i]['id']).values('survey')
            for j in range(len(items)):
                if items[j]['survey'] not in survey_ids:
                    survey_ids.append(items[j]['survey'])

        std_drivers = []
        for k in range(len(survey_ids)):
            items = Driver.objects.filter(survey_id=survey_ids[k]).values()
            for l in range(len(items)):
                if items[l] not in std_drivers:
                    std_drivers.append(items[l])
        
        for i in range(len(std_drivers)):
            if (self.object_id != std_drivers[i]['survey_id']):
                obj = Driver(driverName=std_drivers[i]['driverName'],
                        iconPath=std_drivers[i]['iconPath'],
                        driveOrder=std_drivers[i]['driveOrder'],
                        survey_id=self.object_id)
                obj.save()

                driver_amqs = AMQuestion.objects.filter(driver_id=std_drivers[i]['id'], survey_id=std_drivers[i]['survey_id']).values()
                print(driver_amqs)
                for j in range(len(driver_amqs)):
                    amqshgroup = AMQuestionSHGroup.objects.filter(amQuestion_id=driver_amqs[j]['id']).values()
                    amqoption = AMQuestionOption.objects.filter(amQuestion_id=driver_amqs[j]['id']).values()
                    amqskipoption = AMQuestionSkipOption.objects.filter(amQuestion_id=driver_amqs[j]['id']).values()

                    obj1 = AMQuestion(survey_id=self.object_id,
                                        driver_id=obj.id, subdriver=driver_amqs[j]['subdriver'],
                                        questionText=driver_amqs[j]['questionText'],
                                        controlType_id=driver_amqs[j]['controlType_id'],
                                        questionSequence=driver_amqs[j]['questionSequence'],
                                        sliderTextLeft=driver_amqs[j]['sliderTextLeft'],
                                        sliderTextRight=driver_amqs[j]['sliderTextRight'],
                                        skipOptionYN=driver_amqs[j]['skipOptionYN'],
                                        topicPrompt=driver_amqs[j]['topicPrompt'],
                                        commentPrompt=driver_amqs[j]['commentPrompt'],
                                        # shGroup=driver_amqs[j]['shGroup'],
                                        # option=driver_amqs[j]['option'],
                                        # skipOption=driver_amqs[j]['skipOption'],
                                        amqOrder=driver_amqs[j]['amqOrder'],
                                        shortForm=driver_amqs[j]['shortForm'],
                                        longForm=driver_amqs[j]['longForm'])
                    obj1.save()

                    for a in range(len(amqshgroup)):
                        o_shgroup = AMQuestionSHGroup(shGroup_id=amqshgroup[a]['shgroup_id'], amQuestion_id=obj1.id)
                        o_shgroup.save()
                    for b in range(len(amqoption)):
                        o_option = AMQuestionOption(option_id=amqoption[b]['option_id'], amQuestion_id=obj1.id)
                        o_option.save()
                    for c in range(len(amqskipoption)):
                        o_skipoption = AMQuestionSkipOption(skipOption_id=amqskipoption[c]['skipoption_id'], amQuestion_id=obj1.id)
                        o_skipoption.save()

                driver_aoqs = AOQuestion.objects.filter(driver_id=std_drivers[i]['id'], survey_id=std_drivers[i]['survey_id']).values()
                for k in range(len(driver_aoqs)):
                    aoqshgroup = AOQuestionSHGroup.objects.filter(aoQuestion_id=driver_aoqs[k]['id']).values()
                    aoqoption = AOQuestionOption.objects.filter(aoQuestion_id=driver_aoqs[k]['id']).values()
                    aoqskipoption = AOQuestionSkipOption.objects.filter(aoQuestion_id=driver_aoqs[k]['id']).values()

                    obj2 = AOQuestion(survey_id=self.object_id,
                                        driver_id=obj.id, subdriver=driver_aoqs[k]['subdriver'],
                                        questionText=driver_aoqs[k]['questionText'],
                                        controlType_id=driver_aoqs[k]['controlType_id'],
                                        questionSequence=driver_aoqs[k]['questionSequence'],
                                        sliderTextLeft=driver_aoqs[k]['sliderTextLeft'],
                                        sliderTextRight=driver_aoqs[k]['sliderTextRight'],
                                        skipOptionYN=driver_aoqs[k]['skipOptionYN'],
                                        topicPrompt=driver_aoqs[k]['topicPrompt'],
                                        commentPrompt=driver_aoqs[k]['commentPrompt'],
                                        # shGroup=driver_aoqs[k]['shGroup'],
                                        # option=driver_aoqs[k]['option'],
                                        # skipOption=driver_aoqs[k]['skipOption'],
                                        amqOrder=driver_aoqs[k]['amqOrder'],
                                        shortForm=driver_aoqs[k]['shortForm'],
                                        longForm=driver_aoqs[k]['longForm'])
                    obj2.save()

                    for a in range(len(aoqshgroup)):
                        o_shgroup = AOQuestionSHGroup(shGroup_id=aoqshgroup[a]['shgroup_id'], amQuestion_id=obj2.id)
                        o_shgroup.save()
                    for b in range(len(aoqoption)):
                        o_option = AOQuestionOption(option_id=aoqoption[b]['option_id'], amQuestion_id=obj2.id)
                        o_option.save()
                    for c in range(len(aoqskipoption)):
                        o_skipoption = AOQuestionSkipOption(skipOption_id=aoqskipoption[c]['skipoption_id'], amQuestion_id=obj2.id)
                        o_skipoption.save()

        messages.success(request, 'Driver has been reset.')
        return HttpResponseRedirect("../#/tab/inline_1/")

    def reset_amq(self, request):
        # get superuser ids
        superusers = User.objects.filter(is_superuser=True).values('id')
        survey_ids = []

        for i in range(len(superusers)):
            items = ProjectUser.objects.filter(user_id=superusers[i]['id']).values('survey')
            for j in range(len(items)):
                if items[j]['survey'] not in survey_ids:
                    survey_ids.append(items[j]['survey'])

        std_drivers = []
        for k in range(len(survey_ids)):
            items = Driver.objects.filter(survey_id=survey_ids[k]).values()
            for l in range(len(items)):
                if items[l] not in std_drivers:
                    std_drivers.append(items[l])
        
        for i in range(len(std_drivers)):
            if (self.object_id != std_drivers[i]['survey_id']):
                obj = Driver(driverName=std_drivers[i]['driverName'],
                        iconPath=std_drivers[i]['iconPath'],
                        driveOrder=std_drivers[i]['driveOrder'],
                        survey_id=self.object_id)
                obj.save()

                driver_amqs = AMQuestion.objects.filter(driver_id=std_drivers[i]['id'], survey_id=std_drivers[i]['survey_id']).values()
                print(driver_amqs)
                for j in range(len(driver_amqs)):
                    amqshgroup = AMQuestionSHGroup.objects.filter(amQuestion_id=driver_amqs[j]['id']).values()
                    amqoption = AMQuestionOption.objects.filter(amQuestion_id=driver_amqs[j]['id']).values()
                    amqskipoption = AMQuestionSkipOption.objects.filter(amQuestion_id=driver_amqs[j]['id']).values()

                    obj1 = AMQuestion(survey_id=self.object_id,
                                        driver_id=obj.id, subdriver=driver_amqs[j]['subdriver'],
                                        questionText=driver_amqs[j]['questionText'],
                                        controlType_id=driver_amqs[j]['controlType_id'],
                                        questionSequence=driver_amqs[j]['questionSequence'],
                                        sliderTextLeft=driver_amqs[j]['sliderTextLeft'],
                                        sliderTextRight=driver_amqs[j]['sliderTextRight'],
                                        skipOptionYN=driver_amqs[j]['skipOptionYN'],
                                        topicPrompt=driver_amqs[j]['topicPrompt'],
                                        commentPrompt=driver_amqs[j]['commentPrompt'],
                                        # shGroup=driver_amqs[j]['shGroup'],
                                        # option=driver_amqs[j]['option'],
                                        # skipOption=driver_amqs[j]['skipOption'],
                                        amqOrder=driver_amqs[j]['amqOrder'],
                                        shortForm=driver_amqs[j]['shortForm'],
                                        longForm=driver_amqs[j]['longForm'])
                    obj1.save()

                    for a in range(len(amqshgroup)):
                        o_shgroup = AMQuestionSHGroup(shGroup_id=amqshgroup[a]['shgroup_id'], amQuestion_id=obj1.id)
                        o_shgroup.save()
                    for b in range(len(amqoption)):
                        o_option = AMQuestionOption(option_id=amqoption[b]['option_id'], amQuestion_id=obj1.id)
                        o_option.save()
                    for c in range(len(amqskipoption)):
                        o_skipoption = AMQuestionSkipOption(skipOption_id=amqskipoption[c]['skipoption_id'], amQuestion_id=obj1.id)
                        o_skipoption.save()

        messages.success(request, 'AM Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_2/")

    def reset_aoq(self, request):
        # get superuser ids
        superusers = User.objects.filter(is_superuser=True).values('id')
        survey_ids = []

        for i in range(len(superusers)):
            items = ProjectUser.objects.filter(user_id=superusers[i]['id']).values('survey')
            for j in range(len(items)):
                if items[j]['survey'] not in survey_ids:
                    survey_ids.append(items[j]['survey'])

        std_drivers = []
        for k in range(len(survey_ids)):
            items = Driver.objects.filter(survey_id=survey_ids[k]).values()
            for l in range(len(items)):
                if items[l] not in std_drivers:
                    std_drivers.append(items[l])
        
        for i in range(len(std_drivers)):
            if (self.object_id != std_drivers[i]['survey_id']):
                obj = Driver(driverName=std_drivers[i]['driverName'],
                        iconPath=std_drivers[i]['iconPath'],
                        driveOrder=std_drivers[i]['driveOrder'],
                        survey_id=self.object_id)
                obj.save()

                driver_aoqs = AOQuestion.objects.filter(driver_id=std_drivers[i]['id'], survey_id=std_drivers[i]['survey_id']).values()
                for k in range(len(driver_aoqs)):
                    aoqshgroup = AOQuestionSHGroup.objects.filter(aoQuestion_id=driver_aoqs[k]['id']).values()
                    aoqoption = AOQuestionOption.objects.filter(aoQuestion_id=driver_aoqs[k]['id']).values()
                    aoqskipoption = AOQuestionSkipOption.objects.filter(aoQuestion_id=driver_aoqs[k]['id']).values()

                    obj2 = AOQuestion(survey_id=self.object_id,
                                        driver_id=obj.id, subdriver=driver_aoqs[k]['subdriver'],
                                        questionText=driver_aoqs[k]['questionText'],
                                        controlType_id=driver_aoqs[k]['controlType_id'],
                                        questionSequence=driver_aoqs[k]['questionSequence'],
                                        sliderTextLeft=driver_aoqs[k]['sliderTextLeft'],
                                        sliderTextRight=driver_aoqs[k]['sliderTextRight'],
                                        skipOptionYN=driver_aoqs[k]['skipOptionYN'],
                                        topicPrompt=driver_aoqs[k]['topicPrompt'],
                                        commentPrompt=driver_aoqs[k]['commentPrompt'],
                                        # shGroup=driver_aoqs[k]['shGroup'],
                                        # option=driver_aoqs[k]['option'],
                                        # skipOption=driver_aoqs[k]['skipOption'],
                                        amqOrder=driver_aoqs[k]['amqOrder'],
                                        shortForm=driver_aoqs[k]['shortForm'],
                                        longForm=driver_aoqs[k]['longForm'])
                    obj2.save()

                    for a in range(len(aoqshgroup)):
                        o_shgroup = AOQuestionSHGroup(shGroup_id=aoqshgroup[a]['shgroup_id'], amQuestion_id=obj2.id)
                        o_shgroup.save()
                    for b in range(len(aoqoption)):
                        o_option = AOQuestionOption(option_id=aoqoption[b]['option_id'], amQuestion_id=obj2.id)
                        o_option.save()
                    for c in range(len(aoqskipoption)):
                        o_skipoption = AOQuestionSkipOption(skipOption_id=aoqskipoption[c]['skipoption_id'], amQuestion_id=obj2.id)
                        o_skipoption.save()

        messages.success(request, 'AO Question has been reset.')
        return HttpResponseRedirect("../#/tab/inline_3/")

    def get_client(self, obj):
        return obj.project.client
    get_client.short_description = 'Client'
    get_client.admin_order_field = 'project__client'

    inlines = [
        ProjectUserInline,
        DriverInline,
        AMQuestionInline,
        AOQuestionInline,
        SHGroupInline,
        SHCategoryInline,
        ConfigPageInline
    ]

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
    list_display = ['pageOrder', 'survey', 'pageName', 'pageText']
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