import os
from pathlib import Path
from email.mime.image import MIMEImage

from snippets.models import Snippet
from snippets.serializers import NikelMobilePageSerializer, ConfigPageSerializer, UserAvatarSerializer, SHMappingSerializer, ProjectVideoUploadSerializer, AMQuestionSerializer, AOQuestionSerializer, StakeHolderSerializer, SHCategorySerializer, MyMapLayoutStoreSerializer, ProjectMapLayoutStoreSerializer, UserByProjectSerializer, ProjectByUserSerializer, SkipOptionSerializer, DriverSerializer, AOQuestionSerializer, OrganizationSerializer, OptionSerializer, ProjectUserSerializer, SHGroupSerializer, UserSerializer, PageSettingSerializer, PageSerializer, AMResponseSerializer, AMResponseTopicSerializer, AOResponseSerializer, AOResponseTopicSerializer, AOPageSerializer, TeamSerializer
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from snippets.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import viewsets
from page_setting.models import PageSetting
from cms.models import Page
from aboutme.models import AMQuestion, AMResponse, AMResponseTopic
from aboutothers.models import AOResponse, AOResponseTopic, AOPage
from team.models import Team
from shgroup.models import SHGroup, ProjectUser, MyMapLayout, ProjectMapLayout, SHCategory, SHMapping
from option.models import Option, SkipOption
from rest_framework import status
from organization.models import Organization, UserAvatar, UserTeam
from aboutothers.models import AOQuestion
from survey.models import Driver, Project, ProjectVideoUpload, ConfigPage, NikelMobilePage
from rest_framework.views import APIView
from django.forms.models import model_to_dict

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import filters

from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.conf import settings

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'id': token.user_id})
 
#class UserViewSet(viewsets.ReadOnlyModelViewSet):
class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()
    serializer_class = UserSerializer

# class SnippetViewSet(viewsets.ModelViewSet):
#     """
#     This viewset automatically provides `list`, `create`, `retrieve`,
#     `update` and `destroy` actions.

#     Additionally we also provide an extra `highlight` action.
#     """
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#     permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    
#     @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
#     def highlight(self, request, *args, **kwargs):
#         snippet = self.get_object()
#         return Response(snippet.highlighted)

#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)

class PageSettingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = PageSetting.objects.all()
    serializer_class = PageSettingSerializer

# working now v1
# class PageViewSet(viewsets.ReadOnlyModelViewSet):
#     permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
#     queryset = Page.objects.all()
#     serializer_class = PageSerializer

#     def list(self, request, *kwargs):
#         serializer = self.get_serializer(self.get_queryset(), many=True)
#         temp = serializer.data
#         drivers = Driver.objects.all().values()
#         list_drivers = [entry for entry in drivers]
#         survey_param = ''

#         t_survey_param = self.request.GET.get('survey')
#         if t_survey_param:
#             survey_param = int(t_survey_param)

#         for i in range(len(temp)):

#             if temp[i]['pages'] is not None:
#                 temp[i]['pages'] = {}
#                 temp[i]['pages']['driver'] = list_drivers

#                 for j in range(len(list_drivers)):
#                     if survey_param and isinstance(survey_param, int):
                        
#                         amquestion = AMQuestion.objects.filter(driver_id=list_drivers[j]['id'], survey_id=survey_param).values()
#                         list_amquestion = [entry1 for entry1 in amquestion]
#                         temp[i]['pages']['driver'][j]['amquestion'] = list_amquestion

#                         aoquestion = AOQuestion.objects.filter(driver_id=list_drivers[j]['id'], survey_id=survey_param).values()
#                         list_aoquestion = [entry2 for entry2 in aoquestion]
#                         temp[i]['pages']['driver'][j]['aoquestion'] = list_aoquestion
#                     else:
#                         amquestion = AMQuestion.objects.filter(driver_id=list_drivers[j]['id']).values()
#                         list_amquestion = [entry1 for entry1 in amquestion]
#                         temp[i]['pages']['driver'][j]['amquestion'] = list_amquestion

#                         aoquestion = AOQuestion.objects.filter(driver_id=list_drivers[j]['id']).values()
#                         list_aoquestion = [entry2 for entry2 in aoquestion]
#                         temp[i]['pages']['driver'][j]['aoquestion'] = list_aoquestion

#         return Response(temp)

# v2
class PageViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    def list(self, request, *kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        list_drivers = serializer.data
        # drivers = Driver.objects.all().values()
        # list_drivers = [entry for entry in drivers]
        survey_param = ''
        projectuser_param = ''

        t_survey_param = self.request.GET.get('survey')
        t_projectuser_param = self.request.GET.get('projectuser')

        if t_survey_param:
            survey_param = int(t_survey_param)

        if t_projectuser_param:
            projectuser_param = int(t_projectuser_param)

        for i in range(len(list_drivers)):
            if survey_param and isinstance(survey_param, int):
                
                amquestion_queryset = AMQuestion.objects.filter(driver_id=list_drivers[i]['id'], survey_id=survey_param)
                am_serializer = AMQuestionSerializer(amquestion_queryset, many=True)
                list_drivers[i]['amquestion'] = am_serializer.data

                if projectuser_param and isinstance(projectuser_param, int):
                    try:
                        projectuser = ProjectUser.objects.get(id=projectuser_param)

                        for j in range(len(list_drivers[i]['amquestion'])):
                            amresponsetopic_queryset = AMResponseTopic.objects.filter(amQuestion_id=list_drivers[i]['amquestion'][j]['id'], responseUser_id=projectuser_param)
                            amresponsetopic_serializer = AMResponseTopicSerializer(amresponsetopic_queryset, many=True)
                            list_drivers[i]['amquestion'][j]['topic'] = amresponsetopic_serializer.data
                            
                            try:
                                # 2020-05-20
                                #ret = AMResponse.objects.get(user_id=projectuser.user, survey_id=survey_param, amQuestion_id=list_drivers[i]['amquestion'][j]['id'])
                                ret = AMResponse.objects.get(projectUser_id=projectuser_param, survey_id=survey_param, amQuestion_id=list_drivers[i]['amquestion'][j]['id'])
                                list_drivers[i]['amquestion'][j]['responsestatus'] = True
                                list_drivers[i]['amquestion'][j]['response'] = model_to_dict(ret)
                            except AMResponse.DoesNotExist:
                                ret = None
                                list_drivers[i]['amquestion'][j]['responsestatus'] = False
                                list_drivers[i]['amquestion'][j]['response'] = []
                    except ProjectUser.DoesNotExist:
                        projectuser = None

                aoquestion_queryset = AOQuestion.objects.filter(driver_id=list_drivers[i]['id'], survey_id=survey_param)
                ao_serializer = AOQuestionSerializer(aoquestion_queryset, many=True)
                list_drivers[i]['aoquestion'] = ao_serializer.data

                if projectuser_param and isinstance(projectuser_param, int):
                    try:
                        projectuser = ProjectUser.objects.get(id=projectuser_param)

                        for j in range(len(list_drivers[i]['aoquestion'])):
                            aoresponsetopic_queryset = AOResponseTopic.objects.filter(aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'], responseUser_id=projectuser_param)
                            aoresponsetopic_serializer = AOResponseTopicSerializer(aoresponsetopic_queryset, many=True)
                            list_drivers[i]['aoquestion'][j]['topic'] = aoresponsetopic_serializer.data

                            try:
                                # 2020-05-20
                                # ret = AOResponse.objects.get(subjectUser_id=projectuser.user, survey_id=survey_param, aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'])
                                ret = AOResponse.objects.get(subProjectUser_id=projectuser_param, survey_id=survey_param, aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'])
                                list_drivers[i]['aoquestion'][j]['responsestatus'] = True
                                list_drivers[i]['aoquestion'][j]['response'] = model_to_dict(ret)
                            except AOResponse.DoesNotExist:
                                ret = None
                                list_drivers[i]['aoquestion'][j]['responsestatus'] = False
                                list_drivers[i]['aoquestion'][j]['response'] = []
                    except ProjectUser.DoesNotExist:
                        projectuser = None

            else:
                amquestion_queryset = AMQuestion.objects.filter(driver_id=list_drivers[i]['id'])
                am_serializer = AMQuestionSerializer(amquestion_queryset, many=True)
                list_drivers[i]['amquestion'] = am_serializer.data

                if projectuser_param and isinstance(projectuser_param, int):
                    try:
                        projectuser = ProjectUser.objects.get(id=projectuser_param)

                        for j in range(len(list_drivers[i]['amquestion'])):
                            amresponsetopic_queryset = AMResponseTopic.objects.filter(amQuestion_id=list_drivers[i]['amquestion'][j]['id'], responseUser_id=projectuser_param)
                            amresponsetopic_serializer = AMResponseTopicSerializer(amresponsetopic_queryset, many=True)
                            list_drivers[i]['amquestion'][j]['topic'] = amresponsetopic_serializer.data

                            try:
                                # 2020-05-20
                                # ret = AMResponse.objects.get(user_id=projectuser.user, survey_id=survey_param, amQuestion_id=list_drivers[i]['amquestion'][j]['id'])
                                ret = AMResponse.objects.get(projectUser_id=projectuser_param, survey_id=survey_param, amQuestion_id=list_drivers[i]['amquestion'][j]['id'])
                                list_drivers[i]['amquestion'][j]['responsestatus'] = True
                                list_drivers[i]['amquestion'][j]['response'] = model_to_dict(ret)
                            except AMResponse.DoesNotExist:
                                ret = None
                                list_drivers[i]['amquestion'][j]['responsestatus'] = False
                                list_drivers[i]['amquestion'][j]['response'] = []
                    except ProjectUser.DoesNotExist:
                        projectuser = None

                aoquestion_queryset = AOQuestion.objects.filter(driver_id=list_drivers[i]['id'])
                ao_serializer = AOQuestionSerializer(aoquestion_queryset, many=True)
                list_drivers[i]['aoquestion'] = ao_serializer.data

                if projectuser_param and isinstance(projectuser_param, int):
                    try:
                        projectuser = ProjectUser.objects.get(id=projectuser_param)

                        for j in range(len(list_drivers[i]['aoquestion'])):
                            aoresponsetopic_queryset = AOResponseTopic.objects.filter(aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'], responseUser_id=projectuser_param)
                            aoresponsetopic_serializer = AOResponseTopicSerializer(aoresponsetopic_queryset, many=True)
                            list_drivers[i]['aoquestion'][j]['topic'] = aoresponsetopic_serializer.data

                            try:
                                # 2020-05-20
                                # ret = AOResponse.objects.get(subjectUser_id=projectuser.user, survey_id=survey_param, aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'])
                                ret = AOResponse.objects.get(subProjectUser_id=projectuser_param, survey_id=survey_param, aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'])
                                list_drivers[i]['aoquestion'][j]['responsestatus'] = True
                                list_drivers[i]['aoquestion'][j]['response'] = model_to_dict(ret)
                            except AOResponse.DoesNotExist:
                                ret = None
                                list_drivers[i]['aoquestion'][j]['responsestatus'] = False
                                list_drivers[i]['aoquestion'][j]['response'] = []
                    except ProjectUser.DoesNotExist:
                        projectuser = None

        return Response(list_drivers)

class AMResponseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        
        if many == True:
            for item in data:
                defaults = item
                try:
                    # 2020-05-20
                    # obj = AMResponse.objects.get(survey_id=item['survey'], project_id=item['project'], user_id=item['user'], amQuestion_id=item['amQuestion']) 
                    obj = AMResponse.objects.get(survey_id=item['survey'], project_id=item['project'], projectUser_id=item['projectUser'], amQuestion_id=item['amQuestion']) 
                    
                    obj.integerValue = defaults['integerValue']
                    obj.topicValue = defaults['topicValue']
                    obj.commentValue = defaults['commentValue']
                    obj.skipValue = defaults['skipValue']
                    obj.topicTags = defaults['topicTags']
                    obj.commentTags = defaults['commentTags']

                    obj.save()

                except AMResponse.DoesNotExist:
                    # 2020-05-20
                    # obj = AMResponse(amQuestion_id=defaults['amQuestion'], 
                    #             user_id=defaults['user'], subjectUser_id=defaults['subjectUser'], 
                    #             survey_id=defaults['survey'], project_id=defaults['project'], 
                    #             controlType=defaults['controlType'], integerValue=defaults['integerValue'],
                    #             topicValue=defaults['topicValue'], commentValue=defaults['commentValue'],
                    #             skipValue=defaults['skipValue'], topicTags=defaults['topicTags'],
                    #             commentTags=defaults['commentTags'])
                    obj = AMResponse(amQuestion_id=defaults['amQuestion'], 
                                projectUser_id=defaults['projectUser'], subProjectUser_id=defaults['subProjectUser'], 
                                survey_id=defaults['survey'], project_id=defaults['project'], 
                                controlType=defaults['controlType'], integerValue=defaults['integerValue'],
                                topicValue=defaults['topicValue'], commentValue=defaults['commentValue'],
                                skipValue=defaults['skipValue'], topicTags=defaults['topicTags'],
                                commentTags=defaults['commentTags'])

                    obj.save()
                    
        elif many == False:
            defaults = data
            try:
                # 2020-05-20
                # obj = AMResponse.objects.get(survey_id=defaults['survey'], project_id=defaults['project'], user_id=defaults['user'], amQuestion_id=defaults['amQuestion'])
                obj = AMResponse.objects.get(survey_id=defaults['survey'], project_id=defaults['project'], projectUser_id=defaults['projectUser'], amQuestion_id=defaults['amQuestion'])
                
                obj.integerValue = defaults['integerValue']
                obj.topicValue = defaults['topicValue']
                obj.commentValue = defaults['commentValue']
                obj.skipValue = defaults['skipValue']
                obj.topicTags = defaults['topicTags']
                obj.commentTags = defaults['commentTags']

                obj.save()
            except AMResponse.DoesNotExist:

                # 2020-05-20
                # obj = AMResponse(amQuestion_id=data['amQuestion'], 
                #                 user_id=data['user'], subjectUser_id=data['subjectUser'], 
                #                 survey_id=data['survey'], project_id=data['project'], 
                #                 controlType=data['controlType'], integerValue=data['integerValue'],
                #                 topicValue=data['topicValue'], commentValue=data['commentValue'],
                #                 skipValue=data['skipValue'], topicTags=data['topicTags'],
                #                 commentTags=data['commentTags'])
                obj = AMResponse(amQuestion_id=data['amQuestion'], 
                                projectUser_id=data['projectUser'], subProjectUser_id=data['subProjectUser'], 
                                survey_id=data['survey'], project_id=data['project'], 
                                controlType=data['controlType'], integerValue=data['integerValue'],
                                topicValue=data['topicValue'], commentValue=data['commentValue'],
                                skipValue=data['skipValue'], topicTags=data['topicTags'],
                                commentTags=data['commentTags'])

                obj.save()

        # 2020-05-20
        # result = AMResponse.objects.all().values('user', 'subjectUser', 'survey', 'project', 'amQuestion', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags')
        result = AMResponse.objects.all().values('projectUser', 'subProjectUser', 'survey', 'project', 'amQuestion', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags')

        list_result = [entry for entry in result]
        
        serializer = self.get_serializer(data=list_result, many=True)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AMResponseExcelViewSet(XLSXFileMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'amresponse_export.xlsx'

class AMResponseTopicViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponseTopic.objects.all()
    serializer_class = AMResponseTopicSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AOResponseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = AOResponse.objects.all()
    serializer_class = AOResponseSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        
        if many == True:
            for item in data:
                defaults = item
                try:
                    # 2020-05-20
                    # obj = AOResponse.objects.get(survey_id=item['survey'], project_id=item['project'], user_id=item['user'], subjectUser_id=item['subjectUser'], aoQuestion_id=item['aoQuestion'])
                    obj = AOResponse.objects.get(survey_id=item['survey'], project_id=item['project'], projectUser_id=item['projectUser'], subProjectUser_id=item['subProjectUser'], aoQuestion_id=item['aoQuestion'])

                    obj.integerValue = defaults['integerValue']
                    obj.topicValue = defaults['topicValue']
                    obj.commentValue = defaults['commentValue']
                    obj.skipValue = defaults['skipValue']
                    obj.topicTags = defaults['topicTags']
                    obj.commentTags = defaults['commentTags']

                    obj.save()

                except AOResponse.DoesNotExist:
                    # 2020-05-20
                    # obj = AOResponse(aoQuestion_id=defaults['aoQuestion'],
                    #             user_id=defaults['user'], subjectUser_id=defaults['subjectUser'],
                    #             survey_id=defaults['survey'], project_id=defaults['project'],
                    #             controlType=defaults['controlType'], integerValue=defaults['integerValue'],
                    #             topicValue=defaults['topicValue'], commentValue=defaults['commentValue'],
                    #             skipValue=defaults['skipValue'], topicTags=defaults['topicTags'],
                    #             commentTags=defaults['commentTags'])
                    obj = AOResponse(aoQuestion_id=defaults['aoQuestion'],
                                projectUser_id=defaults['projectUser'], subProjectUser_id=defaults['subProjectUser'],
                                survey_id=defaults['survey'], project_id=defaults['project'],
                                controlType=defaults['controlType'], integerValue=defaults['integerValue'],
                                topicValue=defaults['topicValue'], commentValue=defaults['commentValue'],
                                skipValue=defaults['skipValue'], topicTags=defaults['topicTags'],
                                commentTags=defaults['commentTags'])
                    obj.save()
        elif many == False:
            defaults = data
            try:
                # 2020-05-20
                # obj = AOResponse.objects.get(survey_id=item['survey'], project_id=item['project'], user_id=item['user'], subjectUser_id=item['subjectUser'], aoQuestion_id=item['aoQuestion'])
                obj = AOResponse.objects.get(survey_id=item['survey'], project_id=item['project'], projectUser_id=item['projectUser'], subProjectUser_id=item['subProjectUser'], aoQuestion_id=item['aoQuestion'])

                obj.integerValue = defaults['integerValue']
                obj.topicValue = defaults['topicValue']
                obj.commentValue = defaults['commentValue']
                obj.skipValue = defaults['skipValue']
                obj.topicTags = defaults['topicTags']
                obj.commentTags = defaults['commentTags']

                obj.save()
            except AOResponse.DoesNotExist:
                # 2020-05-20
                # obj = AOResponse(aoQuestion_id=defaults['aoQuestion'],
                #             user_id=defaults['user'], subjectUser_id=defaults['subjectUser'],
                #             survey_id=defaults['survey'], project_id=defaults['project'],
                #             controlType=defaults['controlType'], integerValue=defaults['integerValue'],
                #             topicValue=defaults['topicValue'], commentValue=defaults['commentValue'],
                #             skipValue=defaults['skipValue'], topicTags=defaults['topicTags'],
                #             commentTags=defaults['commentTags'])
                obj = AOResponse(aoQuestion_id=defaults['aoQuestion'],
                            projectUser_id=defaults['projectUser'], subProjectUser_id=defaults['subProjectUser'],
                            survey_id=defaults['survey'], project_id=defaults['project'],
                            controlType=defaults['controlType'], integerValue=defaults['integerValue'],
                            topicValue=defaults['topicValue'], commentValue=defaults['commentValue'],
                            skipValue=defaults['skipValue'], topicTags=defaults['topicTags'],
                            commentTags=defaults['commentTags'])
                obj.save()
        
        # 2020-05-20
        # result = AOResponse.objects.all().values('user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags')
        result = AOResponse.objects.all().values('projectUser', 'subProjectUser', 'survey', 'project', 'aoQuestion', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags')
        
        list_result = [entry for entry in result]

        serializer = self.get_serializer(data=list_result, many=True)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AOResponseExcelViewSet(XLSXFileMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = AOResponse.objects.all()
    serializer_class = AOResponseSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'aoresponse_export.xlsx'
    
class AOResponseTopicViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = AOResponseTopic.objects.all()
    serializer_class = AOResponseTopicSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AOPageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = AOPage.objects.all()
    serializer_class = AOPageSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class TeamViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class SHGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = SHGroup.objects.all()
    serializer_class = SHGroupSerializer

    def get_queryset(self):
        queryset = SHGroup.objects.all()

        # updated project to survey   2020-05-20
        # project = self.request.query_params.get('project', None)
        # if project is not None:
        #    queryset = queryset.filter(project__id=project)
        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class OptionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

class SkipOptionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = SkipOption.objects.all()
    serializer_class = SkipOptionSerializer

class ProjectUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = ProjectUserSerializer

    def get_queryset(self):
        queryset = ProjectUser.objects.all()
        return queryset

    def update(self, request, *args, **kwargs):
        ret = super(ProjectUserViewSet, self).update(request, *args, **kwargs)

        projectUser_id = ret.data['id']

        shMyCategories = request.data['shMyCategory']
        
        MyMapLayout.objects.filter(user_id=request.user.id, project_id=request.data['project']).delete()
        obj = MyMapLayout.objects.create(user_id=request.user.id, project_id=request.data['project'])

        obj.user_id = request.user.id
        obj.project_id = request.data['project']
        obj.layout_json = ''   

        # 2020-05-20     added projectUser, subProjectUser
        # SHMapping.objects.filter(projectUser_id=projectUser_id).delete()
        myProjectUser_id = request.data['myProjectUser']
        SHMapping.objects.filter(projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id).delete()

        for i in range(len(shMyCategories)):
            new_obj = ProjectUser.objects.get(id=projectUser_id)
            obj.projectUser.add(new_obj)

            try:
                # 2020-05-20
                # shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=projectUser_id)
                shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
            except SHMapping.DoesNotExist:
                # 2020-05-20
                # mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=projectUser_id, relationshipStatus="")
                mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                mapObj.save()
        
        obj.save()

        shProjectCategories = request.data['shProjectCategory']

        ProjectMapLayout.objects.filter(user_id=request.user.id, project_id=request.data['project']).delete()
        obj1 = ProjectMapLayout.objects.create(user_id=request.user.id, project_id=request.data['project'])

        obj1.user_id = request.user.id
        obj1.project_id = request.data['project']
        obj1.layout_json = ''

        for j in range(len(shProjectCategories)):
            new_obj1 = ProjectUser.objects.get(id=projectUser_id)
            obj1.projectUser.add(new_obj1)

            try:
                # 2020-05-20
                # shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=projectUser_id)
                shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
            except SHMapping.DoesNotExist:
                # 2020-05-20
                # mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=projectUser_id, relationshipStatus="")
                mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                mapObj1.save()
        
        obj1.save()

        return ret

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        projectUser_id = serializer.data['id']
        headers = self.get_success_headers(serializer.data)
        
        shMyCategories = request.data['shMyCategory']
        # 2020-05-20
        myProjectUser_id = request.data['myProjectUser']

        obj = MyMapLayout.objects.create(user_id=request.user.id, project_id=data['project'])

        obj.user_id = request.user.id
        obj.project_id = data['project']
        obj.layout_json = ''

        for i in range(len(shMyCategories)):
            new_obj = ProjectUser.objects.get(id=projectUser_id)
            obj.projectUser.add(new_obj)

            try:
                # 2020-05-20
                # shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=projectUser_id)
                shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
            except SHMapping.DoesNotExist:
                # 2020-05-20
                # mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=projectUser_id, relationshipStatus="")
                mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                mapObj.save()

        obj.save()

        shProjectCategories = request.data['shProjectCategory']

        obj1 = ProjectMapLayout.objects.create(user_id=request.user.id, project_id=data['project'])

        obj1.user_id = request.user.id
        obj1.project_id = data['project']
        obj1.layout_json = ''

        for j in range(len(shProjectCategories)):
            new_obj1 = ProjectUser.objects.get(id=projectUser_id)
            obj1.projectUser.add(new_obj1)

            try:
                # 2020-05-20
                # shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=projectUser_id)
                shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
            except SHMapping.DoesNotExist:
                # 2020-05-20
                # mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=projectUser_id, relationshipStatus="")
                mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                mapObj1.save()
        
        obj1.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AOQuestionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AOQuestion.objects.all()
    serializer_class = AOQuestionSerializer

    def get_queryset(self):
        queryset = AOQuestion.objects.all()
        shGroup = self.request.query_params.get('shGroup', None)
        if shGroup is not None:
            queryset = queryset.filter(shGroup__id=shGroup)
        return queryset

class ProjectVideoUploadViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectVideoUpload.objects.all()
    serializer_class = ProjectVideoUploadSerializer

    def get_queryset(self):
        queryset = ProjectVideoUpload.objects.all()
        project = self.request.query_params.get('project', None)
        if project is not None:
            queryset = queryset.filter(project__id=project)
        return queryset

class ConfigPageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ConfigPage.objects.all()
    serializer_class = ConfigPageSerializer

    def get_queryset(self):
        queryset = ConfigPage.objects.all()
        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey)
        return queryset

class UserAvatarViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = UserAvatar.objects.all()
    serializer_class = UserAvatarSerializer
        
class ProjectByUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = ProjectByUserSerializer

    def get_queryset(self):
        queryset = ProjectUser.objects.all()
        user = self.request.query_params.get('user', None)
        if user is not None:
            queryset = queryset.filter(user__id=user)
        return queryset

class UserByProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = UserByProjectSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        myProjectUser_id = self.request.GET.get('myProjectUser')

        for i in range(len(response.data)):
            response.data[i]['am_total'] = AMQuestion.objects.count()
            response.data[i]['am_response'] = []
            # 2020-05-20
            # for item1 in AMResponse.objects.filter(user_id=response.data[i]['user']['id'], project_id=response.data[i]['project']['id']).values('amQuestion'):
            #     response.data[i]['am_response'].append(item1['amQuestion']) 
            # response.data[i]['am_answered'] = AMResponse.objects.filter(user_id=response.data[i]['user']['id'], project_id=response.data[i]['project']['id']).count()
            # response.data[i]['ao_total'] = AOQuestion.objects.count()
            # response.data[i]['ao_response'] = []
            # for item2 in AOResponse.objects.filter(subjectUser_id=response.data[i]['user']['id'], project_id=response.data[i]['project']['id']).values('aoQuestion'):
            #     response.data[i]['ao_response'].append(item2['aoQuestion']) 
            # response.data[i]['ao_answered'] = AOResponse.objects.filter(subjectUser_id=response.data[i]['user']['id'], project_id=response.data[i]['project']['id']).count()
            for item1 in AMResponse.objects.filter(projectUser_id=response.data[i]['id'], project_id=response.data[i]['project']['id']).values('amQuestion'):
                response.data[i]['am_response'].append(item1['amQuestion']) 
            response.data[i]['am_answered'] = AMResponse.objects.filter(projectUser_id=response.data[i]['id'], project_id=response.data[i]['project']['id']).count()
            response.data[i]['ao_total'] = AOQuestion.objects.count()
            response.data[i]['ao_response'] = []
            for item2 in AOResponse.objects.filter(subProjectUser_id=response.data[i]['id'], project_id=response.data[i]['project']['id']).values('aoQuestion'):
                response.data[i]['ao_response'].append(item2['aoQuestion']) 
            response.data[i]['ao_answered'] = AOResponse.objects.filter(subProjectUser_id=response.data[i]['id'], project_id=response.data[i]['project']['id']).count()

            # 2020-05-20
            response.data[i]['shCategory'] = []
            # for item3 in SHMapping.objects.filter(projectUser_id=response.data[i]['id']).values('shCategory'):
            for item3 in SHMapping.objects.filter(projectUser_id=myProjectUser_id, subProjectUser_id=response.data[i]['id']).values('shCategory'):
                response.data[i]['shCategory'].append(item3['shCategory'])

        return response

    def get_queryset(self):
        queryset = ProjectUser.objects.all()

        # 2020-05-27
        # project = self.request.query_params.get('project', None)
        # user = self.request.query_params.get('user', None)
        
        # if (project is not None ) & (user is not None):
        #     queryset = queryset.filter(project__id=project, user__id=user)
        # elif project is not None:
        #     queryset = queryset.filter(project__id=project)    
        # elif user is not None:
        #     queryset = queryset.filter(user__id=user)
        survey = self.request.query_params.get('survey', None)
        user = self.request.query_params.get('user', None)
        
        if (survey is not None ) & (user is not None):
            queryset = queryset.filter(project__id=survey, user__id=user)
        elif survey is not None:
            queryset = queryset.filter(project__id=survey)    
        elif user is not None:
            queryset = queryset.filter(user__id=user)

        return queryset

class DriverViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    # added survey to the driver table     2020-05-20
    def get_queryset(self):
        queryset = Driver.objects.all()
        survey = self.request.query_params.get('survey', None)

        if survey is not None:
            queryset = queryset.filter(survey__id=survey)

        return queryset

class MyMapLayoutViewSet(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = MyMapLayout.objects.all()
    serializer_class = MyMapLayoutStoreSerializer
    filterset_fields = ['user', 'project']

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # 2020-05-20
        myProjectUser_id = self.request.GET.get('myProjectUser')
        
        for i in range(len(response.data)):
            response.data[i]['pu_category'] = []
            for item in response.data[i]['projectUser']:
                # 2020-05-20
                # catIDs = SHMapping.objects.filter(projectUser_id=item)
                catIDs = SHMapping.objects.filter(projectUser_id=myProjectUser_id, subProjectUser_id=item)

                for catID in catIDs:
                    try:
                        obj = SHCategory.objects.get(id=catID.shCategory_id, mapType=2)
                        response.data[i]['pu_category'].append({'projectUser':item, 'category':catID.shCategory_id})
                    except SHCategory.DoesNotExist:
                        continue
        return response

    def create(self, request, *args, **kwargs):
        data = request.data
        content_type = request.content_type
        # 2020-05-20
        myProjectUser_id = data['myProjectUser']

        try:
            obj = MyMapLayout.objects.get(user_id=data['user'], project_id=data['project'])

            obj.projectUser.clear()
            
            if "application/json" in content_type:
                

                for item in data['pu_category']:
                    new_obj = ProjectUser.objects.get(id=item['projectUser'])
                    obj.projectUser.add(new_obj)

                    try:
                        # 2020-05-20
                        # shObj = SHMapping.objects.get(shCategory_id=item['category'], projectUser_id=item['projectUser'])
                        shObj = SHMapping.objects.get(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'])
                    except SHMapping.DoesNotExist:
                        # 2020-05-20
                        # mapObj = SHMapping(shCategory_id=item['category'], projectUser_id=item['projectUser'], relationshipStatus="")
                        mapObj = SHMapping(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'], relationshipStatus="")
                        mapObj.save()

            # else:
            #     for item in data.getlist('pu_category'):
            #         new_obj = ProjectUser.objects.get(id=item.projectUser)
            #         obj.projectUser.add(new_obj)

            obj.save()

        except MyMapLayout.DoesNotExist:
            obj = MyMapLayout.objects.create(user_id=data['user'], project_id=data['project'])

            obj.user_id = data['user']
            obj.project_id = data['project']
            obj.layout_json = data['layout_json']

            if "application/json" in content_type:
                for item in data['pu_category']:
                    new_obj = ProjectUser.objects.get(id=item['projectUser'])
                    obj.projectUser.add(new_obj)

                    try:
                        # 2020-05-20
                        # shObj = SHMapping.objects.get(shCategory_id=item['category'], projectUser_id=item['projectUser'])
                        shObj = SHMapping.objects.get(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'])
                    except SHMapping.DoesNotExist:
                        # 2020-05-20
                        # mapObj = SHMapping(shCategory_id=item['category'], projectUser_id=item['projectUser'], relationshipStatus="")
                        mapObj = SHMapping(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'], relationshipStatus="")
                        mapObj.save()
            # else:
            #     for item in data.getlist('projectUser'):
            #         new_obj = ProjectUser.objects.get(id=item)
            #         obj.projectUser.add(new_obj)

            obj.save()

        result = model_to_dict(MyMapLayout.objects.get(user_id=data['user'], project_id=data['project']))

        list_result = result
        for idx in range(len(result['projectUser'])):
            list_result['projectUser'][idx] = result['projectUser'][idx].id

        serializer = self.get_serializer(data=list_result)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ProjectMapLayoutViewSet(viewsets.ModelViewSet):
    '''
    List: GET all project layouts
    Detail: GET project layout with an id
    Create: POST a layout to be stored against a projectUser id and project id
    Update: PUT a layout to be stored against a projectUser id and project id
    Delete: DELETE a layout with a given id
    Filter: GET a layout matching a projectUser id and project id. Filter on query params.
    (projectUser id, project id) combinations are unique
    '''
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectMapLayout.objects.all()
    serializer_class = ProjectMapLayoutStoreSerializer
    filterset_fields = ['user', 'project']

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # 2020-05-20
        myProjectUser_id = self.request.GET.get('myProjectUser')

        for i in range(len(response.data)):
            response.data[i]['pu_category'] = []
            for item in response.data[i]['projectUser']:
                # 2020-05-20
                # catIDs = SHMapping.objects.filter(projectUser_id=item)
                catIDs = SHMapping.objects.filter(projectUser_id=myProjectUser_id, subProjectUser_id=item)

                for catID in catIDs:
                    try:
                        obj = SHCategory.objects.get(id=catID.shCategory_id, mapType=3)
                        response.data[i]['pu_category'].append({'projectUser':item, 'category':catID.shCategory_id})
                    except SHCategory.DoesNotExist:
                        continue

        return response

    def create(self, request, *args, **kwargs):
        data = request.data
        content_type = request.content_type

        # 2020-05-20
        myProjectUser_id = data['myProjectUser']

        try:
            obj = ProjectMapLayout.objects.get(user_id=data['user'], project_id=data['project'])

            obj.projectUser.clear()

            if "application/json" in content_type:
                for item in data["pu_category"]:
                    new_obj = ProjectUser.objects.get(id=item['projectUser'])
                    obj.projectUser.add(new_obj)

                    try:
                        # 2020-05-20
                        # shObj = SHMapping.objects.get(shCategory_id=item['category'], projectUser_id=item['projectUser'])
                        shObj = SHMapping.objects.get(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'])
                    except SHMapping.DoesNotExist:
                        # 2020-05-20
                        # mapObj = SHMapping(shCategory_id=item['category'], projectUser_id=item['projectUser'], relationshipStatus="")
                        mapObj = SHMapping(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'], relationshipStatus="")
                        mapObj.save()
            obj.save()

        except ProjectMapLayout.DoesNotExist:
            obj = ProjectMapLayout.objects.create(user_id=data['user'], project_id=data['project'])

            obj.user_id = data['user']
            obj.project_id = data['project']
            obj.layout_json = data['layout_json']

            if "application/json" in content_type:
                for item in data['pu_category']:
                    new_obj = ProjectUser.objects.get(id=item['projectUser'])
                    obj.projectUser.add(new_obj)

                    try:
                        # 2020-05-20
                        # shObj = SHMapping.objects.get(shCategory_id=item['category'], projectUser_id=item['projectUser'])
                        shObj = SHMapping.objects.get(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'])
                    except SHMapping.DoesNotExist:
                        # 2020-05-20
                        # mapObj = SHMapping(shCategory_id=item['category'], projectUser_id=item['projectUser'], relationshipStatus="")
                        mapObj = SHMapping(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'], relationshipStatus="")
                        mapObj.save()
            
            obj.save()

        result = model_to_dict(ProjectMapLayout.objects.get(user_id=data['user'], project_id=data['project']))

        list_result = result
        for idx in range(len(result['projectUser'])):
            list_result['projectUser'][idx] = result['projectUser'][idx].id

        serializer = self.get_serializer(data=list_result)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class SHCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = SHCategory.objects.all()
    serializer_class = SHCategorySerializer
    filterset_fields = ['mapType', 'survey']

    def get_queryset(self):
        queryset = SHCategory.objects.all()
        mapType = self.request.query_params.get('mapType', None)
        if mapType is not None:
            # mapType = 2 : mymap
            # mapType = 3 : projectmap
            queryset = queryset.filter(mapType__id=mapType)
        return queryset

class SHMappingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = SHMapping.objects.all()
    serializer_class = SHMappingSerializer
    filterset_fields = ['shCategory']

class SetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    @classmethod
    def get_extra_actions(cls):
        return []

    def post(self, request):
        password = request.data['password']
        email = request.data['email']
        
        try:
            token = Token.objects.get(key=request.data['token'])
            user = User.objects.get(id=token.user_id)

            if (email == user.email):
                user.set_password(password)
                user.save()

                return Response('success', status=status.HTTP_201_CREATED) 

            return Response("Invaid Email", status=status.HTTP_400_BAD_REQUEST)

        except Token.DoesNotExist:
            token = None

            return Response("Invaid Token", status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def post(self, request):
        password = request.data['password']
        email = request.data['email']
        
        try:
            token = Token.objects.get(key=request.data['token'])
            user = User.objects.get(id=token.user_id)

            if (email == user.email):
                user.set_password(password)
                user.save()

                return Response('success', status=status.HTTP_201_CREATED) 

            return Response("Invaid Email", status=status.HTTP_400_BAD_REQUEST)

        except Token.DoesNotExist:
            token = None

            return Response("Invaid Token", status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def post(self, request):
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        email = request.data['email']
        team = request.data['team']
        organization = request.data['organization']

        try:
            token = Token.objects.get(key=request.data['token'])
            try:
                user = User.objects.get(id=token.user_id)
            
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = email

                try:
                    userTeam = UserTeam.objects.get(user_id=token.user_id)
                    userTeam.name = team

                    userTeam.save()
                except UserTeam.DoesNotExist:
                    userTeam = UserTeam(name=team, user_id=token.user_id)

                    userTeam.save()

                try:
                    userOrganization = Organization.objects.get(user_id=token.user_id)
                    userOrganization.name = organization

                    userOrganization.save()
                
                except Organization.DoesNotExist:
                    userOrganization = Organization(name=organization, user_id=token.user_id)

                    userOrganization.save()

                user.save()

                return Response('success', status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                user = None

                return Response("Invalid User", status=status.HTTP_400_BAD_REQUEST)

        except Token.DoesNotExist:
            token = None

            return Response("Invalid Token", status=status.HTTP_400_BAD_REQUEST)
            
class StakeHolderUserView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        organizations = Organization.objects.all()
        serializer = StakeHolderSerializer(organizations, many=True)
        return Response(serializer.data)

    def post(self, request):
        
        serializer = StakeHolderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            
            dt = User.objects.filter(username=serializer.data['user']['username']).values_list('pk', flat=True)

            return Response(dt[0], status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)

class NikelMobilePageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = NikelMobilePage.objects.all()
    serializer_class = NikelMobilePageSerializer

    def get_queryset(self):
        queryset = NikelMobilePage.objects.all()
        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey)
        return queryset