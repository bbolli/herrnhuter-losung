#!/usr/bin/env python3
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
    escape,
    Flask,
    Markup,
    render_template,
    url_for,
)

app = Flask(__name__)

date_url = '<int:y>-<int:m>-<int:d>'
oneday = datetime.timedelta(days=1)
speak_re = re.compile(r'/(.+?:)/')
strong_re = re.compile(r'#(.+?)#')


@app.template_filter('htmlize')
def htmlize(t):
    t = speak_re.sub(r'<em>\1</em>', str(escape(t)))
    t = strong_re.sub(r'<strong>\1</strong>', t)
    return Markup(t)


def url_for_date(date):
    return url_for('today') + f'{date.year}-{date.month:02}-{date.day:02}'


def render(data):
    if 'error' in data:
        return render_template('error.html', error=data), data['code']
    return render_template('verse.html', verse=data)


@app.route('/')
def today():
    return render(verse_today())


@app.route(f'/{date_url}')
def verse(y, m, d):
    return render(verse_date(y, m, d))


@app.route('/api/today')
def verse_today():
    return get_verse(datetime.date.today())


@app.route(f'/api/{date_url}')
def verse_date(y, m, d):
    if 0 < y < 100:
        y += 2000
    try:
        date = datetime.date(y, m, d)
    except ValueError:
        return {'error': f"Ungültiges Datum {y}-{m}-{d}", 'code': 400}
    return get_verse(date)


@app.errorhandler(404)
def not_found(e):
    return render({'error': "Diese Seite gibt es hier nicht", 'code': 404})


@app.errorhandler(500)
def internal_error(e):
    return render({'error': e, 'code': 500})


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
        # don't cache failure to allow for a newly appearing verse file
        return None
    cache[year] = root
    return root


def get_verse(date):
    year = f'{date.year:04}'
    if not (root := load_year(year)):
        return {'error': f"Losungen für Jahr {year} nicht vorhanden", 'code': 404}
    if not (node := root.find(f'./Losungen[Datum="{date.isoformat()}T00:00:00"]')):
        return {'error': f"Vers für {date} nicht gefunden‽", 'code': 404}
    return {
        'date': date.isoformat(),
        'weekday': node.findtext('Wtag'),
        'sunday_name': node.findtext('Sonntag'),
        'verse_text': node.findtext('Losungstext'),
        'verse_verse': node.findtext('Losungsvers'),
        'teach_text': node.findtext('Lehrtext'),
        'teach_verse': node.findtext('Lehrtextvers'),
        'yesterday': url_for_date(date - oneday),
        'tomorrow': url_for_date(date + oneday) if date < datetime.date.today() else None
    }


if __name__ == '__main__':
    app.run()
