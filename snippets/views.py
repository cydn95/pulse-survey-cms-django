from snippets.models import Snippet
from snippets.serializers import SnippetSerializer, UserSerializer, PageSettingSerializer, PageSerializer, AMResponseSerializer, AMResponseTopicSerializer, AOResponseSerializer, AOResponseTopicSerializer, AOPageSerializer
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

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
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
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly,
    #                       IsOwnerOrReadOnly]
    permission_classes = [permissions.IsAuthenticated,]

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
    permission_classes = [permissions.IsAuthenticated,]
    queryset = PageSetting.objects.all()
    serializer_class = PageSettingSerializer

class PageViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated,]
    queryset = Page.objects.all()
    serializer_class = PageSerializer

class AMResponseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,]
    queryset = AMResponse.objects.all()
    serializer_class = AMResponseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class AMResponseTopicViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,]
    queryset = AMResponseTopic.objects.all()
    serializer_class = AMResponseTopicSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AOResponseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,]
    queryset = AOResponse.objects.all()
    serializer_class = AOResponseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AOResponseTopicViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,]
    queryset = AOResponseTopic.objects.all()
    serializer_class = AOResponseTopicSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AOPageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,]
    queryset = AOPage.objects.all()
    serializer_class = AOPageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
