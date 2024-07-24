#!/usr/bin/python3

# usage: losung.py [--news] [yyyy-mm-dd]

import glob
import re
import sys
import time
import xmlbuilder
from xml.etree import cElementTree as ElementTree

news = len(sys.argv) > 1 and sys.argv[1] == '--news'
if news:
    del sys.argv[1]
today = time.strftime('%Y-%m-%d') if len(sys.argv) == 1 else sys.argv[1]
speak_re = re.compile(r'/(.+?:)/')
emph_re = re.compile(r'#(.+?)#')

f = xmlbuilder.HTMLBuilder(encoding='', stream=sys.stdout)


def textvers(t):
    t = speak_re.sub(r'<em>\1</em>', xmlbuilder.escape(t))
    t = emph_re.sub(r'<strong>\1</strong>', t)
    return xmlbuilder.Safe(t)


fn = glob.glob('/home/bb/lib/los*%s*.xml' % today[:4])
root = ElementTree.parse(fn[0]).getroot()
for d in root:
    date = d.findtext('Datum')
    if date is not None and date.startswith(today):
        sonntag = d.findtext('Sonntag')
        los_t = textvers(d.findtext('Losungstext'))
        los_v = d.findtext('Losungsvers')
        lehr_t = textvers(d.findtext('Lehrtext'))
        lehr_v = d.findtext('Lehrtextvers')
        break
else:
    sys.exit(1)

if news:
    print('Losung\nmeta-source: losung\n')
    if sonntag:
        f.h4(sonntag, class_='dbvSunday')
else:
    f.h3('Losung')
    if sonntag:
        f.h2(sonntag, class_='dbvSunday')
f.p(los_t, class_='dbvText')
f.p(los_v, class_='dbvVers')
f.p(lehr_t, class_='dbvText')
f.p(lehr_v, class_='dbvVers')
if not news:
    with f.p(class_="dbvCopyright"):
        f['©']
        f.a("EBU", href="https://www.ebu.de/",
            title="Evang. Brüder-Unität Bad Boll/Friedrich Reinhardt Verlag")
        f[',']
        f.a("losungen.de", href="https://www.losungen.de/")
