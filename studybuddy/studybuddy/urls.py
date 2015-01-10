from django.conf.urls import patterns, include, url
from django.contrib import admin
from studybuddy import views
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'studybuddy.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^create_study_session/$', views.create_study_session),
    url(r'^dashboard/', views.dashboardMain, name='dashboardMain'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^user/create/', 'studybuddy.views.createUser', name='createUser'),
    url(r'^test/', 'studybuddy.views.test'),
    url(r'^user/login/', 'studybuddy.views.loginUser', name='loginUser'),
    url(r'^user/logout/', 'studybuddy.views.logoutUser', name='logoutUser'),
    url(r'^studyinterests/query/', 'studybuddy.views.studyInterestsQuery', name='studyInterestsQuery'),
    url(r'^studyinterests/queryuser/', 'studybuddy.views.userStudyInterestsQuery', name='userStudyInterestsQuery'),
    url(r'^studyinterests/update/', 'studybuddy.views.userStudyInterestsUpdate', name='userStudyInterestsUpdate'),
)
