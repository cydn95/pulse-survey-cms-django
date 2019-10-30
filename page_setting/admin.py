from django.contrib import admin
from .models import PageSetting, ExtendedPage
from aboutme.models import PageAMQuestion
from aboutothers.models import PageAOQuestion
from cms.admin.pageadmin import PageAdmin
from cms.models.pagemodel import Page
from jet.admin import CompactInline

class ExtendedPageAdmin(admin.StackedInline):
    model = ExtendedPage
    can_delete = False

PageAdmin.inlines.append(ExtendedPageAdmin)
try:
    admin.site.unregister(Page)
except:
    pass
admin.site.register(Page, PageAdmin)

class AMQuestionInline(admin.StackedInline):
# class AMQuestionInline(admin.StackedInline):
    model = PageAMQuestion
    extra = 0

    #max_num = 5

class AOQuestionInline(admin.StackedInline):
    model = PageAOQuestion
    extra = 0
    #max_num = 5

class PageSettingAdmin(admin.ModelAdmin):
    #fields = ['page', 'pageType']
    readonly_fields = []
    
    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ['page']
        return self.readonly_fields

    fieldsets = [
        (None, {'fields': ('page', 'pageType')}),
    ]

    inlines = [AMQuestionInline, AOQuestionInline]

    list_display = ('page', 'pageType')

admin.site.register(PageSetting, PageSettingAdmin)
