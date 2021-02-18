import os
import re
from pathlib import Path
from email.mime.image import MIMEImage

from snippets.models import Snippet
from snippets.serializers import AMQuestionSubDriverSerializer, AOQuestionSubDriverSerializer, DriverSubDriverSerializer, ProjectSerializer, ToolTipGuideSerializer, SurveySerializer, NikelMobilePageSerializer, ConfigPageSerializer, UserAvatarSerializer, SHMappingSerializer, ProjectVideoUploadSerializer, AMQuestionSerializer, AOQuestionSerializer, StakeHolderSerializer, SHCategorySerializer, MyMapLayoutStoreSerializer, ProjectMapLayoutStoreSerializer, UserBySurveySerializer, SurveyByUserSerializer, SkipOptionSerializer, DriverSerializer, AOQuestionSerializer, OrganizationSerializer, OptionSerializer, ProjectUserSerializer, SHGroupSerializer, UserSerializer, PageSettingSerializer, PageSerializer, AMResponseSerializer, AMResponseTopicSerializer, AOResponseSerializer, AOResponseTopicSerializer, AOPageSerializer, TeamSerializer
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
from aboutme.models import AMQuestion, AMResponse, AMResponseTopic, AMQuestionSHGroup
from aboutothers.models import AOResponse, AOResponseTopic, AOPage
from team.models import Team
from shgroup.models import SHGroup, ProjectUser, MyMapLayout, ProjectMapLayout, SHCategory, SHMapping
from option.models import Option, SkipOption
from rest_framework import status
from organization.models import Organization, UserAvatar, UserTeam, UserGuideMode
from aboutothers.models import AOQuestion
from survey.models import ToolTipGuide, Survey, Driver, Project, ProjectVideoUpload, ConfigPage, NikelMobilePage
from rest_framework.views import APIView
from django.forms.models import model_to_dict
from django.db.models import Q

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import filters
from django.http import HttpResponse
from django.middleware import csrf

from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.conf import settings
import boto3
import json

#initialize comprehend module
comprehend = boto3.client(service_name='comprehend', region_name='us-east-2')

def get_csrf(request):
    return HttpResponse("{0}".format(csrf.get_token(request)), content_type="text/plain")

class CustomAuthToken(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super(CustomAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'id': token.user_id})
 
class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()

        email = self.request.query_params.get('email', None)
        if email is not None:
            queryset = queryset.filter(email=email)

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        for i in range(len(response.data)):
            if response.data[i]['guidemode'] is None:
                response.data[i]['guide'] = True
            else:
                response.data[i]['guide'] = response.data[i]['guidemode']['name']

        return response

    def retrieve(self, request, pk=None):
        response = super().retrieve(request, pk)
        
        if response.data['guidemode'] is None:
            response.data['guide'] = True
        else:
            response.data['guide'] = response.data['guidemode']['name']

        return response

class PageSettingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = PageSetting.objects.all()
    serializer_class = PageSettingSerializer

# v2
class PageViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    def list(self, request, *kwargs):
        
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

        queryset = Driver.objects.filter(survey_id=survey_param)
        #serializer = self.get_serializer(self.get_queryset(), many=True)
        serializer = self.get_serializer(queryset, many=True)
        list_drivers = serializer.data

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

                            # try:
                                # 2020-05-20
                                # ret = AOResponse.objects.get(subjectUser_id=projectuser.user, survey_id=survey_param, aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'])
                                # 2020-08-20
                                # ret = AOResponse.objects.get(subProjectUser_id=projectuser_param, survey_id=survey_param, aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'])
                            ret = AOResponse.objects.filter(projectUser_id=projectuser_param, survey_id=survey_param, aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'])
                            
                            if (len(ret) > 0):
                                list_drivers[i]['aoquestion'][j]['responsestatus'] = True
                                list_drivers[i]['aoquestion'][j]['response'] = []
                                for k in range(len(ret)):
                                    item = model_to_dict(ret[k])
                                    list_drivers[i]['aoquestion'][j]['response'].append(item)
                            # except AOResponse.DoesNotExist:
                            else:
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

                            # try:
                                # 2020-05-20
                                # ret = AOResponse.objects.get(subjectUser_id=projectuser.user, survey_id=survey_param, aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'])
                                # 2020-08-20
                                # ret = AOResponse.objects.get(subProjectUser_id=projectuser_param, survey_id=survey_param, aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'])
                            ret = AOResponse.objects.filter(projectUser_id=projectuser_param, survey_id=survey_param, aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'])
                            
                            if (len(ret) > 0):
                                list_drivers[i]['aoquestion'][j]['responsestatus'] = True
                                list_drivers[i]['aoquestion'][j]['response'] = []
                                for k in range(len(ret)):
                                    item = model_to_dict(ret[k])
                                    list_drivers[i]['aoquestion'][j]['response'].append(item)
                            # except AOResponse.DoesNotExist:
                            else:
                                list_drivers[i]['aoquestion'][j]['responsestatus'] = False
                                list_drivers[i]['aoquestion'][j]['response'] = []

                    except ProjectUser.DoesNotExist:
                        projectuser = None

        return Response(list_drivers)

class AOResponseReportViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AOResponse.objects.all()
    serializer_class = AOResponseSerializer

    def get_queryset(self):
        queryset = AOResponse.objects.all()

        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey)

        return queryset

    def list(self, request, *args, **kwargs):

        response = super().list(request, *args, **kwargs)
        for i in range(len(response.data)):
            aoquestion_queryset = AOQuestion.objects.filter(id=response.data[i]['aoQuestion'])
            ao_serializer = AOQuestionSerializer(aoquestion_queryset, many=True)
            response.data[i]['aoQuestionData'] = ao_serializer.data
            response.data[i]['report'] = {
                "Sentiment": "ERROR",
                "MixedScore": 0,
                "NegativeScore": 0,
                "NeutralScore": 0,
                "PositiveScore": 0,
            }

            if response.data[i]['controlType'] == 'TEXT' or response.data[i]['controlType'] == 'MULTI_TOPICS':
                Text = response.data[i]['topicValue'] + " " + response.data[i]['commentValue']

                if response.data[i]['topicValue'] != "" or response.data[i]['commentValue'] != "":
                    sentimentData = comprehend.detect_sentiment(Text=Text, LanguageCode="en")
                    
                    # new
                    response.data[i]['integerValue'] = int(
                        abs(sentimentData["SentimentScore"]["Positive"] * 100))

                    if "Sentiment" in sentimentData:
                        response.data[i]['report']["Sentiment"] = sentimentData["Sentiment"]
                    if "SentimentScore" in sentimentData:
                        if "Mixed" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["MixedScore"] = sentimentData["SentimentScore"]["Mixed"]
                        if "Negative" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NegativeScore"] = sentimentData["SentimentScore"]["Negative"]
                        if "Neutral" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NeutralScore"] = sentimentData["SentimentScore"]["Neutral"]
                        if "Positive" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["PositiveScore"] = sentimentData["SentimentScore"]["Positive"]

        return response

class AMResponseReportViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer

    def get_queryset(self):
        queryset = AMResponse.objects.all()

        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey)

        return queryset

    def list(self, request, *args, **kwargs):

        response = super().list(request, *args, **kwargs)

        for i in range(len(response.data)):
            amquestion_queryset = AMQuestion.objects.filter(id=response.data[i]['amQuestion'])
            am_serializer = AMQuestionSerializer(amquestion_queryset, many=True)
            response.data[i]['amQuestionData'] = am_serializer.data
            response.data[i]['report'] = {
                "Sentiment": "ERROR",
                "MixedScore": 0,
                "NegativeScore": 0,
                "NeutralScore": 0,
                "PositiveScore": 0,
            }

            if response.data[i]['controlType'] == 'TEXT' or response.data[i]['controlType'] == 'MULTI_TOPICS':
                Text = response.data[i]['topicValue'] + " " + response.data[i]['commentValue']

                if response.data[i]['topicValue'] != "" or response.data[i]['commentValue'] != "":
                    sentimentData = comprehend.detect_sentiment(Text=Text, LanguageCode="en")
                    
                    # new
                    response.data[i]['integerValue'] = int(
                        abs(sentimentData["SentimentScore"]["Positive"] * 100))
                        
                    if "Sentiment" in sentimentData:
                        response.data[i]['report']["Sentiment"] = sentimentData["Sentiment"]
                    if "SentimentScore" in sentimentData:
                        if "Mixed" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["MixedScore"] = sentimentData["SentimentScore"]["Mixed"]
                        if "Negative" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NegativeScore"] = sentimentData["SentimentScore"]["Negative"]
                        if "Neutral" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NeutralScore"] = sentimentData["SentimentScore"]["Neutral"]
                        if "Positive" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["PositiveScore"] = sentimentData["SentimentScore"]["Positive"]

        return response

class AOResponseFeedbackSummaryViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AOResponse.objects.all()
    serializer_class = AOResponseSerializer

    def get_queryset(self):
        queryset = AOResponse.objects.all()

        survey = self.request.query_params.get('survey', None)
        subProjectUser = self.request.query_params.get('subProjectUser', None)
        
        if (survey is not None) & (subProjectUser is not None):
            queryset = queryset.filter(survey_id=survey, subProjectUser_id=subProjectUser)
        elif survey is not None:
            queryset = queryset.filter(survey_id=survey)
        elif subProjectUser is not None:
            queryset = queryset.filter(subProjectUser_id=subProjectUser)

        return queryset

    def list(self, request, *args, **kwargs):

        response = super().list(request, *args, **kwargs)
        # print(response.data)
        for i in range(len(response.data)):
            aoquestion_queryset = AOQuestion.objects.filter(id=response.data[i]['aoQuestion'])
            ao_serializer = AOQuestionSerializer(aoquestion_queryset, many=True)
            response.data[i]['aoQuestionData'] = ao_serializer.data
            # response.data[i]['amQuestionData'] = AMQuestion.objects.filter(id=response.data[i]['amQuestion']).values()[0]
            # response.data[i]['shGroups'] = AMQuestionSHGroup.objects.filter(amQuestion=response.data[i]['amQuestion']).values_list('shGroup')
            response.data[i]['report'] = {
                "Sentiment": "ERROR",
                "MixedScore": 0,
                "NegativeScore": 0,
                "NeutralScore": 0,
                "PositiveScore": 0,
            }

            if response.data[i]['controlType'] == 'TEXT' or response.data[i]['controlType'] == 'MULTI_TOPICS':
                Text = response.data[i]['topicValue'] + " " + response.data[i]['commentValue']

                if response.data[i]['topicValue'] != "" or response.data[i]['commentValue'] != "":
                    sentimentData = comprehend.detect_sentiment(Text=Text, LanguageCode="en")
                    
                    # new
                    response.data[i]['integerValue'] = int(
                        abs(sentimentData["SentimentScore"]["Positive"] * 100))

                    if "Sentiment" in sentimentData:
                        response.data[i]['report']["Sentiment"] = sentimentData["Sentiment"]
                    if "SentimentScore" in sentimentData:
                        if "Mixed" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["MixedScore"] = sentimentData["SentimentScore"]["Mixed"]
                        if "Negative" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NegativeScore"] = sentimentData["SentimentScore"]["Negative"]
                        if "Neutral" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NeutralScore"] = sentimentData["SentimentScore"]["Neutral"]
                        if "Positive" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["PositiveScore"] = sentimentData["SentimentScore"]["Positive"]

        return response

class AMResponseFeedbackSummaryViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer

    def get_queryset(self):
        queryset = AMResponse.objects.all()

        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey)

        return queryset

    def list(self, request, *args, **kwargs):

        response = super().list(request, *args, **kwargs)
        # print(response.data)
        for i in range(len(response.data)):
            amquestion_queryset = AMQuestion.objects.filter(id=response.data[i]['amQuestion'])
            am_serializer = AMQuestionSerializer(amquestion_queryset, many=True)
            response.data[i]['amQuestionData'] = am_serializer.data
            # response.data[i]['amQuestionData'] = AMQuestion.objects.filter(id=response.data[i]['amQuestion']).values()[0]
            # response.data[i]['shGroups'] = AMQuestionSHGroup.objects.filter(amQuestion=response.data[i]['amQuestion']).values_list('shGroup')
            response.data[i]['report'] = {
                "Sentiment": "ERROR",
                "MixedScore": 0,
                "NegativeScore": 0,
                "NeutralScore": 0,
                "PositiveScore": 0,
            }

            if response.data[i]['controlType'] == 'TEXT' or response.data[i]['controlType'] == 'MULTI_TOPICS':
                Text = response.data[i]['topicValue'] + " " + response.data[i]['commentValue']

                if response.data[i]['topicValue'] != "" or response.data[i]['commentValue'] != "":
                    sentimentData = comprehend.detect_sentiment(Text=Text, LanguageCode="en")
                    print(sentimentData)

                    # new
                    response.data[i]['integerValue'] = int(
                        abs(sentimentData["SentimentScore"]["Positive"] * 100))

                    if "Sentiment" in sentimentData:
                        response.data[i]['report']["Sentiment"] = sentimentData["Sentiment"]
                    if "SentimentScore" in sentimentData:
                        if "Mixed" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["MixedScore"] = sentimentData["SentimentScore"]["Mixed"]
                        if "Negative" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NegativeScore"] = sentimentData["SentimentScore"]["Negative"]
                        if "Neutral" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NeutralScore"] = sentimentData["SentimentScore"]["Neutral"]
                        if "Positive" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["PositiveScore"] = sentimentData["SentimentScore"]["Positive"]

        return response

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

                    if obj.controlType == "TEXT" or obj.controlType == "MULTI_TOPICS":
                        text = obj.topicValue + " " + obj.commentValue

                        sentimentResult = comprehend.detect_sentiment(Text=text, LanguageCode="en")
                        obj.integerValue = int(abs(sentimentResult["SentimentScore"]["Positive"] * 100))
                    else:                   
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

                    if defaults["controlType"] == "TEXT" or defaults["controlType"] == "MULTI_TOPICS":
                        text = defaults['topicValue'] + " " + defaults['commentValue']

                        sentimentResult = comprehend.detect_sentiment(Text=text, LanguageCode="en")
                        defaults["integerValue"] = int(abs(sentimentResult["SentimentScore"]["Positive"] * 100))

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
                
                if obj.controlType == "TEXT" or obj.controlType == "MULTI_TOPICS":
                    text = obj.topicValue + " " + obj.commentValue

                    sentimentResult = comprehend.detect_sentiment(Text=text, LanguageCode="en")
                    obj.integerValue = int(abs(sentimentResult["SentimentScore"]["Positive"] * 100))
                else:                   
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
                if data["controlType"] == "TEXT" or data["controlType"] == "MULTI_TOPICS":
                    text = data['topicValue'] + " " + data['commentValue']

                    sentimentResult = comprehend.detect_sentiment(Text=text, LanguageCode="en")
                    data["integerValue"] = int(abs(sentimentResult["SentimentScore"]["Positive"] * 100))

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

# Sentiment api
class AMResponseFeedbackSummaryForSentimentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer

    def get_queryset(self):
        queryset = AMResponse.objects.filter(amQuestion__driver__driverName="Sentiment")

        survey = self.request.query_params.get('survey', None)
        startDate = self.request.query_params.get('stdt', None)
        endDate = self.request.query_params.get('eddt', None)
        if (survey is not None) & (startDate is not None) & (endDate is not None):
            queryset = queryset.filter(survey__id=survey, amQuestion__driver__driverName="Sentiment", updated_at__range=[startDate, endDate])
        elif survey is not None:
            queryset = queryset.filter(survey__id=survey, amQuestion__driver__driverName="Sentiment")
        elif (startDate is not None) & (endDate is not None):
            queryset = queryset.filter(
                amQuestion__driver__driverName="Sentiment", updated_at__range=[startDate, endDate])

        return queryset

    def list(self, request, *args, **kwargs):

        response = super().list(request, *args, **kwargs)
        for i in range(len(response.data)):
            amquestion_queryset = AMQuestion.objects.filter(id=response.data[i]['amQuestion'])
            am_serializer = AMQuestionSerializer(amquestion_queryset, many=True)
            response.data[i]['amQuestionData'] = am_serializer.data

            response.data[i]['report'] = {
                "Sentiment": "ERROR",
                "MixedScore": 0,
                "NegativeScore": 0,
                "NeutralScore": 0,
                "PositiveScore": 0,
            }

            if response.data[i]['controlType'] == 'TEXT' or response.data[i]['controlType'] == 'MULTI_TOPICS':
                Text = response.data[i]['topicValue'] + " " + response.data[i]['commentValue']

                if response.data[i]['topicValue'] != "" or response.data[i]['commentValue'] != "":
                    sentimentData = comprehend.detect_sentiment(Text=Text, LanguageCode="en")

                    response.data[i]['integerValue'] = int(abs(sentimentData['SentimentScore']['Positive'] * 100))

                    if "Sentiment" in sentimentData:
                        response.data[i]['report']['Sentiment'] = sentimentData['Sentiment']
                    if "SentimentScore" in sentimentData:
                        if "Mixed" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["MixedScore"] = sentimentData["SentimentScore"]["Mixed"]
                        if "Negative" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NegativeScore"] = sentimentData["SentimentScore"]["Negative"]
                        if "Neutral" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NeutralScore"] = sentimentData["SentimentScore"]["Neutral"]
                        if "Positive" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["PositiveScore"] = sentimentData["SentimentScore"]["Positive"]

        return response

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
                    # 2020-12-17
                    # obj = AOResponse.objects.get(survey_id=item['survey'], project_id=item['project'], projectUser_id=item['projectUser'], subProjectUser_id=item['subProjectUser'], shCategory_id=item['shCategory'], aoQuestion_id=item['aoQuestion'])
                    obj = AOResponse.objects.get(survey_id=item['survey'], project_id=item['project'], projectUser_id=item['projectUser'], subProjectUser_id=item['subProjectUser'], aoQuestion_id=item['aoQuestion'])

                    if obj.controlType == "TEXT" or obj.controlType == "MULTI_TOPICS":
                        text = obj.topicValue + " " + obj.commentValue

                        sentimentResult = comprehend.detect_sentiment(Text=text, LanguageCode="en")
                        obj.integerValue = int(abs(sentimentResult["SentimentScore"]["Positive"] * 100))
                    else:
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
                    
                    if defaults["controlType"] == "TEXT" or defaults["controlType"] == "MULTI_TOPICS":
                        text = defaults['topicValue'] + " " + defaults['commentValue']

                        sentimentResult = comprehend.detect_sentiment(Text=text, LanguageCode="en")
                        defaults["integerValue"] = int(abs(sentimentResult["SentimentScore"]["Positive"] * 100))

                    obj = AOResponse(aoQuestion_id=defaults['aoQuestion'],
                                projectUser_id=defaults['projectUser'], subProjectUser_id=defaults['subProjectUser'],
                                shCategory_id=defaults['shCategory'],
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
                # obj = AOResponse.objects.get(survey_id=item['survey'], project_id=item['project'], projectUser_id=item['projectUser'], subProjectUser_id=item['subProjectUser'], shCategory_id=item['shCategory'], aoQuestion_id=item['aoQuestion'])
                obj = AOResponse.objects.get(survey_id=item['survey'], project_id=item['project'], projectUser_id=item['projectUser'], subProjectUser_id=item['subProjectUser'], aoQuestion_id=item['aoQuestion'])

                if obj.controlType == "TEXT" or obj.controlType == "MULTI_TOPICS":
                    text = obj.topicValue + " " + obj.commentValue

                    sentimentResult = comprehend.detect_sentiment(Text=text, LanguageCode="en")
                    obj.integerValue = int(abs(sentimentResult["SentimentScore"]["Positive"] * 100))
                else:
                    obj.integerValue = defaults['integerValue']
                
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

                if defaults["controlType"] == "TEXT" or defaults["controlType"] == "MULTI_TOPICS":
                    text = defaults["topicValue"] + " " + defaults["commentValue"]

                    sentimentResult = comprehend.detect_sentiment(Text=text, LanguageCode="en")
                    defaults["integerValue"] = int(abs(sentimentResult["SentimentScore"]["Positive"] * 100))

                obj = AOResponse(aoQuestion_id=defaults['aoQuestion'],
                            projectUser_id=defaults['projectUser'], subProjectUser_id=defaults['subProjectUser'],
                            shCategory_id=defaults['shCategory'],
                            survey_id=defaults['survey'], project_id=defaults['project'],
                            controlType=defaults['controlType'], integerValue=defaults['integerValue'],
                            topicValue=defaults['topicValue'], commentValue=defaults['commentValue'],
                            skipValue=defaults['skipValue'], topicTags=defaults['topicTags'],
                            commentTags=defaults['commentTags'])
                obj.save()
        
        # 2020-05-20
        # result = AOResponse.objects.all().values('user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags')
        result = AOResponse.objects.all().values('projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags')
        
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

    def get_queryset(self):
        queryset = Team.objects.all()

        project = self.request.query_params.get('project', None)
        if project is not None:
            queryset = queryset.filter(project__id=project)

        return queryset
        
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

class TemoraryTestForProjectUser(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = ProjectUserSerializer

    def get_queryset(self):
        queryset = ProjectUser.objects.all()
        return queryset

    def update(self, request, *args, **kwargs):
        ret = super(ProjectUserViewSet, self).update(request, *args, **kwargs)

        print(ret)

        return ret
        
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
        
        # MyMapLayout.objects.filter(user_id=request.user.id, project_id=request.data['project']).delete()
        obj = MyMapLayout.objects.get(user_id=request.user.id, project_id=request.data['project'])

        # obj.user_id = request.user.id
        # obj.project_id = request.data['project']
        # obj.layout_json = ''   

        # 2020-05-20     added projectUser, subProjectUser
        # SHMapping.objects.filter(projectUser_id=projectUser_id).delete()
        myProjectUser_id = request.data['myProjectUser']
        SHMapping.objects.filter(projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id).delete()

        for i in range(len(shMyCategories)):
            # new_obj = ProjectUser.objects.get(id=projectUser_id)
            # obj.projectUser.add(new_obj)

            try:
                # 2020-05-20
                # shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=projectUser_id)
                shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
            except SHMapping.DoesNotExist:
                # 2020-05-20
                # mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=projectUser_id, relationshipStatus="")
                mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                mapObj.save()
        
        # obj.save()

        shProjectCategories = request.data['shProjectCategory']

        # ProjectMapLayout.objects.filter(user_id=request.user.id, project_id=request.data['project']).delete()
        obj1 = ProjectMapLayout.objects.get(user_id=request.user.id, project_id=request.data['project'])

        # obj1.user_id = request.user.id
        # obj1.project_id = request.data['project']
        # obj1.layout_json = ''

        for j in range(len(shProjectCategories)):
            # new_obj1 = ProjectUser.objects.get(id=projectUser_id)
            # obj1.projectUser.add(new_obj1)

            try:
                # 2020-05-20
                # shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=projectUser_id)
                shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
            except SHMapping.DoesNotExist:
                # 2020-05-20
                # mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=projectUser_id, relationshipStatus="")
                mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                mapObj1.save()
        
        # obj1.save()

        return ret

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=many)
        
        projectUser_id = 0

        existCheckObj = ProjectUser.objects.filter(survey_id=data['survey'], user_id=data['user'])

        if len(existCheckObj) > 0:
            projectUser_id = existCheckObj[0].id
        else:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            projectUser_id = serializer.data['id']
            
        # headers = self.get_success_headers(serializer.data)
        
        shMyCategories = request.data['shMyCategory']
        # 2020-05-20
        myProjectUser_id = request.data['myProjectUser']

        try:
            obj = MyMapLayout.objects.get(user_id=request.user.id, project_id=data['project'])
            
            # 2020-11-24 added
            # obj.projectUser.clear()
            new_obj = ProjectUser.objects.get(id=projectUser_id)
            obj.projectUser.add(new_obj)
            
            for i in range(len(shMyCategories)):
                # new_obj = ProjectUser.objects.get(id=projectUser_id)
                # obj.projectUser.add(new_obj)

                try:
                    # 2020-05-20
                    # shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=projectUser_id)
                    shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    # 2020-05-20
                    # mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=projectUser_id, relationshipStatus="")
                    mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj.save()

            # 2020-11-24 added
            obj.save()
            
        except MyMapLayout.DoesNotExist:
            obj = MyMapLayout.objects.create(user_id=request.user.id, project_id=data['project'])

            obj.user_id = request.user.id
            obj.project_id = data['project']
            obj.layout_json = ''

            # 2020-11-24 added
            new_obj = ProjectUser.objects.get(id=projectUser_id)
            obj.projectUser.add(new_obj)

            for i in range(len(shMyCategories)):
                # new_obj = ProjectUser.objects.get(id=projectUser_id)
                # obj.projectUser.add(new_obj)

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

        try:
            obj1 = ProjectMapLayout.objects.get(user_id=request.user.id, project_id=data['project'])

            # 2020-11-24 added
            # obj1.projectUser.clear()
            new_obj1 = ProjectUser.objects.get(id=projectUser_id)
            obj1.projectUser.add(new_obj1)

            for j in range(len(shProjectCategories)):
                #new_obj1 = ProjectUser.objects.get(id=projectUser_id)
                #obj1.projectUser.add(new_obj1)

                try:
                    # 2020-05-20
                    # shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=projectUser_id)
                    shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    # 2020-05-20
                    # mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=projectUser_id, relationshipStatus="")
                    mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj1.save()

            # 2020-11-24 added
            obj1.save()

        except ProjectMapLayout.DoesNotExist:
            obj1 = ProjectMapLayout.objects.create(user_id=request.user.id, project_id=data['project'])

            obj1.user_id = request.user.id
            obj1.project_id = data['project']
            obj1.layout_json = ''

            # 2020-11-24 added
            new_obj1 = ProjectUser.objects.get(id=projectUser_id)
            obj1.projectUser.add(new_obj1)

            for j in range(len(shProjectCategories)):
                # new_obj1 = ProjectUser.objects.get(id=projectUser_id)
                # obj1.projectUser.add(new_obj1)

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

        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response("success", status=status.HTTP_201_CREATED)

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
        
class SurveyByUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = SurveyByUserSerializer

    def get_queryset(self):
        queryset = ProjectUser.objects.all()
        user = self.request.query_params.get('user', None)
        if user is not None:
            queryset = queryset.filter(user__id=user)
        return queryset

class SurveyViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    def get_queryset(self):
        queryset = Survey.objects.all()
        project = self.request.query_params.get('project', None)
        
        if project is not None:
            queryset = queryset.filter(project__id=project, isActive=True)    
        
        return queryset

class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ProjectByUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = SurveyByUserSerializer

    def get_queryset(self):
        queryset = ProjectUser.objects.all()
        user = self.request.query_params.get('user', None)
        if user is not None:
            queryset = queryset.filter(user__id=user)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        new_data = []
        project_ids = []
        for i in range(len(response.data)):
            if response.data[i]['survey']['project'] not in project_ids:
                project_ids.append(response.data[i]['survey']['project'])

        response.data = []
        for i in range(len(project_ids)):
            item = model_to_dict(Project.objects.get(id=project_ids[i]))
            response.data.append(item)

        return response

class UserBySurveyViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = UserBySurveySerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        myProjectUser_id = self.request.GET.get('myProjectUser')
        survey = self.request.GET.get('survey')

        for i in range(len(response.data)):
            filters = ~Q(shGroup=None)
            if response.data[i]['user']['last_login'] is not None:
                response.data[i]['accept_status'] = True
            else:
                response.data[i]['accept_status'] = False

            response.data[i]['am_total'] = AMQuestion.objects.filter(filters).filter(survey__id=survey).count()
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
            for item1 in AMResponse.objects.filter(projectUser_id=response.data[i]['id']).values('amQuestion'):
                response.data[i]['am_response'].append(item1['amQuestion']) 
            response.data[i]['am_answered'] = AMResponse.objects.filter(projectUser_id=response.data[i]['id']).count()
            response.data[i]['ao_total'] = AOQuestion.objects.filter(filters).filter(survey__id=survey).count()
            response.data[i]['ao_response'] = []
            for item2 in AOResponse.objects.filter(subProjectUser_id=response.data[i]['id']).values('aoQuestion'):
                response.data[i]['ao_response'].append(item2['aoQuestion']) 
            response.data[i]['ao_answered'] = AOResponse.objects.filter(subProjectUser_id=response.data[i]['id']).count()

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
        
        if (survey is not None) & (user is not None):
            # queryset = queryset.filter(survey__id=survey, user__id=user).exclude(user__id=self.request.user.id)
            queryset = queryset.filter(survey__id=survey, user__id=user)
        elif survey is not None:
            # queryset = queryset.filter(survey__id=survey).exclude(user__id=self.request.user.id)
            queryset = queryset.filter(survey__id=survey)   
        elif user is not None:
            # queryset = queryset.filter(user__id=user).exclude(user__id=self.request.user.id)
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

class UpdateStakeHolderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = ProjectUserSerializer

    def get_queryset(self):
        queryset = ProjectUser.objects.all()
        return queryset

    def update(self, request, *args, **kwargs):
        ret = super(UpdateStakeHolderViewSet, self).update(request, *args, **kwargs)

        projectUser_id = ret.data['id']

        shMyCategories = request.data['shMyCategory']
        
        # MyMapLayout.objects.filter(user_id=request.user.id, project_id=request.data['project']).delete()
        obj = MyMapLayout.objects.get(user_id=request.user.id, project_id=request.data['project'])

        # obj.user_id = request.user.id
        # obj.project_id = request.data['project']
        # obj.layout_json = ''   

        # 2020-05-20     added projectUser, subProjectUser
        # SHMapping.objects.filter(projectUser_id=projectUser_id).delete()
        myProjectUser_id = request.data['myProjectUser']
        SHMapping.objects.filter(projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id).delete()

        for i in range(len(shMyCategories)):
            # new_obj = ProjectUser.objects.get(id=projectUser_id)
            # obj.projectUser.add(new_obj)

            try:
                # 2020-05-20
                # shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=projectUser_id)
                shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
            except SHMapping.DoesNotExist:
                # 2020-05-20
                # mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=projectUser_id, relationshipStatus="")
                mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                mapObj.save()
        
        # obj.save()

        shProjectCategories = request.data['shProjectCategory']

        # ProjectMapLayout.objects.filter(user_id=request.user.id, project_id=request.data['project']).delete()
        obj1 = ProjectMapLayout.objects.get(user_id=request.user.id, project_id=request.data['project'])

        # obj1.user_id = request.user.id
        # obj1.project_id = request.data['project']
        # obj1.layout_json = ''

        for j in range(len(shProjectCategories)):
            # new_obj1 = ProjectUser.objects.get(id=projectUser_id)
            # obj1.projectUser.add(new_obj1)

            try:
                # 2020-05-20
                # shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=projectUser_id)
                shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
            except SHMapping.DoesNotExist:
                # 2020-05-20
                # mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=projectUser_id, relationshipStatus="")
                mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                mapObj1.save()
        
        # obj1.save()

        return ret

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

class UserGuideModeView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def post(self, request):
        guidemode = request.data['guidemode']

        try:
            token = Token.objects.get(key=request.data['token'])

            try:
                userGuideMode = UserGuideMode.objects.get(user_id=token.user_id)
                userGuideMode.name = guidemode

                userGuideMode.save()
            except UserGuideMode.DoesNotExist:
                userGuideMode = UserGuideMode(name=guidemode, user_id=token.user_id)

                userGuideMode.save()

            return Response('success', status=status.HTTP_201_CREATED)
        except Token.DoesNotExist:
            token = None

            return Response("Invalid Token", status=status.HTTP_400_BAD_REQUEST)

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

class ToolTipGuideViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ToolTipGuide.objects.all()
    serializer_class = ToolTipGuideSerializer

class OverallSentimentReportViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer

    def get_queryset(self):
        queryset = AMResponse.objects.all()
        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        total = 0
        for i in range(len(response.data)):
            total = total + response.data[i]['integerValue']
        cnt = len(response.data)

        percentage = 0
        if (cnt > 0):
            percentage = total / cnt

        response.data = []
        if percentage < 40:
            response.data.append({'emojiType': 'angry', 'value': percentage})
        elif percentage < 50:
            response.data.append({'emojiType': 'worried', 'value': percentage})
        elif percentage < 60:
            response.data.append({'emojiType': 'flat', 'value': percentage})
        elif percentage < 70:
            response.data.append({'emojiType': 'smile', 'value': percentage})
        elif percentage < 80:
            response.data.append({'emojiType': 'big', 'value': percentage})
        else:
            response.data.append({'emojiType': 'green', 'value': percentage})

        return response

###
class ReportByStakeholderViewSet(viewsets.ModelViewSet):

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
        myProjectUser_id = data['myProjectUser']

        try:
            obj = MyMapLayout.objects.get(user_id=data['user'], project_id=data['project'])

            obj.projectUser.clear()
            
            if "application/json" in content_type:
                
                for item in data['pu_category']:
                    new_obj = ProjectUser.objects.get(id=item['projectUser'])
                    obj.projectUser.add(new_obj)

                    try:
                        
                        shObj = SHMapping.objects.get(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'])
                    except SHMapping.DoesNotExist:
                        
                        mapObj = SHMapping(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'], relationshipStatus="")
                        mapObj.save()

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
                        
                        shObj = SHMapping.objects.get(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'])
                    except SHMapping.DoesNotExist:
                        
                        mapObj = SHMapping(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'], relationshipStatus="")
                        mapObj.save()

            obj.save()

        result = model_to_dict(MyMapLayout.objects.get(user_id=data['user'], project_id=data['project']))

        list_result = result
        for idx in range(len(result['projectUser'])):
            list_result['projectUser'][idx] = result['projectUser'][idx].id

        serializer = self.get_serializer(data=list_result)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AOResponseReportv2ViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AOResponse.objects.all()
    serializer_class = AOResponseSerializer

    def get_queryset(self):
        queryset = AOResponse.objects.all()

        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey)

        return queryset

    def list(self, request, *args, **kwargs):

        response = super().list(request, *args, **kwargs)
        for i in range(len(response.data)):
            aoquestion_queryset = AOQuestion.objects.filter(id=response.data[i]['aoQuestion'])
            ao_serializer = AOQuestionSerializer(aoquestion_queryset, many=True)
            response.data[i]['aoQuestionData'] = ao_serializer.data
            response.data[i]['report'] = {
                "Sentiment": "ERROR",
                "MixedScore": 0,
                "NegativeScore": 0,
                "NeutralScore": 0,
                "PositiveScore": 0,
            }

            if response.data[i]['controlType'] == 'TEXT' or response.data[i]['controlType'] == 'MULTI_TOPICS':
                Text = response.data[i]['topicValue'] + " " + response.data[i]['commentValue']

                if response.data[i]['topicValue'] != "" or response.data[i]['commentValue'] != "":
                    sentimentData = comprehend.detect_sentiment(Text=Text, LanguageCode="en")

                    # new
                    response.data[i]['integerValue'] = int(
                        abs(sentimentData["SentimentScore"]["Positive"] * 100))

                    print(sentimentData)
                    if "Sentiment" in sentimentData:
                        response.data[i]['report']["Sentiment"] = sentimentData["Sentiment"]
                    if "SentimentScore" in sentimentData:
                        if "Mixed" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["MixedScore"] = sentimentData["SentimentScore"]["Mixed"]
                        if "Negative" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NegativeScore"] = sentimentData["SentimentScore"]["Negative"]
                        if "Neutral" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NeutralScore"] = sentimentData["SentimentScore"]["Neutral"]
                        if "Positive" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["PositiveScore"] = sentimentData["SentimentScore"]["Positive"]

        return response

class AMResponseFeedbackSummaryv2Viewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer

    def get_queryset(self):
        queryset = AMResponse.objects.all()

        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey)

        return queryset

    def list(self, request, *args, **kwargs):

        response = super().list(request, *args, **kwargs)
        # print(response.data)
        for i in range(len(response.data)):
            amquestion_queryset = AMQuestion.objects.filter(id=response.data[i]['amQuestion'])
            am_serializer = AMQuestionSerializer(amquestion_queryset, many=True)
            response.data[i]['amQuestionData'] = am_serializer.data
            # response.data[i]['amQuestionData'] = AMQuestion.objects.filter(id=response.data[i]['amQuestion']).values()[0]
            # response.data[i]['shGroups'] = AMQuestionSHGroup.objects.filter(amQuestion=response.data[i]['amQuestion']).values_list('shGroup')
            response.data[i]['report'] = {
                "Sentiment": "ERROR",
                "MixedScore": 0,
                "NegativeScore": 0,
                "NeutralScore": 0,
                "PositiveScore": 0,
            }

            if response.data[i]['controlType'] == 'TEXT' or response.data[i]['controlType'] == 'MULTI_TOPICS':
                Text = response.data[i]['topicValue'] + " " + response.data[i]['commentValue']

                if response.data[i]['topicValue'] != "" or response.data[i]['commentValue'] != "":
                    sentimentData = comprehend.detect_sentiment(Text=Text, LanguageCode="en")
                    print(sentimentData)

                    # new
                    response.data[i]['integerValue'] = int(
                        abs(sentimentData["SentimentScore"]["Positive"] * 100))

                    if "Sentiment" in sentimentData:
                        response.data[i]['report']["Sentiment"] = sentimentData["Sentiment"]
                    if "SentimentScore" in sentimentData:
                        if "Mixed" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["MixedScore"] = sentimentData["SentimentScore"]["Mixed"]
                        if "Negative" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NegativeScore"] = sentimentData["SentimentScore"]["Negative"]
                        if "Neutral" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NeutralScore"] = sentimentData["SentimentScore"]["Neutral"]
                        if "Positive" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["PositiveScore"] = sentimentData["SentimentScore"]["Positive"]

        return response

# Engagement api
class AMResponseFeedbackSummaryForEngagementViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer

    def get_queryset(self):
        queryset = AMResponse.objects.filter(amQuestion__driver__driverName="Engagement")

        survey = self.request.query_params.get('survey', None)
        startDate = self.request.query_params.get('stdt', None)
        endDate = self.request.query_params.get('eddt', None)
        if survey is not None:
            queryset = queryset.filter(
                survey__id=survey, amQuestion__driver__driverName="Engagement", updated_at__range=[startDate, endDate])

        return queryset

    def list(self, request, *args, **kwargs):

        response = super().list(request, *args, **kwargs)
        # print(response.data)
        for i in range(len(response.data)):
            amquestion_queryset = AMQuestion.objects.filter(id=response.data[i]['amQuestion'])
            am_serializer = AMQuestionSerializer(amquestion_queryset, many=True)
            response.data[i]['amQuestionData'] = am_serializer.data
            # response.data[i]['amQuestionData'] = AMQuestion.objects.filter(id=response.data[i]['amQuestion']).values()[0]
            # response.data[i]['shGroups'] = AMQuestionSHGroup.objects.filter(amQuestion=response.data[i]['amQuestion']).values_list('shGroup')
            response.data[i]['report'] = {
                "Sentiment": "ERROR",
                "MixedScore": 0,
                "NegativeScore": 0,
                "NeutralScore": 0,
                "PositiveScore": 0,
            }

            if response.data[i]['controlType'] == 'TEXT' or response.data[i]['controlType'] == 'MULTI_TOPICS':
                Text = response.data[i]['topicValue'] + " " + response.data[i]['commentValue']

                if response.data[i]['topicValue'] != "" or response.data[i]['commentValue'] != "":
                    sentimentData = comprehend.detect_sentiment(Text=Text, LanguageCode="en")
                    
                    # new
                    response.data[i]['integerValue'] = int(
                        abs(sentimentData["SentimentScore"]["Positive"] * 100))

                    if "Sentiment" in sentimentData:
                        response.data[i]['report']["Sentiment"] = sentimentData["Sentiment"]
                    if "SentimentScore" in sentimentData:
                        if "Mixed" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["MixedScore"] = sentimentData["SentimentScore"]["Mixed"]
                        if "Negative" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NegativeScore"] = sentimentData["SentimentScore"]["Negative"]
                        if "Neutral" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NeutralScore"] = sentimentData["SentimentScore"]["Neutral"]
                        if "Positive" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["PositiveScore"] = sentimentData["SentimentScore"]["Positive"]

        return response

# Interest api
class AMResponseFeedbackSummaryForInterestViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer

    def get_queryset(self):
        queryset = AMResponse.objects.filter(amQuestion__driver__driverName="Interest")
        
        survey = self.request.query_params.get('survey', None)
        # startDate = self.request.query_params.get('stdt', None)
        # endDate = self.request.query_params.get('eddt', None)
        if survey is not None:
            # queryset = queryset.filter(
            #     survey__id=survey, amQuestion__driver__driverName="Interest", updated_at__range=[startDate, endDate]
            # )
            queryset = queryset.filter(
                survey__id=survey, amQuestion__driver__driverName="Interest"
            )
        
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        
        for i in range(len(response.data)):
            amquestion_queryset = AMQuestion.objects.filter(id=response.data[i]['amQuestion'])
            am_serializer = AMQuestionSerializer(amquestion_queryset, many=True)
            response.data[i]['amQuestionData'] = am_serializer.data

            response.data[i]['report'] = {
                "Sentiment": "ERROR",
                "MixedScore": 0,
                "NegativeScore": 0,
                "NeutralScore": 0,
                "PositiveScore": 0,
            }

            if response.data[i]['controlType'] == 'TEXT' or response.data[i]['controlType'] == 'MULTI_TOPICS':
                Text = response.data[i]['topicValue'] + " " + response.data[i]['commentValue']

                if response.data[i]['topicValue'] != "" or response.data[i]['commentValue'] != "":
                    sentimentData = comprehend.detect_sentiment(Text=Text, LanguageCode="en")
                    
                    # new
                    response.data[i]['integerValue'] = int(
                        abs(sentimentData["SentimentScore"]["Positive"] * 100))

                    if "Sentiment" in sentimentData:
                        response.data[i]['report']["Sentiment"] = sentimentData["Sentiment"]
                    if "SentimentScore" in sentimentData:
                        if "Mixed" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["MixedScore"] = sentimentData["SentimentScore"]["Mixed"]
                        if "Negative" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NegativeScore"] = sentimentData["SentimentScore"]["Negative"]
                        if "Neutral" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NeutralScore"] = sentimentData["SentimentScore"]["Neutral"]
                        if "Positive" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["PositiveScore"] = sentimentData["SentimentScore"]["Positive"]

        return response

class UserBySurveyv2ViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = UserBySurveySerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        myProjectUser_id = self.request.GET.get('myProjectUser')
        survey = self.request.GET.get('survey')

        for i in range(len(response.data)):
            filters = ~Q(shGroup=None)
            if response.data[i]['user']['last_login'] is not None:
                response.data[i]['accept_status'] = True
            else:
                response.data[i]['accept_status'] = False

            response.data[i]['am_total'] = AMQuestion.objects.filter(filters).filter(survey__id=survey).count()
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
            for item1 in AMResponse.objects.filter(projectUser_id=response.data[i]['id']).values('amQuestion'):
                response.data[i]['am_response'].append(item1['amQuestion']) 
            response.data[i]['am_answered'] = AMResponse.objects.filter(projectUser_id=response.data[i]['id']).count()
            response.data[i]['ao_total'] = AOQuestion.objects.filter(filters).filter(survey__id=survey).count()
            response.data[i]['ao_response'] = []
            for item2 in AOResponse.objects.filter(subProjectUser_id=response.data[i]['id']).values('aoQuestion'):
                response.data[i]['ao_response'].append(item2['aoQuestion']) 
            response.data[i]['ao_answered'] = AOResponse.objects.filter(subProjectUser_id=response.data[i]['id']).count()

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
        
        if (survey is not None) & (user is not None):
            # queryset = queryset.filter(survey__id=survey, user__id=user).exclude(user__id=self.request.user.id)
            queryset = queryset.filter(survey__id=survey, user__id=user)
        elif survey is not None:
            # queryset = queryset.filter(survey__id=survey).exclude(user__id=self.request.user.id)
            queryset = queryset.filter(survey__id=survey)   
        elif user is not None:
            # queryset = queryset.filter(user__id=user).exclude(user__id=self.request.user.id)
            queryset = queryset.filter(user__id=user)

        return queryset
        

# temporary test
class ProjectUserv2ViewSet(viewsets.ModelViewSet):
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
        
        obj = MyMapLayout.objects.get(user_id=request.user.id, project_id=request.data['project'])

        myProjectUser_id = request.data['myProjectUser']
        SHMapping.objects.filter(projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id).delete()

        for i in range(len(shMyCategories)):
            
            try:
                
                shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
            except SHMapping.DoesNotExist:
                
                mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                mapObj.save()
        
        shProjectCategories = request.data['shProjectCategory']

        
        obj1 = ProjectMapLayout.objects.get(user_id=request.user.id, project_id=request.data['project'])

        for j in range(len(shProjectCategories)):

            try:
                
                shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
            except SHMapping.DoesNotExist:
                
                mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                mapObj1.save()

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
        myProjectUser_id = request.data['myProjectUser']

        try:
            obj = MyMapLayout.objects.get(user_id=request.user.id, project_id=data['project'])

            for i in range(len(shMyCategories)):
                try:
                    shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj.save()

        except MyMapLayout.DoesNotExist:
            obj = MyMapLayout.objects.create(user_id=request.user.id, project_id=data['project'])

            obj.user_id = request.user.id
            obj.project_id = data['project']
            obj.layout_json = ''

            for i in range(len(shMyCategories)):
                new_obj = ProjectUser.objects.get(id=projectUser_id)
                obj.projectUser.add(new_obj)

                try:
                    shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj.save()

            obj.save()

        shProjectCategories = request.data['shProjectCategory']

        try:
            obj1 = ProjectMapLayout.objects.get(user_id=request.user.id, project_id=data['project'])

            for j in range(len(shProjectCategories)):

                try:
                    
                    shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    
                    mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj1.save()

        except ProjectMapLayout.DoesNotExist:
            obj1 = ProjectMapLayout.objects.create(user_id=request.user.id, project_id=data['project'])

            obj1.user_id = request.user.id
            obj1.project_id = data['project']
            obj1.layout_json = ''

            for j in range(len(shProjectCategories)):
                new_obj1 = ProjectUser.objects.get(id=projectUser_id)
                obj1.projectUser.add(new_obj1)

                try:
                    
                    shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    
                    mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj1.save()
            
            obj1.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AcknowledgeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AOResponse.objects.all()
    serializer_class = AOResponseSerializer

    def get_queryset(self):
        queryset = AOResponse.objects.all()

        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey)

        return queryset

    def list(self, request, *args, **kwargs):

        response = super().list(request, *args, **kwargs)
        for i in range(len(response.data)):
            aoquestion_queryset = AOQuestion.objects.filter(id=response.data[i]['aoQuestion'])
            ao_serializer = AOQuestionSerializer(aoquestion_queryset, many=True)
            response.data[i]['aoQuestionData'] = ao_serializer.data
            response.data[i]['report'] = {
                "Sentiment": "ERROR",
                "MixedScore": 0,
                "NegativeScore": 0,
                "NeutralScore": 0,
                "PositiveScore": 0,
            }

            if response.data[i]['controlType'] == 'TEXT' or response.data[i]['controlType'] == 'MULTI_TOPICS':
                Text = response.data[i]['topicValue'] + " " + response.data[i]['commentValue']

                if response.data[i]['topicValue'] != "" or response.data[i]['commentValue'] != "":
                    sentimentData = comprehend.detect_sentiment(Text=Text, LanguageCode="en")
                    print(sentimentData)

                    # new
                    response.data[i]['integerValue'] = int(
                        abs(sentimentData["SentimentScore"]["Positive"] * 100))

                    if "Sentiment" in sentimentData:
                        response.data[i]['report']["Sentiment"] = sentimentData["Sentiment"]
                    if "SentimentScore" in sentimentData:
                        if "Mixed" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["MixedScore"] = sentimentData["SentimentScore"]["Mixed"]
                        if "Negative" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NegativeScore"] = sentimentData["SentimentScore"]["Negative"]
                        if "Neutral" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["NeutralScore"] = sentimentData["SentimentScore"]["Neutral"]
                        if "Positive" in sentimentData["SentimentScore"]:
                            response.data[i]['report']["PositiveScore"] = sentimentData["SentimentScore"]["Positive"]

        return response

class AcknowledgeDetailViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = SurveyByUserSerializer

    def get_queryset(self):
        queryset = ProjectUser.objects.all()
        user = self.request.query_params.get('user', None)
        if user is not None:
            queryset = queryset.filter(user__id=user)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        new_data = []
        project_ids = []
        for i in range(len(response.data)):
            if response.data[i]['survey']['project'] not in project_ids:
                project_ids.append(response.data[i]['survey']['project'])

        response.data = []
        for i in range(len(project_ids)):
            item = model_to_dict(Project.objects.get(id=project_ids[i]))
            response.data.append(item)

        return response


class SHCategoryForAcknowledgeViewSet(viewsets.ModelViewSet):
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

class SHMappingForAcknowledgeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = SHMapping.objects.all()
    serializer_class = SHMappingSerializer
    filterset_fields = ['shCategory']

class WordCloudView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        amqueryset = AMResponse.objects.all()
        aoqueryset = AOResponse.objects.all()

        survey = self.request.query_params.get('survey', None)
        projectUser = self.request.query_params.get('projectUser', None)

        if (survey is not None) & (projectUser is not None):
            amqueryset = amqueryset.filter(survey__id=survey, subProjectUser__id=projectUser)
            aoqueryset = aoqueryset.filter(survey__id=survey, subProjectUser__id=projectUser)
        elif survey is not None:
            amqueryset = amqueryset.filter(survey__id=survey)
            aoqueryset = aoqueryset.filter(survey__id=survey)
        elif projectUser is not None:
            amqueryset = amqueryset.filter(subProjectUser__id=projectUser)
            aoqueryset = aoqueryset.filter(subProjectUser__id=projectUser)
        
        amserializer = AMResponseSerializer(amqueryset, many=True)
        aoserializer = AOResponseSerializer(aoqueryset, many=True)

        res = amserializer.data + aoserializer.data

        # normal english stopwords
        stopwords = ['a', 'about', 'above', 'across', 'after']
        stopwords += ['afterwards', 'along', 'among', 'another']
        stopwords += ['again', 'against', 'all', 'almost', 'alone']
        stopwords += ['already', 'also', 'although', 'always', 'am']
        stopwords += ['amongst', 'amoungst', 'amount', 'an', 'and']
        stopwords += ['any', 'anyhow', 'anyone', 'anything', 'anyway']
        stopwords += ['anywhere', 'back', 'be', 'became', 'both']
        stopwords += ['are', 'aren\'t', 'around', 'as', 'at']
        stopwords += ['because', 'become', 'becomes', 'becoming', 'been']
        stopwords += ['before', 'beforehand', 'behind', 'being', 'below']
        stopwords += ['beside', 'besides', 'between', 'beyond', 'bill']
        stopwords += ['bottom', 'but', 'by', 'call', 'can']
        stopwords += ['co', 'computer', 'con', 'could', 'couldnt']
        stopwords += ['describe', 'detail', 'did', 'didn\'t', 'do']
        stopwords += ['cannot', 'cant', 'can\'t', 'couldn\'t', 'cry']
        stopwords += ['de', 'does', 'doesn\'t', 'eleven', 'else']
        stopwords += ['doing', 'don\'t', 'done', 'down', 'due']
        stopwords += ['during', 'each', 'eg', 'eight', 'either']
        stopwords += ['elsewhere', 'empty', 'enough', 'etc', 'even']
        stopwords += ['every', 'everyone', 'everything', 'everywhere', 'except']
        stopwords += ['ever', 'fire', 'first', 'found', 'get']
        stopwords += ['few', 'fifteen', 'fifty', 'fill', 'find']
        stopwords += ['five', 'for', 'former', 'formerly', 'forty']
        stopwords += ['four', 'from', 'front', 'full', 'further']
        stopwords += ['go', 'had', 'has', 'hasnt', 'have']
        stopwords += ['give', 'he', 'hence', 'her', 'he\'ll']
        stopwords += ['hadn\'t', 'hasn\'t', 'haven\'t', 'having', 'he\'d']
        stopwords += ['he\'s', 'here\'s', 'how\'s', 'hers', 'however']
        stopwords += ['here', 'hereafter', 'hereby', 'herein', 'hereupon']
        stopwords += ['herself', 'him', 'himself', 'his', 'how']
        stopwords += ['hundred', 'i', 'ie', 'if', 'in']
        stopwords += ['i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'isn\'t']
        stopwords += ['inc', 'indeed', 'it\'s', 'itself', 'keep']
        stopwords += ['interest', 'into', 'is', 'it', 'its']
        stopwords += ['last', 'latter', 'latterly', 'least', 'less']
        stopwords += ['many', 'may', 'me', 'meanwhile', 'might']
        stopwords += ['let\'s', 'ltd', 'made', 'mill', 'mine']
        stopwords += ['more', 'moreover', 'most', 'mostly', 'move']
        stopwords += ['must', 'mustn\'t', 'my', 'myself', 'name']
        stopwords += ['much', 'namely', 'neither', 'never', 'none']
        stopwords += ['nevertheless', 'next', 'nine', 'no', 'nobody']
        stopwords += ['noone', 'nor', 'not', 'nothing', 'now']
        stopwords += ['off', 'often', 'on','once', 'one']
        stopwords += ['nowhere', 'of', 'only', 'onto', 'or']
        stopwords += ['other', 'others', 'ought', 'otherwise', 'our']
        stopwords += ['out', 'over', 'own', 'part', 'per']
        stopwords += ['ours', 'ourselves', 'perhaps', 'please', 'see']
        stopwords += ['put', 'rather', 're', 's', 'same']
        stopwords += ['seeming', 'seems', 'serious', 'several', 'shan\'t']
        stopwords += ['seem', 'seemed', 'she', 'should', 'there\'s']
        stopwords += ['she\'d', 'she\'ll', 'she\'s', 'shouldn\'t', 'that\'s']
        stopwords += ['show', 'side', 'since', 'sincere', 'six']
        stopwords += ['sixty', 'so', 'take', 'them', 'themselves']
        stopwords += ['some', 'somehow', 'someone', 'something', 'sometime']
        stopwords += ['sometimes', 'somewhere', 'still', 'such', 'system']
        stopwords += ['ten', 'than', 'that', 'the', 'their']
        stopwords += ['then', 'thence', 'there', 'thereafter', 'thereby']
        stopwords += ['therefore', 'therein', 'thereupon', 'these', 'they']
        stopwords += ['they\'d', 'they\'ll', 'they\'re', 'they\'ve', 'though']
        stopwords += ['thick', 'thin', 'third', 'this', 'those']
        stopwords += ['three', 'through', 'throughout', 'thru', 'thus']
        stopwords += ['to', 'twelve', 'up', 'upon', 'we']
        stopwords += ['together', 'too', 'top', 'toward', 'towards']
        stopwords += ['twenty', 'two', 'un', 'under', 'until']
        stopwords += ['us', 'very', 'via', 'was', 'wasn\'t']
        stopwords += ['we\'d', 'we\'ll', 'we\'re', 'we\'ve', 'weren\'t']
        stopwords += ['well', 'were', 'what', 'what\'s', 'when\'s']
        stopwords += ['whatever', 'when', 'whence', 'whenever', 'where']
        stopwords += ['whereafter', 'whereas', 'whereby', 'wherein', 'whereupon']
        stopwords += ['wherever', 'whether', 'which', 'while', 'whither']
        stopwords += ['where\'s', 'who', 'will', 'with', 'your']
        stopwords += ['who\'s', 'why\'s', 'won\'t', 'wouldn\'t', 'yours']
        stopwords += ['whoever', 'whole', 'whom', 'whose', 'why']
        stopwords += ['within', 'without', 'would', 'yet', 'you']
        stopwords += ['you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'yourself']
        stopwords += ['yourselves']

        # MySQL Stopwords
        stopwords += ['a\'s', 'accordingly', 'allows', 'anybody', 'anyways']
        stopwords += ['appropriate', 'aside', 'available', 'certain', 'com']
        stopwords += ['consider', 'corresponding', 'according', 'actually', 'ain\'t']
        stopwords += ['allow', 'apart', 'appear', 'appreciate', 'ask']
        stopwords += ['asking', 'associated', 'away', 'awfully', 'believe']
        stopwords += ['best', 'better', 'both', 'brief', 'c\'mon']
        stopwords += ['c\'s', 'came', 'cause', 'causes', 'certainly']
        stopwords += ['changes', 'clearly', 'come', 'comes', 'concerning']
        stopwords += ['consequently', 'considering', 'contain', 'containing', 'contains']
        stopwords += ['course', 'currently', 'definitely', 'described', 'despite']
        stopwords += ['different', 'downwards','edu', 'entirely', 'especially']
        stopwords += ['et', 'exactly', 'example', 'far', 'fifth']
        stopwords += ['followed', 'following', 'follows', 'forth', 'furthermore']
        stopwords += ['gets', 'getting', 'given', 'gives', 'goes']
        stopwords += ['going', 'gone', 'got', 'gotten', 'greetings']
        stopwords += ['happens', 'hardly', 'hello', 'help', 'hi']
        stopwords += ['hither', 'hopefully', 'howbeit', 'ignored', 'immediate']
        stopwords += ['inasmuch', 'indicate', 'indicated', 'indicates', 'inner']
        stopwords += ['insofar', 'instead', 'inward', 'just', 'keeps']
        stopwords += ['kept', 'know', 'known', 'knows', 'lately']
        stopwords += ['later', 'lest', 'let', 'like', 'liked']
        stopwords += ['likely', 'little', 'look', 'looking', 'looks']
        stopwords += ['mainly', 'maybe', 'mean', 'merely', 'nd']
        stopwords += ['near', 'nearly', 'necessary', 'need', 'needs']
        stopwords += ['new', 'non', 'normally', 'novel', 'obviously']
        stopwords += ['oh', 'ok', 'okay', 'old', 'ones']
        stopwords += ['outside', 'overall', 'particular', 'particularly', 'placed']
        stopwords += ['plus', 'possible', 'presumably', 'probably', 'provides']
        stopwords += ['que', 'quite', 'qv', 'rd', 'really']
        stopwords += ['reasonably', 'regarding', 'regardless', 'regards', 'relatively']
        stopwords += ['respectively', 'right', 'said', 'saw', 'say']
        stopwords += ['saying', 'says', 'second', 'secondly', 'seeing']
        stopwords += ['seen', 'self', 'selves', 'sensible', 'sent']
        stopwords += ['seriously', 'seven', 'shall', 'somewhat', 'soon']
        stopwords += ['sorry', 'specified', 'specify', 'specifying', 'sub']
        stopwords += ['sup', 'sure', 't\'s', 'taken', 'tell']
        stopwords += ['tends', 'th', 'thank', 'thanks', 'thanx']
        stopwords += ['thats', 'theirs', 'theres', 'think', 'thorough']
        stopwords += ['thoroughly', 'took', 'tried', 'tries', 'truly']
        stopwords += ['try', 'trying', 'twice', 'unfortunately', 'unless']
        stopwords += ['unlikely', 'unto', 'use', 'used', 'useful']
        stopwords += ['uses', 'using', 'usually', 'value', 'various']
        stopwords += ['viz', 'vs', 'want', 'wants', 'way']
        stopwords += ['welcome', 'went', 'willing', 'wish', 'wonder']
        stopwords += ['yes', 'zero']

        wordstring = ''
        for i in range(len(res)):
            if res[i]['topicValue'] != "":
                wordstring += ' ' + res[i]['topicValue']
            if res[i]['commentValue'] != "":
                wordstring += ' ' + res[i]['commentValue']
            if res[i]['skipValue'] != "":
                wordstring += ' ' + res[i]['skipValue']
            if res[i]['topicTags'] != "":
                wordstring += ' ' + res[i]['topicTags']
            if res[i]['commentTags'] != "":
                wordstring += ' ' + res[i]['commentTags']

        # wordList = wordstring.split()
        wordList = re.findall(r"[\w\']+", wordstring.lower())
        filteredWordList = [w for w in wordList if w not in stopwords]
        wordfreq = [filteredWordList.count(p) for p in filteredWordList]
        dictionary = dict(list(zip(filteredWordList, wordfreq)))

        aux = [(dictionary[key], key) for key in dictionary]
        aux.sort()
        aux.reverse()
        
        return Response(aux)

class BubbleChartView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []
    
    def get(self, format=None):
        amqueryset = AMResponse.objects.all()
        aoqueryset = AOResponse.objects.all()

        survey = self.request.query_params.get('survey', None)
        projectUser = self.request.query_params.get('projectUser', None)
    
    ### t
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        survey = self.request.query_params.get('survey', None)
        driver = self.request.query_params.get('driver', None)

        for i in range(len(response.data)):
            amsubdriver_queryset = ''
            aosubdriver_queryset = ''
            if (survey is not None) & (driver is not None):
                amsubdriver_queryset = AMQuestion.objects.filter(survey__id=survey, driver__id=driver).values('subdriver').distinct()
                aosubdriver_queryset = AOQuestion.objects.filter(survey__id=survey, driver__id=driver).values('subdriver').distinct()
            elif survey is not None:
                amsubdriver_queryset = AMQuestion.objects.filter(survey__id=survey).values('subdriver').distinct()
                aosubdriver_queryset = AOQuestion.objects.filter(survey__id=survey).values('subdriver').distinct()
            elif driver is not None:
                amsubdriver_queryset = AMQuestion.objects.filter(driver__id=driver).values('subdriver').distinct()
                aosubdriver_queryset = AOQuestion.objects.filter(driver__id=driver).values('subdriver').distinct()
            else:
                amsubdriver_queryset = AMQuestion.objects.all().values('subdriver').distinct()
                aosubdriver_queryset = AOQuestion.objects.all().values('subdriver').distinct()

            amsubdriver_serializer = AMQuestionSubDriverSerializer(amsubdriver_queryset, many=True)
            aosubdriver_serializer = AOQuestionSubDriverSerializer(aosubdriver_queryset, many=True)

            response.data[i]['subdriver'] = []
            response.data[i]['subdriver'] = []

            for item in amsubdriver_serializer.data:
                response.data[i]['subdriver'].append(item['subdriver'])
            for item in aosubdriver_serializer.data:
                if not item['subdriver'] in response.data[i]['subdriver']:
                    response.data[i]['subdriver'].append(item['subdriver'])

        return response
    ### t
    
class SubDriverViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Driver.objects.all()
    serializer_class = DriverSubDriverSerializer

    def get_queryset(self):
        queryset = Driver.objects.all()
        survey = self.request.query_params.get('survey', None)
        driver = self.request.query_params.get('driver', None)

        if (survey is not None) & (driver is not None):
            queryset = queryset.filter(survey__id=survey, id=driver)
        elif survey is not None:
            queryset = queryset.filter(survey__id=survey)
        elif driver is not None:
            queryset = queryset.filter(id=driver)

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        survey = self.request.query_params.get('survey', None)
        driver = self.request.query_params.get('driver', None)

        for i in range(len(response.data)):
            amsubdriver_queryset = ''
            aosubdriver_queryset = ''
            if (survey is not None) & (driver is not None):
                amsubdriver_queryset = AMQuestion.objects.filter(survey__id=survey, driver__id=driver).values('subdriver').distinct()
                aosubdriver_queryset = AOQuestion.objects.filter(survey__id=survey, driver__id=driver).values('subdriver').distinct()
            elif survey is not None:
                amsubdriver_queryset = AMQuestion.objects.filter(survey__id=survey).values('subdriver').distinct()
                aosubdriver_queryset = AOQuestion.objects.filter(survey__id=survey).values('subdriver').distinct()
            elif driver is not None:
                amsubdriver_queryset = AMQuestion.objects.filter(driver__id=driver).values('subdriver').distinct()
                aosubdriver_queryset = AOQuestion.objects.filter(driver__id=driver).values('subdriver').distinct()
            else:
                amsubdriver_queryset = AMQuestion.objects.all().values('subdriver').distinct()
                aosubdriver_queryset = AOQuestion.objects.all().values('subdriver').distinct()

            amsubdriver_serializer = AMQuestionSubDriverSerializer(amsubdriver_queryset, many=True)
            aosubdriver_serializer = AOQuestionSubDriverSerializer(aosubdriver_queryset, many=True)

            response.data[i]['subdriver'] = []
            response.data[i]['subdriver'] = []

            for item in amsubdriver_serializer.data:
                response.data[i]['subdriver'].append(item['subdriver'])
            for item in aosubdriver_serializer.data:
                if not item['subdriver'] in response.data[i]['subdriver']:
                    response.data[i]['subdriver'].append(item['subdriver'])

        return response