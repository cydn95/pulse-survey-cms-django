from shgroup.serializers import MyMapLayoutStoreSerializer, ProjectMapLayoutStoreSerializer
from snippets.models import Snippet
from snippets.serializers import SkipOptionSerializer, DriverSerializer, AOQuestionSerializer, OrganizationSerializer, OptionSerializer, ProjectUserSerializer, SHGroupSerializer, SnippetSerializer, UserSerializer, PageSettingSerializer, PageSerializer, AMResponseSerializer, AMResponseTopicSerializer, AOResponseSerializer, AOResponseTopicSerializer, AOPageSerializer, TeamSerializer
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
from aboutme.models import AMResponse, AMResponseTopic
from aboutothers.models import AOResponse, AOResponseTopic, AOPage
from team.models import Team
from shgroup.models import SHGroup, ProjectUser, MyMapLayout, ProjectMapLayout
from option.models import Option, SkipOption
from rest_framework import status
from organization.models import Organization
from aboutothers.models import AOQuestion
from survey.models import Driver

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import filters

from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer

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

class PageViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = Page.objects.all()
    serializer_class = PageSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        print(data, many)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AMResponseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAuthenticatedOrReadOnly]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        print(data, many)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
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
        print(data, many)
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
        print(data, many)
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
        print(data, many)
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
        print(data, many)
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
        print(data, many)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class SHGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = SHGroup.objects.all()
    serializer_class = SHGroupSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        print(data, many)
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

    def create(self, request, *args, **kwargs):
        data = request.data.get("items") if 'items' in request.data else request.data
        many = isinstance(data, list)
        print(data, many)
        serializer = self.get_serializer(data=data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
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
    
class DriverViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer


class MyMapLayoutViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = MyMapLayout.objects.all()
    serializer_class = MyMapLayoutStoreSerializer

    def get_queryset(self):
        projectUser = self.kwargs.get('projectUser', None)
        project = self.kwargs.get('project', None)
        if projectUser and project:
            return MyMapLayout.objects.filter(projectUser=projectUser, project=project)
        return super(MyMapLayoutViewSet, self).get_queryset()


class ProjectMapLayoutViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAuthenticatedOrReadOnly]
    queryset = ProjectMapLayout.objects.all()
    serializer_class = ProjectMapLayoutStoreSerializer

    def get_queryset(self):
        projectUser = self.kwargs.get('projectUser', None)
        project = self.kwargs.get('project', None)
        if projectUser and project:
            return ProjectMapLayout.objects.filter(projectUser=projectUser, project=project)
        return super(ProjectMapLayoutViewSet, self).get_queryset()