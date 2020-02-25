import os
from pathlib import Path
from email.mime.image import MIMEImage

from snippets.models import Snippet
from snippets.serializers import StakeHolderSerializer, SHCategorySerializer, MyMapLayoutStoreSerializer, ProjectMapLayoutStoreSerializer, UserByProjectSerializer, ProjectByUserSerializer, SkipOptionSerializer, DriverSerializer, AOQuestionSerializer, OrganizationSerializer, OptionSerializer, ProjectUserSerializer, SHGroupSerializer, SnippetSerializer, UserSerializer, PageSettingSerializer, PageSerializer, AMResponseSerializer, AMResponseTopicSerializer, AOResponseSerializer, AOResponseTopicSerializer, AOPageSerializer, TeamSerializer
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
from shgroup.models import SHGroup, ProjectUser, MyMapLayout, ProjectMapLayout, SHCategory
from option.models import Option, SkipOption
from rest_framework import status
from organization.models import Organization
from aboutothers.models import AOQuestion
from survey.models import Driver, Project
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
 

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PageSettingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = PageSetting.objects.all()
    serializer_class = PageSettingSerializer

# working now
class PageViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = Page.objects.all()
    serializer_class = PageSerializer

    def list(self, request, *kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        temp = serializer.data
        drivers = Driver.objects.all().values()
        list_drivers = [entry for entry in drivers]
        #print(list_drivers)

        for i in range(len(temp)):
            #print("item")
            #print(temp[i])

            if temp[i]['pages'] is not None:
                temp[i]['pages'] = {}
                temp[i]['pages']['driver'] = list_drivers

                for j in range(len(list_drivers)):
                    #temp[i]['pages']['driver'][j]['amquestion'] = []
                    temp[i]['pages']['driver'][j]['aoquestion'] = []

                    amquestion = AMQuestion.objects.filter(driver_id=list_drivers[j]['id']).values()
                    list_amquestion = [entry1 for entry1 in amquestion]
                    temp[i]['pages']['driver'][j]['amquestion'] = list_amquestion

                    aoquestion = AOQuestion.objects.filter(driver_id=list_drivers[j]['id']).values()
                    list_aoquestion = [entry2 for entry2 in aoquestion]
                    temp[i]['pages']['driver'][j]['aoquestion'] = list_aoquestion
            # for j in range(len(list_drivers)):
            #     print(list_drivers[j]['id'])
            #     temp[i]['pages']['ampage'][]['driver_id'] = list_drivers[j]['id']
                # temp[i]['pages']['ampage'][j]['driverName'] = list_drivers[j].driverName

        return Response(temp)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     data = request.accepted_renderer.render({'test': queryset, 'request': request})
    #     return Response(data, content_type=f'application/json')

    # def create(self, request, *args, **kwargs):
    #     data = request.data.get("items") if 'items' in request.data else request.data
    #     many = isinstance(data, list)
    #     #print(data, many)
    #     serializer = self.get_serializer(data=data, many=many)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
                    obj = AMResponse.objects.get(survey_id=item['survey'], project_id=item['project'], user_id=item['user'], amQuestion_id=item['amQuestion']) 
                    
                    obj.integerValue = defaults['integerValue']
                    obj.topicValue = defaults['topicValue']
                    obj.commentValue = defaults['commentValue']
                    obj.skipValue = defaults['skipValue']
                    obj.topicTags = defaults['topicTags']
                    obj.commentTags = defaults['commentTags']

                    obj.save()

                except AMResponse.DoesNotExist:
                    obj = AMResponse(amQuestion_id=defaults['amQuestion'], 
                                user_id=defaults['user'], subjectUser_id=defaults['subjectUser'], 
                                survey_id=defaults['survey'], project_id=defaults['project'], 
                                controlType=defaults['controlType'], integerValue=defaults['integerValue'],
                                topicValue=defaults['topicValue'], commentValue=defaults['commentValue'],
                                skipValue=defaults['skipValue'], topicTags=defaults['topicTags'],
                                commentTags=defaults['commentTags'])

                    obj.save()
                    
        elif many == False:
            defaults = data
            try:
                obj = AMResponse.objects.get(survey_id=defaults['survey'], project_id=defaults['project'], user_id=defaults['user'], amQuestion_id=defaults['amQuestion'])
                
                obj.integerValue = defaults['integerValue']
                obj.topicValue = defaults['topicValue']
                obj.commentValue = defaults['commentValue']
                obj.skipValue = defaults['skipValue']
                obj.topicTags = defaults['topicTags']
                obj.commentTags = defaults['commentTags']

                obj.save()
            except AMResponse.DoesNotExist:

                obj = AMResponse(amQuestion_id=data['amQuestion'], 
                                user_id=data['user'], subjectUser_id=data['subjectUser'], 
                                survey_id=data['survey'], project_id=data['project'], 
                                controlType=data['controlType'], integerValue=data['integerValue'],
                                topicValue=data['topicValue'], commentValue=data['commentValue'],
                                skipValue=data['skipValue'], topicTags=data['topicTags'],
                                commentTags=data['commentTags'])

                obj.save()

        
        result = AMResponse.objects.all().values('user', 'subjectUser', 'survey', 'project', 'amQuestion', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags')
        
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
        #print(data, many)
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
        #print(data, many)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
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
        #print(data, many)
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
        #print(data, many)
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
        #print(data, many)
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
        project = self.request.query_params.get('project', None)
        if project is not None:
            queryset = queryset.filter(project__id=project)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        #print(data, many)
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
        shCategory = self.request.query_params.get('shCategory', None)
        if shCategory is not None:
            try:
                if int(shCategory) > 0:
                    queryset = queryset.filter(shCategory__id=shCategory)
                elif int(shCategory) == 0:
                    queryset = queryset.filter(shCategory__isnull=True)
            except ValueError:
                queryset = ProjectUser.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        #print(data, many)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        # print(serializer.data['project'])
        
        # project = Project.objects.get(id=serializer.data['project'])
        # user = User.objects.get(id=serializer.data['user'])
        # token = Token.objects.get(user_id=serializer.data['user'])

        # image_path_logo = os.path.join(settings.STATIC_ROOT, 'email', 'img', 'logo-2.png')
        # image_name_logo = Path(image_path_logo).name
        # image_path_container = os.path.join(settings.STATIC_ROOT, 'email', 'img', 'container.png')
        # image_name_container = Path(image_path_container).name
        # image_path_connect = os.path.join(settings.STATIC_ROOT, 'email', 'img', 'connect.png')
        # image_name_connect = Path(image_path_connect).name

        # subject = 'Welcome to Pulse'
        # message = get_template('email.html').render(
        #     {
        #         'project_name': project,
        #         'image_name_logo': image_name_logo,
        #         'image_name_container': image_name_container,
        #         'image_name_connect': image_name_connect,
        #         'token': token.key,
        #         'email': user.email,
        #         'first_name': user.first_name,
        #         'last_name': user.last_name,
        #         'site_url': settings.SITE_URL
        #     }
        # )
        # email_from = settings.DEFAULT_FROM_EMAIL
        # recipient_list = [user.email,]

        # #send_mail(subject=subject, message='test', html_message=message, from_email=email_from, recipient_list=recipient_list, fail_silently=True)
        # email = EmailMultiAlternatives(subject=subject, body=message, from_email=email_from, to=recipient_list)
        # email.attach_alternative(message, "text/html")
        # email.content_subtype = 'html'
        # email.mixed_subtype = 'related'

        # with open(image_path_logo, mode='rb') as f_logo:
        #     image_logo = MIMEImage(f_logo.read())
        #     email.attach(image_logo)
        #     image_logo.add_header('Content-ID', f"<{image_name_logo}>")
        
        # with open(image_path_container, mode='rb') as f_container:
        #     image_container = MIMEImage(f_container.read())
        #     email.attach(image_container)
        #     image_container.add_header('Content-ID', f"<{image_name_container}>")

        # with open(image_path_connect, mode='rb') as f_connect:
        #     image_connect = MIMEImage(f_connect.read())
        #     email.attach(image_connect)
        #     image_connect.add_header('Content-ID', f"<{image_name_connect}>")

        # email.send()

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AOQuestionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    serializer_class = AOQuestionSerializer

    def get_queryset(self):
        queryset = AOQuestion.objects.all()
        shGroup = self.request.query_params.get('shGroup', None)
        if shGroup is not None:
            queryset = queryset.filter(shGroup__id=shGroup)
        return queryset

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

    def get_queryset(self):
        queryset = ProjectUser.objects.all()
        project = self.request.query_params.get('project', None)
        if project is not None:
            queryset = queryset.filter(project__id=project)
        return queryset

class DriverViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer


class MyMapLayoutViewSet(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = MyMapLayout.objects.all()
    serializer_class = MyMapLayoutStoreSerializer
    filterset_fields = ['user', 'project']

    def create(self, request, *args, **kwargs):
        data = request.data
        content_type = request.content_type
        #print(content_type)
        try:
            obj = MyMapLayout.objects.get(user_id=data['user'], project_id=data['project'])

            obj.projectUser.clear()
            
            # if type(data) != "dict":
            #     print(1)
            #     for item in data.getlist('projectUser'):
            #         new_obj = ProjectUser.objects.get(id=item)
            #         obj.projectUser.add(new_obj)
            if "application/json" in content_type:
                for item in data['projectUser']:
                    new_obj = ProjectUser.objects.get(id=item)
                    obj.projectUser.add(new_obj)
            else:
                for item in data.getlist('projectUser'):
                    new_obj = ProjectUser.objects.get(id=item)
                    obj.projectUser.add(new_obj)

            obj.save()

        except MyMapLayout.DoesNotExist:
            obj = MyMapLayout.objects.create(user_id=data['user'], project_id=data['project'])

            obj.user_id = data['user']
            obj.project_id = data['project']
            obj.layout_json = data['layout_json']

            # if type(data) != "dict":
            #     print(1)
            #     for item in data.getlist('projectUser'):
            #         new_obj = ProjectUser.objects.get(id=item)
            #         obj.projectUser.add(new_obj)
            if "application/json" in content_type:
                for item in data['projectUser']:
                    new_obj = ProjectUser.objects.get(id=item)
                    obj.projectUser.add(new_obj)
            else:
                for item in data.getlist('projectUser'):
                    new_obj = ProjectUser.objects.get(id=item)
                    obj.projectUser.add(new_obj)

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

class SHCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = SHCategory.objects.all()
    serializer_class = SHCategorySerializer
    filterset_fields = ['mapType', 'survey']

class SetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    @classmethod
    def get_extra_actions(cls):
        return []

    # def get(self, format=None):
    #     organizations = Organization.objects.all()
    #     serializer = StakeHolderSerializer(organizations, many=True)
    #     return Response(serializer.data)

    def post(self, request):
        print(request.data['email'])
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

class StakeHolderUserView(APIView):
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
            
            #print(serializer.data['user']['username'])

            dt = User.objects.filter(username=serializer.data['user']['username']).values_list('pk', flat=True)

            # subject = 'Test Message Title'
            # message = get_template('email.html').render(
            #     {
            #         'project_name': 'Test Project'
            #     }
            # )
            # email_from = settings.DEFAULT_FROM_EMAIL
            # recipient_list = ['mrstevenwong815@gmail.com',]

            # send_mail(subject=subject, message='test', html_message=message, from_email=email_from, recipient_list=recipient_list, fail_silently=True)

            return Response(dt[0], status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
