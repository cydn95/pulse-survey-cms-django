import os
import re
import boto3
import json

from django.http import HttpResponse
from django.middleware import csrf
from django.core.mail import send_mail, EmailMultiAlternatives
from django.dispatch import receiver
from django.urls import reverse

from django_rest_passwordreset.signals import reset_password_token_created

from django.template.loader import get_template, render_to_string
from django.conf import settings

from pathlib import Path
from email.mime.image import MIMEImage

from jinja2 import Undefined

from snippets.serializers import AMResponseAcknowledgementSerializerForFlag, AMResponseForSummarySerializer, AMResponseForAdvisorSerializer, AMResponseForDriverAnalysisSerializer, AOResponseForDriverAnalysisSerializer, AOResponseTopPositiveNegativeSerializer, KeyThemeUpDownVoteSerializer, AMResponseAcknowledgementSerializer, AOResponseForMatrixSerializer, AOResponseAcknowledgementSerializer, AMResponseForReportSerializer, AOResponseForReportSerializer, ProjectUserForReportSerializer, ProjectUserForAdvisorSerializer, AMQuestionSubDriverSerializer, AOQuestionSubDriverSerializer, DriverSubDriverSerializer, ProjectSerializer, ToolTipGuideSerializer, SurveySerializer, NikelMobilePageSerializer, ConfigPageSerializer, UserAvatarSerializer, SHMappingSerializer, ProjectVideoUploadSerializer, AMQuestionSerializer, AOQuestionSerializer, StakeHolderSerializer, SHCategorySerializer, MyMapLayoutStoreSerializer, ProjectMapLayoutStoreSerializer, UserBySurveySerializer, SurveyByUserSerializer, SkipOptionSerializer, DriverSerializer, AOQuestionSerializer, OrganizationSerializer, OptionSerializer, ProjectUserSerializer, SHGroupSerializer, UserSerializer, PageSettingSerializer, PageSerializer, AMResponseSerializer, AMResponseTopicSerializer, AOResponseSerializer, AOResponseTopicSerializer, AOPageSerializer, TeamSerializer, SegmentSerializer

from rest_framework import generics, permissions, renderers, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from page_setting.models import PageSetting
from cms.models import Page
from aboutme.models import AMResponseAcknowledgement, AMQuestion, AMResponse, AMResponseTopic, AMQuestionSHGroup
from snippets.models import EmailRecord
from aboutothers.models import AOResponseAcknowledgement, AOResponse, AOResponseTopic, AOPage
from team.models import Team
from shgroup.models import KeyThemeUpDownVote, SHGroup, ProjectUser, MyMapLayout, ProjectMapLayout, SHCategory, SHMapping, Segment
from option.models import Option, SkipOption
from organization.models import Organization, UserAvatar, UserTeam, UserGuideMode
from aboutothers.models import AOQuestion
from survey.models import ToolTipGuide, Survey, Driver, Project, ProjectVideoUpload, ConfigPage, NikelMobilePage
from django.forms.models import model_to_dict
from django.db.models import Q, Count, Avg

from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer
from smtplib import SMTPException

#initialize comprehend module
comprehend = boto3.client(service_name='comprehend', region_name='us-east-2')

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

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        # 'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        # 'reset_password_url': "{}?token={}".format(instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')), reset_password_token.key),
        'button_url': "https://pulse.projectai.com/reset-password?token={}".format(reset_password_token.key)
    }

    subject = 'Password reset'
    message = get_template('emailv3.html').render(context)
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [reset_password_token.user.email]

    email = EmailMultiAlternatives(subject=subject, body=message, from_email=email_from, to=recipient_list)
    email.attach_alternative(message, "text/html")
    email.content_subtype = 'html'
    email.mixed_subtype = 'related'

    try:
        email.send()
        emailRecord = EmailRecord(recipient=reset_password_token.user.email, message=message)
        emailRecord.save()
    except SMTPException as e:
        print('There was an error sending an email: ', e)

    # # render email text
    # email_html_message = render_to_string('email/user_reset_password.html', context)
    # email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    # msg = EmailMultiAlternatives(
    #     # title:
    #     "Password Reset for {title}".format(title="Some website title"),
    #     # message:
    #     email_plaintext_message,
    #     # from:
    #     "pulse@projectai.com",
    #     # to:
    #     [reset_password_token.user.email]
    # )
    # msg.attach_alternative(email_html_message, "text/html")
    # msg.send()

def preApiCheck(survey, projectUser):
    # prefix check
    # the logged in user has to response fully

    try:
        isSuperUser = ProjectUser.objects.get(id=projectUser)
        responsePercent = SHGroup.objects.get(
            survey__id=survey, id=isSuperUser.shGroup_id).responsePercent
        if isSuperUser.isSuperUser == True:
            return 201  # super user

        prefAmQuestionQueryset = AMQuestion.objects.filter(survey__id=survey, shGroup__in=[isSuperUser.shGroup_id])
        prefAmQuestionSerializer = AMQuestionSerializer(prefAmQuestionQueryset, many=True)
        prefAmQuestionData = prefAmQuestionSerializer.data

        totalCnt = 0
        answeredCnt = 0
        for i in range(len(prefAmQuestionData)):
            totalCnt = totalCnt + 1
            ret = AMResponse.objects.filter(
                    projectUser_id=projectUser, survey_id=survey, amQuestion_id=prefAmQuestionData[i]['id'], latestResponse=True)
            if (len(ret) > 0):
                if ret[0].controlType == 'MULTI_TOPICS':
                    if len(ret[0].topicValue) > 0:
                        answeredCnt = answeredCnt + 1
                else:
                    answeredCnt = answeredCnt + 1
            # else:
            #     return 228

        if totalCnt > 0:
            currentPercent = answeredCnt * 100 / totalCnt
            if currentPercent < responsePercent:
                return 228
        else:
            return 228
                
    except ProjectUser.DoesNotExist:
        return 404

    except SHGroup.DoesNotExist:
        return 404

    # 3 people has to response to this user
    thresholdCnt = Survey.objects.get(id=survey).anonymityThreshold

    # prefAryProjectUsers = []
    # prefTestResultQueryset = AMResponse.objects.all().filter(survey__id=survey)
    # prefTestResultSerializer = AMResponseForDriverAnalysisSerializer(prefTestResultQueryset, many=True)
    # prefTestResultData = prefTestResultSerializer.data

    projectUserCnt = AMResponse.objects.filter(survey__id=survey).values_list('projectUser', flat=True).distinct()
    # for i in range(len(prefTestResultData)): 
    #     if prefTestResultData[i]['projectUser']["id"] not in prefAryProjectUsers:
    #             prefAryProjectUsers.append(
    #                 prefTestResultData[i]['projectUser']["id"])
    
    # if (len(prefAryProjectUsers) < thresholdCnt):

    totalCompleteCnt = 0
    # tempTest = []
    for i in range(len(projectUserCnt)):
        tempProjectUserInfo = ProjectUser.objects.get(id=projectUserCnt[i])
        tempResponsePercent = SHGroup.objects.get(id=tempProjectUserInfo.shGroup_id).responsePercent
        # tempTest.append(tempProjectUserInfo.shGroup_id)
        tempAmQuestionQueryset = AMQuestion.objects.filter(
            survey__id=survey, shGroup__in=[tempProjectUserInfo.shGroup_id])
        tempAmQuestionSerializer = AMQuestionSerializer(
            tempAmQuestionQueryset, many=True)
        tempAmQuestionData = tempAmQuestionSerializer.data

        tempCnt = 0
        tempAnsweredCnt = 0
        for j in range(len(tempAmQuestionData)):
            tempCnt = tempCnt + 1
            tempRet = AMResponse.objects.filter(projectUser_id=projectUserCnt[i], survey_id=survey, amQuestion_id=tempAmQuestionData[j]['id'], latestResponse=True)
            if (len(tempRet) > 0):
                # tempAnsweredCnt = tempAnsweredCnt + 1
                if tempRet[0].controlType == 'MULTI_TOPICS':
                    if len(tempRet[0].topicValue) > 0:
                        tempAnsweredCnt = tempAnsweredCnt + 1
                else:
                    tempAnsweredCnt = tempAnsweredCnt + 1

        if tempCnt > 0:
            tempCurrentPercent = tempAnsweredCnt * 100 / tempCnt
            if tempCurrentPercent >= tempResponsePercent:
                totalCompleteCnt = totalCompleteCnt + 1
    # return tempTest
    if totalCompleteCnt < thresholdCnt:
        return 227

    return 200


# class AOResponseAcknowledgementViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
#     queryset = AOResponseAcknowledgement.objects.all()
#     serializer_class = AOResponseAcknowledgementSerializer

#     def get_queryset(self):
#         queryset = AMResponseAcknowledgement.objects.all()

#         amresponse = self.request.query_params.get('response', None)
#         projectUser = self.request.query_params.get('projectuser', None)

#         if (amresponse is not None) & (projectUser is not None):
#             queryset = queryset.filter(amResponse__id=amresponse, projectUser__id=projectUser)
        
#         if amresponse is not None:
#             queryset = queryset.filter(amResponse__id=amresponse)

#         if projectUser is not None:
#             queryset = queryset.filter(projectUser__id=projectUser)
            
#         return queryset

# acknowledgement api
class AMResponseAcknowledgementViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponseAcknowledgement.objects.all()
    serializer_class = AMResponseAcknowledgementSerializer

    def get_queryset(self):
        queryset = AMResponseAcknowledgement.objects.all()

        amresponse = self.request.query_params.get('response', None)
        projectUser = self.request.query_params.get('projectuser', None)

        if (amresponse is not None) & (projectUser is not None):
            queryset = queryset.filter(amResponse__id=amresponse, projectUser__id=projectUser)
        
        if amresponse is not None:
            queryset = queryset.filter(amResponse__id=amresponse)

        if projectUser is not None:
            queryset = queryset.filter(projectUser__id=projectUser)

        return queryset

class KeyThemeUpDownVoteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = KeyThemeUpDownVote.objects.all()
    serializer_class = KeyThemeUpDownVoteSerializer

    def get_queryset(self):
        queryset = KeyThemeUpDownVote.objects.all()

        keyTheme = self.request.query_params.get('key', None)
        voteValue = self.request.query_params.get('vote', None)     # 1: upvote    -1: downvote

        if (keyTheme is not None) & (voteValue is not None):
            queryset = queryset.filter(keyTheme=keyTheme, voteValue=voteValue)

        if keyTheme is not None:
            queryset = queryset.filter(keyTheme=keyTheme)
        
        if voteValue is not None:
            queryset = queryset.filter(voteValue=voteValue)

        return queryset

# updated amresponse api
class AMResponseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if "items" in request.data else request.data
        many = isinstance(data, list)

        textList = []
        sentimentData = []

        tempData = [data[i:i + 25] for i in range(0, len(data), 25)]
        if many == True:
            for i in range(len(tempData)):
                for item in tempData[i]:
                    if item['controlType'] == "MULTI_TOPICS":
                        amresponsetopic_queryset = AMResponseTopic.objects.filter(
                            amQuestion_id=item['amQuestion'], responseUser_id=item['subProjectUser'])
                        amresponsetopic_serializer = AMResponseTopicSerializer(
                            amresponsetopic_queryset, many=True)
                        amresponsetopic_data = amresponsetopic_serializer.data
                        temptopictext = " "
                        for j in range(len(amresponsetopic_data)):
                            temptopictext = temptopictext + " " + amresponsetopic_data[j]['topicName']
                        textList = textList + [temptopictext]
                    else:
                        temptopictext = item['topicValue'] + " " + item['commentValue']
                        textList = textList + [temptopictext]
                tempSentimentData = comprehend.batch_detect_sentiment(TextList=textList, LanguageCode="en")
                sentimentData = sentimentData + tempSentimentData['ResultList']
                textList = []

        if many == True:
            for i in range(len(data)):
                if data[i]['controlType'] == "TEXT" or data[i]['controlType'] == "MULTI_TOPICS":
                    # 2021-07-31
                    if sentimentData[i]['Sentiment'] == "POSITIVE":
                        data[i]['integerValue'] = int(abs(sentimentData[i]['SentimentScore']['Positive'] * 100))
                        # data[i]['integerValue'] = 100
                    elif sentimentData[i]['Sentiment'] == "NEGATIVE":
                        data[i]['integerValue'] = 100 - int(abs(sentimentData[i]['SentimentScore']['Negative'] * 100))
                        # data[i]['integerValue'] = 10
                    else:
                        if sentimentData[i]['SentimentScore']['Positive'] > sentimentData[i]['SentimentScore']['Negative']:
                            data[i]['integerValue'] = 55
                        elif sentimentData[i]['SentimentScore']['Positive'] == sentimentData[i]['SentimentScore']['Negative']:
                            data[i]['integerValue'] = 45
                        else:
                            data[i]['integerValue'] = 35
                
                    # obj = AMResponse.objects.get(survey_id=data[i]['survey'], project_id=data[i]['project'], projectUser_id=data[i]['projectUser'], subProjectUser_id=data[i]['subProjectUser'], amQuestion_id=data[i]['amQuestion'], latestResponse=True)
                tempItem = AMResponse.objects.filter(survey_id=data[i]['survey'], project_id=data[i]['project'], projectUser_id=data[i]['projectUser'],
                                                 subProjectUser_id=data[i]['subProjectUser'], amQuestion_id=data[i]['amQuestion'], latestResponse=True)
                if (len(tempItem) > 0):
                    saveStatus = False
                    for oldItem in tempItem:
                        obj = oldItem
                        if obj.topicValue != data[i]['topicValue'] or obj.commentValue != data[i]['commentValue'] or obj.integerValue != data[i]['integerValue'] or obj.skipValue != data[i]['skipValue'] or obj.topicTags != data[i]['topicTags'] or obj.commentTags != data[i]['commentTags']:
                            obj.latestResponse = False
                            obj.save()
                            response = AMResponseAcknowledgement.objects.filter(amResponse_id=obj.id)

                            if saveStatus == False:
                                obj1 = AMResponse(amQuestion_id=data[i]['amQuestion'], projectUser_id=data[i]['projectUser'], subProjectUser_id=data[i]['subProjectUser'], survey_id=data[i]['survey'], project_id=data[i]['project'],
                                controlType=data[i]['controlType'], integerValue=data[i]['integerValue'], topicValue=data[i]['topicValue'], commentValue=data[i]['commentValue'], skipValue=data[i]['skipValue'], topicTags=data[i]['topicTags'], commentTags=data[i]['commentTags'], latestResponse=True)
                                obj1.save()
                                if len(response) > 0:
                                    response[0].amResponse_id = obj1.id
                                    response[0].save()
                                saveStatus = True
                    # obj = tempItem[0]
                    # if obj.topicValue != data[i]['topicValue'] or obj.commentValue != data[i]['commentValue'] or obj.integerValue != data[i]['integerValue'] or obj.skipValue != data[i]['skipValue'] or obj.topicTags != data[i]['topicTags'] or obj.commentTags != data[i]['commentTags']:
                    #     obj.latestResponse = False

                    #     obj.save()

                    
                else:
                    obj = AMResponse(amQuestion_id=data[i]['amQuestion'], projectUser_id=data[i]['projectUser'], subProjectUser_id=data[i]['subProjectUser'], survey_id=data[i]['survey'], project_id=data[i]['project'], controlType=data[i]['controlType'], integerValue=data[i]['integerValue'], topicValue=data[i]['skipValue'], topicTags=data[i]['topicTags'], commentTags=data[i]['commentTags'], latestResponse=True)
                    obj.save()
        elif many == False:
            defaults = data
            
                # obj = AMResponse.objects.get(survey_id=defaults['survey'], project_id=defaults['project'], projectUser_id=defaults['projectUser'], subProjectUser_id=defaults['subProjectUser'], amQuestion_id=defaults['amQuestion'], latestResponse=True)
            tempItem = AMResponse.objects.filter(survey_id=defaults['survey'], project_id=defaults['project'], projectUser_id=defaults['projectUser'],
                                             subProjectUser_id=defaults['subProjectUser'], amQuestion_id=defaults['amQuestion'], latestResponse=True)
            if (len(tempItem) > 0):
                for oldItem in tempItem:
                    obj = oldItem
                    obj.latestResponse = False
                    obj.save()

                # obj = tempItem[0]

                # if obj.topicValue != defaults['topicValue'] or obj.commentValue != defaults['commentValue'] or obj.integerValue != defaults['integerValue'] or obj.skipValue != defaults['skipValue'] or obj.topicTags != defaults['topicTags'] or obj.commentTags != defaults['commentTags']:
                #     obj.latestResponse = False
                #     obj.save()

                if defaults['controlType'] == "TEXT" or defaults['controlType'] == "MULTI_TOPICS":
                    text = defaults["topicValue"] + \
                        " " + defaults["commentValue"]

                    sentimentResult = comprehend.detect_sentiment(
                        Text=text, LanguageCode="en")
                    # defaults["integerValue"] = int(abs(sentimentResult["SentimentScore"]["Positive"] * 100))
                    # 2021-07-31
                    if sentimentResult['Sentiment'] == "POSITIVE":
                        defaults['integerValue'] = int(abs(sentimentResult['SentimentScore']['Positive'] * 100))
                    elif sentimentResult['Sentiment'] == "NEGATIVE":
                        defaults['integerValue'] = 100 - int(abs(sentimentResult['SentimentScore']['Negative'] * 100))
                    else:
                        if sentimentResult['SentimentScore']['Positive'] > sentimentResult['SentimentScore']['Negative']:
                            defaults['integerValue'] = 55
                        elif sentimentResult['SentimentScore']['Positive'] == sentimentResult['SentimentScore']['Negative']:
                            defaults['integerValue'] = 45
                        else:
                            defaults['integerValue'] = 35
                            
                obj1 = AMResponse(amQuestion_id=defaults['amQuestion'], projectUser_id=defaults['projectUser'], subProjectUser_id=defaults['subProjectUser'], survey_id=defaults['survey'], project_id=defaults['project'], controlType=defaults['controlType'], integerValue=defaults['integerValue'], topicValue=defaults['topicValue'], commentValue=defaults['commentValue'], skipValue=defaults['skipValue'], topicTags=defaults['topicTags'], commentTags=defaults['commentTags'], latestResponse=True)
                obj1.save()
            else:
                if defaults['controlType'] == "TEXT" or defaults['controlType'] == "MULTI_TOPICS":
                    text = defaults['topicValue'] + " " + defaults['commentValue']

                    sentimentResult = comprehend.detect_sentiment(Text=text, LanguageCode="en")
                    # defaults['integerValue'] = int(abs(sentimentResult["SentimentScore"]["Positive"] * 100))
                    # 2021-07-31
                    if sentimentResult['Sentiment'] == "POSITIVE":
                        defaults['integerValue'] = int(
                            abs(sentimentResult['SentimentScore']['Positive'] * 100))
                    elif sentimentResult['Sentiment'] == "NEGATIVE":
                        defaults['integerValue'] = 100 - int(abs(sentimentResult['SentimentScore']['Negative'] * 100))
                    else:
                        if sentimentResult['SentimentScore']['Positive'] > sentimentResult['SentimentScore']['Negative']:
                            defaults['integerValue'] = 55
                        elif sentimentResult['SentimentScore']['Positive'] == sentimentResult['SentimentScore']['Negative']:
                            defaults['integerValue'] = 45
                        else:
                            defaults['integerValue'] = 35

                obj = AMResponse(amQuestion_id=defaults['amQuestion'], projectUser_id=defaults['projectUser'], subProjectUser_id=defaults['subProjectUser'], survey_id=defaults['survey'], project_id=defaults['project'], controlType=defaults['controlType'], integerValue=defaults['integerValue'], topicValue=defaults['topicValue'], commentValue=defaults['commentValue'], skipValue=defaults['skipValue'], topicTags=defaults['topicTags'], commentTags=defaults['commentTags'], latestResponse=True)
                obj.save()

        return Response({'data': data, "sentiment": sentimentData}, status=status.HTTP_201_CREATED)

# amresponsetopic api
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

# updated batch comprened aoresponse api
class AOResponseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AOResponse.objects.all()
    serializer_class = AOResponseSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if "items" in request.data else request.data
        many = isinstance(data, list)

        textList = []
        sentimentData = []

        tempData = [data[i:i + 25] for i in range(0, len(data), 25)]
        if many == True:
            for i in range(len(tempData)):
                for item in tempData[i]:
                    if item['controlType'] == "MULTI_TOPICS":
                        aoresponsetopic_queryset = AOResponseTopic.objects.filter(
                            aoQuestion_id=item['aoQuestion'], responseUser_id=item['subProjectUser'])
                        aoresponsetopic_serializer = AOResponseTopicSerializer(
                            aoresponsetopic_queryset, many=True)
                        aoresponsetopic_data = aoresponsetopic_serializer.data
                        temptopictext = " "
                        for j in range(len(aoresponsetopic_data)):
                            temptopictext = temptopictext + " " + aoresponsetopic_data[j]['topicName']
                        textList.append(temptopictext)
                    else:
                        textList.append(item['topicValue'] + " " + item['commentValue'])
                tempSentimentData = comprehend.batch_detect_sentiment(TextList=textList, LanguageCode="en")
                sentimentData = sentimentData + tempSentimentData['ResultList']
                textList = []

        if many == True:
            for i in range(len(data)):
                if data[i]['controlType'] == "TEXT" or data[i]['controlType'] == "MULTI_TOPICS":
                    # 2021-07-31
                    if sentimentData[i]['Sentiment'] == "POSITIVE":
                        data[i]['integerValue'] = int(abs(sentimentData[i]['SentimentScore']['Positive'] * 100))
                    elif sentimentData[i]['Sentiment'] == "NEGATIVE":
                        data[i]['integerValue'] = 100 - int(abs(sentimentData[i]['SentimentScore']['Negative'] * 100))
                    else:
                        if sentimentData[i]['SentimentScore']['Positive'] > sentimentData[i]['SentimentScore']['Negative']:
                            data[i]['integerValue'] = 55
                        elif sentimentData[i]['SentimentScore']['Positive'] == sentimentData[i]['SentimentScore']['Negative']:
                            data[i]['integerValue'] = 45
                        else:
                            data[i]['integerValue'] = 35
                    # data[i]['integerValue'] = int(abs(sentimentData[i]['SentimentScore']['Positive'] * 100))
                
                    # obj = AOResponse.objects.get(survey_id=data[i]['survey'], project_id=data[i]['project'], projectUser_id=data[i]['projectUser'], subProjectUser_id=data[i]['subProjectUser'], aoQuestion_id=data[i]['aoQuestion'], latestResponse=True)
                tempItem = AOResponse.objects.filter(survey_id=data[i]['survey'], project_id=data[i]['project'], projectUser_id=data[i]['projectUser'], subProjectUser_id=data[i]['subProjectUser'], aoQuestion_id=data[i]['aoQuestion'], latestResponse=True)

                if (len(tempItem) > 0):
                    saveStatus = False
                    for oldItem in tempItem:
                        obj = oldItem
                        if obj.topicValue != data[i]['topicValue'] or obj.commentValue != data[i]['commentValue'] or obj.integerValue != data[i]['integerValue'] or obj.skipValue != data[i]['skipValue'] or obj.topicTags != data[i]['topicTags'] or obj.commentTags != data[i]['commentTags']:
                            obj.latestResponse = False
                            obj.save()

                            if saveStatus == False:
                                obj1 = AOResponse(aoQuestion_id=data[i]['aoQuestion'], projectUser_id=data[i]['projectUser'], subProjectUser_id=data[i]['subProjectUser'], shCategory_id=data[i]['shCategory'], survey_id=data[i]['survey'], project_id=data[i]['project'], controlType=data[i]['controlType'], integerValue=data[i]['integerValue'], topicValue=data[i]['topicValue'], commentValue=data[i]['commentValue'], skipValue=data[i]['skipValue'], topicTags=data[i]['topicTags'], commentTags=data[i]['commentTags'], latestResponse=True)
                                obj1.save()

                                saveStatus = True
                    # obj = tempItem[0]

                    # if obj.topicValue != data[i]['topicValue'] or obj.commentValue != data[i]['commentValue'] or obj.integerValue != data[i]['integerValue'] or obj.skipValue != data[i]['skipValue'] or obj.topicTags != data[i]['topicTags'] or obj.commentTags != data[i]['commentTags']:
                    #     obj.latestResponse = False

                    #     obj.save()
                        
                    
                else:
                    obj = AOResponse(aoQuestion_id=data[i]['aoQuestion'], projectUser_id=data[i]['projectUser'], subProjectUser_id=data[i]['subProjectUser'], shCategory_id=data[i]['shCategory'], survey_id=data[i]['survey'], project_id=data[i]['project'], controlType=data[i]['controlType'], integerValue=data[i]['integerValue'], topicValue=data[i]['topicValue'], commentValue=data[i]['commentValue'], skipValue=data[i]['skipValue'], topicTags=data[i]['topicTags'], commentTags=data[i]['commentTags'], latestResponse=True)
                    obj.save()
        elif many == False:
            defaults = data
            
                # obj = AOResponse.objects.get(survey_id=defaults['survey'], project_id=defaults['project'], projectUser_id=defaults['projectUser'],
                                            #  subProjectUser_id=defaults['subProjectUser'], aoQuestion_id=defaults['aoQuestion'], latestResponse=True)
            tempItem = AOResponse.objects.filter(survey_id=defaults['survey'], project_id=defaults['project'], projectUser_id=defaults['projectUser'],
                                             subProjectUser_id=defaults['subProjectUser'], aoQuestion_id=defaults['aoQuestion'], latestResponse=True)[0]

            if (len(tempItem) > 0):
                # obj = tempItem[0]

                # if obj.topicValue != defaults['topicValue'] or obj.commentValue != defaults['commentValue'] or obj.integerValue != defaults['integerValue'] or obj.skipValue != defaults['skipValue'] or obj.topicTags != defaults['topicTags'] or obj.commentTags != defaults['commentTags']:
                #     obj.latestResponse = False
                #     obj.save()
                for oldItem in tempItem:
                    obj = oldItem
                    obj.latestResponse = False
                    obj.save()

                if defaults["controlType"] == "TEXT" or defaults["controlType"] == "MULTI_TOPICS":
                    text = defaults["topicValue"] + \
                        " " + defaults["commentValue"]

                    sentimentResult = comprehend.detect_sentiment(
                        Text=text, LanguageCode="en")

                    # 2021-07-31
                    if sentimentResult['Sentiment'] == "POSITIVE":
                        defaults['integerValue'] = int(abs(sentimentResult['SentimentScore']['Positive'] * 100))
                    elif sentimentResult['Sentiment'] == "NEGATIVE":
                        defaults['integerValue'] = 100 - int(abs(sentimentResult['SentimentScore']['Negative'] * 100))
                    else:
                        if sentimentResult['SentimentScore']['Positive'] > sentimentResult['SentimentScore']['Negative']:
                            defaults['integerValue'] = 55
                        elif sentimentResult['SentimentScore']['Positive'] == sentimentResult['SentimentScore']['Negative']:
                            defaults['integerValue'] = 45
                        else:
                            defaults['integerValue'] = 35

                obj1 = AOResponse(aoQuestion_id=defaults['aoQuestion'],
                                projectUser_id=defaults['projectUser'], subProjectUser_id=defaults['subProjectUser'],
                                shCategory_id=defaults['shCategory'],
                                survey_id=defaults['survey'], project_id=defaults['project'],
                                controlType=defaults['controlType'], integerValue=defaults['integerValue'],
                                topicValue=defaults['topicValue'], commentValue=defaults['commentValue'],
                                skipValue=defaults['skipValue'], topicTags=defaults['topicTags'],
                                commentTags=defaults['commentTags'], latestResponse=True)
                obj1.save()

            else:
                if defaults["controlType"] == "TEXT" or defaults["controlType"] == "MULTI_TOPICS":
                    text = defaults["topicValue"] + " " + defaults["commentValue"]

                    sentimentResult = comprehend.detect_sentiment(Text=text, LanguageCode="en")
                    # defaults["integerValue"] = int(abs(sentimentResult["SentimentScore"]["Positive"] * 100))
                    # 2021-07-31
                    if sentimentResult['Sentiment'] == "POSITIVE":
                        defaults['integerValue'] = int(
                            abs(sentimentResult['SentimentScore']['Positive'] * 100))
                    elif sentimentResult['Sentiment'] == "NEGATIVE":
                        defaults['integerValue'] = 100 - int(abs(sentimentResult['SentimentScore']['Negative'] * 100))
                    else:
                        if sentimentResult['SentimentScore']['Positive'] > sentimentResult['SentimentScore']['Negative']:
                            defaults['integerValue'] = 55
                        elif sentimentResult['SentimentScore']['Positive'] == sentimentResult['SentimentScore']['Negative']:
                            defaults['integerValue'] = 45
                        else:
                            defaults['integerValue'] = 35

                obj = AOResponse(aoQuestion_id=defaults['aoQuestion'],
                            projectUser_id=defaults['projectUser'], subProjectUser_id=defaults['subProjectUser'],
                            shCategory_id=defaults['shCategory'],
                            survey_id=defaults['survey'], project_id=defaults['project'],
                            controlType=defaults['controlType'], integerValue=defaults['integerValue'],
                            topicValue=defaults['topicValue'], commentValue=defaults['commentValue'],
                            skipValue=defaults['skipValue'], topicTags=defaults['topicTags'],
                            commentTags=defaults['commentTags'], latestResponse=True)
                obj.save()
        
        return Response(True, status=status.HTTP_201_CREATED)

# aoresponsetopic api
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

# amresponseexcel api
class AMResponseExcelViewSet(XLSXFileMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'amresponse_export.xlsx'

# aoresponseexcel api
class AOResponseExcelViewSet(XLSXFileMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = AOResponse.objects.all()
    serializer_class = AOResponseSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'aoresponse_export.xlsx'

# amresponsereport api
class AMResponseReportViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,
                          permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    # serializer_class = AMResponseSerializer
    serializer_class = AMResponseForReportSerializer

    def get_queryset(self):
        try:
            queryset = AMResponse.objects.all()

            survey = self.request.query_params.get('survey', None)
            projectUser = self.request.query_params.get('projectUser', None)
            driver = self.request.query_params.get('driver', None)
            startDate = self.request.query_params.get('stdt', None)
            endDate = self.request.query_params.get('eddt', None)
            controlType = self.request.query_params.get('controltype', None)

            if (survey is not None) & (controlType is not None) & (driver is not None) & (projectUser is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    controlType=controlType, survey__id=survey, subProjectUser__id=projectUser, amQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            elif (survey is not None) & (controlType is not None) & (driver is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    controlType=controlType, survey__id=survey, amQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            elif (survey is not None) & (controlType is not None) & (projectUser is not None) & (driver is not None):
                queryset = queryset.filter(
                    controlType=controlType, survey__id=survey, subProjectUser__id=projectUser, amQuestion__driver__driverName=driver)
            elif (survey is not None) & (controlType is not None) & (driver is not None):
                queryset = queryset.filter(
                    controlType=controlType, survey__id=survey, amQuestion__driver__driverName=driver)
            elif (survey is not None) & (controlType is not None) & (projectUser is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    controlType=controlType, survey__id=survey, subProjectUser__id=projectUser, created_at__range=[startDate, endDate])
            elif (survey is not None) & (controlType is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    controlType=controlType, survey__id=survey, created_at__range=[startDate, endDate])
            elif (survey is not None) & (driver is not None) & (projectUser is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    survey__id=survey, subProjectUser__id=projectUser, amQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            elif (survey is not None) & (driver is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    survey__id=survey, amQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            elif (survey is not None) & (driver is not None):
                queryset = queryset.filter(
                    survey__id=survey, amQuestion__driver__driverName=driver)
            elif (survey is not None) & (projectUser is not None):
                queryset = queryset.filter(
                    survey__id=survey, subProjectUser__id=projectUser)
            elif (survey is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    survey__id=survey, created_at__range=[startDate, endDate])
            elif (survey is not None):
                queryset = queryset.filter(survey__id=survey)

            return queryset
        except:
            return None

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)

            for i in range(len(response.data)):
                amquestion_queryset = AMQuestion.objects.filter(
                    id=response.data[i]['amQuestion'])
                am_serializer = AMQuestionSerializer(
                    amquestion_queryset, many=True)
                response.data[i]['amQuestionData'] = am_serializer.data
                
            return response
        except Exception as error:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

# aoresponsereport api
class AOResponseReportViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AOResponse.objects.all()
    serializer_class = AOResponseForReportSerializer

    def get_queryset(self):
        try:
            queryset = AOResponse.objects.all()

            survey = self.request.query_params.get('survey', None)
            projectUser = self.request.query_params.get('projectUser', None)
            driver = self.request.query_params.get('driver', None)
            startDate = self.request.query_params.get('stdt', None)
            endDate = self.request.query_params.get('eddt', None)
            controlType = self.request.query_params.get('controltype', None)
 
            if (controlType is not None) & (driver is not None) & (projectUser is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    controlType=controlType, survey__id=survey, subProjectUser__id=projectUser, amQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            elif (controlType is not None) & (driver is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    controlType=controlType, survey__id=survey, amQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            elif (controlType is not None) & (projectUser is not None) & (driver is not None):
                queryset = queryset.filter(
                    controlType=controlType, survey__id=survey, subProjectUser__id=projectUser, amQuestion__driver__driverName=driver)
            elif (controlType is not None) & (driver is not None):
                queryset = queryset.filter(
                    controlType=controlType, survey__id=survey, amQuestion__driver__driverName=driver)
            elif (controlType is not None) & (projectUser is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    controlType=controlType, survey__id=survey, subProjectUser__id=projectUser, created_at__range=[startDate, endDate])
            elif (controlType is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    controlType=controlType, survey__id=survey, created_at__range=[startDate, endDate])
            elif (driver is not None) & (projectUser is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    survey__id=survey, subProjectUser__id=projectUser, amQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            elif (driver is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    survey__id=survey, amQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            elif driver is not None:
                queryset = queryset.filter(survey__id=survey, amQuestion__driver__driverName=driver)
            elif projectUser is not None:
                queryset = queryset.filter(survey__id=survey, subProjectUser__id=projectUser)
            elif (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    survey__id=survey, created_at__range=[startDate, endDate])

            return queryset
        except:
            return None

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            for i in range(len(response.data)):
                aoquestion_queryset = AOQuestion.objects.filter(id=response.data[i]['aoQuestion'])
                ao_serializer = AOQuestionSerializer(aoquestion_queryset, many=True)
                response.data[i]['aoQuestionData'] = ao_serializer.data
                
            return response
        except Exception as error:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

# aoresponsetoppositivenegativereport api
# class AOResponseTopPositiveNegativeViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
#     queryset = AOResponse.objects.all()
#     serializer_class = AOResponseTopPositiveNegativeSerializer

#     def get_queryset(self):
#         try:
#             queryset = AOResponse.objects.all().filter(Q(controlType='TEXT')|Q(controlType='MULTI_TOPICS')).order_by('-integerValue')

#             survey = self.request.query_params.get('survey', None)
#             projectUser = self.request.query_params.get('projectuser', None)
#             startDate = self.request.query_params.get('stdt', None)
#             endDate = self.request.query_params.get('eddt', None)

#             if (survey is not None) & (projectUser is not None) & (startDate is not None) & (endDate is not None):
#                 queryset = queryset.filter(
#                     survey__id=survey, subProjectUser__id=projectUser, created_at__range=[startDate, endDate])
#             elif (survey is not None) & (projectUser is not None):
#                 queryset = queryset.filter(
#                     survey__id=survey, subProjectUser__id=projectUser)
#             elif (survey is not None) & (startDate is not None) & (endDate is not None):
#                 queryset = queryset.filter(
#                     survey__id=survey, created_at__range=[startDate, endDate])
#             elif (survey is not None):
#                 queryset = queryset.filter(survey__id=survey)

#             return queryset
#         except:
#             return None
    
#     def list(self, request, *args, **kwargs):
#         try:
#             response = super().list(request, *args, **kwargs)
            
#             res = response.data

#             wordstring = ''
#             for i in range(len(res)):
#                 if res[i]['topicValue'] != "":
#                     wordstring += ' ' + res[i]['topicValue']
#                 if res[i]['commentValue'] != "":
#                     wordstring += ' ' + res[i]['commentValue']
#                 if res[i]['skipValue'] != "":
#                     wordstring += ' ' + res[i]['skipValue']
#                 if res[i]['topicTags'] != "":
#                     wordstring += ' ' + res[i]['topicTags']
#                 if res[i]['commentTags'] != "":
#                     wordstring += ' ' + res[i]['commentTags']

#             wordList = re.findall(r"[\w\']+", wordstring.lower())
#             filteredWordList = [w for w in wordList if w not in stopwords]
#             wordfreq = [filteredWordList.count(p) for p in filteredWordList]
#             dictionary = dict(list(zip(filteredWordList, wordfreq)))

#             aux = [(dictionary[key], key) for key in dictionary]
#             aux.sort()
#             aux.reverse()

#             ret = ''
#             # ret = {'topPositive': response.data[:3], 'topNegative': response.data[-3:]}
#             ret = {'topPositive': aux[:3], 'topNegative': aux[-3:]}

#             return Response(ret, status=status.HTTP_200_OK)
#         except Exception as error:
#             return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
class AMResponseTopPositiveNegativeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer

    def get_queryset(self):
        try:
            queryset = AMResponse.objects.all().filter(Q(controlType='TEXT')|Q(controlType='MULTI_TOPICS')).order_by('-integerValue')

            survey = self.request.query_params.get('survey', None)
            # projectUser = self.request.query_params.get('projectuser', None)
            # startDate = self.request.query_params.get('stdt', None)
            # endDate = self.request.query_params.get('eddt', None)

            # if (survey is not None) & (projectUser is not None) & (startDate is not None) & (endDate is not None):
            #     queryset = queryset.filter(survey__id=survey, subProjectUser__id=projectUser, created_at__range=[startDate, endDate])
            # elif (survey is not None) & (projectUser is not None):
            #     queryset = queryset.filter(survey__id=survey, subProjectUser__id=projectUser)
            # elif (survey is not None) & (startDate is not None) & (endDate is not None):
            #     queryset = queryset.filter(survey__id=survey, created_at__range=[startDate, endDate])
            if (survey is not None):
                queryset = queryset.filter(survey__id=survey)

            return queryset
        except:
            return None
    
    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)

            survey = self.request.GET.get('survey', None)

            # res = AMResponse.objects.all().filter(Q(controlType='TEXT') | Q(controlType='MULTI_TOPICS')).filter(survey__id=survey).values('amQuestion__subdriver').annotate(score=Avg('integerValue')).order_by('-score')
            res = AMResponse.objects.all().filter(controlType='SLIDER').filter(survey__id=survey).values('amQuestion__subdriver').annotate(score=Avg('integerValue')).order_by('-score')
            # wordstring = ''
            # for i in range(len(res)):
            #     if res[i]['topicValue'] != "":
            #         wordstring += ' ' + res[i]['topicValue']
            # wordList = re.findall(r"[\w\']+", wordstring.lower())
            # filteredWordList = [w for w in wordList if w not in stopwords]
            # wordfreq = [filteredWordList.count(p) for p in filteredWordList]
            # dictionary = dict(list(zip(filteredWordList, wordfreq)))

            # aux = [(dictionary[key], key) for key in dictionary]
            # aux.sort()
            # aux.reverse()
            # for i in range(len(res)):


            # ret = ''
            # ret = {'topPositive': aux[:3], 'topNegative': aux[-3:]}

            aux = []
            for i in range(len(res)):
                item = [res[i]['score'], res[i]['amQuestion__subdriver']]
                aux.append(item)

            topNegative = []
            topPositive = []
            if len(aux) >= 3:
                topPositive = aux[:3]
                tempTopNegative = aux[-3:]
                topNegative.append(tempTopNegative[2])
                topNegative.append(tempTopNegative[1])
                topNegative.append(tempTopNegative[0])
            elif len(aux) == 2:
                topPositive = aux[:2]
                tempTopNegative = aux[-2:]
                # topNegative.append(tempTopNegative[2])
                topNegative.append(tempTopNegative[1])
                topNegative.append(tempTopNegative[0])
            elif len(aux) == 1:
                topPositive = aux[:1]
                tempTopNegative = aux[-1:]
                # topNegative.append(tempTopNegative[2])
                # topNegative.append(tempTopNegative[1])
                topNegative.append(tempTopNegative[0])
            
            ret = {'topPositive': topPositive, 'topNegative': topNegative}

            return Response(ret, status=status.HTTP_200_OK)
        except Exception as error:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

# configpage api
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

# driver api
class DriverViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,
                          permissions.IsAuthenticatedOrReadOnly]
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    # added survey to the driver table     2020-05-20
    def get_queryset(self):
        queryset = Driver.objects.all()
        survey = self.request.query_params.get('survey', None)

        if survey is not None:
            queryset = queryset.filter(survey__id=survey)

        return queryset

# feedbacksummaryreport api
# need to consider
# class AOResponseFeedbackSummaryViewset(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated,
#                           permissions.IsAuthenticatedOrReadOnly]
#     queryset = AOResponse.objects.all()
#     serializer_class = AOResponseForMatrixSerializer

#     def get_queryset(self):
#         try:
#             queryset = AOResponse.objects.all()

#             survey = self.request.query_params.get('survey', None)
#             subProjectUser = self.request.query_params.get('projectuser', None)
#             startDate = self.request.query_params.get('stdt', None)
#             endDate = self.request.query_params.get('eddt', None)

#             if (survey is not None) & (subProjectUser is not None) & (startDate is not None) & (endDate is not None):
#                 queryset = queryset.filter(
#                     survey_id=survey, subProjectUser_id=subProjectUser, created_at__range=[startDate, endDate])
#             elif (survey is not None) & (subProjectUser is not None):
#                 queryset = queryset.filter(
#                     survey_id=survey, subProjectUser_id=subProjectUser)
#             elif (survey is not None) & (startDate is not None) & (endDate is not None):
#                 queryset = queryset.filter(survey_id=survey, created_at__range=[startDate, endDate])
#             elif (survey is not None):
#                 queryset = queryset.filter(survey_id=survey)

#             return queryset
#         except:
#             return None

#     def list(self, request, *args, **kwargs):
#         try:
#             response = super().list(request, *args, **kwargs)
            
#             survey = self.request.GET.get('survey', None)
#             subProjectUser = self.request.GET.get('projectuser', None)
#             startDate = self.request.GET.get('stdt', None)
#             endDate = self.request.GET.get('eddt', None)

#             for i in range(len(response.data)):
#                 aoquestion_queryset = AOQuestion.objects.filter(
#                     id=response.data[i]['aoQuestion'])
#                 ao_serializer = AOQuestionSerializer(
#                     aoquestion_queryset, many=True)
#                 response.data[i]['aoQuestionData'] = ao_serializer.data

#             # add amresponse data
#             amresponsequeryset = AMResponse.objects.all()
#             if (survey is not None) & (subProjectUser is not None) & (startDate is not None) & (endDate is not None):
#                 amresponsequeryset = amresponsequeryset.filter(survey_id=survey, subProjectUser_id=subProjectUser, created_at__range=[startDate, endDate])
#             elif (survey is not None) & (subProjectUser is not None):
#                 amresponsequeryset = amresponsequeryset.filter(survey_id=survey, subProjectUser_id=subProjectUser)
#             elif (survey is not None) & (startDate is not None) & (endDate is not None):
#                 amresponsequeryset = amresponsequeryset.filter(survey_id=survey, created_at__range=[startDate, endDate])
#             elif (survey is not None):
#                 amresponsequeryset = amresponsequeryset.filter(survey_id=survey)

#             amresponseserializer = AMResponseForDriverAnalysisSerializer(amresponsequeryset, many=True)
#             amresponsedata = amresponseserializer.data

#             # replace am to ao for frontend
#             for i in range(len(amresponsedata)):
#                 amresponsedata[i]['aoQuestion'] = amresponsedata[i]['amQuestion']
#                 amquestion_queryset = AMQuestion.objects.filter(
#                     id=amresponsedata[i]['amQuestion'])
#                 am_serializer = AMQuestionSerializer(
#                     amquestion_queryset, many=True)
#                 amresponsedata[i]['aoQuestionData'] = am_serializer.data
#                 response.data.append(amresponsedata[i])

#             return response
#         except Exception as error:
#             return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

class AOResponseFeedbackSummaryViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,
                          permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseForSummarySerializer

    def get_queryset(self):
        try:
            queryset = AMResponse.objects.all()

            survey = self.request.query_params.get('survey', None)
            subProjectUser = self.request.query_params.get('projectuser', None)
            startDate = self.request.query_params.get('stdt', None)
            endDate = self.request.query_params.get('eddt', None)
            trend = self.request.query_params.get('trend', None)

            if (survey is not None) & (subProjectUser is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    survey_id=survey, subProjectUser_id=subProjectUser, created_at__range=[startDate, endDate], controlType="SLIDER", latestResponse=True, amQuestion__driver__isnull=False)
            elif (survey is not None) & (subProjectUser is not None):
                queryset = queryset.filter(
                    survey_id=survey, subProjectUser_id=subProjectUser, controlType="SLIDER", latestResponse=True, amQuestion__driver__isnull=False)
            elif (survey is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(survey_id=survey, created_at__range=[startDate, endDate], controlType="SLIDER", latestResponse=True, amQuestion__driver__isnull=False)
            elif (survey is not None):
                queryset = queryset.filter(survey_id=survey, controlType="SLIDER", latestResponse=True, amQuestion__driver__isnull=False)

            if (trend == "1"):
                queryset = queryset.filter(amQuestion__subdriver="Overall Sentiment")

            return queryset
        except:
            return None

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            
            survey = self.request.GET.get('survey', None)
            subProjectUser = self.request.GET.get('projectuser', None)
            startDate = self.request.GET.get('stdt', None)
            endDate = self.request.GET.get('eddt', None)

            # for i in range(len(response.data)):
            #     amquestion_queryset = AMQuestion.objects.filter(
            #         id=response.data[i]['amQuestion'])
            #     am_serializer = AMQuestionSerializer(
            #         amquestion_queryset, many=True)
            #     response.data[i]['amQuestionData'] = am_serializer.data

            return response
        except Exception as error:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

# mymaplayouts api
class MyMapLayoutViewSet(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = MyMapLayout.objects.all()
    serializer_class = MyMapLayoutStoreSerializer
    filterset_fields = ['user', 'project']

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

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

# nikelmobilepage api
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

# option api
class OptionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

# overallsentimentreport api
class OverallSentimentReportViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer

    def get_queryset(self):
        try:
            queryset = AMResponse.objects.all()
            survey = self.request.query_params.get('survey', None)
            startDate = self.request.query_params.get('stdt', None)
            endDate = self.request.query_params.get('eddt', None)

            if (survey is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(
                    survey__id=survey, created_at__range=[startDate, endDate], amQuestion__subdriver="Overall Sentiment", latestResponse=True, controlType="SLIDER")
            elif (survey is not None):
                queryset = queryset.filter(survey__id=survey, amQuestion__subdriver="Overall Sentiment", latestResponse=True, controlType="SLIDER")

            return queryset
        except:
            return None

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)

            # survey = self.request.GET.get('survey', None)
            # startDate = self.request.GET.get('stdt', None)
            # endDate = self.request.GET.get('eddt', None)

            # add amresponse data
            # aoresponsequeryset = AOResponse.objects.all()
            # if (survey is not None) & (startDate is not None) & (endDate is not None):
            #     aoresponsequeryset = aoresponsequeryset.filter(
            #         survey_id=survey, created_at__range=[startDate, endDate])
            # elif (survey is not None):
            #     aoresponsequeryset = aoresponsequeryset.filter(
            #         survey_id=survey)
            # aoresponseserializer = AOResponseSerializer(aoresponsequeryset, many=True)
            # aoresponsedata = aoresponseserializer.data

            # for i in range(len(aoresponsedata)):
            #     response.data.append(aoresponsedata[i])

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
        except Exception as error:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

# pages api
class PageViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    def list(self, request, *kwargs):
        
        survey_param = ''
        projectuser_param = ''

        t_survey_param = self.request.GET.get('survey')
        t_projectuser_param = self.request.GET.get('projectuser')

        if t_survey_param:
            survey_param = int(t_survey_param)

        if t_projectuser_param:
            projectuser_param = int(t_projectuser_param)

        queryset = Driver.objects.filter(survey_id=survey_param)
        serializer = self.get_serializer(queryset, many=True)
        list_drivers = serializer.data

        for i in range(len(list_drivers)):
            if survey_param and isinstance(survey_param, int):
                
                # 2020-07-22 add shgroup filter
                # amquestion_queryset = AMQuestion.objects.filter(driver_id=list_drivers[i]['id'], survey_id=survey_param)
                # am_serializer = AMQuestionSerializer(amquestion_queryset, many=True)
                # list_drivers[i]['amquestion'] = am_serializer.data

                if projectuser_param and isinstance(projectuser_param, int):
                    try:
                        projectuser = ProjectUser.objects.get(id=projectuser_param)

                        amquestion_queryset = AMQuestion.objects.filter(driver_id=list_drivers[i]['id'], survey_id=survey_param, shGroup__in=[projectuser.shGroup_id])
                        am_serializer = AMQuestionSerializer(amquestion_queryset, many=True)
                        list_drivers[i]['amquestion'] = am_serializer.data

                        for j in range(len(list_drivers[i]['amquestion'])):
                            amresponsetopic_queryset = AMResponseTopic.objects.filter(amQuestion_id=list_drivers[i]['amquestion'][j]['id'], responseUser_id=projectuser_param)
                            amresponsetopic_serializer = AMResponseTopicSerializer(amresponsetopic_queryset, many=True)
                            list_drivers[i]['amquestion'][j]['topic'] = amresponsetopic_serializer.data
                            
                            
                            ret = AMResponse.objects.filter(projectUser_id=projectuser_param, survey_id=survey_param, amQuestion_id=list_drivers[i]['amquestion'][j]['id'], latestResponse=True)
                            if (len(ret) > 0):
                                list_drivers[i]['amquestion'][j]['responsestatus'] = True
                                list_drivers[i]['amquestion'][j]['response'] = model_to_dict(ret[0])
                            else:
                                ret = None
                                list_drivers[i]['amquestion'][j]['responsestatus'] = False
                                list_drivers[i]['amquestion'][j]['response'] = []
                    except ProjectUser.DoesNotExist:
                        projectuser = None

                # 2020-07-22 add shgroup filter
                # aoquestion_queryset = AOQuestion.objects.filter(driver_id=list_drivers[i]['id'], survey_id=survey_param)
                # ao_serializer = AOQuestionSerializer(aoquestion_queryset, many=True)
                # list_drivers[i]['aoquestion'] = ao_serializer.data

                if projectuser_param and isinstance(projectuser_param, int):
                    try:
                        projectuser = ProjectUser.objects.get(id=projectuser_param)

                        aoquestion_queryset = AOQuestion.objects.filter(driver_id=list_drivers[i]['id'], survey_id=survey_param, shGroup__in=[projectuser.shGroup_id])
                        ao_serializer = AOQuestionSerializer(aoquestion_queryset, many=True)
                        list_drivers[i]['aoquestion'] = ao_serializer.data
                        
                        for j in range(len(list_drivers[i]['aoquestion'])):
                            aoresponsetopic_queryset = AOResponseTopic.objects.filter(aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'], responseUser_id=projectuser_param)
                            aoresponsetopic_serializer = AOResponseTopicSerializer(aoresponsetopic_queryset, many=True)
                            list_drivers[i]['aoquestion'][j]['topic'] = aoresponsetopic_serializer.data

                            ret = AOResponse.objects.filter(projectUser_id=projectuser_param, survey_id=survey_param, aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'], latestResponse=True)
                            
                            if (len(ret) > 0):
                                list_drivers[i]['aoquestion'][j]['responsestatus'] = True
                                list_drivers[i]['aoquestion'][j]['response'] = []
                                for k in range(len(ret)):
                                    item = model_to_dict(ret[k])
                                    list_drivers[i]['aoquestion'][j]['response'].append(item)
                            
                            else:
                                list_drivers[i]['aoquestion'][j]['responsestatus'] = False
                                list_drivers[i]['aoquestion'][j]['response'] = []
                    except ProjectUser.DoesNotExist:
                        projectuser = None

            else:
                # 2020-07-22 add shgroup filter
                # amquestion_queryset = AMQuestion.objects.filter(driver_id=list_drivers[i]['id'])
                # am_serializer = AMQuestionSerializer(amquestion_queryset, many=True)
                # list_drivers[i]['amquestion'] = am_serializer.data

                if projectuser_param and isinstance(projectuser_param, int):
                    try:
                        projectuser = ProjectUser.objects.get(id=projectuser_param)

                        amquestion_queryset = AMQuestion.objects.filter(driver_id=list_drivers[i]['id'], shGroup__in=[projectuser.shGroup_id])
                        am_serializer = AMQuestionSerializer(amquestion_queryset, many=True)
                        list_drivers[i]['amquestion'] = am_serializer.data

                        for j in range(len(list_drivers[i]['amquestion'])):
                            amresponsetopic_queryset = AMResponseTopic.objects.filter(amQuestion_id=list_drivers[i]['amquestion'][j]['id'], responseUser_id=projectuser_param)
                            amresponsetopic_serializer = AMResponseTopicSerializer(amresponsetopic_queryset, many=True)
                            list_drivers[i]['amquestion'][j]['topic'] = amresponsetopic_serializer.data

                            
                            ret = AMResponse.objects.filter(projectUser_id=projectuser_param, survey_id=survey_param, amQuestion_id=list_drivers[i]['amquestion'][j]['id'], latestResponse=True)
                            if (len(ret) > 0):
                                list_drivers[i]['amquestion'][j]['responsestatus'] = True
                                list_drivers[i]['amquestion'][j]['response'] = model_to_dict(ret)
                            else:
                                ret = None
                                list_drivers[i]['amquestion'][j]['responsestatus'] = False
                                list_drivers[i]['amquestion'][j]['response'] = []
                    except ProjectUser.DoesNotExist:
                        projectuser = None

                # 2020-07-22 add shgroup filter
                # aoquestion_queryset = AOQuestion.objects.filter(driver_id=list_drivers[i]['id'])
                # ao_serializer = AOQuestionSerializer(aoquestion_queryset, many=True)
                # list_drivers[i]['aoquestion'] = ao_serializer.data

                if projectuser_param and isinstance(projectuser_param, int):
                    try:
                        projectuser = ProjectUser.objects.get(id=projectuser_param)
                        
                        aoquestion_queryset = AOQuestion.objects.filter(driver_id=list_drivers[i]['id'], shGroup__in=[projectuser.shGroup_id])
                        ao_serializer = AOQuestionSerializer(aoquestion_queryset, many=True)
                        list_drivers[i]['aoquestion'] = ao_serializer.data

                        for j in range(len(list_drivers[i]['aoquestion'])):
                            aoresponsetopic_queryset = AOResponseTopic.objects.filter(aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'], responseUser_id=projectuser_param)
                            aoresponsetopic_serializer = AOResponseTopicSerializer(aoresponsetopic_queryset, many=True)
                            list_drivers[i]['aoquestion'][j]['topic'] = aoresponsetopic_serializer.data

                            ret = AOResponse.objects.filter(projectUser_id=projectuser_param, survey_id=survey_param, aoQuestion_id=list_drivers[i]['aoquestion'][j]['id'], latestResponse=True)
                            
                            if (len(ret) > 0):
                                list_drivers[i]['aoquestion'][j]['responsestatus'] = True
                                list_drivers[i]['aoquestion'][j]['response'] = []
                                for k in range(len(ret)):
                                    item = model_to_dict(ret[k])
                                    list_drivers[i]['aoquestion'][j]['response'].append(item)
                            else:
                                list_drivers[i]['aoquestion'][j]['responsestatus'] = False
                                list_drivers[i]['aoquestion'][j]['response'] = []

                    except ProjectUser.DoesNotExist:
                        projectuser = None

        return Response(list_drivers)

# project api
class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

# projectuser api
class ProjectUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,
                          permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = ProjectUserSerializer

    def get_queryset(self):
        queryset = ProjectUser.objects.all()
        return queryset

    def update(self, request, *args, **kwargs):
        ret = super(ProjectUserViewSet, self).update(request, *args, **kwargs)

        projectUser_id = ret.data['id']

        shMyCategories = request.data['shMyCategory']
        myProjectUser_id = request.data['myProjectUser']
        if (ProjectUser.objects.get(id=myProjectUser_id).user != request.user):
            return Response("Malicious Request", status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = MyMapLayout.objects.get(
                user_id=request.user.id, project_id=request.data['project'])
            new_obj = ProjectUser.objects.get(id=projectUser_id)
            obj.projectUser.add(new_obj)
            
            SHMapping.objects.filter(
                projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id).delete()

            for i in range(len(shMyCategories)):
                try:
                    shObj = SHMapping.objects.get(
                        shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    mapObj = SHMapping(
                        shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj.save()

            obj.save()

        except MyMapLayout.DoesNotExist:
            obj = MyMapLayout.objects.create(user_id=request.user.id, project_id=request.data['project'])
            obj.user_id = request.user.id
            obj.project_id = request.data['project']
            obj.layout_json = ''

            new_obj = ProjectUser.objects.get(id=projectUser_id)
            obj.projectUser.add(new_obj)

            for i in range(len(shMyCategories)):
                try:
                    shObj = SHMapping.objects.get(
                        shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    mapObj = SHMapping(
                        shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj.save()

            obj.save()

        shProjectCategories = request.data['shProjectCategory']

        try:
            obj1 = ProjectMapLayout.objects.get(
                user_id=request.user.id, project_id=request.data['project'])
            new_obj1 = ProjectUser.objects.get(id=projectUser_id)
            obj1.projectUser.add(new_obj1)

            for j in range(len(shProjectCategories)):
                try:
                    shObj1 = SHMapping.objects.get(
                        shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    mapObj1 = SHMapping(
                        shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj1.save()
            obj1.save()

        except ProjectMapLayout.DoesNotExist:
            obj1 = ProjectMapLayout.objects.create(user_id=request.user.id, project_id=request.data['project'])
            obj1.user_id = request.user.id
            obj1.project_id = request.data['project']
            obj1.layout_json = ''

            new_obj1 = ProjectUser.objects.get(id=projectUser_id)
            obj1.projectUser.add(new_obj1)

            for j in range(len(shProjectCategories)):
                try:
                    shObj1 = SHMapping.objects.get(
                        shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    mapObj1 = SHMapping(
                        shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj1.save()
            obj1.save()

        return ret

    def create(self, request, *args, **kwargs):
        data = request.data.get(
            "items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=many)

        projectUser_id = 0

        existCheckObj = ProjectUser.objects.filter(
            survey_id=data['survey'], user_id=data['user'])

        if len(existCheckObj) > 0:
            projectUser_id = existCheckObj[0].id
        else:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            projectUser_id = serializer.data['id']

        shMyCategories = request.data['shMyCategory']
        myProjectUser_id = request.data['myProjectUser']
        if (ProjectUser.objects.get(id=myProjectUser_id).user != request.user):
            return Response("Malicious Request", status=status.HTTP_400_BAD_REQUEST)
        try:
            obj = MyMapLayout.objects.get(
                user_id=request.user.id, project_id=data['project'])

            new_obj = ProjectUser.objects.get(id=projectUser_id)
            obj.projectUser.add(new_obj)

            for i in range(len(shMyCategories)):
                try:
                    shObj = SHMapping.objects.get(
                        shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    mapObj = SHMapping(
                        shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj.save()

            obj.save()

        except MyMapLayout.DoesNotExist:
            obj = MyMapLayout.objects.create(
                user_id=request.user.id, project_id=data['project'])

            obj.user_id = request.user.id
            obj.project_id = data['project']
            obj.layout_json = ''

            new_obj = ProjectUser.objects.get(id=projectUser_id)
            obj.projectUser.add(new_obj)

            for i in range(len(shMyCategories)):
                try:
                    shObj = SHMapping.objects.get(
                        shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    mapObj = SHMapping(
                        shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj.save()

            obj.save()

        shProjectCategories = request.data['shProjectCategory']

        try:
            obj1 = ProjectMapLayout.objects.get(
                user_id=request.user.id, project_id=data['project'])

            new_obj1 = ProjectUser.objects.get(id=projectUser_id)
            obj1.projectUser.add(new_obj1)

            for j in range(len(shProjectCategories)):
                try:
                    shObj1 = SHMapping.objects.get(
                        shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    mapObj1 = SHMapping(
                        shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj1.save()

            obj1.save()

        except ProjectMapLayout.DoesNotExist:
            obj1 = ProjectMapLayout.objects.create(
                user_id=request.user.id, project_id=data['project'])

            obj1.user_id = request.user.id
            obj1.project_id = data['project']
            obj1.layout_json = ''

            new_obj1 = ProjectUser.objects.get(id=projectUser_id)
            obj1.projectUser.add(new_obj1)

            for j in range(len(shProjectCategories)):
                try:
                    shObj1 = SHMapping.objects.get(
                        shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
                except SHMapping.DoesNotExist:
                    mapObj1 = SHMapping(
                        shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                    mapObj1.save()

            obj1.save()

        return Response("success", status=status.HTTP_201_CREATED)

# projectmaplayouts api
class ProjectMapLayoutViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectMapLayout.objects.all()
    serializer_class = ProjectMapLayoutStoreSerializer
    filterset_fields = ['user', 'project']

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        myProjectUser_id = self.request.GET.get('myProjectUser')

        for i in range(len(response.data)):
            response.data[i]['pu_category'] = []
            for item in response.data[i]['projectUser']:
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

        myProjectUser_id = data['myProjectUser']

        try:
            obj = ProjectMapLayout.objects.get(user_id=data['user'], project_id=data['project'])

            obj.projectUser.clear()

            if "application/json" in content_type:
                for item in data["pu_category"]:
                    new_obj = ProjectUser.objects.get(id=item['projectUser'])
                    obj.projectUser.add(new_obj)

                    try:
                        shObj = SHMapping.objects.get(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'])
                    except SHMapping.DoesNotExist:
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
                        shObj = SHMapping.objects.get(shCategory_id=item['category'], projectUser_id=myProjectUser_id, subProjectUser_id=item['projectUser'])
                    except SHMapping.DoesNotExist:
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

# projectbyuser api
class ProjectByUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = SurveyByUserSerializer

    def get_queryset(self):
        queryset = ProjectUser.objects.all()
        user = self.request.user
        if user is not None:
            queryset = queryset.filter(user=user, survey__isActive=True)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # new_data = []
        # project_ids = []
        queryset = ProjectUser.objects.all()
        user = self.request.user
        if user is not None:
            queryset = queryset.filter(user=user, survey__isActive=True, sendInvite=True)
        queryset = queryset.values_list('survey__project', 'projectAdmin')
        # for i in range(len(response.data)):
        #     if response.data[i]['survey']['project'] not in project_ids:
        #         item = {
        #             "projectAdmin": response.data[i]['projectAdmin'],
        #             "projectId": response.data[i]['survey']['project']
        #         }
        #         project_ids.append(item)

        response.data = []
        for i in range(len(queryset)):
            item = model_to_dict(Project.objects.get(id=queryset[i][0]))
            item["projectAdmin"] = queryset[i][1]
            response.data.append(item)

        return response

# shgroup api
class SHGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = SHGroup.objects.all()
    serializer_class = SHGroupSerializer

    def get_queryset(self):
        queryset = SHGroup.objects.all()

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

# skipoption api
class SkipOptionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = SkipOption.objects.all()
    serializer_class = SkipOptionSerializer
  
# surveybyproject api
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

# shcategory api
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

# class SubDriverViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
#     queryset = Driver.objects.all()
#     serializer_class = DriverSubDriverSerializer

#     def get_queryset(self):
#         queryset = Driver.objects.all()
#         survey = self.request.query_params.get('survey', None)
#         driver = self.request.query_params.get('driver', None)

#         if (survey is not None) & (driver is not None):
#             queryset = queryset.filter(survey__id=survey, id=driver)
#         elif survey is not None:
#             queryset = queryset.filter(survey__id=survey)
#         elif driver is not None:
#             queryset = queryset.filter(id=driver)

#         return queryset

#     def list(self, request, *args, **kwargs):
#         response = super().list(request, *args, **kwargs)
#         survey = self.request.query_params.get('survey', None)
#         driver = self.request.query_params.get('driver', None)

#         for i in range(len(response.data)):
#             amsubdriver_queryset = ''
#             aosubdriver_queryset = ''
#             if (survey is not None) & (driver is not None):
#                 amsubdriver_queryset = AMQuestion.objects.filter(survey__id=survey, driver__id=driver).values('subdriver').distinct()
#                 aosubdriver_queryset = AOQuestion.objects.filter(survey__id=survey, driver__id=driver).values('subdriver').distinct()
#             elif survey is not None:
#                 amsubdriver_queryset = AMQuestion.objects.filter(survey__id=survey).values('subdriver').distinct()
#                 aosubdriver_queryset = AOQuestion.objects.filter(survey__id=survey).values('subdriver').distinct()
#             elif driver is not None:
#                 amsubdriver_queryset = AMQuestion.objects.filter(driver__id=driver).values('subdriver').distinct()
#                 aosubdriver_queryset = AOQuestion.objects.filter(driver__id=driver).values('subdriver').distinct()
#             else:
#                 amsubdriver_queryset = AMQuestion.objects.all().values('subdriver').distinct()
#                 aosubdriver_queryset = AOQuestion.objects.all().values('subdriver').distinct()

#             amsubdriver_serializer = AMQuestionSubDriverSerializer(amsubdriver_queryset, many=True)
#             aosubdriver_serializer = AOQuestionSubDriverSerializer(aosubdriver_queryset, many=True)

#             response.data[i]['subdriver'] = []
#             response.data[i]['subdriver'] = []

#             for item in amsubdriver_serializer.data:
#                 response.data[i]['subdriver'].append(item['subdriver'])
#             for item in aosubdriver_serializer.data:
#                 if not item['subdriver'] in response.data[i]['subdriver']:
#                     response.data[i]['subdriver'].append(item['subdriver'])

#         return response

# subdriver api
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

# team api
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

# organization api
class OrganizationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = ProjectUserSerializer

    def get_queryset(self):
        queryset = ProjectUser.objects.all()

        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey)
        
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        survey = self.request.GET.get('survey')
        list = []
        for projectUser in response.data:
            organization = Organization.objects.filter(user_id=projectUser['user']).values()
            list.append(organization[0])
        return Response(list, status=status.HTTP_200_OK)

# tooltipguide api
class ToolTipGuideViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ToolTipGuide.objects.all()
    serializer_class = ToolTipGuideSerializer

# users api
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

# updatestakeholder api
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
        
        # obj = MyMapLayout.objects.get(user_id=request.user.id, project_id=request.data['project'])

        myProjectUser_id = request.data['myProjectUser']
        if (ProjectUser.objects.get(id=myProjectUser_id).user != request.user):
            return Response("Malicious Request", status=status.HTTP_400_BAD_REQUEST)
        SHMapping.objects.filter(projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id).delete()

        for i in range(len(shMyCategories)):
            try:
                shObj = SHMapping.objects.get(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
            except SHMapping.DoesNotExist:
                mapObj = SHMapping(shCategory_id=shMyCategories[i], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                mapObj.save()
        
        shProjectCategories = request.data['shProjectCategory']

        # obj1 = ProjectMapLayout.objects.get(user_id=request.user.id, project_id=request.data['project'])

        for j in range(len(shProjectCategories)):
            
            try:
                shObj1 = SHMapping.objects.get(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id)
            except SHMapping.DoesNotExist:
                mapObj1 = SHMapping(shCategory_id=shProjectCategories[j], projectUser_id=myProjectUser_id, subProjectUser_id=projectUser_id, relationshipStatus="")
                mapObj1.save()

        return ret

# userbysurvey api
class UserBySurveyViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all()
    serializer_class = UserBySurveySerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # need to consider ??????
        myProjectUser_id = self.request.GET.get('projectuser')
        survey = self.request.GET.get('survey')
        startDate = self.request.GET.get('stdt', None)
        endDate = self.request.GET.get('eddt', None)

        if (startDate is not None) & (endDate is not None):
            for i in range(len(response.data)):
                filters = ~Q(shGroup=None)
                if response.data[i]['user']['last_login'] is not None:
                    response.data[i]['accept_status'] = True
                else:
                    response.data[i]['accept_status'] = False

                response.data[i]['am_total'] = AMQuestion.objects.filter(filters).filter(survey__id=survey).count()
                response.data[i]['am_response'] = []

                for item1 in AMResponse.objects.filter(projectUser_id=response.data[i]['id'], latestResponse=True, created_at__range=[startDate, endDate]).values('amQuestion'):
                    response.data[i]['am_response'].append(item1['amQuestion']) 
                response.data[i]['am_answered'] = AMResponse.objects.filter(
                    projectUser_id=response.data[i]['id'], latestResponse=True, created_at__range=[startDate, endDate]).count()
                response.data[i]['ao_total'] = AOQuestion.objects.filter(filters).filter(survey__id=survey).count()
                response.data[i]['ao_response'] = []
                for item2 in AOResponse.objects.filter(subProjectUser_id=response.data[i]['id'], latestResponse=True, created_at__range=[startDate, endDate]).values('aoQuestion'):
                    response.data[i]['ao_response'].append(item2['aoQuestion']) 
                response.data[i]['ao_answered'] = AOResponse.objects.filter(
                    subProjectUser_id=response.data[i]['id'], latestResponse=True, created_at__range=[startDate, endDate]).count()

                response.data[i]['shCategory'] = []
                
                for item3 in SHMapping.objects.filter(projectUser_id=myProjectUser_id, subProjectUser_id=response.data[i]['id']).values('shCategory'):
                    response.data[i]['shCategory'].append(item3['shCategory'])
        else:
            for i in range(len(response.data)):
                filters = ~Q(shGroup=None)
                if response.data[i]['user']['last_login'] is not None:
                    response.data[i]['accept_status'] = True
                else:
                    response.data[i]['accept_status'] = False

                response.data[i]['am_total'] = AMQuestion.objects.filter(
                    filters).filter(survey__id=survey).count()
                response.data[i]['am_response'] = []

                for item1 in AMResponse.objects.filter(projectUser_id=response.data[i]['id'], latestResponse=True).values('amQuestion'):
                    response.data[i]['am_response'].append(item1['amQuestion'])
                response.data[i]['am_answered'] = AMResponse.objects.filter(
                    projectUser_id=response.data[i]['id'], latestResponse=True).count()
                response.data[i]['ao_total'] = AOQuestion.objects.filter(
                    filters).filter(survey__id=survey).count()
                response.data[i]['ao_response'] = []
                for item2 in AOResponse.objects.filter(subProjectUser_id=response.data[i]['id'], latestResponse=True).values('aoQuestion'):
                    response.data[i]['ao_response'].append(item2['aoQuestion'])
                response.data[i]['ao_answered'] = AOResponse.objects.filter(
                    subProjectUser_id=response.data[i]['id'], latestResponse=True).count()

                response.data[i]['shCategory'] = []

                for item3 in SHMapping.objects.filter(projectUser_id=myProjectUser_id, subProjectUser_id=response.data[i]['id']).values('shCategory'):
                    response.data[i]['shCategory'].append(item3['shCategory'])

        return response

    def get_queryset(self):
        queryset = ProjectUser.objects.all()

        survey = self.request.query_params.get('survey', None)
        user = self.request.query_params.get('user', None)

        if (survey is not None) & (user is not None):
            queryset = queryset.filter(survey__id=survey, user__id=user)
        elif survey is not None:
            queryset = queryset.filter(survey__id=survey)   
        elif user is not None:
            queryset = queryset.filter(user__id=user)

        return queryset

# adminuserbysurvey api
class AdminUserBySurveyViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectUser.objects.all().filter(isArchived=False)
    serializer_class = UserBySurveySerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        survey = self.request.GET.get('survey')

        identifiedTeamMemberCnt = 0
        identifiedStakeholderCnt = 0
        invitedTeamMemberCnt = 0
        invitedStakeholderCnt = 0
        totalIdentifiedCnt = len(response.data)
        totalInvitedCnt = 0

        for i in range(len(response.data)):
            if response.data[i]['sendInvite'] == True:
                totalInvitedCnt = totalInvitedCnt + 1
            if response.data[i]['shType'] is not None:
                if response.data[i]['shType']['shTypeName'] == 'Team Member':
                    identifiedTeamMemberCnt = identifiedTeamMemberCnt + 1
                    if response.data[i]['sendInvite'] == True:
                        invitedTeamMemberCnt = invitedTeamMemberCnt + 1
                if response.data[i]['shType']['shTypeName'] == 'Stakeholder':
                    identifiedStakeholderCnt = identifiedStakeholderCnt + 1
                    if response.data[i]['sendInvite'] == True:
                        invitedStakeholderCnt = invitedStakeholderCnt + 1

            filters = ~Q(shGroup=None)
            if response.data[i]['user']['last_login'] is not None:
                response.data[i]['accept_status'] = True
            else:
                response.data[i]['accept_status'] = False

            response.data[i]['am_total'] = AMQuestion.objects.filter(
                filters).filter(survey__id=survey).count()
            response.data[i]['am_response'] = []

            for item1 in AMResponse.objects.filter(projectUser_id=response.data[i]['id'], latestResponse=True).values('amQuestion'):
                response.data[i]['am_response'].append(item1['amQuestion'])
            response.data[i]['am_answered'] = AMResponse.objects.filter(
                projectUser_id=response.data[i]['id'], latestResponse=True).count()
            response.data[i]['ao_total'] = AOQuestion.objects.filter(
                filters).filter(survey__id=survey).count()
            response.data[i]['ao_response'] = []
            for item2 in AOResponse.objects.filter(subProjectUser_id=response.data[i]['id'], latestResponse=True).values('aoQuestion'):
                response.data[i]['ao_response'].append(item2['aoQuestion'])
            response.data[i]['ao_answered'] = AOResponse.objects.filter(
                subProjectUser_id=response.data[i]['id'], latestResponse=True).count()

            # mappedByOthers field value in user admin page
            response.data[i]['mappedByOthers'] = SHMapping.objects.filter(subProjectUser_id=response.data[i]['id']).count()
        
        # return value for user administration
        ret = {
            "projectUser": response.data,
            "identifiedTeamMemberCnt": identifiedTeamMemberCnt,
            "identifiedStakeholderCnt": identifiedStakeholderCnt,
            "invitedTeamMemberCnt": invitedTeamMemberCnt,
            "invitedStakeholderCnt": invitedStakeholderCnt,
            "totalIdentifiedCnt": totalIdentifiedCnt,
            "totalInvitedCnt": totalInvitedCnt
        }

        return Response(ret, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = ProjectUser.objects.all()

        survey = self.request.query_params.get('survey', None)
        # user = self.request.query_params.get('user', None)

        # if (survey is not None) & (user is not None):
        #     queryset = queryset.filter(survey__id=survey, user__id=user)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey)   
        # elif user is not None:
        #     queryset = queryset.filter(user__id=user)

        return queryset

# adminproject api
class AdminProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer



# adminsurveysetup api
class AdminSurveySetupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    def get_queryset(self):
        queryset = Survey.objects.all()

        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(id=survey)

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)

            survey = self.request.GET.get('survey', None)
            if survey is None:
                return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

            if len(response.data) == 0:
                return Response([], status=status.HTTP_200_OK)
            tour = ConfigPage.objects.filter(survey_id=survey).values()
            moreInfo = NikelMobilePage.objects.filter(survey_id=survey).values()

            ret = response.data[0]
            ret['tour'] = tour
            ret['moreInfo'] = moreInfo

            return Response(ret, status=status.HTTP_200_OK)
        except Exception as error:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

# adminsurveyconfiguration api
class AdminSurveyConfigurationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    def get_queryset(self):
        queryset = Survey.objects.all()

        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(id=survey)

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)

            survey = self.request.GET.get('survey', None)
            if survey is None:
                return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

            if len(response.data) == 0:
                return Response([], status=status.HTTP_200_OK)

            shGroups = SHGroup.objects.filter(survey_id=survey).values()
            projectTeams = Team.objects.filter(project_id=response.data[0]['project']).values()

            drivers = Driver.objects.filter(survey_id=survey).values()
            myMaps = SHCategory.objects.filter(survey_id=survey, mapType__name="MyMap").values()
            projectMaps = SHCategory.objects.filter(survey_id=survey, mapType__name="ProjectMap").values()

            ret = response.data[0]
            ret['shGroup'] = shGroups
            ret['projectTeam'] = projectTeams
            ret['myMap'] = myMaps
            ret['projectMap'] = projectMaps
            
            return Response(ret, status=status.HTTP_200_OK)
        except Exception as error:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

# wip
# adminsurveyadd api
class AdminSurveyAddViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if "items" in request.data else request.data
        many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        projectUser = ProjectUser(survey_id=serializer.data['id'], user_id=177, projectUserTitle="Consultant", projectOrganization="Other", projectAdmin=True, addByProjectUser_id=703)
        projectUser.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# wip
# flagged response api
class AdminReportConfigurationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Segment.objects.all()
    serializer_class = SegmentSerializer

    def get_queryset(self):
        queryset = Segment.objects.all()
        return queryset
        
# wip
# adminsurveyedit api
class AdminSurveyEditView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def save_dict_list(self, data, model, serializer_instance, survey=60):
        for i in range(len(data)):
            if 'id' in data[i]:
                instance = model.objects.get(id=data[i]['id'])
                for key in data[i]:
                    if data[i][key] is None:
                        pass
                    elif isinstance(data[i][key], dict):
                        pass
                    elif key == 'survey':
                        setattr(instance, 'survey_id', data[i][key])
                    else:
                        setattr(instance, key, data[i][key])
                instance.save()
            else:
                if model==ProjectUser:
                    users = User.objects.filter(email=data[i]['user']['email'])
                    if len(users) == 0:
                        user = User(first_name=data[i]['user']['first_name'], last_name=data[i]['user']['last_name'], email=data[i]['user']['email'], username=data[i]['user']['email'], password="p#vh#@3jkda3$")
                        user.save()
                        organization = Organization(name=data[i]['user']['organization']['name'], user_id=user.id)
                        organization.save()
                    else:
                        user = users[0]
                    projectUser = ProjectUser(addByProjectUser_id=data[i]['addByProjectUser']['id'], projectOrganization=data[i]['projectOrganization'], projectUserRoleDesc=data[i]['projectUserRoleDesc'], projectUserTitle=data[i]['projectUserTitle'], shGroup_id=data[i]['shGroup']['id'], shType_id=data[i]['shType']['id'], team_id=data[i]['team']['id'], user_id=user.id, survey_id=survey, sendInvite=data[i]['sendInvite'])
                    projectUser.save()
                elif model==Driver:
                    driver = Driver(survey_id=data[i]['survey_id'], driverName=data[i]['driverName'], driveOrder=data[i]['driveOrder'], iconPath=data[i]['iconPath'])
                    driver.save()
                elif model==AMQuestion:
                    amQuestion = AMQuestion(survey_id=data[i]['survey_id'], controlType_id=data[i]['controlType_id'], amqOrder=data[i]['amqOrder'], driver_id=data[i]['driver_id'], subdriver=data[i]['subdriver'], questionText=data[i]['questionText'], sliderTextLeft=data[i]['sliderTextLeft'], sliderTextRight=data[i]['sliderTextRight'], topicPrompt=data[i]['topicPrompt'], skipOptionYN=True, commentPrompt=data[i]['commentPrompt'])
                    amQuestion.save()
                    amQuestion.shGroup = data[i]['shGroup']
                    amQuestion.skipOption=data[i]['skipOption']
                    amQuestion.save()
                elif model==AOQuestion:
                    aoQuestion = AOQuestion(survey_id=data[i]['survey_id'], controlType_id=data[i]['controlType_id'], amqOrder=data[i]['amqOrder'], driver_id=data[i]['driver_id'], subdriver=data[i]['subdriver'], questionText=data[i]['questionText'], sliderTextLeft=data[i]['sliderTextLeft'], sliderTextRight=data[i]['sliderTextRight'], topicPrompt=data[i]['topicPrompt'], skipOptionYN=True, commentPrompt=data[i]['commentPrompt'])
                    aoQuestion.save()
                    aoQuestion.shGroup = data[i]['shGroup']
                    aoQuestion.skipOption=data[i]['skipOption']
                    aoQuestion.save()
                elif model==Segment:
                    if 'shgroups' in data[i]:
                        shgroups = data[i]['shgroups']
                    else:
                        shgroups = []
                    if 'teams' in data[i]:
                        teams = data[i]['teams']
                    else:
                        teams = []
                    if 'organizations' in data[i]:
                        organizations = data[i]['organizations']
                    else:
                        organizations = []
                    segment_data = Segment(shgroups=shgroups, teams=teams, organizations=organizations, survey_id=survey)
                    segment_data.save()
                elif model==SHGroup:
                    shGroup = SHGroup(survey_id=data[i]['survey_id'], SHGroupName=data[i]['SHGroupName'], responsePercent=data[i]['responsePercent'])
                    shGroup.save()
                else:
                    serializer = serializer_instance(data=data[i])
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

    def save_user_list(self, userList):
        for userData in userList:
            if 'id' in userData:
                instance = ProjectUser.objects.get(id=userData['id'])
                if userData['shGroup'] is not None:
                    instance.shGroup_id = userData['shGroup']['id']
                if userData['shType'] is not None:
                    instance.shType_id = userData['shType']['id']
                if userData['team'] is not None:
                    instance.team_id = userData['team']['id']
                instance.save()
                jsonData = [userData['user']]
                self.save_dict_list(jsonData, User, UserSerializer)
                if userData['user']['organization'] is not None:
                    instance = Organization.objects.get(id=userData['user']['organization']['id'])
                    instance.name = userData['user']['organization']['name']
                    instance.save()
            else:
                pass

    def post(self, request):
        survey = request.data['survey']

        # saving survey
        newSurvey = Survey.objects.get(id=survey)
        newSurvey.surveyTitle = request.data['projectSetup']['surveyTitle']
        newSurvey.customGroup1 = request.data['projectConfiguration']['customGroup1']
        newSurvey.customGroup2 = request.data['projectConfiguration']['customGroup2']
        newSurvey.customGroup3 = request.data['projectConfiguration']['customGroup3']
        newSurvey.anonymityThreshold = request.data['projectConfiguration']['anonymityThreshold']
        newSurvey.projectManager = request.data['projectSetup']['projectManager']
        newSurvey.save()

        # saving tour
        if len(request.data['projectSetup']['tour']) > 0:
            if 'id' in request.data['projectSetup']['tour'][0]:
                tour = ConfigPage.objects.get(survey_id=survey)
                tour.pageName = request.data['projectSetup']['tour'][0]["pageName"]
                tour.tabName = request.data['projectSetup']['tour'][0]["tabName"]
                tour.pageContent = request.data['projectSetup']['tour'][0]["pageContent"]
                tour.save()
            else:
                tour = ConfigPage(pageName=request.data['projectSetup']['tour'][0]["pageName"], tabName=request.data['projectSetup']['tour'][0]["tabName"], pageContent=request.data['projectSetup']['tour'][0]["pageContent"])
        else:
            pass

        # saving more info
        moreInfo = request.data['projectSetup']['moreInfo']
        self.save_dict_list(moreInfo, NikelMobilePage, NikelMobilePageSerializer, survey)

        # saving drivers
        driverList = request.data['projectConfiguration']['driverList']
        self.save_dict_list(driverList, Driver, DriverSerializer, survey)

        # saving my maps and project maps
        # myMaps = request.data['projectConfiguration']['myMap']
        # self.save_dict_list(myMaps, SHCategory, SHCategorySerializer)
        
        # projectMaps = request.data['projectConfiguration']['projectMap']
        # self.save_dict_list(projectMaps, SHCategory, SHCategorySerializer)

        # saving shGroups
        shGroups = request.data['projectConfiguration']['shGroup']
        self.save_dict_list(shGroups, SHGroup, SHGroupSerializer, survey)

        # saving project teams
        projectTeams = request.data['projectConfiguration']['projectTeam']
        self.save_dict_list(projectTeams, Team, TeamSerializer, survey)

        #saving project users
        projectUsers = request.data['userAdministration']['projectUser']
        self.save_dict_list(projectUsers, ProjectUser, ProjectUserSerializer, survey)
        self.save_user_list(projectUsers)

        #saving amQuestions and aoQuestions
        amQuestions = request.data['surveyConfiguration']['amQuestionList']
        self.save_dict_list(amQuestions, AMQuestion, AMQuestionSerializer, survey)
        
        aoQuestions = request.data['surveyConfiguration']['aoQuestionList']
        self.save_dict_list(aoQuestions, AOQuestion, AOQuestionSerializer, survey)

        if 'segments' in request.data:
            segment = request.data['segments']
            self.save_dict_list([segment], Segment, SegmentSerializer, survey)

        flaggedResponses = request.data['flaggedResponses']
        for fr in flaggedResponses:
            print(fr)
            response = AMResponseAcknowledgement.objects.get(id=fr)
            response.flagStatus = 0
            response.save()
        # if survey is None:
        #     return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

        # try:
        #     project = Survey.objects.get(id=survey)

        res = {
            "self": self,
            "request": request
        }
        return Response(request.data, status=status.HTTP_200_OK)

#adminuploadimages api
class AdminUploadImagesView(APIView):
    def post(self, request):
        data = request.data
        survey = Survey.objects.get(id=data['survey'])
        if 'projectLogo' in data:
            survey.projectLogo = data['projectLogo']
            # del data['projectLogo']
        else:
            survey.projectLogo = ''
        if 'companyLogo' in data:
            survey.companyLogo = data['companyLogo']
            # del data['companyLogo']
        else:
            survey.companyLogo = ''
        # if data['video'] is not None:
        #     configpage = ConfigPage
        #     survey.companyLogo = data['companyLogo']
        #     del data['companyLogo']
        survey.save()
        return Response({'data': 'hello'}, status=status.HTTP_200_OK)

# adminsurveybyuser api
class AdminSurveyByUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    def get_queryset(self):
        queryset = Survey.objects.all()

        user = self.request.user
        if user is not None:
            projectAdminList = ProjectUser.objects.filter(user=user, projectAdmin=True).values_list('survey', flat=True)
            projectAdminList = list(projectAdminList)
            queryset = queryset.filter(id__in=projectAdminList)

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)

            # user = self.request.GET.get('user', None)

            # projectAdminList = ProjectUser.objects.filter(user__id=user, projectAdmin=True).values_list('survey', flat=True)
            # projectAdminList = list(projectAdminList)
            ret = []

            for i in range(len(response.data)):
                seatsPurchased = response.data[i]['seatsPurchased']
                totalIdentified = ProjectUser.objects.filter(survey__id=response.data[i]['id']).count()
                teamMembers = ProjectUser.objects.filter(survey__id=response.data[i]['id'], shType__shTypeName='Team Member').count()
                stakeholders = ProjectUser.objects.filter(survey__id=response.data[i]['id'], shType__shTypeName='Stakeholder').count()
                totalInvited = ProjectUser.objects.filter(survey__id=response.data[i]['id'], sendInvite=True).count()
                seatsAvailable = seatsPurchased - totalInvited
                overallSentimentObj = AMResponse.objects.filter(
                    survey__id=response.data[i]['id'], amQuestion__subdriver="Overall Sentiment", latestResponse=True, controlType="SLIDER").aggregate(Avg('integerValue'))
                overallSentiment = 0
                if overallSentimentObj["integerValue__avg"] is not None:
                    overallSentiment = round(overallSentimentObj["integerValue__avg"] / 10, 2)

                item = {
                    "id": response.data[i]['id'],
                    "surveyTitle": response.data[i]['surveyTitle'],
                    "projectManager": response.data[i]['projectManager'],
                    "totalIdentified": totalIdentified,
                    "createdAt": response.data[i]['created_at'],
                    "teamMembers": teamMembers,
                    "stakeholders": stakeholders,
                    "totalInvited": totalInvited,
                    "seatsAvailable": seatsAvailable,
                    "overallSentiment": overallSentiment,
                    "isActive": response.data[i]['isActive'],
                }

                ret.append(item)

            return Response(ret, status=status.HTTP_200_OK)

        except Exception as error:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        # ret = super(AdminSurveyByUserViewSet, self).partial_update(request, *args, **kwargs)
        kwargs['partial'] = True

        return super().update(request, *args, **kwargs)

#adminreportaccess api
class AdminSurveyReportAccessViewSet(viewsets.ModelViewSet):
    permisson_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Segment.objects.all()
    serializer_class = SegmentSerializer

    def get_queryset(self):
        queryset = Segment.objects.all()

        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey)

        return queryset

# adminamquestion api    
class AdminSurveyAMQuestionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AMQuestion.objects.all().order_by('amqOrder')
    serializer_class = AMQuestionSerializer

    def get_queryset(self):
        queryset = AMQuestion.objects.all()

        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey).order_by('amqOrder')

        return queryset

# adminaoquestion api
class AdminSurveyAOQuestionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AOQuestion.objects.all().order_by('aoqOrder')
    serializer_class = AOQuestionSerializer

    def get_queryset(self):
        queryset = AOQuestion.objects.all()

        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(survey__id=survey).order_by('aoqOrder')

        return queryset

# useravatar api
class UserAvatarViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = UserAvatar.objects.all()
    serializer_class = UserAvatarSerializer

# get comment is flagged
class IsFlaggedView(APIView):
    def get_object(self, pk, request):
        userId = request.GET.get('user')
        return AMResponseAcknowledgement.objects.filter(amResponse__amQuestion__id=pk, amResponse__projectUser__user_id=userId).values()
    def get(self, request, *args, **kwargs):
        temp = self.get_object(kwargs['pk'], request)
        if len(temp) > 0:
            temp = temp[len(temp) - 1]
            # return Response(temp, status=status.HTTP_200_OK)
            if temp is not None:
                if temp['flagStatus'] > 0:
                    return Response(True, status=status.HTTP_200_OK)
                else:
                    return Response(False, status=status.HTTP_200_OK)
        else:
            return Response(False, status=status.HTTP_200_OK)

class FlaggedResponsesViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponseAcknowledgement.objects.all()
    serializer_class = AMResponseAcknowledgementSerializerForFlag
    def get_queryset(self):
        queryset = AMResponseAcknowledgement.objects.filter(flagStatus__range=[1, 5])

        survey = self.request.query_params.get('survey', None)
        if survey is not None:
            queryset = queryset.filter(amResponse__survey__id=survey)

        return queryset

# api-token-auth api
class CustomAuthToken(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super(CustomAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'id': token.user_id})

# get_csrf api
def get_csrf(request):
    return HttpResponse("{0}".format(csrf.get_token(request)), content_type="text/plain")

# amquestioncnt api
class AMQuestionCountBySHGroup(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        queryset = AMQuestion.objects.all()
        survey = self.request.query_params.get('survey', None)
        driver = self.request.query_params.get('driver', None)
        project = self.request.query_params.get('project', None)
        user = self.request.user

        if survey is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if driver is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if project is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if user is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

        queryset = queryset.filter(survey__id=survey, driver__driverName=driver)

        shgroup = SHGroup.objects.all()
        shgroup = shgroup.filter(survey__id=survey)

        shgroupserializer = SHGroupSerializer(shgroup, many=True)
        for i in range(len(shgroupserializer.data)):
            shgroupserializer.data[i]['questionCnt'] = queryset.filter(
                shGroup__id=shgroupserializer.data[i]['id']).count()
        
        team = Team.objects.all()
        team = team.filter(project__id=project)

        teamserializer = TeamSerializer(team, many=True)
        for i in range(len(teamserializer.data)):
            teamserializer.data[i]['questionCnt'] = queryset.filter(
                survey__project__id=teamserializer.data[i]['project']).count()

        organization = Organization.objects.all()
        organization = organization.filter(user=user)

        organizationserializer = OrganizationSerializer(organization, many=True)
        for i in range(len(organizationserializer.data)):
            organizationserializer.data[i]['questionCnt'] = queryset.count()
        
        ret = ''
        ret = {
            "shgroupData": shgroupserializer.data,
            "teamData": teamserializer.data,
            "organizationData": organizationserializer.data
        }

        return Response(ret, status=status.HTTP_200_OK)

class PasswordChecker(object):
   def strongPasswordChecker(self, s):
      missing_type = 3
      if any('a' <= c <= 'z' for c in s): missing_type -= 1
      if any('A' <= c <= 'Z' for c in s): missing_type -= 1
      if any(c.isdigit() for c in s): missing_type -= 1
      change = 0
      one = two = 0
      p = 2
      while p < len(s):
         if s[p] == s[p-1] == s[p-2]:
            length = 2
            while p < len(s) and s[p] == s[p-1]:
               length += 1
               p += 1
            change += length / 3
            if length % 3 == 0: one += 1
            elif length % 3 == 1: two += 1
         else:
            p += 1
      if len(s) < 6:
         return max(missing_type, 6 - len(s))
      elif len(s) <= 20:
         return max(missing_type, change)
      else:
         delete = len(s) - 20
         change -= min(delete, one)
         change -= min(max(delete - one, 0), two * 2) / 2
         change -= max(delete - one - 2 * two, 0) / 3
         return delete + max(missing_type, change)

# changepassword api
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated,
                          permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def post(self, request):
        password = request.data['password']
        email = request.data['email']

        try:
            token = Token.objects.get(key=request.data['token'])
            user = User.objects.get(id=token.user_id)
            ob = PasswordChecker()
            if (ob.strongPasswordChecker(password) != 0):
                Response("Password is too weak", status=status.HTTP_400_BAD_REQUEST)

            if (email == user.email):
                user.set_password(password)
                user.save()

                return Response('success', status=status.HTTP_201_CREATED)

            return Response("Invaid Email", status=status.HTTP_400_BAD_REQUEST)

        except Token.DoesNotExist:
            token = None

            return Response("Invaid Token", status=status.HTTP_400_BAD_REQUEST)

# perceptionreality api
class PerceptionRealityView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        survey = self.request.query_params.get('survey', None)
        projectUser = self.request.query_params.get('projectUser', None)

        if survey is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if projectUser is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
            
        amqueryset = AMResponse.objects.filter(survey__id=survey, subProjectUser__id=projectUser)
        aoqueryset = AOResponse.objects.filter(survey__id=survey, subProjectUser__id=projectUser)

        amserializer = AMResponseSerializer(amqueryset, many=True)
        aoserializer = AOResponseSerializer(aoqueryset, many=True)

        perception = 0
        perceptionTotal = 0
        reality = 0
        realityTotal = 0
        for i in range(len(aoserializer.data)):
            perceptionTotal = perceptionTotal + aoserializer.data[i]['integerValue']
        for j in range(len(amserializer.data)):
            realityTotal = realityTotal + amserializer.data[j]['integerValue']

        if perceptionTotal > 0:
            perception = perceptionTotal / len(aoserializer.data)

        if realityTotal > 0:
            reality = realityTotal / len(amserializer.data)

        res = [perception, reality]

        return Response(res, status=status.HTTP_200_OK)

# stakeholder api
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

# setpassword api
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
            ob = PasswordChecker()
            if (ob.strongPasswordChecker(password) != 0):
                Response("Password is too weak", status=status.HTTP_400_BAD_REQUEST)    
            if (email == user.email):
                user.set_password(password)
                user.save()

                return Response('success', status=status.HTTP_201_CREATED) 

            return Response("Invaid Email", status=status.HTTP_400_BAD_REQUEST)

        except Token.DoesNotExist:
            token = None

            return Response("Invaid Token", status=status.HTTP_400_BAD_REQUEST)

# userprofile api
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

# userguidemode api
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

# wordcloud api
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
        driver = self.request.query_params.get('driver', None)
        limit = self.request.query_params.get('limit', None)

        if (survey is not None) & (projectUser is not None) & (driver is not None):
            amqueryset = amqueryset.filter(survey__id=survey, subProjectUser__id=projectUser, amQuestion__driver__driverName=driver)
            aoqueryset = aoqueryset.filter(survey__id=survey, subProjectUser__id=projectUser, aoQuestion__driver__driverName=driver)
        elif (survey is not None) & (projectUser is not None):
            amqueryset = amqueryset.filter(survey__id=survey, subProjectUser__id=projectUser)
            aoqueryset = aoqueryset.filter(survey__id=survey, subProjectUser__id=projectUser)
        elif (survey is not None) & (driver is not None):
            amqueryset = amqueryset.filter(survey__id=survey, amQuestion__driver__driverName=driver)
            aoqueryset = aoqueryset.filter(survey__id=survey, aoQuestion__driver__driverName=driver)
        elif (projectUser is not None) & (driver is not None):
            amqueryset = amqueryset.filter(subProjectUser__id=survey, amQuestion__driver__driverName=driver)
            aoqueryset = aoqueryset.filter(
                subProjectUser__id=survey, aoQuestion__driver__driverName=driver)
        elif survey is not None:
            amqueryset = amqueryset.filter(survey__id=survey)
            aoqueryset = aoqueryset.filter(survey__id=survey)
        elif projectUser is not None:
            amqueryset = amqueryset.filter(subProjectUser__id=projectUser)
            aoqueryset = aoqueryset.filter(subProjectUser__id=projectUser)
        elif driver is not None:
            amqueryset = amqueryset.filter(amQuestion__driver__driverName=driver)
            aoqueryset = aoqueryset.filter(aoQuestion__driver__driverName=driver)
        
        amserializer = AMResponseSerializer(amqueryset, many=True)
        aoserializer = AOResponseSerializer(aoqueryset, many=True)

        res = amserializer.data + aoserializer.data

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

        wordList = re.findall(r"[\w\']+", wordstring.lower())
        filteredWordList = [w for w in wordList if w not in stopwords]
        wordfreq = [filteredWordList.count(p) for p in filteredWordList]
        dictionary = dict(list(zip(filteredWordList, wordfreq)))

        aux = [(dictionary[key], key) for key in dictionary]
        aux.sort()
        aux.reverse()
        
        if limit is not None:
            return Response(aux[:int(limit)])
        else:
            return Response(aux)

# bubblechart api
class BubbleChartView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        survey = self.request.query_params.get('survey', None)
        projectUser = self.request.query_params.get('projectUser', None)

        if survey is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if projectUser is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

        shgroupqueryset = SHGroup.objects.filter(survey__id=survey)
        shgroupserializer = SHGroupSerializer(shgroupqueryset, many=True)
        
        for i in range(len(shgroupserializer.data)):
            amqueryset = AMResponse.objects.filter(survey__id=survey, subProjectUser__id=projectUser, amQuestion__shGroup__id=shgroupserializer.data[i]['id'])
            aoqueryset = AOResponse.objects.filter(survey__id=survey, subProjectUser__id=projectUser, aoQuestion__shGroup__id=shgroupserializer.data[i]['id'])
            aoqueryforzset = AOResponse.objects.filter(survey__id=survey, aoQuestion__shGroup__id=shgroupserializer.data[i]['id'])

            amserializer = AMResponseSerializer(amqueryset, many=True)
            aoserializer = AOResponseSerializer(aoqueryset, many=True)
            aoforzserializer = AOResponseSerializer(aoqueryforzset, many=True)

            perception = 0
            perceptionTotal = 0
            reality = 0
            realityTotal = 0
            zvalue = 0
            zvalueTotal = 0

            for j in range(len(amserializer.data)):
                realityTotal = realityTotal + amserializer.data[j]['integerValue']
            for k in range(len(aoserializer.data)):
                perceptionTotal = perceptionTotal + aoserializer.data[k]['integerValue']
            for m in range(len(aoforzserializer.data)):
                zvalueTotal = zvalueTotal + aoforzserializer.data[m]['integerValue']

            if realityTotal > 0:
                reality = realityTotal / len(amserializer.data)
            if perceptionTotal > 0:
                perception = perceptionTotal / len(aoserializer.data)
            if zvalueTotal > 0:
                zvalue = zvalueTotal / len(aoforzserializer.data)

            shgroupserializer.data[i]['point'] = {"x": reality, "y": perception, "z": zvalue}

        res = shgroupserializer.data

        return Response(res, status=status.HTTP_200_OK)

# keymenucnt api
class KeyThemesMenuCntView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        projectUser = self.request.query_params.get('projectuser', None)
        survey = self.request.query_params.get('survey', None)
        
        if survey is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if projectUser is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        
        # risk
        ktamresponsequeryset = AMResponse.objects.all().filter(
                amQuestion__questionText="What do you see as the biggest risks to the project?",
                survey__id=survey, controlType="MULTI_TOPICS", latestResponse=True).order_by('projectUser')
        ktamresponseserializer = AMResponseSerializer(ktamresponsequeryset, many=True)
        wordlist = []
        res = ktamresponseserializer.data
        for i in range(len(res)):
            # if res[i]['topicValue'] != "":
            #     wordlist.append(res[i]['topicValue'])
            amresponsetopic_queryset = AMResponseTopic.objects.filter(amQuestion_id=res[i]['amQuestion'], responseUser_id=res[i]['subProjectUser'])
            amresponsetopic_serializer = AMResponseTopicSerializer(amresponsetopic_queryset, many=True)
            amresponsetopic_data = amresponsetopic_serializer.data
            for j in range(len(amresponsetopic_data)):
                wordlist.append(
                    amresponsetopic_data[j]['topicName'].lower().capitalize())

        wordfreq = [wordlist.count(p) for p in wordlist]
        dictionary = dict(list(zip(wordlist, wordfreq)))
        aux = [(dictionary[key], key) for key in dictionary]

        # overall sentiment
        overallsentimentktamresponsequeryset = AMResponse.objects.all().filter(
                amQuestion__questionText="How do you feel about this project in your own words?",
            survey__id=survey, latestResponse=True).order_by('projectUser')
        overallsentimentktamresponseserializer = AMResponseForReportSerializer(overallsentimentktamresponsequeryset, many=True)

        # unspoken problem
        unspokenproblemktamresponsequeryset = AMResponse.objects.all().filter(
                amQuestion__questionText="Is there a problem that people aren't talking openly about?",
                survey__id=survey, latestResponse=True).order_by('projectUser')
        unspokenproblemktamresponseserializer = AMResponseForReportSerializer(unspokenproblemktamresponsequeryset, many=True)

        # project interest
        piktamresponsequeryset = AMResponse.objects.all().filter(
                amQuestion__questionText="What do you care most about on this project?",
            survey__id=survey, controlType="MULTI_TOPICS", latestResponse=True).order_by('projectUser')
        piktamresponseserializer = AMResponseSerializer(
            piktamresponsequeryset, many=True)
        piwordlist = []
        pires = piktamresponseserializer.data
        for i in range(len(pires)):
            # if pires[i]['topicValue'] != "":
            #     piwordlist.append(pires[i]['topicValue'])
            amresponsetopic_queryset = AMResponseTopic.objects.filter(amQuestion_id=pires[i]['amQuestion'], responseUser_id=pires[i]['subProjectUser'])
            amresponsetopic_serializer = AMResponseTopicSerializer(amresponsetopic_queryset, many=True)
            amresponsetopic_data = amresponsetopic_serializer.data
            for j in range(len(amresponsetopic_data)):
                piwordlist.append(amresponsetopic_data[j]['topicName'].lower().capitalize())

        piwordfreq = [piwordlist.count(p) for p in piwordlist]
        pidictionary = dict(list(zip(piwordlist, piwordfreq)))
        piaux = [(pidictionary[key], key) for key in pidictionary]
        
        # personal interest
        peiktamresponsequeryset = AMResponse.objects.all().filter(
            amQuestion__questionText="What do you personally want to get out of this project?",
            survey__id=survey, controlType="MULTI_TOPICS", latestResponse=True).order_by('projectUser')
        peiktamresponseserializer = AMResponseSerializer(
            peiktamresponsequeryset, many=True)
        peiwordlist = []
        peires = peiktamresponseserializer.data
        for i in range(len(peires)):
            # if peires[i]['topicValue'] != "":
            #     peiwordlist.append(peires[i]['topicValue'])
            amresponsetopic_queryset = AMResponseTopic.objects.filter(amQuestion_id=peires[i]['amQuestion'], responseUser_id=peires[i]['subProjectUser'])
            amresponsetopic_serializer = AMResponseTopicSerializer(amresponsetopic_queryset, many=True)
            amresponsetopic_data = amresponsetopic_serializer.data
            for j in range(len(amresponsetopic_data)):
                peiwordlist.append(amresponsetopic_data[j]['topicName'].lower().capitalize())

        peiwordfreq = [peiwordlist.count(p) for p in peiwordlist]
        peidictionary = dict(list(zip(peiwordlist, peiwordfreq)))
        peiaux = [(peidictionary[key], key) for key in peidictionary]

        # improvement - positives
        ipktamresponsequeryset = AMResponse.objects.all().filter(
            amQuestion__questionText="In your opinion, what is going well on the project?",
            survey__id=survey, controlType="MULTI_TOPICS", latestResponse=True).order_by('projectUser')
        ipktamresponseserializer = AMResponseSerializer(
            ipktamresponsequeryset, many=True)
        ipwordlist = []
        ipres = ipktamresponseserializer.data
        for i in range(len(ipres)):
            # if ipres[i]['topicValue'] != "":
            #     ipwordlist.append(ipres[i]['topicValue'])
            amresponsetopic_queryset = AMResponseTopic.objects.filter(
                amQuestion_id=ipres[i]['amQuestion'], responseUser_id=ipres[i]['subProjectUser'])
            amresponsetopic_serializer = AMResponseTopicSerializer(
                amresponsetopic_queryset, many=True)
            amresponsetopic_data = amresponsetopic_serializer.data
            for j in range(len(amresponsetopic_data)):
                ipwordlist.append(amresponsetopic_data[j]['topicName'].lower().capitalize())

        ipwordfreq = [ipwordlist.count(p) for p in ipwordlist]
        ipdictionary = dict(list(zip(ipwordlist, ipwordfreq)))
        ipaux = [(ipdictionary[key], key) for key in ipdictionary]

        # improvement - start
        istktamresponsequeryset = AMResponse.objects.all().filter(
            amQuestion__questionText="What should we start doing?",
            survey__id=survey, controlType="MULTI_TOPICS", latestResponse=True).order_by('projectUser')
        istktamresponseserializer = AMResponseSerializer(
            istktamresponsequeryset, many=True)
        istwordlist = []
        istres = istktamresponseserializer.data
        for i in range(len(istres)):
            # if istres[i]['topicValue'] != "":
            #     istwordlist.append(istres[i]['topicValue'])
            amresponsetopic_queryset = AMResponseTopic.objects.filter(amQuestion_id=istres[i]['amQuestion'], responseUser_id=istres[i]['subProjectUser'])
            amresponsetopic_serializer = AMResponseTopicSerializer(amresponsetopic_queryset, many=True)
            amresponsetopic_data = amresponsetopic_serializer.data
            for j in range(len(amresponsetopic_data)):
                istwordlist.append(amresponsetopic_data[j]['topicName'].lower().capitalize())

        istwordfreq = [istwordlist.count(p) for p in istwordlist]
        istdictionary = dict(list(zip(istwordlist, istwordfreq)))
        istaux = [(istdictionary[key], key) for key in istdictionary]

        # improvement - stop
        ispktamresponsequeryset = AMResponse.objects.all().filter(
            amQuestion__questionText="What should we stop doing?",
            survey__id=survey, controlType="MULTI_TOPICS", latestResponse=True).order_by('projectUser')
        ispktamresponseserializer = AMResponseSerializer(
            ispktamresponsequeryset, many=True)
        ispwordlist = []
        ispres = ispktamresponseserializer.data
        for i in range(len(ispres)):
            # if ispres[i]['topicValue'] != "":
            #     ispwordlist.append(ispres[i]['topicValue'])
            amresponsetopic_queryset = AMResponseTopic.objects.filter(amQuestion_id=ispres[i]['amQuestion'], responseUser_id=ispres[i]['subProjectUser'])
            amresponsetopic_serializer = AMResponseTopicSerializer(amresponsetopic_queryset, many=True)
            amresponsetopic_data = amresponsetopic_serializer.data
            for j in range(len(amresponsetopic_data)):
                ispwordlist.append(amresponsetopic_data[j]['topicName'].lower().capitalize())

        ispwordfreq = [ispwordlist.count(p) for p in ispwordlist]
        ispdictionary = dict(list(zip(ispwordlist, ispwordfreq)))
        ispaux = [(ispdictionary[key], key) for key in ispdictionary]

        # improvement - change
        icktamresponsequeryset = AMResponse.objects.all().filter(
            amQuestion__questionText="What should we do differently?",
            survey__id=survey, controlType="MULTI_TOPICS", latestResponse=True).order_by('projectUser')
        icktamresponseserializer = AMResponseSerializer(
            icktamresponsequeryset, many=True)
        icwordlist = []
        icres = icktamresponseserializer.data
        for i in range(len(icres)):
            # if icres[i]['topicValue'] != "":
            #     icwordlist.append(icres[i]['topicValue'])
            amresponsetopic_queryset = AMResponseTopic.objects.filter(amQuestion_id=icres[i]['amQuestion'], responseUser_id=icres[i]['subProjectUser'])
            amresponsetopic_serializer = AMResponseTopicSerializer(amresponsetopic_queryset, many=True)
            amresponsetopic_data = amresponsetopic_serializer.data
            for j in range(len(amresponsetopic_data)):
                icwordlist.append(amresponsetopic_data[j]['topicName'].lower().capitalize())

        icwordfreq = [icwordlist.count(p) for p in icwordlist]
        icdictionary = dict(list(zip(icwordlist, icwordfreq)))
        icaux = [(icdictionary[key], key) for key in icdictionary]

        finalResult = {
            "risks": len(aux),
            "overall_sentiment": len(overallsentimentktamresponseserializer.data),
            "unspoken_problem": len(unspokenproblemktamresponseserializer.data),
            "project_interest": len(piaux),
            "personal_interest": len(peiaux),
            "improvement_keep": len(ipaux),
            "improvement_start": len(istaux),
            "improvement_change": len(icaux),
            "improvement_stop": len(ispaux)
        }

        return Response(finalResult, status=status.HTTP_200_OK)

# class MyMatrixView(APIView):
#     permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

#     @classmethod
#     def get_extra_actions(cls):
#         return []

#     def get(self, format=None):
#         # params
#         # 1: group by "person"
#         # 2: group by "group"
#         # 3: group by "team"
#         # 4: group by "organisation"
#         projectUser = self.request.query_params.get('projectuser', None)
#         survey = self.request.query_params.get('survey', None)

#         if survey is None:
#             return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
#         if projectUser is None:
#             return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

#         driverqueryset = Driver.objects.all().filter(survey__id=survey, isStandard=True).order_by('driveOrder')
#         driverserializer = DriverSerializer(driverqueryset, many=True)
        
#         for i in range(len(driverserializer.data)):
#             aoresponsequeryset = AOResponse.objects.all().filter(aoQuestion__driver__id=driverserializer.data[i]['id'], survey__id=survey, subProjectUser__id=projectUser).order_by('projectUser')
#             aoresponseserializer = AOResponseForMatrixSerializer(aoresponsequeryset, many=True)
#             driverserializer.data[i]['aoResponseData'] = aoresponseserializer.data
        
#         paQuestionList = (
#             "How do you think {{{FULLNAME}}} feels the {{{PROJECTNAME}}} project is going?",
#             "How engaged do you think {{{FULLNAME}}} should be on this project?",
#             "How engaged / involved do you think {{{FULLNAME}}} actually is on this project?",
#             "How influential do you think {{{FULLNAME}}} is on this project?",
#             "Do you think {{{FULLNAME}}} thinks this project will meet its objectives?",
#             "How do you think {{{FULLNAME}}} views the overall culture on the project?",
#             "How would you describe your working relationship with {{{FULLNAME}}} at present?",
#             "How important do you think this project is to {{{FULLNAME}}}?"
#         )

#         paaoresponsequeryset = AOResponse.objects.all().filter(
#             Q(aoQuestion__questionText="How do you think {{{FULLNAME}}} feels the {{{PROJECTNAME}}} project is going?") |
#             Q(aoQuestion__questionText="How engaged do you think {{{FULLNAME}}} should be on this project?") |
#             Q(aoQuestion__questionText="How engaged / involved do you think {{{FULLNAME}}} actually is on this project?") |
#             Q(aoQuestion__questionText="How influential do you think {{{FULLNAME}}} is on this project?") |
#             Q(aoQuestion__questionText="Do you think {{{FULLNAME}}} thinks this project will meet its objectives?") |
#             Q(aoQuestion__questionText="How do you think {{{FULLNAME}}} views the overall culture on the project?") |
#             Q(aoQuestion__questionText="How would you describe your working relationship with {{{FULLNAME}}} at present?") |
#             Q(aoQuestion__questionText="How important do you think this project is to {{{FULLNAME}}}?"),
#             survey__id=survey, subProjectUser__id=projectUser).order_by('projectUser')
#         paaoresponseserializer = AOResponseForMatrixSerializer(paaoresponsequeryset, many=True)
        
#         perceptionAccuracyDriverItem = {
#             "id": 9999999,
#             "driverName": "Perception Accuracy",
#             "iconPath": "",
#             "driveOrder": 999999,
#             "isStandard": True,
#             "survey": survey,
#             "aoResponseData": paaoresponseserializer.data
#         }

#         retList = list(driverserializer.data)
#         retList.append(perceptionAccuracyDriverItem)

#         return Response(retList, status=status.HTTP_200_OK)


# keytheme api
# AM - Confidence - Risk: What do you see as the biggest risks to the project?
# AM - Sentiment - Own Words: How do you feel about this project in your own words?
# AM - Culture - Unspoken Problem: Is there a problem that people aren't talking openly about?
# AM - Interest - Project Interest: What do you care most about on this project?
# AM - Interest - Personal Interest: What do you personally want to get out of this project?
# AM - Improvement - Positives: In your opinion, what is going well on the project?
# AM - Improvement - Start: What should we start doing?
# AM - Improvement - Stop: What should we stop doing?
# AM - Improvement - Change: What should we do differently?
class KeyThemesView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        projectUser = self.request.query_params.get('projectuser', None)
        survey = self.request.query_params.get('survey', None)
        tab = self.request.query_params.get('tab', None)
        limit = self.request.query_params.get('limit', None)

        if survey is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if projectUser is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if tab is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if (int(tab) < 1) | (int(tab) > 9):
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        
        # Risk
        # AM - Confidence - Risk: What do you see as the biggest risks to the project?
        if tab == "1":
            ktamresponsequeryset = AMResponse.objects.all().filter(
                amQuestion__questionText="What do you see as the biggest risks to the project?",
                survey__id=survey, controlType="MULTI_TOPICS", latestResponse=True).order_by('projectUser')
            ktamresponseserializer = AMResponseSerializer(ktamresponsequeryset, many=True)

            wordlist = []
            res = ktamresponseserializer.data
            for i in range(len(res)):
                # if res[i]['topicValue'] != "":
                #     wordlist.append(res[i]['topicValue'])
                amresponsetopic_queryset = AMResponseTopic.objects.filter(amQuestion_id=res[i]['amQuestion'], responseUser_id=res[i]['subProjectUser'])
                amresponsetopic_serializer = AMResponseTopicSerializer(amresponsetopic_queryset, many=True)
                amresponsetopic_data = amresponsetopic_serializer.data
                for j in range(len(amresponsetopic_data)):
                    wordlist.append(amresponsetopic_data[j]['topicName'].lower().capitalize())

            wordfreq = [wordlist.count(p) for p in wordlist]
            dictionary = dict(list(zip(wordlist, wordfreq)))

            aux = [(dictionary[key], key) for key in dictionary]
            aux.sort()
            aux.reverse()

            ret = []
            for j in range(len(aux)):
                upvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=1, voteValue=1).count()
                downvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=1, voteValue=-1).count()
                tempQueryset = KeyThemeUpDownVote.objects.filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=1, projectUser=projectUser)
                myStatus = KeyThemeUpDownVoteSerializer(tempQueryset, many=True)

                ret.append({"key": aux[j][1], "freq": aux[j][0],
                            "upvoteCount": upvoteCnt, "downvoteCount": downvoteCnt, "myStatus": myStatus.data})

            if limit is not None:
                return Response(ret[:int(limit)], status=status.HTTP_200_OK)
            else:
                return Response(ret, status=status.HTTP_200_OK)

        # Overall Sentiment
        # AM - Sentiment - Own Words: How do you feel about this project in your own words?
        elif tab == "2":
            ktamresponsequeryset = AMResponse.objects.all().filter(
                amQuestion__questionText="How do you feel about this project in your own words?",
                survey__id=survey, latestResponse=True).order_by('projectUser')
            ktamresponseserializer = AMResponseForReportSerializer(ktamresponsequeryset, many=True)

            ret = ktamresponseserializer.data
            for i in range(len(ret)):
                tmpQuerySet = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'])
                amResponseAcknowledgementSerializer = AMResponseAcknowledgementSerializer(tmpQuerySet, many=True)
                ret[i]['acknowledgementData'] = amResponseAcknowledgementSerializer.data
                ret[i]['likeCount'] = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], likeStatus=1).count()
                ret[i]['dislikeCount'] = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], likeStatus=2).count()
                ret[i]['thanksForSharingCount'] = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], acknowledgeStatus=1).count()
                ret[i]['greatIdeaCount'] = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], acknowledgeStatus=2).count()
                ret[i]['workingOnItCount'] = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], acknowledgeStatus=3).count()
                ret[i]['letsTalkAboutItCount'] = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], acknowledgeStatus=4).count()
                ret[i]['agreeCount'] = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], acknowledgeStatus=5).count()
                ret[i]['tellUsMoreCount'] = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], acknowledgeStatus=6).count()
                ret[i]['individualCount'] = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], flagStatus=1).count()
                ret[i]['commenterCount'] = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], flagStatus=2).count()
                ret[i]['nonConstructiveCount'] = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], flagStatus=3).count()
                ret[i]['outOfPolicyCount'] = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], flagStatus=4).count()
                ret[i]['aggressiveCount'] = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], flagStatus=5).count()
                myQuerySet = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], projectUser__id=projectUser)
                myAmResponseAcknowledgementSerializer = AMResponseAcknowledgementSerializer(myQuerySet, many=True)
                ret[i]['myStatus'] = myAmResponseAcknowledgementSerializer.data
            
            return Response(ret, status=status.HTTP_200_OK)

        # Unspoken Problem
        # AM - Culture - Unspoken Problem: Is there a problem that people aren't talking openly about?
        elif tab == "3":
            ktamresponsequeryset = AMResponse.objects.all().filter(
                amQuestion__questionText="Is there a problem that people aren't talking openly about?",
                survey__id=survey, latestResponse=True).order_by('projectUser')
            ktamresponseserializer = AMResponseForReportSerializer(ktamresponsequeryset, many=True)

            ret = ktamresponseserializer.data
            for i in range(len(ret)):
                tmpQuerySet = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'])
                amResponseAcknowledgementSerializer = AMResponseAcknowledgementSerializer(tmpQuerySet, many=True)
                ret[i]['acknowledgementData'] = amResponseAcknowledgementSerializer.data
                ret[i]['likeCount'] = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'], likeStatus=1).count()
                ret[i]['dislikeCount'] = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'], likeStatus=2).count()
                ret[i]['thanksForSharingCount'] = AMResponseAcknowledgement.objects.all(
                ).filter(amResponse__id=ret[i]['id'], acknowledgeStatus=1).count()
                ret[i]['greatIdeaCount'] = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'], acknowledgeStatus=2).count()
                ret[i]['workingOnItCount'] = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'], acknowledgeStatus=3).count()
                ret[i]['letsTalkAboutItCount'] = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'], acknowledgeStatus=4).count()
                ret[i]['agreeCount'] = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'], acknowledgeStatus=5).count()
                ret[i]['tellUsMoreCount'] = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'], acknowledgeStatus=6).count()
                ret[i]['individualCount'] = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'], flagStatus=1).count()
                ret[i]['commenterCount'] = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'], flagStatus=2).count()
                ret[i]['nonConstructiveCount'] = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'], flagStatus=3).count()
                ret[i]['outOfPolicyCount'] = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'], flagStatus=4).count()
                ret[i]['aggressiveCount'] = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'], flagStatus=5).count()
                myQuerySet = AMResponseAcknowledgement.objects.all().filter(amResponse__id=ret[i]['id'], projectUser__id=projectUser)
                myAmResponseAcknowledgementSerializer = AMResponseAcknowledgementSerializer(
                    myQuerySet, many=True)
                ret[i]['myStatus'] = myAmResponseAcknowledgementSerializer.data

            return Response(ret, status=status.HTTP_200_OK)

        # Project Interest
        # AM - Interest - Project Interest: What do you care most about on this project?
        elif tab == "4":
            ktamresponsequeryset = AMResponse.objects.all().filter(
                amQuestion__questionText="What do you care most about on this project?",
                survey__id=survey, controlType="MULTI_TOPICS", latestResponse=True).order_by('projectUser')
            ktamresponseserializer = AMResponseSerializer(
                ktamresponsequeryset, many=True)

            wordlist = []
            res = ktamresponseserializer.data
            for i in range(len(res)):
                # if res[i]['topicValue'] != "":
                #     wordlist.append(res[i]['topicValue'])
                amresponsetopic_queryset = AMResponseTopic.objects.filter(amQuestion_id=res[i]['amQuestion'], responseUser_id=res[i]['subProjectUser'])
                amresponsetopic_serializer = AMResponseTopicSerializer(amresponsetopic_queryset, many=True)
                amresponsetopic_data = amresponsetopic_serializer.data
                for j in range(len(amresponsetopic_data)):
                    wordlist.append(amresponsetopic_data[j]['topicName'].lower().capitalize())

            wordfreq = [wordlist.count(p) for p in wordlist]
            dictionary = dict(list(zip(wordlist, wordfreq)))

            aux = [(dictionary[key], key) for key in dictionary]
            aux.sort()
            aux.reverse()

            ret = []
            for j in range(len(aux)):
                upvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=4, voteValue=1).count()
                downvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=4, voteValue=-1).count()
                tempQueryset = KeyThemeUpDownVote.objects.filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=4, projectUser=projectUser)
                myStatus = KeyThemeUpDownVoteSerializer(tempQueryset, many=True)

                ret.append({"key": aux[j][1], "freq": aux[j][0],
                            "upvoteCount": upvoteCnt, "downvoteCount": downvoteCnt, "myStatus": myStatus.data})

            if limit is not None:
                return Response(ret[:int(limit)], status=status.HTTP_200_OK)
            else:
                return Response(ret, status=status.HTTP_200_OK)

        # Personal Interest
        # AM - Interest - Personal Interest:What do you personally want to get out of this project?
        elif tab == "5":
            ktamresponsequeryset = AMResponse.objects.all().filter(
                amQuestion__questionText="What do you personally want to get out of this project?",
                survey__id=survey, controlType="MULTI_TOPICS").order_by('projectUser')
            ktamresponseserializer = AMResponseSerializer(
                ktamresponsequeryset, many=True)

            
            wordlist = []
            res = ktamresponseserializer.data
            for i in range(len(res)):
                # if res[i]['topicValue'] != "":
                #     wordlist.append(res[i]['topicValue'])
                amresponsetopic_queryset = AMResponseTopic.objects.filter(
                    amQuestion_id=res[i]['amQuestion'], responseUser_id=res[i]['subProjectUser'])
                amresponsetopic_serializer = AMResponseTopicSerializer(
                    amresponsetopic_queryset, many=True)
                amresponsetopic_data = amresponsetopic_serializer.data
                for j in range(len(amresponsetopic_data)):
                    wordlist.append(amresponsetopic_data[j]['topicName'].lower().capitalize())

            wordfreq = [wordlist.count(p) for p in wordlist]
            dictionary = dict(list(zip(wordlist, wordfreq)))

            aux = [(dictionary[key], key) for key in dictionary]
            aux.sort()
            aux.reverse()

            ret = []
            for j in range(len(aux)):
                upvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=5, voteValue=1).count()
                downvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=5, voteValue=-1).count()
                tempQueryset = KeyThemeUpDownVote.objects.filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=5, projectUser=projectUser)
                myStatus = KeyThemeUpDownVoteSerializer(
                    tempQueryset, many=True)

                ret.append({"key": aux[j][1], "freq": aux[j][0],
                            "upvoteCount": upvoteCnt, "downvoteCount": downvoteCnt, "myStatus": myStatus.data})

            if limit is not None:
                return Response(ret[:int(limit)], status=status.HTTP_200_OK)
            else:
                return Response(ret, status=status.HTTP_200_OK)

        # Positives
        # AM - Improvement - Positives: In your opinion, what is going well on the project?
        elif tab == "6":
            ktamresponsequeryset = AMResponse.objects.all().filter(
                amQuestion__questionText="In your opinion, what is going well on the project?",
                survey__id=survey, controlType="MULTI_TOPICS", latestResponse=True).order_by('projectUser')
            ktamresponseserializer = AMResponseSerializer(
                ktamresponsequeryset, many=True)

            wordlist = []
            res = ktamresponseserializer.data
            for i in range(len(res)):
                # if res[i]['topicValue'] != "":
                #     wordlist.append(res[i]['topicValue'])
                amresponsetopic_queryset = AMResponseTopic.objects.filter(
                    amQuestion_id=res[i]['amQuestion'], responseUser_id=res[i]['subProjectUser'])
                amresponsetopic_serializer = AMResponseTopicSerializer(
                    amresponsetopic_queryset, many=True)
                amresponsetopic_data = amresponsetopic_serializer.data
                for j in range(len(amresponsetopic_data)):
                    wordlist.append(amresponsetopic_data[j]['topicName'].lower().capitalize())

            wordfreq = [wordlist.count(p) for p in wordlist]
            dictionary = dict(list(zip(wordlist, wordfreq)))

            aux = [(dictionary[key], key) for key in dictionary]
            aux.sort()
            aux.reverse()

            ret = []
            for j in range(len(aux)):
                upvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=6, voteValue=1).count()
                downvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=6, voteValue=-1).count()
                tempQueryset = KeyThemeUpDownVote.objects.filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=6, projectUser=projectUser)
                myStatus = KeyThemeUpDownVoteSerializer(
                    tempQueryset, many=True)

                ret.append({"key": aux[j][1], "freq": aux[j][0],
                            "upvoteCount": upvoteCnt, "downvoteCount": downvoteCnt, "myStatus": myStatus.data})

            if limit is not None:
                return Response(ret[:int(limit)], status=status.HTTP_200_OK)
            else:
                return Response(ret, status=status.HTTP_200_OK)

        # Start
        # AM - Improvement - Start: What should we start doing?
        elif tab == "7":
            ktamresponsequeryset = AMResponse.objects.all().filter(
                amQuestion__questionText="What should we start doing?",
                survey__id=survey, controlType="MULTI_TOPICS", latestResponse=True).order_by('projectUser')
            ktamresponseserializer = AMResponseSerializer(
                ktamresponsequeryset, many=True)

            wordlist = []
            res = ktamresponseserializer.data
            for i in range(len(res)):
                # if res[i]['topicValue'] != "":
                #     wordlist.append(res[i]['topicValue'])
                amresponsetopic_queryset = AMResponseTopic.objects.filter(
                    amQuestion_id=res[i]['amQuestion'], responseUser_id=res[i]['subProjectUser'])
                amresponsetopic_serializer = AMResponseTopicSerializer(
                    amresponsetopic_queryset, many=True)
                amresponsetopic_data = amresponsetopic_serializer.data
                for j in range(len(amresponsetopic_data)):
                    wordlist.append(amresponsetopic_data[j]['topicName'].lower().capitalize())

            wordfreq = [wordlist.count(p) for p in wordlist]
            dictionary = dict(list(zip(wordlist, wordfreq)))

            aux = [(dictionary[key], key) for key in dictionary]
            aux.sort()
            aux.reverse()

            ret = []
            for j in range(len(aux)):
                upvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=7, voteValue=1).count()
                downvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=7, voteValue=-1).count()
                tempQueryset = KeyThemeUpDownVote.objects.filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=7, projectUser=projectUser)
                myStatus = KeyThemeUpDownVoteSerializer(
                    tempQueryset, many=True)

                ret.append({"key": aux[j][1], "freq": aux[j][0],
                            "upvoteCount": upvoteCnt, "downvoteCount": downvoteCnt, "myStatus": myStatus.data})

            if limit is not None:
                return Response(ret[:int(limit)], status=status.HTTP_200_OK)
            else:
                return Response(ret, status=status.HTTP_200_OK)

        # stop
        # AM - Improvement - Stop: What should we stop doing?
        elif tab == "8":
            ktamresponsequeryset = AMResponse.objects.all().filter(
                amQuestion__questionText="What should we stop doing?",
                survey__id=survey, controlType="MULTI_TOPICS", latestResponse=True).order_by('projectUser')
            ktamresponseserializer = AMResponseSerializer(ktamresponsequeryset, many=True)

            wordlist = []
            res = ktamresponseserializer.data
            for i in range(len(res)):
                # if res[i]['topicValue'] != "":
                #     wordlist.append(res[i]['topicValue'])
                amresponsetopic_queryset = AMResponseTopic.objects.filter(
                    amQuestion_id=res[i]['amQuestion'], responseUser_id=res[i]['subProjectUser'])
                amresponsetopic_serializer = AMResponseTopicSerializer(
                    amresponsetopic_queryset, many=True)
                amresponsetopic_data = amresponsetopic_serializer.data
                for j in range(len(amresponsetopic_data)):
                    wordlist.append(amresponsetopic_data[j]['topicName'].lower().capitalize())

            wordfreq = [wordlist.count(p) for p in wordlist]
            dictionary = dict(list(zip(wordlist, wordfreq)))

            aux = [(dictionary[key], key) for key in dictionary]
            aux.sort()
            aux.reverse()

            ret = []
            for j in range(len(aux)):
                upvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=8, voteValue=1).count()
                downvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=8, voteValue=-1).count()
                tempQueryset = KeyThemeUpDownVote.objects.filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=8, projectUser=projectUser)
                myStatus = KeyThemeUpDownVoteSerializer(
                    tempQueryset, many=True)

                ret.append({"key": aux[j][1], "freq": aux[j][0],
                            "upvoteCount": upvoteCnt, "downvoteCount": downvoteCnt, "myStatus": myStatus.data})

            if limit is not None:
                return Response(ret[:int(limit)], status=status.HTTP_200_OK)
            else:
                return Response(ret, status=status.HTTP_200_OK)

        # change
        # AM - Improvement - Change: What should we do differently?
        elif tab == "9":
            ktamresponsequeryset = AMResponse.objects.all().filter(
                amQuestion__questionText="What should we do differently?",
                survey__id=survey, controlType="MULTI_TOPICS", latestResponse=True).order_by('projectUser')
            ktamresponseserializer = AMResponseSerializer(
                ktamresponsequeryset, many=True)

            wordlist = []
            res = ktamresponseserializer.data
            for i in range(len(res)):
                # if res[i]['topicValue'] != "":
                #     wordlist.append(res[i]['topicValue'])
                amresponsetopic_queryset = AMResponseTopic.objects.filter(
                    amQuestion_id=res[i]['amQuestion'], responseUser_id=res[i]['subProjectUser'])
                amresponsetopic_serializer = AMResponseTopicSerializer(
                    amresponsetopic_queryset, many=True)
                amresponsetopic_data = amresponsetopic_serializer.data
                for j in range(len(amresponsetopic_data)):
                    wordlist.append(amresponsetopic_data[j]['topicName'].lower().capitalize())

            wordfreq = [wordlist.count(p) for p in wordlist]
            dictionary = dict(list(zip(wordlist, wordfreq)))

            aux = [(dictionary[key], key) for key in dictionary]
            aux.sort()
            aux.reverse()

            ret = []
            for j in range(len(aux)):
                upvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=9, voteValue=1).count()
                downvoteCnt = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=9, voteValue=-1).count()
                tags = KeyThemeUpDownVote.objects.all().filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=9)[0].tags
                tempQueryset = KeyThemeUpDownVote.objects.filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=9, projectUser=projectUser)
                myStatus = KeyThemeUpDownVoteSerializer(
                    tempQueryset, many=True)

                ret.append({"key": aux[j][1], "freq": aux[j][0],
                            "upvoteCount": upvoteCnt, "downvoteCount": downvoteCnt, "myStatus": myStatus.data, "tags": tags})

            if limit is not None:
                return Response(ret[:int(limit)], status=status.HTTP_200_OK)
            else:
                return Response(ret, status=status.HTTP_200_OK)

# mymatrix api
class MyMatrixView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        # params
        # 1: group by "person"
        # 2: group by "group"
        # 3: group by "team"
        # 4: group by "organisation"
        projectUser = self.request.query_params.get('projectuser', None)
        survey = self.request.query_params.get('survey', None)

        if survey is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if projectUser is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

        driverqueryset = Driver.objects.all().filter(survey__id=survey, isStandard=True).order_by('driveOrder')
        driverserializer = DriverSerializer(driverqueryset, many=True)
        
        for i in range(len(driverserializer.data)):
            aoresponsequeryset = AOResponse.objects.all().filter(aoQuestion__driver__id=driverserializer.data[i]['id'], survey__id=survey, subProjectUser__id=projectUser).order_by('projectUser')
            aoresponseserializer = AOResponseForMatrixSerializer(aoresponsequeryset, many=True)
            driverserializer.data[i]['aoResponseData'] = aoresponseserializer.data
        
        paQuestionList = (
            "How do you think {{{FULLNAME}}} feels the {{{PROJECTNAME}}} project is going?",
            "How engaged do you think {{{FULLNAME}}} should be on this project?",
            "How engaged / involved do you think {{{FULLNAME}}} actually is on this project?",
            "How influential do you think {{{FULLNAME}}} is on this project?",
            "Do you think {{{FULLNAME}}} thinks this project will meet its objectives?",
            "How do you think {{{FULLNAME}}} views the overall culture on the project?",
            "How would you describe your working relationship with {{{FULLNAME}}} at present?",
            "How important do you think this project is to {{{FULLNAME}}}?"
        )

        paaoresponsequeryset = AOResponse.objects.all().filter(
            Q(aoQuestion__questionText="How do you think {{{FULLNAME}}} feels the {{{PROJECTNAME}}} project is going?") |
            Q(aoQuestion__questionText="How engaged do you think {{{FULLNAME}}} should be on this project?") |
            Q(aoQuestion__questionText="How engaged / involved do you think {{{FULLNAME}}} actually is on this project?") |
            Q(aoQuestion__questionText="How influential do you think {{{FULLNAME}}} is on this project?") |
            Q(aoQuestion__questionText="Do you think {{{FULLNAME}}} thinks this project will meet its objectives?") |
            Q(aoQuestion__questionText="How do you think {{{FULLNAME}}} views the overall culture on the project?") |
            Q(aoQuestion__questionText="How would you describe your working relationship with {{{FULLNAME}}} at present?") |
            Q(aoQuestion__questionText="How important do you think this project is to {{{FULLNAME}}}?"),
            survey__id=survey, subProjectUser__id=projectUser).order_by('projectUser')
        paaoresponseserializer = AOResponseForMatrixSerializer(paaoresponsequeryset, many=True)
        
        perceptionAccuracyDriverItem = {
            "id": 9999999,
            "driverName": "Perception Accuracy",
            "iconPath": "",
            "driveOrder": 999999,
            "isStandard": True,
            "survey": survey,
            "aoResponseData": paaoresponseserializer.data
        }

        retList = list(driverserializer.data)
        retList.append(perceptionAccuracyDriverItem)

        return Response(retList, status=status.HTTP_200_OK)

# projectmatrix api
class ProjectMatrixView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        survey = self.request.query_params.get('survey', None)
        projectUser = self.request.query_params.get('projectuser', None)

        if survey is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if projectUser is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

        driverqueryset = Driver.objects.all().filter(
            survey__id=survey, isStandard=True).order_by('driveOrder')
        driverserializer = DriverSerializer(driverqueryset, many=True)

        for i in range(len(driverserializer.data)):
            aoresponsequeryset = AOResponse.objects.all().filter(aoQuestion__driver__id=driverserializer.data[i]['id'], survey__id=survey).order_by('projectUser')
            aoresponseserializer = AOResponseForMatrixSerializer(aoresponsequeryset, many=True)
            driverserializer.data[i]['aoResponseData'] = aoresponseserializer.data

        paQuestionList = (
            "How do you think {{{FULLNAME}}} feels the {{{PROJECTNAME}}} project is going?",
            "How engaged do you think {{{FULLNAME}}} should be on this project?",
            "How engaged / involved do you think {{{FULLNAME}}} actually is on this project?",
            "How influential do you think {{{FULLNAME}}} is on this project?",
            "Do you think {{{FULLNAME}}} thinks this project will meet its objectives?",
            "How do you think {{{FULLNAME}}} views the overall culture on the project?",
            "How would you describe your working relationship with {{{FULLNAME}}} at present?",
            "How important do you think this project is to {{{FULLNAME}}}?"
        )

        paaoresponsequeryset = AOResponse.objects.all().filter(
            Q(aoQuestion__questionText="How do you think {{{FULLNAME}}} feels the {{{PROJECTNAME}}} project is going?") |
            Q(aoQuestion__questionText="How engaged do you think {{{FULLNAME}}} should be on this project?") |
            Q(aoQuestion__questionText="How engaged / involved do you think {{{FULLNAME}}} actually is on this project?") |
            Q(aoQuestion__questionText="How influential do you think {{{FULLNAME}}} is on this project?") |
            Q(aoQuestion__questionText="Do you think {{{FULLNAME}}} thinks this project will meet its objectives?") |
            Q(aoQuestion__questionText="How do you think {{{FULLNAME}}} views the overall culture on the project?") |
            Q(aoQuestion__questionText="How would you describe your working relationship with {{{FULLNAME}}} at present?") |
            Q(aoQuestion__questionText="How important do you think this project is to {{{FULLNAME}}}?"),
            survey__id=survey).order_by('projectUser')
        paaoresponseserializer = AOResponseForMatrixSerializer(
            paaoresponsequeryset, many=True)

        perceptionAccuracyDriverItem = {
            "id": 9999999,
            "driverName": "Perception Accuracy",    
            "iconPath": "",
            "driveOrder": 999999,
            "isStandard": True,
            "survey": survey,
            "aoResponseData": paaoresponseserializer.data
        }

        retList = list(driverserializer.data)
        retList.append(perceptionAccuracyDriverItem)

        return Response(retList, status=status.HTTP_200_OK)
          
# advisorinsights api
class AdvisorInsightsView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        survey = self.request.query_params.get('survey', None)
        # projectUser = self.request.query_params.get('projectuser', None)

        if survey is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        # if projectUser is None:
        #     return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

        # amresponsereportqueryset = AMResponse.objects.all().filter(survey__id=survey, controlType="SLIDER", amQuestion__subdriver__in=["Optimism", "Overall Sentiment", "Safety"])
        amresponsereportqueryset = AMResponse.objects.all().filter(survey__id=survey, controlType="SLIDER", amQuestion__subdriver__in=["Optimism", "Overall Sentiment", "Safety"], latestResponse=True)
        amresponsereportserializer = AMResponseForAdvisorSerializer(amresponsereportqueryset, many=True)
        amresponsereportdata = amresponsereportserializer.data
        aryProjectUsers = AMResponse.objects.all().filter(survey__id=survey, controlType="SLIDER", amQuestion__subdriver__in=["Optimism", "Overall Sentiment", "Safety"], latestResponse=True).values_list('projectUser', flat=True).distinct()

        # aryTeams = []
        # aryProjectUsers = []
        # aryDepartments = []
        # aryOrganizations = []
        # aryShGroups = []
        # aryTeamsData = {}
        # aryShGroupsData = {}
        # aryOrganizationsData = {}

        aryPositiveNegativeTeams = []
        aryPositiveNegativeShGroups = []
        aryPositiveNegativeOrganizations = []
        aryPositiveNegativeTeamsData = {}
        aryPositiveNegativeShGroupsData = {}
        aryPositiveNegativeOrganizationsData = {}

        aryOptimisticPessimisticTeams = []
        aryOptimisticPessimisticShGroups = []
        aryOptimisticPessimisticOrganizations = []
        aryOptimisticPessimisticTeamsData = {}
        aryOptimisticPessimisticShGroupsData = {}
        aryOptimisticPessimisticOrganizationsData = {}

        aryLeastSafeTeams = []
        aryLeastSafeShGroups = []
        aryLeastSafeOrganizations = []
        aryLeastSafeTeamsData = {}
        aryLeastSafeShGroupsData = {}
        aryLeastSafeOrganizationsData = {}
        
        positiveNegativeQuestionId = 0
        optimisticPessimisticQuestionId = 0
        leastSafeQuestionId = 0

        try:
            positiveNegativeQuestionId = AMQuestion.objects.get(survey__id=survey, subdriver="Overall Sentiment").id
        except AMQuestion.DoesNotExist:
            pass

        try:
            optimisticPessimisticQuestionId = AMQuestion.objects.get(survey__id=survey, subdriver="Optimism").id
        except AMQuestion.DoesNotExist:
            pass

        # leastSafeQuestionId = AMQuestion.objects.get(
        #     survey__id=survey, questionText="Is it safe to speak up to share an unpopular opinion?").id
        try:
            leastSafeQuestionId = AMQuestion.objects.get(survey__id=survey, subdriver="Safety").id
        except AMQuestion.DoesNotExist:
            pass
            
        # leastSafeTeamName = ""
        # leastSafeTeamTotalScore = 0
        # leastSafeTeamCnt = 0
        # leastSafeTeamScore = 0
        # leastSafeShGroupName = ""
        # leastSafeShGroupTotalScore = 0
        # leastSafeShGroupCnt = 0
        # leastSafeShGroupScore = 0
        # leastSafeOrgName = ""
        # leastSafeOrgTotalScore = 0
        # leastSafeOrgCnt = 0
        # leastSafeOrgScore = 0
        # for i in range(len(amresponsereportdata)):
            # if amresponsereportdata[i]['projectUser']["team"]["name"] not in aryTeams:
            #     aryTeams.append(
            #         amresponsereportdata[i]['projectUser']["team"]["name"])
            # if (amresponsereportdata[i]['projectUser']['shGroup'] is not None):
            #     if amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName'] not in aryShGroups:
            #         aryShGroups.append(
            #             amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName'])
            # if (amresponsereportdata[i]['projectUser']["id"] not in aryProjectUsers):
            #     aryProjectUsers.append(
            #         amresponsereportdata[i]['projectUser']["id"])
            # if (amresponsereportdata[i]['projectUser']['user']['userteam'] is not None):
            #     if (amresponsereportdata[i]['projectUser']['user']['userteam']['name'] not in aryDepartments):
            #         aryDepartments.append(
            #             amresponsereportdata[i]['projectUser']['user']['userteam']['name'])
            # if amresponsereportdata[i]['projectUser']['projectOrganization'] is not None:
            #     if amresponsereportdata[i]['projectUser']['projectOrganization'] not in aryOrganizations:
            #         aryOrganizations.append(amresponsereportdata[i]['projectUser']['projectOrganization'])

            # if positiveNegativeQuestionId == amresponsereportdata[i]['amQuestion']:
            #     aryPositiveNegativeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]] = {"totalScore": 0, "cnt": 0, "score": 0}
            #     if (amresponsereportdata[i]['projectUser']['shGroup'] is not None):
            #         aryPositiveNegativeShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']] = {"totalScore": 0, "cnt": 0, "score": 0}
            #     if amresponsereportdata[i]['projectUser']['projectOrganization'] is not None:
            #         aryPositiveNegativeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']] = {"totalScore": 0, "cnt": 0, "score": 0}

            # if optimisticPessimisticQuestionId == amresponsereportdata[i]['amQuestion']:
            #     aryOptimisticPessimisticTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]] = {"totalScore": 0, "cnt": 0, "score": 0}
            #     if (amresponsereportdata[i]['projectUser']['shGroup'] is not None):
            #         aryOptimisticPessimisticShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']] = {"totalScore": 0, "cnt": 0, "score": 0}
            #     if amresponsereportdata[i]['projectUser']['projectOrganization'] is not None:
            #         aryOptimisticPessimisticOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']] = {"totalScore": 0, "cnt": 0, "score": 0}

            # if leastSafeQuestionId == amresponsereportdata[i]['amQuestion']:
            #     aryLeastSafeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]] = {"totalScore": 0, "cnt": 0, "score": 0}
            #     if (amresponsereportdata[i]['projectUser']['shGroup'] is not None):
            #         aryLeastSafeShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']] = {"totalScore": 0, "cnt": 0, "score": 0}
            #     if amresponsereportdata[i]['projectUser']['projectOrganization'] is not None:
            #         aryLeastSafeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']] = {"totalScore": 0, "cnt": 0, "score": 0}

        for i in range(len(amresponsereportdata)):
            # if amresponsereportdata[i]['projectUser']["survey"] == survey:
            if positiveNegativeQuestionId == amresponsereportdata[i]['amQuestion']:
                if amresponsereportdata[i]['projectUser']["team"]["name"] not in aryPositiveNegativeTeamsData:
                    aryPositiveNegativeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]] = {"totalScore": 0, "cnt": 0, "score": 0}
                aryPositiveNegativeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["totalScore"] += amresponsereportdata[i]["integerValue"]
                aryPositiveNegativeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["cnt"] += 1
                aryPositiveNegativeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["score"] = round(aryPositiveNegativeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["totalScore"] / 10 / aryPositiveNegativeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["cnt"], 2)
                
                if (amresponsereportdata[i]['projectUser']['shGroup'] is not None):
                    if amresponsereportdata[i]['projectUser']["shGroup"]["SHGroupName"] not in aryPositiveNegativeShGroupsData:
                        aryPositiveNegativeShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]
                                                    ["SHGroupName"]] = {"totalScore": 0, "cnt": 0, "score": 0}
                    aryPositiveNegativeShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]
                                                    ["SHGroupName"]]["totalScore"] += amresponsereportdata[i]["integerValue"]
                    aryPositiveNegativeShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]
                                                    ["SHGroupName"]]["cnt"] += 1
                    aryPositiveNegativeShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]
                                                    ["SHGroupName"]]["score"] = round(aryPositiveNegativeShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]["SHGroupName"]]["totalScore"] / 10 / aryPositiveNegativeShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]["SHGroupName"]]["cnt"], 2)
                if amresponsereportdata[i]['projectUser']['projectOrganization'] is not None:
                    if amresponsereportdata[i]['projectUser']["projectOrganization"] not in aryPositiveNegativeOrganizationsData:
                        aryPositiveNegativeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']] = {"totalScore": 0, "cnt": 0, "score": 0}
                    aryPositiveNegativeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["totalScore"] += amresponsereportdata[i]["integerValue"]
                    aryPositiveNegativeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["cnt"] += 1
                    aryPositiveNegativeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["score"] = round(aryPositiveNegativeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["totalScore"] / 10 / aryPositiveNegativeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["cnt"], 2)
                    
            if optimisticPessimisticQuestionId == amresponsereportdata[i]['amQuestion']:
                if amresponsereportdata[i]['projectUser']["team"]["name"] not in aryOptimisticPessimisticTeamsData:
                    aryOptimisticPessimisticTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]] = {"totalScore": 0, "cnt": 0, "score": 0}
                aryOptimisticPessimisticTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["totalScore"] += amresponsereportdata[i]["integerValue"]
                aryOptimisticPessimisticTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["cnt"] += 1
                aryOptimisticPessimisticTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["score"] = round(aryOptimisticPessimisticTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["totalScore"] / 10 / aryOptimisticPessimisticTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["cnt"], 2)
                
                if (amresponsereportdata[i]['projectUser']['shGroup'] is not None):
                    if amresponsereportdata[i]['projectUser']["shGroup"]["SHGroupName"] not in aryOptimisticPessimisticShGroupsData:
                        aryOptimisticPessimisticShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]
                                                    ["SHGroupName"]] = {"totalScore": 0, "cnt": 0, "score": 0}
                    aryOptimisticPessimisticShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]
                                                ["SHGroupName"]]["totalScore"] += amresponsereportdata[i]["integerValue"]
                    aryOptimisticPessimisticShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]
                                                    ["SHGroupName"]]["cnt"] += 1
                    aryOptimisticPessimisticShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]
                                                    ["SHGroupName"]]["score"] = round(aryOptimisticPessimisticShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]["SHGroupName"]]["totalScore"] / 10 / aryOptimisticPessimisticShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]["SHGroupName"]]["cnt"], 2)
                if amresponsereportdata[i]['projectUser']['projectOrganization'] is not None:
                    if amresponsereportdata[i]['projectUser']['projectOrganization'] not in aryOptimisticPessimisticOrganizationsData:
                        aryOptimisticPessimisticOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']] = {"totalScore": 0, "cnt": 0, "score": 0}
                    aryOptimisticPessimisticOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["totalScore"] += amresponsereportdata[i]["integerValue"]
                    aryOptimisticPessimisticOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["cnt"] += 1
                    aryOptimisticPessimisticOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["score"] = round(aryOptimisticPessimisticOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["totalScore"] / 10 / aryOptimisticPessimisticOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["cnt"], 2)
                # aryOptimisticPessimisticTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["totalScore"] += amresponsereportdata[i]["integerValue"]
                # aryOptimisticPessimisticTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["cnt"] += 1
                # aryOptimisticPessimisticTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["score"] = round(aryOptimisticPessimisticTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["totalScore"] / 10 / aryOptimisticPessimisticTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["cnt"], 2)
                # if (amresponsereportdata[i]['projectUser']['shGroup'] is not None):
                #     aryOptimisticPessimisticShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['totalScore'] += amresponsereportdata[i]["integerValue"]
                #     aryOptimisticPessimisticShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['cnt'] += 1
                #     aryOptimisticPessimisticShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['score'] = round(aryOptimisticPessimisticShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['totalScore'] / 10 / aryOptimisticPessimisticShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['cnt'], 2)
                # if amresponsereportdata[i]['projectUser']['projectOrganization'] is not None:
                #     aryOptimisticPessimisticOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]['totalScore'] += amresponsereportdata[i]["integerValue"]
                #     aryOptimisticPessimisticOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]['cnt'] += 1
                #     aryOptimisticPessimisticOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]['score'] = round(aryOptimisticPessimisticOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]['totalScore'] / 10 / aryOptimisticPessimisticOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]['cnt'], 2)

            if leastSafeQuestionId == amresponsereportdata[i]['amQuestion']:
                if amresponsereportdata[i]['projectUser']["team"]["name"] not in aryLeastSafeTeamsData:
                    aryLeastSafeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]] = {"totalScore": 0, "cnt": 0, "score": 0}
                aryLeastSafeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["totalScore"] += amresponsereportdata[i]["integerValue"]
                aryLeastSafeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["cnt"] += 1
                aryLeastSafeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["score"] = round(aryLeastSafeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["totalScore"] / 10 / aryLeastSafeTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["cnt"], 2)
                
                if (amresponsereportdata[i]['projectUser']['shGroup'] is not None):
                    if amresponsereportdata[i]['projectUser']["shGroup"]["SHGroupName"] not in aryLeastSafeShGroupsData:
                        aryLeastSafeShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']
                                                    ['SHGroupName']] = {"totalScore": 0, "cnt": 0, "score": 0}
                    aryLeastSafeShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']
                                                ['SHGroupName']]["totalScore"] += amresponsereportdata[i]["integerValue"]
                    aryLeastSafeShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']
                                                    ['SHGroupName']]["cnt"] += 1
                    aryLeastSafeShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']
                                                ['SHGroupName']]["score"] = round(aryLeastSafeShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]["SHGroupName"]]["totalScore"] / 10 / aryLeastSafeShGroupsData[amresponsereportdata[i]['projectUser']["shGroup"]["SHGroupName"]]["cnt"], 2)
                if amresponsereportdata[i]['projectUser']['projectOrganization'] is not None:
                    if amresponsereportdata[i]['projectUser']['projectOrganization'] not in aryLeastSafeOrganizationsData:
                        aryLeastSafeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']] = {"totalScore": 0, "cnt": 0, "score": 0}
                    aryLeastSafeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["totalScore"] += amresponsereportdata[i]["integerValue"]
                    aryLeastSafeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["cnt"] += 1
                    aryLeastSafeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["score"] = round(aryLeastSafeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["totalScore"] / 10 / aryLeastSafeOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']]["cnt"], 2)
        aryFilteredProjectUsers = aryProjectUsers
        recommendedProjectUsersQuerySet = ProjectUser.objects.filter(survey=survey, pk__in=aryFilteredProjectUsers)
        recommendedProjectUserSerializer = ProjectUserForAdvisorSerializer(
            recommendedProjectUsersQuerySet, many=True)
        
        # test data for catchup
        aryFilteredCatchupProjectUsers = aryProjectUsers
        recommendedCatchupProjectUsersQuerySet = ProjectUser.objects.filter(survey=survey, pk__in=aryFilteredCatchupProjectUsers)
        recommendedCatchupProjectUserSerializer = ProjectUserForAdvisorSerializer(recommendedCatchupProjectUsersQuerySet, many=True)

        responsedTeamMembers = 0
        responsedStakeholders = 0
        invitedTeamMembers = ProjectUser.objects.filter(survey__id=survey, sendInvite=True, shType__shTypeName="Team Member").values()
        invitedStakeholders = ProjectUser.objects.filter(
            survey__id=survey, sendInvite=True, shType__shTypeName="Stakeholder").values()

        # shGroups = SHGroup.objects.filter(survey_id=survey)
        # for shGroup in shGroups:
        #     AMResponse.objects.filter(survey_id=survey, projectUser__shType__shTypeName="Stakeholder", projectUser__shGroup__id=shGroup.id, sendInvite=True, amQuestion__shGroup__id=shGroup.id).values('projectUser__id').annotate(total=Count('projectUser__id'))


        for k in range(len(invitedTeamMembers)):
            try:
                responsePercent = SHGroup.objects.get(
                    survey__id=survey, id=invitedTeamMembers[k]['shGroup_id']).responsePercent
                prefAmQuestionQueryset = AMQuestion.objects.filter(
                    survey__id=survey, shGroup__in=[invitedTeamMembers[k]['shGroup_id']])
                # prefAmQuestionSerializer = AMQuestionSerializer(prefAmQuestionQueryset, many=True)
                # prefAmQuestionData = prefAmQuestionSerializer.data

                totalCnt = prefAmQuestionQueryset.count()
                answeredCnt = AMResponse.objects.filter(Q(projectUser_id=invitedTeamMembers[k]['id'], survey_id=survey, latestResponse=True) & (~Q(controlType='MULTI_TOPICS') | (Q(controlType='MULTI_TOPICS') & ~Q(topicValue='')))).count()
                # answeredCnt = 0
                # for i in range(len(prefAmQuestionData)):
                #     totalCnt = totalCnt + 1
                #     ret = AMResponse.objects.filter(
                #             projectUser_id=invitedTeamMembers[k]['id'], survey_id=survey, amQuestion_id=prefAmQuestionData[i]['id'], latestResponse=True)
                #     if (len(ret) > 0):
                #         if ret[0].controlType == 'MULTI_TOPICS':
                #             if len(ret[0].topicValue) > 0:
                #                 answeredCnt = answeredCnt + 1
                #         else:
                #             answeredCnt = answeredCnt + 1
                
                if totalCnt > 0:
                    currentPercent = answeredCnt * 100 / totalCnt
                    if currentPercent >= responsePercent:
                        responsedTeamMembers = responsedTeamMembers + 1

            except SHGroup.DoesNotExist:
                continue

        for k in range(len(invitedStakeholders)):
            try:
                responsePercent = SHGroup.objects.get(
                    survey__id=survey, id=invitedStakeholders[k]['shGroup_id']).responsePercent
                prefAmQuestionQueryset = AMQuestion.objects.filter(
                    survey__id=survey, shGroup__in=[invitedStakeholders[k]['shGroup_id']])
                # prefAmQuestionSerializer = AMQuestionSerializer(prefAmQuestionQueryset, many=True)
                # prefAmQuestionData = prefAmQuestionSerializer.data

                totalCnt = prefAmQuestionQueryset.count()
                answeredCnt = AMResponse.objects.filter(Q(projectUser_id=invitedStakeholders[k]['id'], survey_id=survey, latestResponse=True) & (~Q(controlType='MULTI_TOPICS') | (Q(controlType='MULTI_TOPICS') & ~Q(topicValue='')))).count()
                # for i in range(len(prefAmQuestionData)):
                #     totalCnt = totalCnt + 1
                #     ret = AMResponse.objects.filter(
                #             projectUser_id=invitedStakeholders[k]['id'], survey_id=survey, amQuestion_id=prefAmQuestionData[i]['id'], latestResponse=True)
                #     if (len(ret) > 0):
                #         if ret[0].controlType == 'MULTI_TOPICS':
                #             if len(ret[0].topicValue) > 0:
                #                 answeredCnt = answeredCnt + 1
                #         else:
                #             answeredCnt = answeredCnt + 1
                
                if totalCnt > 0:
                    currentPercent = answeredCnt * 100 / totalCnt
                    if currentPercent >= responsePercent:
                        responsedStakeholders = responsedStakeholders + 1

            except SHGroup.DoesNotExist:
                continue

        responseRateFromInvitedTeamMembers = 0
        responseRateFromInvitedStakeholders = 0
        if len(invitedTeamMembers) > 0:
            responseRateFromInvitedTeamMembers = responsedTeamMembers * 100 / len(invitedTeamMembers)
        if len(invitedStakeholders) > 0:
            responseRateFromInvitedStakeholders = responsedStakeholders * 100 / len(invitedStakeholders)
        
        aryPositiveNegativeData = []
        for key in aryPositiveNegativeTeamsData:
            item = aryPositiveNegativeTeamsData[key]
            item["key"] = key
            aryPositiveNegativeData.append(item)
        for key in aryPositiveNegativeOrganizationsData:
            item = aryPositiveNegativeOrganizationsData[key]
            item["key"] = key
            aryPositiveNegativeData.append(item)
        for key in aryPositiveNegativeShGroupsData:
            item = aryPositiveNegativeShGroupsData[key]
            item["key"] = key
            aryPositiveNegativeData.append(item)

        aryPositiveNegativeData.sort(key=lambda x: x["score"], reverse=True)

        aryOptimisticPessimisticData = []
        for key in aryOptimisticPessimisticTeamsData:
            item = aryOptimisticPessimisticTeamsData[key]
            item["key"] = key
            aryOptimisticPessimisticData.append(item)
        for key in aryOptimisticPessimisticOrganizationsData:
            item = aryOptimisticPessimisticOrganizationsData[key]
            item["key"] = key
            aryOptimisticPessimisticData.append(item)
        for key in aryOptimisticPessimisticShGroupsData:
            item = aryOptimisticPessimisticShGroupsData[key]
            item["key"] = key
            aryOptimisticPessimisticData.append(item)

        aryOptimisticPessimisticData.sort(key=lambda x: x["score"], reverse=True)

        aryLeastSafeData = []
        for key in aryLeastSafeTeamsData:
            item = aryLeastSafeTeamsData[key]
            item["key"] = key
            aryLeastSafeData.append(item)
        for key in aryLeastSafeShGroupsData:
            item = aryLeastSafeShGroupsData[key]
            item["key"] = key
            aryLeastSafeData.append(item)
        for key in aryLeastSafeOrganizationsData:
            item = aryLeastSafeOrganizationsData[key]
            item["key"] = key
            aryLeastSafeData.append(item)

        aryLeastSafeData.sort(key=lambda x: x["score"], reverse=True)

        summary = {
            "responseRateFromInvitedTeamMembers": responseRateFromInvitedTeamMembers,
            "responseRateFromInvitedStakeholders": responseRateFromInvitedStakeholders,
        }

        positivelyTeamName = ""
        positivelyTeamScore = ""
        positivelyShGroupName = ""
        positivelyShGroupScore = ""
        positivelyOrgName = ""
        positivelyOrgScore = ""
        if len(aryPositiveNegativeData) > 0:
            positivelyTeamName = aryPositiveNegativeData[0]["key"]
            positivelyTeamScore = aryPositiveNegativeData[0]["score"]
        if len(aryPositiveNegativeData) > 1:
            positivelyShGroupName = aryPositiveNegativeData[1]["key"]
            positivelyShGroupScore = aryPositiveNegativeData[1]["score"]
        if len(aryPositiveNegativeData) > 2:
            positivelyOrgName = aryPositiveNegativeData[2]["key"]
            positivelyOrgScore = aryPositiveNegativeData[2]["score"]

        negativelyTeamName = ""
        negativelyTeamScore = ""
        negativelyShGroupName = ""
        negativelyShGroupScore = ""
        negativelyOrgName = ""
        negativelyOrgScore = ""
        if len(aryPositiveNegativeData) > 0:
            negativelyTeamName = aryPositiveNegativeData[-1]["key"]
            negativelyTeamScore = aryPositiveNegativeData[-1]["score"]
        if len(aryPositiveNegativeData) > 1:
            negativelyShGroupName = aryPositiveNegativeData[-2]["key"]
            negativelyShGroupScore = aryPositiveNegativeData[-2]["score"]
        if len(aryPositiveNegativeData) > 2:
            negativelyOrgName = aryPositiveNegativeData[-3]["key"]
            negativelyOrgScore = aryPositiveNegativeData[-3]["score"]

        optimisticTeamName = ""
        optimisticTeamScore = ""
        optimisticShGroupName = ""
        optimisticShGroupScore = ""
        optimisticOrgName = ""
        optimisticOrgScore = ""
        if len(aryOptimisticPessimisticData) > 0:
            optimisticTeamName = aryOptimisticPessimisticData[0]["key"]
            optimisticTeamScore = aryOptimisticPessimisticData[0]["score"]
        if len(aryOptimisticPessimisticData) > 1:
            optimisticShGroupName = aryOptimisticPessimisticData[1]["key"]
            optimisticShGroupScore = aryOptimisticPessimisticData[1]["score"]
        if len(aryOptimisticPessimisticData) > 2:
            optimisticOrgName = aryOptimisticPessimisticData[2]["key"]
            optimisticOrgScore = aryOptimisticPessimisticData[2]["score"]

        pessimisticTeamName = ""
        pessimisticTeamScore = ""
        pessimisticShGroupName = ""
        pessimisticShGroupScore = ""
        pessimisticOrgName = ""
        pessimisticOrgScore = ""
        if len(aryOptimisticPessimisticData) > 0:
            pessimisticTeamName = aryOptimisticPessimisticData[-1]["key"]
            pessimisticTeamScore = aryOptimisticPessimisticData[-1]["score"]
        if len(aryOptimisticPessimisticData) > 1:
            pessimisticShGroupName = aryOptimisticPessimisticData[-2]["key"]
            pessimisticShGroupScore = aryOptimisticPessimisticData[-2]["score"]
        if len(aryOptimisticPessimisticData) > 2:
            pessimisticOrgName = aryOptimisticPessimisticData[-3]["key"]
            pessimisticOrgScore = aryOptimisticPessimisticData[-3]["score"]

        leastSafeTeamName = ""
        leastSafeTeamScore = ""
        leastSafeShGroupName = ""
        leastSafeShGroupScore = ""
        leastSafeOrgName = ""
        leastSafeOrgScore = ""
        if len(aryLeastSafeData) > 0:
            leastSafeTeamName = aryLeastSafeData[-1]["key"]
            leastSafeTeamScore = aryLeastSafeData[-1]["score"]
        if len(aryLeastSafeData) > 1:
            leastSafeShGroupName = aryLeastSafeData[-2]["key"]
            leastSafeShGroupScore = aryLeastSafeData[-2]["score"]
        if len(aryLeastSafeData) > 2:
            leastSafeOrgName = aryLeastSafeData[-3]["key"]
            leastSafeOrgScore = aryLeastSafeData[-3]["score"]

        detailedData = {
            "positively": {
                "team": {
                    "name": positivelyTeamName,
                    "score": positivelyTeamScore
                },
                "shgroup": {
                    "name": positivelyShGroupName,
                    "score": positivelyShGroupScore
                },
                "org": {
                    "name": positivelyOrgName,
                    "score": positivelyOrgScore
                }
            },
            "negatively": {
                "team": {
                    "name": negativelyTeamName,
                    "score": negativelyTeamScore
                },
                "shgroup": {
                    "name": negativelyShGroupName,
                    "score": negativelyShGroupScore
                },
                "org": {
                    "name": negativelyOrgName,
                    "score": negativelyOrgScore
                }
            },
            "optimistic": {
                "team": {
                    "name": optimisticTeamName,
                    "score": optimisticTeamScore
                },
                "shgroup": {
                    "name": optimisticShGroupName,
                    "score": optimisticShGroupScore
                },
                "org": {
                    "name": optimisticOrgName,
                    "score": optimisticOrgScore
                }
            },
            "pessimistic": {
                "team": {
                    "name": pessimisticTeamName,
                    "score": pessimisticTeamScore
                },
                "shgroup": {
                    "name": pessimisticShGroupName,
                    "score": pessimisticShGroupScore
                },
                "org": {
                    "name": pessimisticOrgName,
                    "score": pessimisticOrgScore
                }
            },
            "least safe": {
                "team": {
                    "name": leastSafeTeamName,
                    "score": leastSafeTeamScore
                },
                "shgroup": {
                    "name": leastSafeShGroupName,
                    "score": leastSafeShGroupScore
                },
                "org": {
                    "name": leastSafeOrgName,
                    "score": leastSafeOrgScore
                }
            }
        }

        return Response({
            "summary": summary, 
            "catchupProjectUsers": recommendedCatchupProjectUserSerializer.data, 
            "recommendedProjectUsers": recommendedProjectUserSerializer.data[:3], 
            "detailedData": detailedData,
            # "aryProjectUsers": aryProjectUsers,
            # "amresponsereportdata": amresponsereportdata
        }, status=status.HTTP_200_OK)

# new advisorinsights api
class NewAdvisorInsightsView(APIView):
    permission_classes = [permissions.IsAuthenticated,
                          permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        survey = self.request.query_params.get('survey', None)

        if survey is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

        amresponsereportqueryset = AMResponse.objects.filter(Q(survey__id=survey), Q(amQuestion__subdriver='Overall Sentiment') | Q(amQuestion__subdriver='Optimism') | Q(amQuestion__subdriver='Safety')).order_by('integerValue')
        amresponsereportserializer = AMResponseForDriverAnalysisSerializer(amresponsereportqueryset, many=True)
        amresponsereportdata = amresponsereportserializer.data

        aryTeams = []
        aryProjectUsers = []
        aryDepartments = []
        aryOrganizations = []
        aryShGroups = []

        aryTeamsData = {}
        aryShGroupsData = {}
        aryOrganizationsData = {}

        positivelyNegativelyQuestionId = AMQuestion.objects.get(survey__id=survey, subdriver="Overall Sentiment").id
        
        optimisticPessimisticQuestionId = AMQuestion.objects.get(survey__id=survey, subdriver="Optimism").id

        leastSafeQuestionId = AMQuestion.objects.get(survey__id=survey, subdriver="Safety").id
        leastSafeTeamName = ""
        leastSafeTeamTotalScore = 0
        leastSafeTeamCnt = 0
        leastSafeTeamScore = 0
        leastSafeShGroupName = ""
        leastSafeShGroupTotalScore = 0
        leastSafeShGroupCnt = 0
        leastSafeShGroupScore = 0
        leastSafeOrgName = ""
        leastSafeOrgTotalScore = 0
        leastSafeOrgCnt = 0
        leastSafeOrgScore = 0

        for i in range(len(amresponsereportdata)):
            if amresponsereportdata[i]['projectUser']["team"]["name"] not in aryTeams:
                aryTeams.append(amresponsereportdata[i]['projectUser']["team"]["name"])
            if amresponsereportdata[i]['projectUser']['shGroup'] is not None:
                if amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName'] not in aryShGroups:
                    aryShGroups.append(amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName'])
            if amresponsereportdata[i]['projectUser']["id"] not in aryProjectUsers:
                aryProjectUsers.append(amresponsereportdata[i]['projectUser']['id'])
            if amresponsereportdata[i]['projectUser']["user"]["userteam"] is not None:
                if amresponsereportdata[i]['projectUser']['user']['userteam']['name'] not in aryDepartments:
                    aryDepartments.append(amresponsereportdata[i]['projectUser']['user']['userteam']['name'])
            if amresponsereportdata[i]['projectUser']['projectOrganization'] is not None:
                if amresponsereportdata[i]['projectUser']['projectOrganization'] not in aryOrganizations:
                    aryOrganizations.append(amresponsereportdata[i]['projectUser']['projectOrganization'])
            
            aryTeamsData[amresponsereportdata[i]['projectUser']['team']['name']] = {"totalScore": 0, "cnt": 0, "score": 0, "compTotalScore": 0, "compCnt": 0, "compScore": 0}
            if amresponsereportdata[i]['projectUser']['shGroup'] is not None:
                aryShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']] = {"totalScore": 0, "cnt": 0, "score": 0, "compTotalScore": 0, "compCnt": 0, "compScore": 0}
            if amresponsereportdata[i]['projectUser']['projectOrganization'] is not None:
                aryOrganizationsData[amresponsereportdata[i]['projectUser']['projectOrganization']] = {"totalScore": 0, "cnt": 0, "score": 0, "compTotalScore": 0, "compCnt": 0, "compScore": 0}
            
            if amresponsereportdata[i]['amQuestion'] == leastSafeQuestionId:
                leastSafeTeamName = amresponsereportdata[i]['projectUser']['team']['name']
                leastSafeTeamTotalScore += amresponsereportdata[i]['integerValue']
                leastSafeTeamCnt += 1
                leastSafeTeamScore = leastSafeTeamTotalScore / 10 / leastSafeTeamCnt

                if amresponsereportdata[i]['projectUser']['shGroup'] is not None:
                    leastSafeShGroupName = amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']
                    leastSafeShGroupTotalScore += amresponsereportdata[i]['integerValue']
                    leastSafeShGroupCnt += 1
                    leastSafeShGroupScore = leastSafeShGroupTotalScore / 10 / leastSafeShGroupCnt

                if amresponsereportdata[i]['projectUser']['projectOrganization'] is not None:
                    leastSafeOrgName = amresponsereportdata[i]['projectUser']['projectOrganization']
                    leastSafeOrgTotalScore += amresponsereportdata[i]['integerValue']
                    leastSafeOrgCnt += 1
                    leastSafeOrgScore = leastSafeOrgTotalScore / 10 / leastSafeOrgCnt

        aryFilteredProjectUsers = aryProjectUsers[:3]
        recommendedProjectUsersQuerySet = ProjectUser.objects.filter(survey=survey, pk__in=aryFilteredProjectUsers)
        recommendedProjectUsersSerializer = ProjectUserForAdvisorSerializer(recommendedProjectUsersQuerySet, many=True)

        # test data for catchup
        aryFilteredCatchupProjectUsers = aryProjectUsers
        recommendedCatchupProjectUsersQuerySet = ProjectUser.objects.filter(survey=survey, pk__in=aryFilteredCatchupProjectUsers)
        recommendedCatchupProjectUserSerializer = ProjectUserForAdvisorSerializer(recommendedCatchupProjectUsersQuerySet, many=True)

        # project = Survey.objects.get(pk=survey).project
        totalTeamMembersCnt = ProjectUser.objects.filter(survey=survey, shType__shTypeName="Team Member").count()
        totalStakeHoldersCnt = ProjectUser.objects.filter(survey=survey, shType__shTypeName="Stakeholder").count()
        responseRateFromInvitedTeamMembers = len(aryTeams) * 100 / totalTeamMembersCnt
        responseRateFromInvitedStakeholders = len(aryProjectUsers) * 100 / totalStakeHoldersCnt
        totalDepartments = len(aryDepartments)

        summary = {
            "responseRateFromInvitedTeamMembers": responseRateFromInvitedTeamMembers,
            "responseRateFromInvitedStakeholders": responseRateFromInvitedStakeholders,
            "totalDepartments": totalDepartments
        }

        

        detailedData = {
            "positively": {
                "team": {
                    "name": "team1",
                    "score": 1,
                },
                "shgroup": {
                    "name": "shgroup1",
                    "score": 2,
                },
                "org": {
                    "name": "org1",
                    "score": 3,
                }
            },
            "negatively": {
                "team": {
                    "name": "team2",
                    "score": 4,
                },
                "shgroup": {
                    "name": "shgroup2",
                    "score": 5,
                },
                "org": {
                    "name": "org2",
                    "score": 6,
                }
            },
            "optimistic": {
                "team": {
                    "name": "team3",
                    "score": 7,
                },
                "shgroup": {
                    "name": "shgroup3",
                    "score": 8,
                },
                "org": {
                    "name": "org3",
                    "score": 9,
                }
            },
            "pessimistic": {
                "team": {
                    "name": "team4",
                    "score": 10,
                },
                "shgroup": {
                    "name": "shgroup4",
                    "score": 11,
                },
                "org": {
                    "name": "org4",
                    "score": 12,
                }
            },
            "least safe": {
                "team": {
                    "name": "team5",
                    "score": 13,
                },
                "shgroup": {
                    "name": "shgroup5",
                    "score": 14,
                },
                "org": {
                    "name": "org5",
                    "score": 15,
                }
            }
        }

        return Response({"summary": [], "data": amresponsereportdata, "catchupProjectUsers": [], "recommendedProjectUsers": [], "detailedData": detailedData}, status=status.HTTP_200_OK)

# driveranalysis api
class DriverAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        survey = self.request.query_params.get('survey', None)
        # projectUser = self.request.query_params.get('projectUser', None)
        driver = self.request.query_params.get('driver', None)
        startDate = self.request.query_params.get('stdt', None)
        endDate = self.request.query_params.get('eddt', None)
        controlType = self.request.query_params.get('controltype', None)

        if survey is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        # if projectUser is None:
        #     return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        # if driver is None:
        #     return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if startDate is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if endDate is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if controlType is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        
        if driver is not None:
            # amresponsereportqueryset = AMResponse.objects.all().filter(controlType=controlType, survey__id=survey, subProjectUser__id=projectUser, amQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            amresponsereportqueryset = AMResponse.objects.all().filter(controlType=controlType, survey__id=survey, amQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            amresponsereportserializer = AMResponseForDriverAnalysisSerializer(
                amresponsereportqueryset, many=True)
            amresponsereportdata = amresponsereportserializer.data

            # aoresponsereportqueryset = AOResponse.objects.all().filter(controlType=controlType, survey__id=survey, subProjectUser__id=projectUser, aoQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            aoresponsereportqueryset = AOResponse.objects.all().filter(controlType=controlType, survey__id=survey, aoQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            aoresponsereportserializer = AOResponseForDriverAnalysisSerializer(aoresponsereportqueryset, many=True)
            aoresponsereportdata = aoresponsereportserializer.data
        else:
            # amresponsereportqueryset = AMResponse.objects.all().filter(controlType=controlType, survey__id=survey, subProjectUser__id=projectUser, amQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            amresponsereportqueryset = AMResponse.objects.all().filter(controlType=controlType, survey__id=survey, created_at__range=[startDate, endDate])
            amresponsereportserializer = AMResponseForDriverAnalysisSerializer(
                amresponsereportqueryset, many=True)
            amresponsereportdata = amresponsereportserializer.data

            # aoresponsereportqueryset = AOResponse.objects.all().filter(controlType=controlType, survey__id=survey, subProjectUser__id=projectUser, aoQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
            aoresponsereportqueryset = AOResponse.objects.all().filter(controlType=controlType, survey__id=survey, created_at__range=[startDate, endDate])
            aoresponsereportserializer = AOResponseForDriverAnalysisSerializer(
                aoresponsereportqueryset, many=True)
            aoresponsereportdata = aoresponsereportserializer.data
        

        # for i in range(len(amresponsereportdata)):

        #     # amquestionqueryset = AMQuestion.objects.filter(
        #     #     id=amresponsereportdata[i]['amQuestion'])
        #     # amserializer = AMQuestionSerializer(amquestionqueryset, many=True)
        #     amserializerdata = AMQuestion.objects.filter(
        #         id=amresponsereportdata[i]['amQuestion']).values()
        #     amresponsereportdata[i]['amQuestionData'] = amserializerdata

        # for j in range(len(aoresponsereportdata)):

        #     # aoquestionqueryset = AOQuestion.objects.filter(id=aoresponsereportdata[j]['aoQuestion'])
        #     # aoserializer = AOQuestionSerializer(aoquestionqueryset, many=True)
        #     aoserializerdata = AOQuestion.objects.filter(id=aoresponsereportdata[j]['aoQuestion']).values()
        #     aoresponsereportdata[j]['aoQuestionData'] = aoserializerdata

        res = amresponsereportdata + aoresponsereportdata

        return Response(res, status=status.HTTP_200_OK)

# danalysiscnt api
class DriverAnalysisCntView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        survey = self.request.query_params.get('survey', None)
        startDate = self.request.query_params.get('stdt', None)
        endDate = self.request.query_params.get('eddt', None)
        controlType = self.request.query_params.get('controltype', None)

        if survey is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if startDate is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if endDate is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if controlType is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

        # engagement
        amEngagementCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Engagement", created_at__range=[startDate, endDate]).count()
        aoEngagementCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Engagement", created_at__range=[startDate, endDate]).count()
        
        # culture
        amCultureCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Culture", created_at__range=[startDate, endDate]).count()
        aoCultureCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Culture", created_at__range=[startDate, endDate]).count()

        # sentiment
        amSentimentCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Sentiment", created_at__range=[startDate, endDate]).count()
        aoSentimentCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Sentiment", created_at__range=[startDate, endDate]).count()

        # interest
        amInterestCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Interest", created_at__range=[startDate, endDate]).count()
        aoInterestCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Interest", created_at__range=[startDate, endDate]).count()

        # confidence
        amConfidenceCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Confidence", created_at__range=[startDate, endDate]).count()
        aoConfidenceCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Confidence", created_at__range=[startDate, endDate]).count()

        # relationships
        amRelationshipsCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Relationships", created_at__range=[startDate, endDate]).count()
        aoRelationshipsCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Relationships", created_at__range=[startDate, endDate]).count()
        
        # improvement
        amImprovementCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Improvement", created_at__range=[startDate, endDate]).count()
        aoImprovementCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Improvement", created_at__range=[startDate, endDate]).count()

        # influence
        amInfluenceCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Influence", created_at__range=[startDate, endDate]).count()
        aoInfluenceCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Influence", created_at__range=[startDate, endDate]).count()

        # about others
        # amAboutOthersCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
        #                                             amQuestion__driver__driverName="About Others", created_at__range=[startDate, endDate]).count()
        # aoAboutOthersCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
        #                                             aoQuestion__driver__driverName="About Others", created_at__range=[startDate, endDate]).count()

        retValue = {
            "Engagement": amEngagementCnt + aoEngagementCnt,
            "Culture": amCultureCnt + aoCultureCnt,
            "Sentiment": amSentimentCnt + aoSentimentCnt,
            "Interest": amInterestCnt + aoInterestCnt,
            "Confidence": amConfidenceCnt + aoConfidenceCnt,
            "Relationships": amRelationshipsCnt + aoRelationshipsCnt,
            "Improvement": amImprovementCnt + aoImprovementCnt,
            "Influence": amInfluenceCnt + aoInfluenceCnt,
            # "About Others": amAboutOthersCnt + aoAboutOthersCnt
        }

        return Response(retValue, status=status.HTTP_200_OK)

# totalshcnt api
class TotalStakeHolderView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        survey = self.request.query_params.get('survey', None)

        if survey is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

        projectusercnt = len(ProjectUser.objects.filter(survey=survey, sendInvite=True))
        projectuserqueryset = ProjectUser.objects.all().filter(survey__id=survey, sendInvite=True)
        projectuserserializer = UserBySurveySerializer(projectuserqueryset, many=True)
        projectuserdata = projectuserserializer.data

        ret = ''
        ret = {
            "stakeHolderCount": projectusercnt,
            "shgroup": {},
            "team": {},
            "org": {}
        }

        aryTeams = []
        arySHGroups = []
        aryOrgs = []
        
        for i in range(len(projectuserdata)):
            # if projectuserdata[i]['team'] is not None:
            #     if projectuserdata[i]['team']['name'] not in aryTeams:
            #         aryTeams.append(projectuserdata[i]['team']['name'])
            #         if (projectuserdata[i]['shType'] is not None):
            #             if (projectuserdata[i]['shType']['shTypeName'] == "Team Member"):
            #                 ret['team'][projectuserdata[i]['team']['name']] = 1
            #             else:
            #                 ret['team'][projectuserdata[i]['team']['name']] = 0
            #         else:
            #             ret['team'][projectuserdata[i]['team']['name']] = 0
            #     else:
            #         if (projectuserdata[i]['shType'] is not None):
            #             if (projectuserdata[i]['shType']['shTypeName'] == "Team Member"):
            #                 ret['team'][projectuserdata[i]['team']['name']] += 1
            #         else:
            #             pass

            # if projectuserdata[i]['shGroup'] is not None:
            #     if projectuserdata[i]['shGroup']['SHGroupName'] not in arySHGroups:
            #         arySHGroups.append(projectuserdata[i]['shGroup']['SHGroupName'])
            #         if (projectuserdata[i]['shType'] is not None):
            #             if (projectuserdata[i]['shType']['shTypeName'] == "Stakeholder"):
            #                 ret['shgroup'][projectuserdata[i]['shGroup']['SHGroupName']] = 1
            #             else:
            #                 ret['shgroup'][projectuserdata[i]['shGroup']['SHGroupName']] = 0
            #         else:
            #             ret['shgroup'][projectuserdata[i]['shGroup']['SHGroupName']] = 0
            #     else:
            #         if (projectuserdata[i]['shType'] is not None):
            #             if (projectuserdata[i]['shType']['shTypeName'] == "Stakeholder"):
            #                 ret['shgroup'][projectuserdata[i]['shGroup']['SHGroupName']] += 1
            #         else:
            #             pass
            if projectuserdata[i]['team'] is not None:
                if projectuserdata[i]['team']['name'] not in aryTeams:
                    aryTeams.append(projectuserdata[i]['team']['name'])
                    ret['team'][projectuserdata[i]['team']['name']] = 1
                else:
                    ret['team'][projectuserdata[i]['team']['name']] += 1

            if projectuserdata[i]['shGroup'] is not None:
                if projectuserdata[i]['shGroup']['SHGroupName'] not in arySHGroups:
                    arySHGroups.append(
                        projectuserdata[i]['shGroup']['SHGroupName'])
                    ret['shgroup'][projectuserdata[i]
                                   ['shGroup']['SHGroupName']] = 1
                else:
                    ret['shgroup'][projectuserdata[i]
                                   ['shGroup']['SHGroupName']] += 1

            # if projectuserdata[i]['user']['organization'] is not None:
            #     if projectuserdata[i]['user']['organization']['name'] not in aryOrgs:
            #         aryOrgs.append(
            #             projectuserdata[i]['user']['organization']['name'])
            #         ret['org'][projectuserdata[i]['user']['organization']['name']] = 1
            #     else:
            #         ret['org'][projectuserdata[i]['user']['organization']['name']] += 1
            if (projectuserdata[i]['projectOrganization'] is not None) & (projectuserdata[i]['projectOrganization'] != ""):
                if projectuserdata[i]['projectOrganization'] not in aryOrgs:
                    aryOrgs.append(
                        projectuserdata[i]['projectOrganization'])
                    ret['org'][projectuserdata[i]['projectOrganization']] = 1
                else:
                    ret['org'][projectuserdata[i]['projectOrganization']] += 1
                    
        return Response(ret, status=status.HTTP_200_OK)

# checkuserpasswordstatus api
class CheckUserPasswordStatusView(APIView):
    # permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    permission_classes = [permissions.AllowAny]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        email = self.request.query_params.get('email', None)

        if email is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            ret = user.has_usable_password()
            if ret == True:
                return Response({"text": "password exist", "code": 200, "passwordstatus": ret}, status=status.HTTP_200_OK)
            else:
                return Response({"text": "password not exist", "code": 231, "passwordstatus": ret}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"text": "user not exist", "code": 230}, status=status.HTTP_200_OK)

# checkdashboardstatus api
class CheckDashboardStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, format=None):
        survey = self.request.query_params.get('survey', None)
        projectUser = self.request.query_params.get('projectuser', None)
        
        if survey is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if projectUser is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)

        # 3 people has to response to this user
        thresholdCnt = Survey.objects.get(id=survey).anonymityThreshold

        # prefix check
        prefCode = preApiCheck(survey, projectUser) 

        shgroupqueryset = SHGroup.objects.filter(survey__id=survey)
        shgroupserializer = SHGroupSerializer(shgroupqueryset, many=True)

        if prefCode == 228:
            return Response({"text": "no data yet", "code": 228, "thresholdCnt": thresholdCnt}, status=status.HTTP_200_OK)
        elif prefCode == 227:
            return Response({"text": "no data yet", "code": 227, "thresholdCnt": thresholdCnt}, status=status.HTTP_200_OK)
        elif prefCode == 201:
            return Response({"text": "superuser", "code": 201, "thresholdCnt": thresholdCnt}, status=status.HTTP_200_OK)
        elif prefCode == 404:
            return Response({"text": "admin error", "code": 404, "thresholdCnt": thresholdCnt}, status=status.HTTP_200_OK)

        return Response({"text": "pass", "code": 200, "data": shgroupserializer.data, "thresholdCnt": thresholdCnt, "precode": prefCode}, status=status.HTTP_200_OK)

# adminbulkinvitationsend api
class AdminBulkInvitationSendView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def post(self, request):
        projectUserRequestData = request.data['ids']
        projectUserIds = json.loads(projectUserRequestData)

        for projectUserId in projectUserIds:
            try:
                obj = ProjectUser.objects.get(id=projectUserId)
                obj.sendInvite = True
                obj.old_sendEmail = False
                obj.sendEmail = True
                obj.save()
            except ProjectUser.DoesNotExist:
                pass

        return Response("success", status=status.HTTP_201_CREATED)

class AdminDelMoreInfoPageView(APIView):
    def get_object(self, pk):
        try:
            return NikelMobilePage.objects.get(id=pk)
        except NikelMobilePage.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def delete(self, request, pk, format=None):
        moreInfoPage = self.get_object(pk)
        moreInfoPage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AdminDelAMQuestionView(APIView):
    def get_object(self, pk):
        try:
            return AMQuestion.objects.get(id=pk)
        except AMQuestion.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def delete(self, request, pk, format=None):
        question = self.get_object(pk)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AdminDelAOQuestionView(APIView):
    def get_object(self, pk):
        try:
            return AOQuestion.objects.get(id=pk)
        except AOQuestion.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def delete(self, request, pk, format=None):
        question = self.get_object(pk)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# adminbulkarchive api
class AdminBulkArchiveView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get_extra_actions(cls):
        return []

    def post(self, request):
        projectUserRequestData = request.data['ids']
        projectUserIds = json.loads(projectUserRequestData)

        for projectUserId in projectUserIds:
            try:
                obj = ProjectUser.objects.get(id=projectUserId)
                obj.isArchived = True
                obj.save()
            except ProjectUser.DoesNotExist:
                pass
        
        return Response("success", status=status.HTTP_201_CREATED)
