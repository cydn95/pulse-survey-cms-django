from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from snippets import views
#from rest_framework.authtoken.views import obtain_auth_token
from .views import CustomAuthToken
from rest_framework.urlpatterns import format_suffix_patterns
from allauth.account.views import confirm_email
from django.contrib import admin
from django.contrib.auth import views as auth_views

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
router.register(r'skipOption', views.SkipOptionViewSet)
router.register(r'aoquestion', views.AOQuestionViewSet, base_name='aoquestion')
router.register(r'driver', views.DriverViewSet)
router.register(r'amresponseexcel', views.AMResponseExcelViewSet)
router.register(r'aoresponseexcel', views.AOResponseExcelViewSet)
router.register(r'mymaplayouts', views.MyMapLayoutViewSet)
router.register(r'projectmaplayouts', views.ProjectMapLayoutViewSet)
router.register(r'projectByUser', views.ProjectByUserViewSet)
router.register(r'userByProject', views.UserByProjectViewSet)
router.register(r'shcategory', views.SHCategoryViewSet)
router.register(r'projectVideoUpload', views.ProjectVideoUploadViewSet)
router.register(r'shmapping', views.SHMappingViewSet)
router.register(r'useravatar', views.UserAvatarViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    url('', include(router.urls)),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^password_reset/', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    url(r'^api-token-auth/', CustomAuthToken.as_view()),
    url(r'^account/', include('allauth.urls')),
    #url('accounts-rest/registration/account-confirm-email/(?P<key>.+)/$', confirm_email, name='account_confirm_email'),
    # url('', include('django_rest_passwordreset.urls', namespace='password_reset')),
]

urlpatterns += format_suffix_patterns([
    url(r'stakeholder', views.StakeHolderUserView.as_view()),
    url(r'setpassword', views.SetPasswordView.as_view()),
    url(r'changepassword', views.ChangePasswordView.as_view())
])