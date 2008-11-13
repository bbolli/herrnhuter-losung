# coding: utf-8

import time, datetime

from django.http import Http404
from django.views.generic.simple import direct_to_template
from django.conf import settings

from models import Losung


def current(request):
    y, m, d = time.localtime()[:3]
    return date(request, y, m, d)

def date(request, y, m, d):
    try:
	losung = Losung(datetime.date(int(y), int(m), int(d)))
    except:
	if settings.DEBUG:
	    raise
	raise Http404

    return direct_to_template(request, 'losung_detail.html', {
	'losung': losung,
	'title': u"Tageslosung",
    })
