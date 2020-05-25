from rest_framework import serializers
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES
from django.contrib.auth.models import User
from page_setting.models import PageSetting, PageType
from cms.models import Page, Title
from aboutme.models import PageAMQuestion, AMQuestion, AMResponse, AMResponseTopic
from aboutothers.models import PageAOQuestion, AOQuestion, AOResponse, AOResponseTopic, AOPage
from page_nav.models import PageNav
from team.models import Team
from shgroup.models import SHGroup, ProjectUser, MyMapLayout, ProjectMapLayout, SHCategory, SHMapping
from option.models import Option, SkipOption
from organization.models import Organization, UserAvatar, UserTeam, UserTitle
from survey.models import Driver, Project, Survey, ProjectVideoUpload, Client, ConfigPage, NikelMobilePage
from rest_framework.authtoken.models import Token

class EnumField(serializers.ChoiceField):
    def __init__(self, enum, **kwargs):
        self.enum = enum
        kwargs['choices'] = [(e.name, e.name) for e in enum]
        super(EnumField, self).__init__(**kwargs)
    
    def to_representation(self, obj):
        return obj.name
    
    def to_internal_value(self, data):
        try:
            return self.enum[data]
        except KeyError:
            self.fail('invalid_choice', input=data)

class OrganizationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Organization
        fields = '__all__'

class UserAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAvatar
        fields = '__all__'

class UserTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTeam
        fields = '__all__'

class UserTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTitle
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    #snippets = serializers.HyperlinkedRelatedField(many=True, view_name='snippet-detail', read_only=True)
    organization = OrganizationSerializer()
    avatar = UserAvatarSerializer()
    userteam = UserTeamSerializer()
    usertitle = UserTitleSerializer()

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'last_login', 'first_name', 'last_name', 'email', 'is_superuser', 'is_staff', 'is_active', 'snippets', 'organization', 'avatar', 'userteam', 'usertitle']


# class SnippetSerializer(serializers.HyperlinkedModelSerializer):
#     owner = serializers.ReadOnlyField(source='owner.username')
#     highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format='html')

#     class Meta:
#         model = Snippet
#         fields = ['url', 'id', 'highlight', 'owner', 'title', 'code', 'linenos', 'language', 'style']

class AMResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMResponse
        fields = '__all__'

class AMResponseTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMResponseTopic
        fields = '__all__'

class SHGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SHGroup
        fields = '__all__'

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'

class SkipOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkipOption
        fields = '__all__'

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'

class AMQuestionSerializer(serializers.ModelSerializer):
    driver = DriverSerializer()
    survey = SurveySerializer()
    class Meta:
        model = AMQuestion
        # fields = '__all__'
        fields = ['id', 'subdriver', 'questionText', 'questionSequence', 
        'sliderTextLeft', 'sliderTextRight', 'skipOptionYN',  
        'topicPrompt', 'commentPrompt', 'survey', 'driver', 'controlType', 
        'shGroup', 'option', 'skipOption']

class PageAMQuestionSerializer(serializers.ModelSerializer):
    amQuestion = AMQuestionSerializer()
    class Meta:
        model = PageAMQuestion
        fields = ['id', 'pageSetting', 'amQuestion']

class AOResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AOResponse
        fields = '__all__'

class AOResponseTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = AOResponseTopic
        fields = '__all__'

class AOQuestionSerializer(serializers.ModelSerializer):
    driver = DriverSerializer()
    survey = SurveySerializer()
    class Meta:
        model = AOQuestion
        fields = ['id', 'subdriver', 'questionText', 'questionSequence', 
        'sliderTextLeft', 'sliderTextRight', 'skipOptionYN', 
        'topicPrompt', 'commentPrompt', 'survey', 'driver', 'controlType', 
        'shGroup', 'option', 'skipOption']

class AOPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AOPage
        fields = '__all__'

class PageAOQuestionSerializer(serializers.ModelSerializer):
    aoQuestion = AOQuestionSerializer()
    class Meta:
        model = PageAOQuestion
        fields = ['id', 'pageSetting', 'aoQuestion']

class PageSettingSerializer(serializers.ModelSerializer):
    pageType = EnumField(enum=PageType)
    ampagesetting = PageAMQuestionSerializer(many=True)
    aopagesetting = PageAOQuestionSerializer(many=True)

    class Meta:
        model = PageSetting
        fields = ['url', 'page_id', 'pageType', 'ampagesetting', 'aopagesetting']

class PageOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageNav
        fields = '__all__'

class PageSerializer(serializers.ModelSerializer):
    pages = PageSettingSerializer()
    page_order = PageOrderSerializer()

    class Meta:
        model = Page
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class ProjectVideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectVideoUpload
        fields = '__all__'

class ConfigPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigPage
        fields = '__all__'

class NikelMobilePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NikelMobilePage
        fields = '__all__'
        
class ProjectByUserSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    
    class Meta:
        model = ProjectUser
        fields = ['id', 'user', 'project', 'shGroup']

class SHCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SHCategory
        fields = '__all__'

class UserByProjectSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    user = UserSerializer()
    team = TeamSerializer()
    shGroup = SHGroupSerializer()
    class Meta:
        model = ProjectUser
        fields = ['id', 'project', 'projectUserTitle', 'user', 'team', 'shGroup']

class ProjectUserSerializer(serializers.ModelSerializer):
    #project = ProjectSerializer()

    class Meta:
        model = ProjectUser
        fields = '__all__'

class MyMapLayoutStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyMapLayout
        fields = ['id', 'user', 'project', 'projectUser', 'layout_json']

    
class ProjectMapLayoutStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMapLayout
        fields = ['id', 'user', 'project', 'projectUser', 'layout_json']

class StakeHolderUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class StakeHolderSerializer(serializers.ModelSerializer):
    user = StakeHolderUserSerializer(required=True)

    class Meta:
        model = Organization
        fields = ['id', 'user', 'name']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = StakeHolderUserSerializer.create(StakeHolderUserSerializer(), validated_data=user_data)
        #Token.objects.create(user=user)
        stakeHolder, created = Organization.objects.update_or_create(user=user, name=validated_data.pop('name'))
        return stakeHolder

class SHMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SHMapping
        # fields = '__all__'
        fields = ['shCategory', 'projectUser', 'subProjectUser', 'relationshipStatus']