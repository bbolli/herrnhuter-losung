#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
import glob
import re
from xml.etree import ElementTree as ET

from flask import (
    Flask,
    Markup,
    abort,
    render_template,
)

app = Flask(__name__)

oneday = datetime.timedelta(days=1)
speak_re = re.compile(r'/(.+?:)/')
strong_re = re.compile(r'#(.+?)#')


def htmlize(t):
    t = speak_re.sub(r'<em>\1</em>', t)
    t = strong_re.sub(r'<strong>\1</strong>', t)
    return Markup(t)


def url_for_date(date):
    return f'/{date.year}-{date.month:02}-{date.day:02}'


class Verse:
    def __init__(self, node):
        self.date = datetime.date.fromisoformat(node.findtext('Datum', '')[:10])
        self.weekday = node.findtext('Wtag')
        self.sunday_name = node.findtext('Sonntag')
        self.verse_text = htmlize(node.findtext('Losungstext'))
        self.verse_verse = node.findtext('Losungsvers')
        self.teach_text = htmlize(node.findtext('Lehrtext'))
        self.teach_verse = node.findtext('Lehrtextvers')

        self.yesterday = url_for_date(self.date - oneday)
        if self.date < datetime.date.today():
            self.tomorrow = url_for_date(self.date + oneday)


@app.route('/')
def today():
    return render(datetime.date.today())


@app.route('/<int:y>-<int:m>-<int:d>')
def verse(y, m, d):
    try:
        date = datetime.date(y, m, d)
    except ValueError:
        abort(404)
    return render(date)


cache = {}

def load_year(year):
    global cache
    try:
        return cache[year]
    except KeyError:
        pass
    try:
        # use a glob because the file name changed from "losung_free_YYYY.xml"
        # to "losungen free YYYY.xml" in 2011
        root = ET.parse(glob.glob(f'lib/losung*{year}.xml')[0])
    except (IndexError, IOError):
        abort(404)
    cache[year] = root
    return root


def render(date):
    root = load_year(date.year)
    verse = root.findall(f'./Losungen[Datum="{date.isoformat()}T00:00:00"]')
    if not verse:
        abort(404)
    return render_template('verse.html', verse=Verse(verse[0]))


if __name__ == '__main__':
    app.run()
