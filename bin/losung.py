#!/usr/bin/python3

# usage: losung.py [--news] [yyyy-mm-dd]

import functools
import glob
import os
import re
import sys
import time
from xml.etree import cElementTree as ElementTree

from xmlbuilder import HTMLBuilder, Safe

verse_root = os.environ.get('VERSE_ROOT', '/home/bb/lib')

speak = functools.partial(re.compile(r'/(.+?:)/').sub, r'<em>\1</em>')
emph = functools.partial(re.compile(r'#(.+?)#').sub, r'<strong>\1</strong>')


def textvers(t: str) -> Safe:
    t = speak(Safe.text(t))
    t = emph(t)
    # t is a str now, it needs to be made Safe again
    return Safe(t)


def vers(when: str, news: bool) -> HTMLBuilder:
    fn = glob.glob(f'{verse_root}/losung*{when[:4]}*.xml')
    root = ElementTree.parse(fn[0]).getroot()
    for d in root:
        date = d.findtext('Datum')
        if date is not None and date.startswith(when):
            sonntag = d.findtext('Sonntag')
            los_t = textvers(d.findtext('Losungstext') or 'n/a')
            los_v = d.findtext('Losungsvers')
            lehr_t = textvers(d.findtext('Lehrtext') or 'n/a')
            lehr_v = d.findtext('Lehrtextvers')
            break
    else:
        print("invalid date", file=sys.stderr)
        sys.exit(1)

    f = HTMLBuilder(encoding='')
    if news:
        f[Safe('Losung\nmeta-source: losung\n')]
    else:
        f.h3('Losung')
    if sonntag:
        f.h4(sonntag, class_='dbvSunday')
    f.p(los_t, class_='dbvText').p(los_v, class_='dbvVers')
    f.p(lehr_t, class_='dbvText').p(lehr_v, class_='dbvVers')
    if not news:
        with f.p(class_="dbvCopyright"):
            f.a("EBU", _pre="© ", _post=",", href="https://www.ebu.de/",
                title="Evang. Brüder-Unität Bad Boll/Friedrich Reinhardt Verlag")
            f.a("losungen.de", href="https://www.losungen.de/")
    return f


if __name__ == '__main__':
    news = len(sys.argv) > 1 and sys.argv[1] == '--news'
    if news:
        del sys.argv[1]
    today = time.strftime('%Y-%m-%d') if len(sys.argv) == 1 else sys.argv[1]
    print(vers(today, news), end='')
