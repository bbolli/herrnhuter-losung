#!/usr/bin/python
# encoding: utf-8

import sys, time, re, glob, xmlgen
from xml.etree import cElementTree as ElementTree

today = time.strftime('%Y-%m-%d') if len(sys.argv) == 1 else sys.argv[1]
speak_re = re.compile(r'/(.+?:)/')
emph_re = re.compile(r'#(.+?)#')

f = xmlgen.Factory()

def textvers(t, v, href=''):
    t = speak_re.sub(r'<em>\1</em>', t)
    t = emph_re.sub(r'<strong>\1</strong>', t)
    return f.p(t, class_="dbvText"), f.p(v, class_="dbvVers")

fn = glob.glob('/home/bb/lib/los*%s*.xml' % today[:4])
root = ElementTree.parse(fn[0]).getroot()
for d in root:
    date = d.findtext('Datum')
    if date is not None and date.startswith(today):
        sonntag = d.findtext('Sonntag')
        sonntag = f.p(sonntag, class_='dbvSunday') if sonntag else ''
        los_t, los_v = textvers(d.findtext('Losungstext'), d.findtext('Losungsvers'))
        lehr_t, lehr_v = textvers(d.findtext('Lehrtext'), d.findtext('Lehrtextvers'))
        break
else:
    sys.exit(1)

print unicode(f.fragment(
    f.h3('Losung'), '\n', sonntag,
    los_t, '\n', los_v, '\n',
    lehr_t, '\n', lehr_v, '\n',
    f.p(class_="dbvCopyright")[u'© ',
        f.a("EBU", href="http://www.ebu.de/", title=u"Evang. Brüder-Unität Bad Boll/Friedrich Reinhardt Verlag"),
        ',\n',
        f.a("losungen.de", href="http://www.losungen.de/")
    ]
)).encode('utf-8')
