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

from snippets.serializers import AMResponseForMatrixSerializer, AMResponseForDriverAnalysisSerializer, AOResponseForDriverAnalysisSerializer, AOResponseTopPositiveNegativeSerializer, KeyThemeUpDownVoteSerializer, AMResponseAcknowledgementSerializer, AOResponseForMatrixSerializer, AOResponseAcknowledgementSerializer, AMResponseForReportSerializer, AOResponseForReportSerializer, ProjectUserForReportSerializer, AMQuestionSubDriverSerializer, AOQuestionSubDriverSerializer, DriverSubDriverSerializer, ProjectSerializer, ToolTipGuideSerializer, SurveySerializer, NikelMobilePageSerializer, ConfigPageSerializer, UserAvatarSerializer, SHMappingSerializer, ProjectVideoUploadSerializer, AMQuestionSerializer, AOQuestionSerializer, StakeHolderSerializer, SHCategorySerializer, MyMapLayoutStoreSerializer, ProjectMapLayoutStoreSerializer, UserBySurveySerializer, SurveyByUserSerializer, SkipOptionSerializer, DriverSerializer, AOQuestionSerializer, OrganizationSerializer, OptionSerializer, ProjectUserSerializer, SHGroupSerializer, UserSerializer, PageSettingSerializer, PageSerializer, AMResponseSerializer, AMResponseTopicSerializer, AOResponseSerializer, AOResponseTopicSerializer, AOPageSerializer, TeamSerializer

from rest_framework import generics, permissions, renderers, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from page_setting.models import PageSetting
from cms.models import Page
from aboutme.models import AMResponseAcknowledgement, AMQuestion, AMResponse, AMResponseTopic, AMQuestionSHGroup
from aboutothers.models import AOResponseAcknowledgement, AOResponse, AOResponseTopic, AOPage
from team.models import Team
from shgroup.models import KeyThemeUpDownVote, SHGroup, ProjectUser, MyMapLayout, ProjectMapLayout, SHCategory, SHMapping
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
                answeredCnt = answeredCnt + 1
            # else:
            #     return 228

        if totalCnt > 0:
            currentPercent = answeredCnt * 100 / totalCnt
            if currentPercent < responsePercent:
                return 228
                
    except ProjectUser.DoesNotExist:
        return 404

    # 3 people has to response to this user
    thresholdCnt = Survey.objects.get(id=survey).anonymityThreshold

    # prefAryProjectUsers = []
    # prefTestResultQueryset = AMResponse.objects.all().filter(survey__id=survey)
    # prefTestResultSerializer = AMResponseForDriverAnalysisSerializer(prefTestResultQueryset, many=True)
    # prefTestResultData = prefTestResultSerializer.data

    cnt = AMResponse.objects.filter(survey__id=survey).values_list('projectUser', flat=True).distinct().count()
    # for i in range(len(prefTestResultData)): 
    #     if prefTestResultData[i]['projectUser']["id"] not in prefAryProjectUsers:
    #             prefAryProjectUsers.append(
    #                 prefTestResultData[i]['projectUser']["id"])
    
    # if (len(prefAryProjectUsers) < thresholdCnt):
    if cnt < thresholdCnt:
        return 227

    return 200

# acknowledgement api
class AOResponseAcknowledgementViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = AOResponseAcknowledgement.objects.all()
    serializer_class = AOResponseAcknowledgementSerializer

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

                            if saveStatus == False:
                                obj1 = AMResponse(amQuestion_id=data[i]['amQuestion'], projectUser_id=data[i]['projectUser'], subProjectUser_id=data[i]['subProjectUser'], survey_id=data[i]['survey'], project_id=data[i]['project'],
                                controlType=data[i]['controlType'], integerValue=data[i]['integerValue'], topicValue=data[i]['topicValue'], commentValue=data[i]['commentValue'], skipValue=data[i]['skipValue'], topicTags=data[i]['topicTags'], commentTags=data[i]['commentTags'], latestResponse=True)
                                obj1.save()

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
    serializer_class = AMResponseForMatrixSerializer

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
                    survey_id=survey, subProjectUser_id=subProjectUser, created_at__range=[startDate, endDate])
            elif (survey is not None) & (subProjectUser is not None):
                queryset = queryset.filter(
                    survey_id=survey, subProjectUser_id=subProjectUser)
            elif (survey is not None) & (startDate is not None) & (endDate is not None):
                queryset = queryset.filter(survey_id=survey, created_at__range=[startDate, endDate])
            elif (survey is not None):
                queryset = queryset.filter(survey_id=survey)

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

            for i in range(len(response.data)):
                amquestion_queryset = AMQuestion.objects.filter(
                    id=response.data[i]['amQuestion'])
                am_serializer = AMQuestionSerializer(
                    amquestion_queryset, many=True)
                response.data[i]['amQuestionData'] = am_serializer.data

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
                    survey__id=survey, created_at__range=[startDate, endDate], amQuestion__subdriver="Overall Sentiment")
            elif (survey is not None):
                queryset = queryset.filter(survey__id=survey, amQuestion__subdriver="Overall Sentiment")

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

# useravatar api
class UserAvatarViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = UserAvatar.objects.all()
    serializer_class = UserAvatarSerializer

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
        user = self.request.query_params.get('user', None)

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
        organization = organization.filter(user__id=user)

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
                wordlist.append(amresponsetopic_data[j]['topicName'])

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
                piwordlist.append(amresponsetopic_data[j]['topicName'])

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
                peiwordlist.append(amresponsetopic_data[j]['topicName'])

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
                ipwordlist.append(amresponsetopic_data[j]['topicName'])

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
                istwordlist.append(amresponsetopic_data[j]['topicName'])

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
                ispwordlist.append(amresponsetopic_data[j]['topicName'])

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
                icwordlist.append(amresponsetopic_data[j]['topicName'])

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
                    wordlist.append(amresponsetopic_data[j]['topicName'])

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
                tmpQuerySet = AMResponseAcknowledgement.objects.all().filter(
                    amResponse__id=ret[i]['id'])
                amResponseAcknowledgementSerializer = AMResponseAcknowledgementSerializer(
                    tmpQuerySet, many=True)
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
                myAmResponseAcknowledgementSerializer = AMResponseAcknowledgementSerializer(
                    myQuerySet, many=True)
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
                    wordlist.append(amresponsetopic_data[j]['topicName'])

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
                    wordlist.append(amresponsetopic_data[j]['topicName'])

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
                    wordlist.append(amresponsetopic_data[j]['topicName'])

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
                    wordlist.append(amresponsetopic_data[j]['topicName'])

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
                    wordlist.append(amresponsetopic_data[j]['topicName'])

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
                    wordlist.append(amresponsetopic_data[j]['topicName'])

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
                tempQueryset = KeyThemeUpDownVote.objects.filter(
                    keyTheme=aux[j][1], survey__id=survey, tab=9, projectUser=projectUser)
                myStatus = KeyThemeUpDownVoteSerializer(
                    tempQueryset, many=True)

                ret.append({"key": aux[j][1], "freq": aux[j][0],
                            "upvoteCount": upvoteCnt, "downvoteCount": downvoteCnt, "myStatus": myStatus.data})

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

        # Summary: 
        # % Response rate from invited Team members
        # % Response rate from invited stakeholders
        # Department counts in total

        # Recommended stakeholders: It will be the stakeholders who have the most negative responses for certain questions

        # top positive shteam name and score
        # top positive shgroup name and score

        # top negative shteam name and score
        # top negative shgroup name and score

        # optimistic would be the groups with high aws comprehend scores (like top positive)
        
        # pessimistic would be the groups with lowest aws comprehend scores (like top negative)

        # "least share to share their opinions" groups with the lowest score for this question

        # Respondant: counts of the SHCategory who have got at least 1 AM or AO response
        # myPeersShCategoryId = SHCategory.objects.get(survey=survey, SHCategoryName="My Peers").id
        # whoINeedShCategoryId = SHCategory.objects.get(survey=survey, SHCategoryName="Who I Need").id
        # myLeadersShCategoryId = SHCategory.objects.get(survey=survey, SHCategoryName="My Leaders").id
        # myDirectReportsShCategoryId = SHCategory.objects.get(survey=survey, SHCategoryName="My Direct Reports").id
        # whoNeedsMeShCategoryId = SHCategory.objects.get(survey=survey, SHCategoryName="Who Needs Me").id

        # myPeersCnt = SHMapping.objects.filter(
        #     subProjectUser=projectUser, shCategory=myPeersShCategoryId).count()
        # whoINeedCnt = SHMapping.objects.filter(
        #     subProjectUser=projectUser, shCategory=whoINeedShCategoryId).count()
        # myLeadersCnt = SHMapping.objects.filter(
        #     subProjectUser=projectUser, shCategory=myLeadersShCategoryId).count()
        # myDirectReportsCnt = SHMapping.objects.filter(
        #     subProjectUser=projectUser, shCategory=myDirectReportsShCategoryId).count()
        # whoNeedsMeCnt = SHMapping.objects.filter(
        #     subProjectUser=projectUser, shCategory=whoNeedsMeShCategoryId).count()

        # respondents = {
        #     "myPeersCnt": myPeersCnt,
        #     "whoINeedCnt": whoINeedCnt,
        #     "myLeadersCnt": myLeadersCnt,
        #     "myDirectReportsCnt": myDirectReportsCnt,
        #     "whoNeedsMeCnt": whoNeedsMeCnt
        # }

        # amresponsereportqueryset = AMResponse.objects.all().filter(survey__id=survey, subProjectUser__id=projectUser).order_by('integerValue')
        # amresponsereportserializer = AMResponseForDriverAnalysisSerializer(amresponsereportqueryset, many=True)
        # amresponsereportdata = amresponsereportserializer.data

        # aoresponsereportqueryset = AOResponse.objects.all().filter(survey__id=survey, subProjectUser__id=projectUser).order_by('integerValue')
        # aoresponsereportserializer = AOResponseForDriverAnalysisSerializer(aoresponsereportqueryset, many=True)
        # aoresponsereportdata = aoresponsereportserializer.data

        amresponsereportqueryset = AMResponse.objects.all().filter(survey__id=survey).order_by('integerValue')
        amresponsereportserializer = AMResponseForDriverAnalysisSerializer(amresponsereportqueryset, many=True)
        amresponsereportdata = amresponsereportserializer.data

        # aoresponsereportqueryset = AOResponse.objects.all().filter(survey__id=survey).order_by('integerValue')
        # aoresponsereportserializer = AOResponseForDriverAnalysisSerializer(aoresponsereportqueryset, many=True)
        # aoresponsereportdata = aoresponsereportserializer.data

        aryTeams = []
        aryProjectUsers = []
        aryDepartments = []
        aryOrganizations = []
        aryShGroups = []

        aryTeamsData = {}
        aryShGroupsData = {}
        aryOrganizationsData = {}

        leastSafeQuestionId = AMQuestion.objects.get(
            survey__id=survey, questionText="Is it safe to speak up to share an unpopular opinion?").id
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
                aryTeams.append(
                    amresponsereportdata[i]['projectUser']["team"]["name"])
            if (amresponsereportdata[i]['projectUser']['shGroup'] is not None):
                if amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName'] not in aryShGroups:
                    aryShGroups.append(
                        amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName'])
            if amresponsereportdata[i]['projectUser']["id"] not in aryProjectUsers:
                aryProjectUsers.append(
                    amresponsereportdata[i]['projectUser']["id"])
            if (amresponsereportdata[i]['projectUser']['user']['userteam'] is not None):
                if (amresponsereportdata[i]['projectUser']['user']['userteam']['name'] not in aryDepartments):
                    aryDepartments.append(
                        amresponsereportdata[i]['projectUser']['user']['userteam']['name'])
            if (amresponsereportdata[i]['projectUser']['user']['organization'] is not None):
                if (amresponsereportdata[i]['projectUser']['user']['organization']['name'] not in aryOrganizations):
                    aryOrganizations.append(
                        amresponsereportdata[i]['projectUser']['user']['organization']['name'])

            aryTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]] = {"totalScore": 0, "cnt": 0, "score": 0, "compTotalScore": 0, "compCnt": 0, "compScore": 0}
            if (amresponsereportdata[i]['projectUser']['shGroup'] is not None):
                aryShGroupsData[amresponsereportdata[i]
                                ['projectUser']['shGroup']['SHGroupName']] = {"totalScore": 0, "cnt": 0, "score": 0, "compTotalScore": 0, "compCnt": 0, "compScore": 0}
            if (amresponsereportdata[i]['projectUser']['user']['organization'] is not None):
                aryOrganizationsData[amresponsereportdata[i]
                                     ['projectUser']['user']['organization']['name']] = {"totalScore": 0, "cnt": 0, "score": 0, "compTotalScore": 0, "compCnt": 0, "compScore": 0}
            
            if amresponsereportdata[i]['amQuestion'] == leastSafeQuestionId:
                leastSafeTeamName = amresponsereportdata[i]['projectUser']["team"]["name"]
                leastSafeTeamTotalScore += amresponsereportdata[i]["integerValue"]
                leastSafeTeamCnt += 1
                leastSafeTeamScore = leastSafeTeamTotalScore / 10 / leastSafeTeamCnt
                
                if (amresponsereportdata[i]['projectUser']['shGroup'] is not None):
                    leastSafeShGroupName = amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']
                    leastSafeShGroupTotalScore += amresponsereportdata[i]["integerValue"]
                    leastSafeShGroupCnt += 1
                    leastSafeShGroupScore = leastSafeShGroupTotalScore / 10 / leastSafeShGroupCnt
                
                if (amresponsereportdata[i]['projectUser']['user']['organization'] is not None):
                    leastSafeOrgName = amresponsereportdata[i]['projectUser']['user']['organization']['name']
                    leastSafeOrgTotalScore += amresponsereportdata[i]["integerValue"]
                    leastSafeOrgCnt += 1
                    leastSafeOrgScore = leastSafeOrgTotalScore / 10 / leastSafeOrgCnt
                
        # for j in range(len(aoresponsereportdata)):
        #     if aoresponsereportdata[j]['projectUser']["team"]["name"] not in aryTeams:
        #         aryTeams.append(
        #             aoresponsereportdata[j]['projectUser']['team']['name'])
        #     if (aoresponsereportdata[j]['projectUser']['shGroup'] is not None):
        #         if aoresponsereportdata[j]['projectUser']['shGroup']['SHGroupName'] not in aryShGroups:
        #             aryShGroups.append(
        #                 aoresponsereportdata[j]['projectUser']['shGroup']['SHGroupName'])
        #     if aoresponsereportdata[j]['projectUser']["id"] not in aryProjectUsers:
        #         aryProjectUsers.append(
        #             aoresponsereportdata[j]['projectUser']["id"])
        #     if (aoresponsereportdata[j]['projectUser']['user']['userteam'] is not None):
        #         if (aoresponsereportdata[j]['projectUser']['user']['userteam']['name'] not in aryDepartments):
        #             aryDepartments.append(
        #                 aoresponsereportdata[j]['projectUser']['user']['userteam']['name'])
        #     if (aoresponsereportdata[j]['projectUser']['user']['organization'] is not None):
        #         if (aoresponsereportdata[j]['projectUser']['user']['organization']['name'] not in aryOrganizations):
        #             aryOrganizations.append(
        #                 aoresponsereportdata[j]['projectUser']['user']['organization']['name'])
        
        #     aryTeamsData[aoresponsereportdata[j]['projectUser']["team"]["name"]] = {"totalScore": 0, "cnt": 0, "score": 0, "compTotalScore": 0, "compCnt": 0, "compScore": 0}
        #     if (aoresponsereportdata[j]['projectUser']['shGroup'] is not None):
        #         aryShGroupsData[aoresponsereportdata[j]
        #                         ['projectUser']['shGroup']['SHGroupName']] = {"totalScore": 0, "cnt": 0, "score": 0, "compTotalScore": 0, "compCnt": 0, "compScore": 0}
        #     if (aoresponsereportdata[j]['projectUser']['user']['organization'] is not None):
        #         aryOrganizationsData[aoresponsereportdata[j]
        #                              ['projectUser']['user']['organization']['name']] = {"totalScore": 0, "cnt": 0, "score": 0, "compTotalScore": 0, "compCnt": 0, "compScore": 0}


        for i in range(len(amresponsereportdata)):
            aryTeamsData[amresponsereportdata[i]
                         ['projectUser']["team"]["name"]]["totalScore"] += amresponsereportdata[i]["integerValue"]
            aryTeamsData[amresponsereportdata[i]
                         ['projectUser']["team"]["name"]]["cnt"] += 1
            aryTeamsData[amresponsereportdata[i]
                         ['projectUser']["team"]["name"]]["score"] = round(aryTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["totalScore"] / 10 / aryTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["cnt"], 2)

            if (amresponsereportdata[i]["controlType"] == "TEXT") | (amresponsereportdata[i]["controlType"] == "MULTI_TOPICS"):
                aryTeamsData[amresponsereportdata[i]
                         ['projectUser']["team"]["name"]]["compTotalScore"] += amresponsereportdata[i]["integerValue"]
                aryTeamsData[amresponsereportdata[i]
                            ['projectUser']["team"]["name"]]["compCnt"] += 1
                aryTeamsData[amresponsereportdata[i]
                             ['projectUser']["team"]["name"]]["compScore"] = round(aryTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["compTotalScore"] / 10 / aryTeamsData[amresponsereportdata[i]['projectUser']["team"]["name"]]["compCnt"], 2)

            if (amresponsereportdata[i]['projectUser']['shGroup'] is not None):
                aryShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['totalScore'] += amresponsereportdata[i]["integerValue"]
                aryShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['cnt'] += 1
                aryShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['score'] = round(aryShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['totalScore'] / 10 / aryShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['cnt'], 2)
        
                if (amresponsereportdata[i]["controlType"] == "TEXT") | (amresponsereportdata[i]["controlType"] == "MULTI_TOPICS"):
                    aryShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['compTotalScore'] += amresponsereportdata[i]["integerValue"]
                    aryShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['compCnt'] += 1
                    aryShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['compScore'] = round(aryShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['compTotalScore'] / 10 / aryShGroupsData[amresponsereportdata[i]['projectUser']['shGroup']['SHGroupName']]['compCnt'], 2)

            if (amresponsereportdata[i]['projectUser']['user']['organization'] is not None):
                aryOrganizationsData[amresponsereportdata[i]['projectUser']['user']['organization']['name']]['totalScore'] += amresponsereportdata[i]["integerValue"]
                aryOrganizationsData[amresponsereportdata[i]['projectUser']['user']['organization']['name']]['cnt'] += 1
                aryOrganizationsData[amresponsereportdata[i]['projectUser']['user']['organization']['name']]['score'] = round(aryOrganizationsData[amresponsereportdata[i]['projectUser']['user']['organization']['name']]['totalScore'] / 10 / aryOrganizationsData[amresponsereportdata[i]['projectUser']['user']['organization']['name']]['cnt'], 2)

                if (amresponsereportdata[i]["controlType"] == "TEXT") | (amresponsereportdata[i]["controlType"] == "MULTI_TOPICS"):
                    aryOrganizationsData[amresponsereportdata[i]['projectUser']['user']['organization']['name']]['compTotalScore'] += amresponsereportdata[i]["integerValue"]
                    aryOrganizationsData[amresponsereportdata[i]['projectUser']['user']['organization']['name']]['compCnt'] += 1
                    aryOrganizationsData[amresponsereportdata[i]['projectUser']['user']['organization']['name']]['compScore'] = round(aryOrganizationsData[amresponsereportdata[i]['projectUser']['user']['organization']['name']]['compTotalScore'] / 10 / aryOrganizationsData[amresponsereportdata[i]['projectUser']['user']['organization']['name']]['compCnt'], 2)

        # for j in range(len(aoresponsereportdata)):
        #     aryTeamsData[aoresponsereportdata[j]['projectUser']["team"]["name"]]["totalScore"] += aoresponsereportdata[j]["integerValue"]
        #     aryTeamsData[aoresponsereportdata[j]['projectUser']["team"]["name"]]["cnt"] += 1
        #     aryTeamsData[aoresponsereportdata[j]['projectUser']["team"]["name"]]["score"] = round(aryTeamsData[aoresponsereportdata[j]['projectUser']["team"]["name"]]["totalScore"] / 10 / aryTeamsData[aoresponsereportdata[j]['projectUser']["team"]["name"]]["cnt"], 2)
            
        #     if (aoresponsereportdata[j]["controlType"] == "TEXT") | (aoresponsereportdata[j]["controlType"] == "MULTI_TOPICS"):
        #         aryTeamsData[aoresponsereportdata[j]['projectUser']["team"]["name"]]["compTotalScore"] += aoresponsereportdata[j]["integerValue"]
        #         aryTeamsData[aoresponsereportdata[j]['projectUser']["team"]["name"]]["compCnt"] += 1
        #         aryTeamsData[aoresponsereportdata[j]['projectUser']["team"]["name"]]["compScore"] = round(aryTeamsData[aoresponsereportdata[j]['projectUser']["team"]["name"]]["compTotalScore"] / 10 / aryTeamsData[aoresponsereportdata[j]['projectUser']["team"]["name"]]["compCnt"], 2)

        #     if (aoresponsereportdata[j]['projectUser']['shGroup'] is not None):
        #         aryShGroupsData[aoresponsereportdata[j]['projectUser']['shGroup']['SHGroupName']]['totalScore'] += aoresponsereportdata[j]["integerValue"]
        #         aryShGroupsData[aoresponsereportdata[j]['projectUser']['shGroup']['SHGroupName']]['cnt'] += 1
        #         aryShGroupsData[aoresponsereportdata[j]['projectUser']['shGroup']['SHGroupName']]['score'] = round(aryShGroupsData[aoresponsereportdata[j]['projectUser']['shGroup']['SHGroupName']]['totalScore'] / 10 / aryShGroupsData[aoresponsereportdata[j]['projectUser']['shGroup']['SHGroupName']]['cnt'], 2)

        #         if (aoresponsereportdata[j]["controlType"] == "TEXT") | (aoresponsereportdata[j]["controlType"] == "MULTI_TOPICS"):
        #             aryShGroupsData[aoresponsereportdata[j]['projectUser']['shGroup']['SHGroupName']]['compTotalScore'] += aoresponsereportdata[j]["integerValue"]
        #             aryShGroupsData[aoresponsereportdata[j]['projectUser']['shGroup']['SHGroupName']]['compCnt'] += 1
        #             aryShGroupsData[aoresponsereportdata[j]['projectUser']['shGroup']['SHGroupName']]['compScore'] = round(aryShGroupsData[aoresponsereportdata[j]['projectUser']['shGroup']['SHGroupName']]['compTotalScore'] / 10 / aryShGroupsData[aoresponsereportdata[j]['projectUser']['shGroup']['SHGroupName']]['compCnt'], 2)

        #     if (aoresponsereportdata[j]['projectUser']['user']['organization'] is not None):
        #         aryOrganizationsData[aoresponsereportdata[j]['projectUser']['user']['organization']['name']]['totalScore'] += aoresponsereportdata[j]["integerValue"]
        #         aryOrganizationsData[aoresponsereportdata[j]['projectUser']['user']['organization']['name']]['cnt'] += 1
        #         aryOrganizationsData[aoresponsereportdata[j]['projectUser']['user']['organization']['name']]['score'] = round(aryOrganizationsData[aoresponsereportdata[j]['projectUser']['user']['organization']['name']]['totalScore'] / 10 / aryOrganizationsData[aoresponsereportdata[j]['projectUser']['user']['organization']['name']]['cnt'], 2)

        #         if (aoresponsereportdata[j]["controlType"] == "TEXT") | (aoresponsereportdata[j]["controlType"] == "MULTI_TOPICS"):
        #             aryOrganizationsData[aoresponsereportdata[j]['projectUser']['user']['organization']['name']]['compTotalScore'] += aoresponsereportdata[j]["integerValue"]
        #             aryOrganizationsData[aoresponsereportdata[j]['projectUser']['user']['organization']['name']]['compCnt'] += 1
        #             aryOrganizationsData[aoresponsereportdata[j]['projectUser']['user']['organization']['name']]['compScore'] = round(aryOrganizationsData[aoresponsereportdata[j]['projectUser']['user']['organization']['name']]['compTotalScore'] / 10 / aryOrganizationsData[aoresponsereportdata[j]['projectUser']['user']['organization']['name']]['compCnt'], 2)

        aryFilteredProjectUsers = aryProjectUsers[:3]
        recommendedProjectUsersQuerySet = ProjectUser.objects.filter(survey=survey, pk__in=aryFilteredProjectUsers)
        recommendedProjectUserSerializer = ProjectUserForReportSerializer(
            recommendedProjectUsersQuerySet, many=True)
        
        # test data for catchup
        aryFilteredCatchupProjectUsers = aryProjectUsers
        recommendedCatchupProjectUsersQuerySet = ProjectUser.objects.filter(survey=survey, pk__in=aryFilteredCatchupProjectUsers)
        recommendedCatchupProjectUserSerializer = ProjectUserForReportSerializer(recommendedCatchupProjectUsersQuerySet, many=True)

        project = Survey.objects.get(pk=survey).project
        totalTeamMembersCnt = Team.objects.filter(project=project).count()
        totalStakeHoldersCnt = ProjectUser.objects.filter(survey=survey).count()
        responseRateFromInvitedTeamMembers = len(aryTeams) * 100 / totalTeamMembersCnt
        responseRateFromInvitedStakeholders = len(aryProjectUsers) * 100 / totalStakeHoldersCnt
        totalDepartments = len(aryDepartments) 

        summary = {
            "responseRateFromInvitedTeamMembers": responseRateFromInvitedTeamMembers,
            "responseRateFromInvitedStakeholders": responseRateFromInvitedStakeholders,
            "totalDepartments": totalDepartments
        }

        positivelyTeamScore = max(aryTeamsData[key]['score'] for key in aryTeamsData) if len(aryTeamsData) > 0 else 0
        negativelyTeamScore = min(aryTeamsData[key]['score'] for key in aryTeamsData) if len(aryTeamsData) > 0 else 0
        optimisticTeamScore = max(aryTeamsData[key]['compScore'] for key in aryTeamsData) if len(aryTeamsData) > 0 else 0
        pessimisticTeamScore = min(
            aryTeamsData[key]['compScore'] for key in aryTeamsData) if len(aryTeamsData) > 0 else 0
        positivelyTeamName = ""
        negativelyTeamName = ""
        optimisticTeamName = ""
        pessimisticTeamName = ""
        for key in aryTeamsData:
            if aryTeamsData[key]['score'] == positivelyTeamScore:
                positivelyTeamName = key
            if aryTeamsData[key]['score'] == negativelyTeamScore:
                negativelyTeamName = key
            if aryTeamsData[key]['compScore'] == optimisticTeamScore:
                optimisticTeamName = key
            if aryTeamsData[key]['compScore'] == pessimisticTeamScore:
                pessimisticTeamName = key

        positivelyShGroupScore = max(aryShGroupsData[key]['score'] for key in aryShGroupsData) if len(aryShGroupsData) > 0 else 0
        negativelyShGroupScore = min(aryShGroupsData[key]['score'] for key in aryShGroupsData) if len(aryShGroupsData) > 0 else 0
        optimisticShGroupScore = max(aryShGroupsData[key]['compScore'] for key in aryShGroupsData) if len(aryShGroupsData) > 0 else 0
        pessimisticShGroupScore = min(aryShGroupsData[key]['compScore'] for key in aryShGroupsData) if len(aryShGroupsData) > 0 else 0
        positivelyShGroupName = ""
        negativelyShGroupName = ""
        optimisticShGroupName = ""
        pessimisticShGroupName = ""
        for key in aryShGroupsData:
            if aryShGroupsData[key]['score'] == positivelyShGroupScore:
                positivelyShGroupName = key
            if aryShGroupsData[key]['score'] == negativelyShGroupScore:
                negativelyShGroupName = key
            if aryShGroupsData[key]['compScore'] == optimisticShGroupScore:
                optimisticShGroupName = key
            if aryShGroupsData[key]['compScore'] == pessimisticShGroupScore:
                pessimisticShGroupName = key

        positivelyOrgScore = max(aryOrganizationsData[key]['score'] for key in aryOrganizationsData) if len(aryOrganizationsData) > 0 else 0
        negativelyOrgScore = min(aryOrganizationsData[key]['score'] for key in aryOrganizationsData) if len(aryOrganizationsData) > 0 else 0
        optimisticOrgScore = max(aryOrganizationsData[key]['score'] for key in aryOrganizationsData) if len(aryOrganizationsData) > 0 else 0
        pessimisticOrgScore = min(aryOrganizationsData[key]['score'] for key in aryOrganizationsData) if len(aryOrganizationsData) > 0 else 0
        positivelyOrgName = ""
        negativelyOrgName = ""
        optimisticOrgName = ""
        pessimisticOrgName = ""
        for key in aryOrganizationsData:
            if aryOrganizationsData[key]['score'] == positivelyOrgScore:
                positivelyOrgName = key
            if aryOrganizationsData[key]['score'] == negativelyOrgScore:
                negativelyOrgName = key
            if aryOrganizationsData[key]['score'] == optimisticOrgScore:
                optimisticOrgName = key
            if aryOrganizationsData[key]['score'] == pessimisticOrgScore:
                pessimisticOrgName = key

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

        return Response({"summary": summary, "catchupProjectUsers": recommendedCatchupProjectUserSerializer.data, "recommendedProjectUsers": recommendedProjectUserSerializer.data[:3], "detailedData": detailedData}, status=status.HTTP_200_OK)

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
        if driver is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if startDate is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if endDate is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
        if controlType is None:
            return Response("Invalid param", status=status.HTTP_400_BAD_REQUEST)
          
        # amresponsereportqueryset = AMResponse.objects.all().filter(controlType=controlType, survey__id=survey, subProjectUser__id=projectUser, amQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
        amresponsereportqueryset = AMResponse.objects.all().filter(controlType=controlType, survey__id=survey, amQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
        amresponsereportserializer = AMResponseForDriverAnalysisSerializer(
            amresponsereportqueryset, many=True)
        amresponsereportdata = amresponsereportserializer.data

        # aoresponsereportqueryset = AOResponse.objects.all().filter(controlType=controlType, survey__id=survey, subProjectUser__id=projectUser, aoQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
        aoresponsereportqueryset = AOResponse.objects.all().filter(controlType=controlType, survey__id=survey, aoQuestion__driver__driverName=driver, created_at__range=[startDate, endDate])
        aoresponsereportserializer = AOResponseForDriverAnalysisSerializer(aoresponsereportqueryset, many=True)
        aoresponsereportdata = aoresponsereportserializer.data

        for i in range(len(amresponsereportdata)):

            amquestionqueryset = AMQuestion.objects.filter(
                id=amresponsereportdata[i]['amQuestion'])
            amserializer = AMQuestionSerializer(amquestionqueryset, many=True)
            amresponsereportdata[i]['amQuestionData'] = amserializer.data

        for j in range(len(aoresponsereportdata)):

            aoquestionqueryset = AOQuestion.objects.filter(id=aoresponsereportdata[j]['aoQuestion'])
            aoserializer = AOQuestionSerializer(aoquestionqueryset, many=True)
            aoresponsereportdata[j]['aoQuestionData'] = aoserializer.data

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

        amEngagementCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Engagement", created_at__range=[startDate, endDate]).count()
        aoEngagementCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Engagement", created_at__range=[startDate, endDate]).count()
        
        amCultureCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Culture", created_at__range=[startDate, endDate]).count()
        aoCultureCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Culture", created_at__range=[startDate, endDate]).count()

        amSentimentCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Sentiment", created_at__range=[startDate, endDate]).count()
        aoSentimentCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Sentiment", created_at__range=[startDate, endDate]).count()

        amInterestCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Interest", created_at__range=[startDate, endDate]).count()
        aoInterestCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Interest", created_at__range=[startDate, endDate]).count()

        amConfidenceCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Confidence", created_at__range=[startDate, endDate]).count()
        aoConfidenceCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Confidence", created_at__range=[startDate, endDate]).count()

        amRelationshipsCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Relationships", created_at__range=[startDate, endDate]).count()
        aoRelationshipsCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Relationships", created_at__range=[startDate, endDate]).count()
        
        amImprovementCnt = AMResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    amQuestion__driver__driverName="Improvement", created_at__range=[startDate, endDate]).count()
        aoImprovementCnt = AOResponse.objects.filter(controlType=controlType, survey__id=survey, 
                                                    aoQuestion__driver__driverName="Improvement", created_at__range=[startDate, endDate]).count()

        retValue = {
            "Engagement": amEngagementCnt + aoEngagementCnt,
            "Culture": amCultureCnt + aoCultureCnt,
            "Sentiment": amSentimentCnt + aoSentimentCnt,
            "Interest": amInterestCnt + aoInterestCnt,
            "Confidence": amConfidenceCnt + aoConfidenceCnt,
            "Relationships": amRelationshipsCnt + aoRelationshipsCnt,
            "Improvement": amImprovementCnt + aoImprovementCnt
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
        projectuserqueryset = ProjectUser.objects.all().filter(
            survey__id=survey, sendInvite=True)
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
            return Response({"text": "no data yet", "code": 228, "thresholdCnt": thresholdCnt}, status=228)
        elif prefCode == 227:
            return Response({"text": "no data yet", "code": 227, "thresholdCnt": thresholdCnt}, status=227)
        elif prefCode == 201:
            return Response({"text": "superuser", "code": 201, "thresholdCnt": thresholdCnt}, status=status.HTTP_200_OK)

        return Response({"text": "pass", "code": 200, "data": shgroupserializer.data, "thresholdCnt": thresholdCnt, "precode": prefCode}, status=status.HTTP_200_OK)

