#!/usr/bin/python
# encoding: utf-8

import time, re, xmlgen
from xml.etree import cElementTree as ElementTree

today = time.strftime('%Y-%m-%d')
speak_re = re.compile(r'/(.+?:)/')
emph_re = re.compile(r'#(.+?)#')

f = xmlgen.Factory()

def textvers(t, v, href=''):
    t = speak_re.sub(r'<em>\1</em>', t)
    t = emph_re.sub(r'<strong>\1</strong>', t)
    return f.p(t, class_="dbvText"), f.p(v, class_="dbvVers")

los_t = None
for d in ElementTree.parse('/home/bb/lib/losung_free_%s.xml' % today[:4]).getroot():
    date = d.findtext('Datum')
    if date is not None and date.startswith(today):
	los_t, los_v = textvers(d.findtext('Losungstext'), d.findtext('Losungsvers'))
	lehr_t, lehr_v = textvers(d.findtext('Lehrtext'), d.findtext('Lehrtextvers'))
	break

if los_t:
    print unicode(f.fragment(
	f.h3('Losung'),
	los_t, los_v,
	lehr_t, lehr_v,
	f.p(class_="dbvCopyright")[u'© ',
	    f.a("EBU", href="http://www.ebu.de/", title=u"Evang. Brüder-Unität Bad Boll/Friedrich Reinhardt Verlag"),
	    ', ',
	    f.a("losungen.de", href="http://www.losungen.de/")
	]
    )).encode('utf-8')
