from rest_framework import serializers
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES
from django.contrib.auth.models import User
from page_setting.models import PageSetting, PageType
from cms.models import Page, Title
from aboutme.models import AMResponseAcknowledgement, PageAMQuestion, AMQuestion, AMResponse, AMResponseTopic
from aboutothers.models import AOResponseAcknowledgement, PageAOQuestion, AOQuestion, AOResponse, AOResponseTopic, AOPage
from page_nav.models import PageNav
from team.models import Team
from shgroup.models import KeyThemeUpDownVote, SHGroup, SHType, ProjectUser, MyMapLayout, ProjectMapLayout, SHCategory, SHMapping, Segment
from option.models import Option, SkipOption
from organization.models import Organization, UserAvatar, UserTeam, UserTitle, UserGuideMode
from survey.models import ToolTipGuide, Driver, Project, Survey, ProjectVideoUpload, Client, ConfigPage, NikelMobilePage
from rest_framework.authtoken.models import Token
from drf_writable_nested.serializers import WritableNestedModelSerializer

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

class UserGuideModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGuideMode
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    avatar = UserAvatarSerializer()
    userteam = UserTeamSerializer()
    usertitle = UserTitleSerializer()
    guidemode = UserGuideModeSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'last_login', 'first_name', 'last_name', 'email', 'is_superuser',
                  'is_staff', 'is_active', 'snippets', 'organization', 'avatar', 'userteam', 'usertitle', 'guidemode']
        
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

class DriverSubDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'driverName', 'survey']

class AMQuestionSubDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMQuestion
        fields = ['subdriver']

class AOQuestionSubDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = AOQuestion
        fields = ['subdriver']
        
class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'

class AMQuestionSerializer(serializers.ModelSerializer):
    driver = DriverSerializer()
    survey = SurveySerializer()
    class Meta:
        model = AMQuestion
        fields = ['id', 'subdriver', 'questionText', 'questionSequence', 
        'sliderTextLeft', 'sliderTextRight', 'skipOptionYN',  
        'topicPrompt', 'commentPrompt', 'survey', 'driver', 'controlType', 
        'shGroup', 'option', 'skipOption', 'amqOrder']

class AMQuestionSerializerForReport(serializers.ModelSerializer):
    driver = DriverSerializer()
    # survey = SurveySerializer()
    class Meta:
        model = AMQuestion
        fields = ['id', 'subdriver', 'questionText', 'questionSequence', 
        'sliderTextLeft', 'sliderTextRight', 'skipOptionYN',  
        'topicPrompt', 'commentPrompt', 'survey', 'driver', 'controlType', 
        'shGroup', 'option', 'skipOption', 'amqOrder']
                 
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
                  'shGroup', 'option', 'skipOption', 'aoqOrder']

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

class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = '__all__'

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'   

class SHTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SHType
        fields = '__all__'
        
class SurveyByUserSerializer(serializers.ModelSerializer):
    survey = SurveySerializer()
    shType = SHTypeSerializer()

    class Meta:
        model = ProjectUser
        fields = ['id', 'user', 'survey', 'shGroup',
                  'projectOrganization', 'shType', 'projectAdmin']

class SHCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SHCategory
        fields = '__all__'

class ProjectUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectUser
        fields = '__all__'

class ProjectUserSerializerForFlag(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ProjectUser
        fields = ['user', 'id']

class ProjectUserForUserAdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ProjectUser

        fields = ['id', 'user']

class UserBySurveySerializer(serializers.ModelSerializer):
    survey = SurveySerializer()
    user = UserSerializer()
    team = TeamSerializer()
    shGroup = SHGroupSerializer()
    shType = SHTypeSerializer()
    addByProjectUser = ProjectUserForUserAdminSerializer()

    class Meta:
        model = ProjectUser

        # commented for isteammember
        # fields = ['id', 'survey', 'projectUserTitle', 'user', 'team', 'shGroup', 'sendInvite', 'isSuperUser', 'isTeamMember', 'isCGroup1', 'isCGroup2', 'isCGroup3']
        fields = ['id', 'survey', 'projectUserTitle', 'projectUserRoleDesc', 'user', 'team', 'shGroup',
                  'sendInvite', 'sendEmail', 'isSuperUser', 'isCGroup1', 'isCGroup2', 'isCGroup3', 'projectOrganization', 'shType', 'projectAdmin', 'addByProjectUser', 'created_at', 'updated_at']

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

        stakeHolder, created = Organization.objects.update_or_create(user=user, name=validated_data.pop('name'))
        
        return stakeHolder

class SHMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SHMapping
        fields = ['shCategory', 'projectUser', 'subProjectUser', 'relationshipStatus']

class NikelMobilePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NikelMobilePage
        fields = '__all__'

# class NikelMobilePageCustomSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = NikelMobilePage
#         fields = ['id', 'pageName', 'pageText', 'backgroundColor', 'pageContent', 'pageOrder', 'survey_id', 'img']

class ToolTipGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolTipGuide
        fields = '__all__'

class ProjectUserForAdvisorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    team = TeamSerializer()
    shGroup = SHGroupSerializer()
    shType = SHTypeSerializer()

    class Meta:
        model = ProjectUser

        # commented for isteammember
        # fields = ['id', 'user', 'team', 'shGroup', 'isTeamMember', 'isCGroup1', 'isCGroup2', 'isCGroup3']
        fields = ['id', 'user', 'team', 'shGroup',
                  'projectOrganization', 'isCGroup1', 'isCGroup2', 'isCGroup3', 'shType']

class ProjectUserForReportSerializer(serializers.ModelSerializer):
    team = TeamSerializer()
    shGroup = SHGroupSerializer()
    shType = SHTypeSerializer()

    class Meta:
        model = ProjectUser

        # commented for isteammember
        # fields = ['id', 'user', 'team', 'shGroup', 'isTeamMember', 'isCGroup1', 'isCGroup2', 'isCGroup3']
        fields = ['id', 'user', 'team', 'shGroup',
                  'projectOrganization', 'isCGroup1', 'isCGroup2', 'isCGroup3', 'shType']


class AMResponseForDriverAnalysisSerializer(serializers.ModelSerializer):
    # projectUser = ProjectUserForReportSerializer()
    subProjectUser = ProjectUserForReportSerializer()
    amQuestion = AMQuestionSerializer()

    class Meta:
        model = AMResponse

        fields = ['id', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'created_at', 'updated_at',
                  'projectUser', 'subProjectUser', 'survey', 'project', 'amQuestion', 'latestResponse']

class AMResponseForSummarySerializer(serializers.ModelSerializer):
    subProjectUser = ProjectUserForReportSerializer()
    amQuestion = AMQuestionSerializerForReport()

    class Meta:
        model = AMResponse
        fields = ['id', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'created_at', 'updated_at',
                  'projectUser', 'subProjectUser', 'survey', 'project', 'amQuestion', 'latestResponse']
    
class AOResponseForDriverAnalysisSerializer(serializers.ModelSerializer):
    # projectUser = ProjectUserForReportSerializer()
    subProjectUser = ProjectUserForReportSerializer()
    aoQuestion = AOQuestionSerializer()

    class Meta:
        model = AOResponse

        fields = ['id', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'created_at', 'updated_at',
                  'projectUser', 'subProjectUser', 'survey', 'project', 'aoQuestion', 'latestResponse']

class AMResponseForReportSerializer(serializers.ModelSerializer):
    subProjectUser = ProjectUserForReportSerializer()

    class Meta:
        model = AMResponse
        fields = ['id', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'created_at', 'updated_at',
                  'projectUser', 'subProjectUser', 'survey', 'project', 'amQuestion', 'latestResponse']

class AOResponseForReportSerializer(serializers.ModelSerializer):
    subProjectUser = ProjectUserForReportSerializer()

    class Meta:
        model = AOResponse
        fields = ['id', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'created_at', 'updated_at',
                  'projectUser', 'subProjectUser', 'survey', 'project', 'aoQuestion', 'latestResponse']

class AOResponseTopPositiveNegativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AOResponse
        fields = '__all__'

class AMResponseForAdvisorSerializer(serializers.ModelSerializer):
    projectUser = ProjectUserForReportSerializer()
    # subProjectUser = ProjectUserForReportSerializer()

    class Meta:
        model = AMResponse
        fields = ['controlType', 'integerValue', 'topicValue', 'commentValue', 'created_at', 'updated_at',
                  'projectUser', 'subProjectUser', 'survey', 'project', 'amQuestion', 'latestResponse']

class AOResponseForMatrixSerializer(serializers.ModelSerializer):
    projectUser = ProjectUserForAdvisorSerializer()
    # subProjectUser = ProjectUserForAdvisorSerializer()

    class Meta:
        model = AOResponse
        fields = ['controlType', 'integerValue', 'topicValue', 'commentValue', 'created_at', 'updated_at',
                  'projectUser', 'subProjectUser', 'survey', 'project', 'aoQuestion', 'latestResponse']

class AMResponseForBubbleChartSerializer(serializers.ModelSerializer):
    amQuestion = AMQuestionSerializer()

    class Meta:
        model = AMResponse
        fields = ['id', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags',
                  'commentTags', 'created_at', 'updated_at', 'projectUser', 'subProjectUser', 'survey', 'project', 'amQuestion', 'latestResponse']


class AOResponseForBubbleChartSerializer(serializers.ModelSerializer):
    aoQuestion = AOQuestionSerializer()

    class Meta:
        model = AOResponse
        fields = ['id', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags',
                  'commentTags', 'created_at', 'updated_at', 'projectUser', 'subProjectUser', 'survey', 'project', 'aoQuestion', 'latestResponse']


class AOResponseAcknowledgementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AOResponseAcknowledgement
        fields = '__all__'


class AMResponseAcknowledgementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMResponseAcknowledgement
        fields = '__all__'

class AMResponseAcknowledgementSerializerForFlag(serializers.ModelSerializer):
    amResponse = AMResponseSerializer()
    projectUser = ProjectUserSerializerForFlag()

    class Meta:
        model = AMResponseAcknowledgement
        fields = ['id', 'flagStatus', 'amResponse', 'updated_at', 'projectUser']

class KeyThemeUpDownVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyThemeUpDownVote
        fields = '__all__'