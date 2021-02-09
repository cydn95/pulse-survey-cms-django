from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from snippets import views
from rest_framework.urlpatterns import format_suffix_patterns
from allauth.account.views import confirm_email
from django.contrib import admin
from django.contrib.auth import views as auth_views

# Create a router and register our viewsets with it.
router = DefaultRouter()

router.register(r'amresponse', views.AMResponseViewSet)
router.register(r'amresponsetopic', views.AMResponseTopicViewSet)
router.register(r'aoresponse', views.AOResponseViewSet)
router.register(r'aoresponsetopic', views.AOResponseTopicViewSet)
router.register(r'amresponseexcel', views.AMResponseExcelViewSet)
router.register(r'aoresponseexcel', views.AOResponseExcelViewSet)
router.register(r'amresponsereport', views.AMResponseReportViewSet)
router.register(r'aoresponsereport', views.AOResponseReportViewSet)
router.register(r'configpage', views.ConfigPageViewSet)
router.register(r'driver', views.DriverViewSet)
router.register(r'engagementtrend', views.AMResponseFeedbackSummaryForEngagementViewset)
router.register(r'feedbacksummaryreport', views.AOResponseFeedbackSummaryViewset)
router.register(r'mymaplayouts', views.MyMapLayoutViewSet)
router.register(r'nikelmobilepage', views.NikelMobilePageViewSet)
router.register(r'option', views.OptionViewSet)
router.register(r'overallsentimentreport', views.OverallSentimentReportViewSet)
router.register(r'pages', views.PageViewSet)
router.register(r'project', views.ProjectViewSet)
router.register(r'projectuser', views.ProjectUserViewSet)
router.register(r'projectmaplayouts', views.ProjectMapLayoutViewSet)
router.register(r'projectbyuser', views.ProjectByUserViewSet)
router.register(r'shgroup', views.SHGroupViewSet)
router.register(r'skipoption', views.SkipOptionViewSet)
router.register(r'surveybyproject', views.SurveyViewSet)
router.register(r'shcategory', views.SHCategoryViewSet)
router.register(r'subdriver', views.SubDriverViewSet)
router.register(r'team', views.TeamViewSet)
router.register(r'tooltipguide', views.ToolTipGuideViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'updatestakeholder', views.UpdateStakeHolderViewSet)
router.register(r'userbysurvey', views.UserBySurveyViewSet)
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
    url(r'^api-token-auth/', views.CustomAuthToken.as_view()),
    url(r'^account/', include('allauth.urls')),
    url(r'^get_csrf/?$', views.get_csrf, name="get_csrf"),
]

urlpatterns += format_suffix_patterns([
    url(r'changepassword', views.ChangePasswordView.as_view()),
    url(r'stakeholder', views.StakeHolderUserView.as_view()),
    url(r'setpassword', views.SetPasswordView.as_view()),
    url(r'userprofile', views.UserProfileView.as_view()),
    url(r'userguidemode', views.UserGuideModeView.as_view()),
    url(r'wordcloud', views.WordCloudView.as_view()),
])

# router.register(r'interestreport', views.AMResponseFeedbackSummaryForInterestViewset)     # deprecated
# router.register(r'perceptionreality', views.PerceptionRealityViewSet)         # deprecated
# router.register(r'fetchperceptioninfo', views.FetchPerceptionInfoViewSet)     # deprecated
# router.register(r'fetchRealityInfo', views.FetchRealityInfoViewSet)           # deprecated
# router.register(r'overallsentimentreportv2', views.ProjectUserv2ViewSet)     # deprecated
# router.register(r'aoresponsereportv2', views.AOResponseReportv2ViewSet)       # deprecated
# router.register(r'feedbacksummaryreportv2', views.AMResponseFeedbackSummaryv2Viewset)     # deprecated
# router.register(r'userbysurveyv2', views.UserBySurveyv2ViewSet)       # deprecated
# router.register(r'projectvideoupload', views.ProjectVideoUploadViewSet)     # deprecated
# router.register(r'surveybyuser', views.SurveyByUserViewSet)           # deprecated
# router.register(r'aoquestion', views.AOQuestionViewSet, base_name='aoquestion')         # deprecated
# router.register(r'aopage', views.AOPageViewSet)         # deprecated
# router.register(r'pagesettings', views.PageSettingViewSet)      # deprecated
# router.register(r'shmapping', views.SHMappingViewSet)         # deprecated
# router.register(r'sentimentreport', views.AMResponseFeedbackSummaryForSentimentViewSet)       # deprecated
