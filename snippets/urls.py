from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from snippets import views
#from rest_framework.authtoken.views import obtain_auth_token
from .views import CustomAuthToken

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
router.register(r'team', views.TeamViewSet)
router.register(r'shgroup', views.SHGroupViewSet)
router.register(r'projectuser', views.ProjectUserViewSet)
router.register(r'option', views.OptionViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    url('', include(router.urls)),
    url('rest-auth/', include('rest_auth.urls')),
    url('api-token-auth/', CustomAuthToken.as_view()),
]