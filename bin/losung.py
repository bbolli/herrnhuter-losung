#!/usr/bin/env python3

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

speak = functools.partial(re.sub, r'/(.+?:)/', r'<em>\1</em>')
emph = functools.partial(re.sub, r'#(.+?)#', r'<strong>\1</strong>')


def textvers(t: str) -> Safe:
    t = speak(Safe.text(t))
    t = emph(t)
    # t is a str now, it needs to be made Safe again
    return Safe(t)


def vers(when: str, news: bool) -> HTMLBuilder | None:
    if not (fn := glob.glob(f'{verse_root}/losung*{when[:4]}*.xml')):
        return None
    root = ElementTree.parse(fn[0]).getroot()
    if (node := root.find(f'Losungen[Datum="{when}T00:00:00.000"]')) is None:
        if (node := root.find(f'Losungen[Datum="{when}T00:00:00"]')) is None:
            return None
    sonntag = node.findtext('Sonntag')
    los_t = textvers(node.findtext('Losungstext') or 'n/a')
    los_v = node.findtext('Losungsvers')
    lehr_t = textvers(node.findtext('Lehrtext') or 'n/a')
    lehr_v = node.findtext('Lehrtextvers')

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
    if v := vers(today, news):
        print(v, end='')
    else:
        print(f"Vers für '{today}' nicht gefunden", file=sys.stderr)
        sys.exit(1)
