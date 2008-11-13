# coding: utf-8

import os, re, datetime
from xml.etree import cElementTree as ElementTree

from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist


speak_re = re.compile(r'/(.+?:)/')
strong_re = re.compile(r'#(.+?)#')
oneday = datetime.timedelta(days=1)
file_template = os.path.join(os.path.dirname(__file__), 'lib', 'losung_free_%s.xml')

def _textvers(t):
    t = escape(t)
    t = speak_re.sub(r'<em>\1</em>', t)
    t = strong_re.sub(r'<strong>\1</strong>', t)
    return mark_safe(t)

class Losung(object):
    """Implements the model of a verse. There's no associated database table."""

    class DoesNotExist(ObjectDoesNotExist):
	pass

    def __init__(self, date=None):
	if date is None:
	    date = datetime.date.today()
	isodate = date.isoformat()
	losungen = ElementTree.parse(file_template % date.year)
	for e in losungen.getroot():
	    d = e.findtext('Datum')
	    if d is not None and d.startswith(isodate):
		self.datum = date
		self.losungstext = _textvers(e.findtext('Losungstext'))
		self.losungsvers = e.findtext('Losungsvers')
		self.lehrtext = _textvers(e.findtext('Lehrtext'))
		self.lehrvers = e.findtext('Lehrtextvers')
		self.sonntag = e.findtext('Sonntag')
		self.gestern = date - oneday
		if date < datetime.date.today():
		    self.morgen = date + oneday
		return
	raise DoesNotExist()
