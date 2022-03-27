# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from django.utils.translation import ugettext_lazy as _
from page_nav.admin import PageNavAdmin
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view
import threading
import datetime
import time
import pytz
from django.utils.timezone import now, timedelta
from aboutme.models import AMResponseAcknowledgement, User, ProjectUser, AMQuestion, Survey, Project
from snippets.models import EmailRecord
from django.db.models import Count
import os
from pathlib import Path
from django.template.loader import get_template, render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from smtplib import SMTPException
from email.mime.image import MIMEImage

admin.autodiscover()

urlpatterns = [
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': {'cmspages': CMSSitemap}}),
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    url(r'^api/v1/', include('snippets.urls')),
    url(r'^api/v1/api-auth/', include('rest_framework.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
]


# Django rest swagger documentation
schema_view = get_swagger_view(title='Pulse CMS API')
urlpatterns += [
    url(r'^api-docs/$', schema_view)
]


urlpatterns += i18n_patterns(
    url(r'^admin/', include('boolean_switch.urls')),
    url(r'^admin/', admin.site.urls),  # NOQA
)

# Change admin site title
admin.site.site_header = _("ProjectAI Administration")
admin.site.site_title = _("ProjectAI Administration")

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        ] + staticfiles_urlpatterns() + urlpatterns



def thread_function(dur):
    print('started')
    tz = pytz.timezone('Australia/Perth')
    while True:
        try:
            # if datetime.datetime.now(tz).hour==17 and datetime.datetime.now(tz).minute==0 and datetime.datetime.now(tz).second==0:
            if datetime.datetime.now(tz).second==0:
                end = datetime.datetime.now(tz)
                start = end - timedelta(days=1)
                ackedUsers = AMResponseAcknowledgement.objects.filter(
                    acknowledgeStatus__range=[1, 6], 
                    updated_at__range=[start, end],
                    ackEmailSent=False
                ).values('amResponse__projectUser__user__id').annotate(total=Count('amResponse__projectUser__user__id'))
                for i in range(len(ackedUsers)):
                    acksBySurvey = AMResponseAcknowledgement.objects.filter(
                        acknowledgeStatus__range=[1, 6], 
                        updated_at__range=[start, end], 
                        ackEmailSent=False, 
                        amResponse__projectUser__user__id=ackedUsers[i]['amResponse__projectUser__user__id']
                    ).values('amResponse__survey').annotate(total=Count('amResponse__survey'))
                    for j in range(len(acksBySurvey)):
                        acksByQuestion = AMResponseAcknowledgement.objects.filter(
                            acknowledgeStatus__range=[1, 6], 
                            updated_at__range=[start, end], 
                            ackEmailSent=False, 
                            amResponse__projectUser__user__id=ackedUsers[i]['amResponse__projectUser__user__id'],
                            amResponse__survey__id=acksBySurvey[j]['amResponse__survey']
                        ).values('amResponse__amQuestion').annotate(total=Count('amResponse__amQuestion'))
                        commentProjectUser = ackedUsers[i]['amResponse__projectUser__user__id']
                        userInfo = User.objects.get(id=commentProjectUser)
                        print('userInfo', userInfo)
                        ackedCount = acksBySurvey[j]['total']
                        surveyName = Survey.objects.get(
                            id=acksBySurvey[j]['amResponse__survey']).surveyTitle
                        surveyTemp = Survey.objects.get(id=acksBySurvey[j]['amResponse__survey'])
                        projectName = Project.objects.get(id=surveyTemp.project_id).projectName
                        ackByQuestions = []
                        for k in range(len(acksByQuestion)):
                            acks = AMResponseAcknowledgement.objects.filter(
                                acknowledgeStatus__range=[1, 6], 
                                updated_at__range=[start, end], 
                                ackEmailSent=False, 
                                amResponse__projectUser__user__id=ackedUsers[i]['amResponse__projectUser__user__id'],
                                amResponse__survey__id=acksBySurvey[j]['amResponse__survey'],
                                amResponse__amQuestion__id=acksByQuestion[k]['amResponse__amQuestion']
                            )
                            ackByQuestion = Object()
                            ackByQuestion.pulse_question = AMQuestion.objects.get(
                                id=acksByQuestion[k]['amResponse__amQuestion']).questionText
                            ackByQuestion.pulseAnswer = acks[0].amResponse.topicValue
                            ackUsers = []
                            for l in range(len(acks)):
                                ackUser = Object()
                                ackProjectUser = ProjectUser.objects.get(id=acks[l].projectUser.id)
                                ackUser.first_name = User.objects.get(id=ackProjectUser.user.id).first_name
                                ackUser.last_name = User.objects.get(id=ackProjectUser.user.id).last_name
                                ackText = ""
                                if acks[l].acknowledgeStatus == 1:
                                    ackText = "Thanks for sharing"
                                elif acks[l].acknowledgeStatus == 2:
                                    ackText = "Great idea"
                                elif acks[l].acknowledgeStatus == 3:
                                    ackText = "Working on it"
                                elif acks[l].acknowledgeStatus == 4:
                                    ackText = "Let's talk about it"
                                elif acks[l].acknowledgeStatus == 5:
                                    ackText = "I agree"
                                elif acks[l].acknowledgeStatus == 6:
                                    ackText = "Tell us more"
                                print('ackText', ackText)
                                ackUser.ackText = ackText
                                ackUsers.append(ackUser)
                            ackByQuestion.ackUsers = ackUsers
                            ackByQuestions.append(ackByQuestion)
                        image_path_logo = os.path.join(
                            settings.STATICFILES_DIRS[0], 'email', 'img', 'logo-2.png')
                        image_name_logo = Path(image_path_logo).name
                        image_path_star = os.path.join(
                            settings.STATICFILES_DIRS[0], 'email', 'img', 'star.png')
                        image_name_star = Path(image_path_star).name

                        subject = projectName + " - Your comment has been acknowledged."
                        message = get_template('ackform3.html').render(
                            {
                                "project_name": "Pulse",
                                "first_name": userInfo.first_name,
                                "last_name": userInfo.last_name,
                                "survey_name": surveyName,
                                "image_name_logo": image_name_logo,
                                "image_name_star": image_name_star,
                                "ackByQuestions": ackByQuestions,
                                "site_url": settings.SITE_URL,
                                "acked_count": ackedCount
                            }
                        )
                        email_from = settings.DEFAULT_FROM_EMAIL
                        recipient_list = [userInfo.email]

                        email = EmailMultiAlternatives(subject=subject, body=message, from_email=email_from, to=recipient_list)
                        email.attach_alternative(message, "text/html")
                        email.content_subtype = "html"
                        email.mixed_subtype = "related"

                        with open(image_path_logo, mode='rb') as f_logo:
                            image_logo = MIMEImage(f_logo.read())
                            email.attach(image_logo)
                            image_logo.add_header('Content-ID', f"<{image_name_logo}>")
                        with open(image_path_star, mode='rb') as f_star:
                            image_star = MIMEImage(f_star.read())
                            email.attach(image_star)
                            image_star.add_header('Content-ID', f"<{image_name_star}>")

                        try:
                            email.send()
                            emailRecord = EmailRecord(recipient=userInfo.email, message=message)
                            emailRecord.save()
                            for ack in acks:
                                ack.ackEmailSent = True
                                ack.save()
                        except SMTPException as e:
                            print('There was an error sending an email: ', e)
                print('Time is out')
        except:
            print('There was an error sending an email')
            pass
        # print(datetime.datetime.now(tz))
        time.sleep(1)
x = threading.Thread(target=thread_function, args=(1,))
x.start()

class Object:
    pass