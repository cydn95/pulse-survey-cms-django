from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from snippets import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'snippets', views.SnippetViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'pagesettings', views.PageSettingViewSet)
router.register(r'pages', views.PageViewSet)
router.register(r'amresponse', views.AMResponseViewSet)
router.register(r'amresponsetopic', views.AMResponseTopicViewSet)
router.register(r'aoresponse', views.AOResponseViewSet)
router.register(r'aoresponsetopic', views.AOResponseTopicViewSet)
router.register(r'aopage', views.AOPageViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    url('', include(router.urls)),
]