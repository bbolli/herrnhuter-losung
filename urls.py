from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^$', views.current, name='current_verse'),
    url(r'^(\d{4})/(\d\d?)/(\d\d?)/$', views.date, name='verse'),
)
