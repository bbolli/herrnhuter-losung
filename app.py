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
    abort,
    escape,
    Flask,
    Markup,
    render_template,
    url_for,
)
from werkzeug.exceptions import HTTPException, NotFound


app = Flask(__name__)

date_url = '<int:y>-<int:m>-<int:d>'
oneday = datetime.timedelta(days=1)
speak_re = re.compile(r'/(.+?:)/')
strong_re = re.compile(r'#(.+?)#')

# type aliases
RenderResult = str | tuple[str, int]
ApiResult = dict[str, str | int | None]


@app.template_filter('htmlize')
def htmlize(t: str) -> Markup:
    t = speak_re.sub(r'<em>\1</em>', str(escape(t)))
    t = strong_re.sub(r'<strong>\1</strong>', t)
    return Markup(t)


def url_for_date(date: datetime.date) -> str:
    return url_for('today') + f'{date.year}-{date.month:02}-{date.day:02}'


def render(data: ApiResult) -> RenderResult:
    if 'error' in data:
        # Satisfy mypy: `code` is always an int, but the type checker
        # cannot know this. Add an explicit type check as hint.
        if isinstance(code := data['code'], int):
            # match fields with the werkzeug HTTPException class
            data['description'] = data.pop('error')
            return render_template("error.html", error=data), code
        else:
            abort(500, f"Typ-Verwirrung in render()-Daten "
                       f"('code' sollte ein 'int' sein): {data!r}")
    return render_template('verse.html', vers=data)


@app.route('/')
def today() -> RenderResult:
    return render(verse_today())


@app.route(f'/{date_url}')
def verse(y: int, m: int, d: int) -> RenderResult:
    return render(verse_date(y, m, d))


@app.route('/api/today')
def verse_today() -> ApiResult:
    return get_verse(datetime.date.today())


@app.route(f'/api/{date_url}')
def verse_date(y: int, m: int, d: int) -> ApiResult:
    if 0 <= y < 100:
        y += datetime.date.today().year // 100 * 100
    try:
        date = datetime.date(y, m, d)
    except ValueError:
        return {'error': f"Ungültiges Datum {y}-{m}-{d}", 'code': 400}
    return get_verse(date)


def error_handler(e: Exception) -> tuple[str, int]:
    if isinstance(e, NotFound):
        e.description = "Diese Seite gibt es hier nicht"
    if isinstance(e, HTTPException):
        return render_template("error.html", error=e), e.code or 500
    raise e


app.register_error_handler(400, error_handler)
app.register_error_handler(404, error_handler)
app.register_error_handler(405, error_handler)
app.register_error_handler(500, error_handler)


cache: dict[str, ET.ElementTree] = {}


def load_year(year: str) -> ET.ElementTree | None:
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


def get_verse(date: datetime.date) -> ApiResult:
    year = f'{date.year:04}'
    if not (root := load_year(year)):
        return {'error': f"Losungen für Jahr {year} nicht vorhanden", 'code': 404}
    if not (node := root.find(f'./Losungen[Datum="{date.isoformat()}T00:00:00"]')):
        return {'error': f"Vers für {date} nicht gefunden‽", 'code': 404}

    result: ApiResult = {
        'datum': date.isoformat(),
        'gestern': url_for_date(date - oneday),
        'morgen': url_for_date(date + oneday) if date < datetime.date.today() else None
    }
    result.update((f.lower(), node.findtext(f)) for f in (
        'Wtag', 'Sonntag', 'Losungstext', 'Losungsvers', 'Lehrtext', 'Lehrtextvers'
    ))
    return result


if __name__ == '__main__':
    app.run()
