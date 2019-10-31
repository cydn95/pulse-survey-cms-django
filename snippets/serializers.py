from rest_framework import serializers
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES
from django.contrib.auth.models import User
from page_setting.models import PageSetting, PageType
from cms.models import Page, Title
from aboutme.models import AMQuestion, AMResponse, AMResponseTopic
from aboutothers.models import AOQuestion, AOResponse, AOResponseTopic, AOPage
from page_nav.models import PageNav

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

class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(many=True, view_name='snippet-detail', read_only=True)

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'last_login', 'first_name', 'last_name', 'email', 'is_superuser', 'is_staff', 'is_active', 'snippets']

class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format='html')

    class Meta:
        model = Snippet
        fields = ['url', 'id', 'highlight', 'owner', 'title', 'code', 'linenos', 'language', 'style']

class AMResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMResponse
        fields = '__all__'

class AMResponseTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMResponseTopic
        fields = '__all__'

class AMQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMQuestion
        fields = '__all__'

class AOResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AOResponse
        fields = '__all__'

class AOResponseTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = AOResponseTopic
        fields = '__all__'

class AOPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AOPage
        fields = '__all__'

class AOQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AOQuestion
        fields = '__all__'

class PageSettingSerializer(serializers.ModelSerializer):
    pageType = EnumField(enum=PageType)
    ampagesetting = AMQuestionSerializer(many=True)
    aopagesetting = AOQuestionSerializer(many=True)

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
