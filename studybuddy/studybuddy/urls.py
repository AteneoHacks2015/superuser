from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'studybuddy.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^user/create/', 'studybuddy.views.createUser', name='createUser'),
    url(r'^test/', 'studybuddy.views.test'),
    url(r'^studyinterests/query/', 'studybuddy.views.studyInterestsQuery', name='studyInterestsQuery'),
)
