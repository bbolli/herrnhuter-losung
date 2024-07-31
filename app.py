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

from datetime import date, timedelta
from functools import partial
from glob import glob
import re
from xml.etree.ElementTree import parse, ElementTree

from flask import (
    Flask,
    render_template,
    url_for,
)
from markupsafe import escape, Markup
from werkzeug.exceptions import HTTPException, NotFound


app = Flask(__name__)

date_url = '<int:y>-<int:m>-<int:d>'
oneday = timedelta(days=1)
speak = partial(re.sub, r'/(.+?:)/', r'<em>\1</em>')
emph = partial(re.sub, r'#(.+?)#', r'<strong>\1</strong>')

# type aliases
RenderResult = str | tuple[str, int]
ApiResult = dict[str, str | int | None | dict[str, str]]


@app.template_filter('htmlize')
def htmlize(t: str) -> Markup:
    t = speak(str(escape(t)))
    t = emph(t)
    return Markup(t)


def url_for_date(dt: date) -> str:
    return url_for('today') + f'{dt.year}-{dt.month:02}-{dt.day:02}'


def error(err: str, code: int) -> ApiResult:
    """Return an ApiResult describing an error condition and code"""
    return {'error': err, 'code': code}


def render(data: ApiResult) -> RenderResult:
    if 'error' in data:
        # Satisfy mypy: `code` is always an int, but the type checker
        # cannot know this. Add an explicit type assertion as hint.
        assert isinstance(data['code'], int)
        # match fields with the werkzeug HTTPException class
        data['description'] = data.pop('error')
        return render_template("error.html", error=data), data['code']
    return render_template('verse.html', vers=data)


@app.route('/')
def today() -> RenderResult:
    return render(verse_today())


@app.route(f'/{date_url}')
def verse(y: int, m: int, d: int) -> RenderResult:
    return render(verse_date(y, m, d))


@app.route('/api/today')
def verse_today() -> ApiResult:
    return get_verse(date.today())


@app.route(f'/api/{date_url}')
def verse_date(y: int, m: int, d: int) -> ApiResult:
    if 0 <= y < 100:
        y += date.today().year // 100 * 100
    try:
        dt = date(y, m, d)
    except ValueError:
        return error(f"Ungültiges Datum {y}-{m}-{d}", 400)
    return get_verse(dt)


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
def error_handler(e: Exception) -> tuple[str, int]:
    if isinstance(e, NotFound):
        e.description = "Diese Seite gibt es hier nicht"
    if isinstance(e, HTTPException):
        return render_template("error.html", error=e), e.code or 500
    raise e


cache: dict[str, ElementTree] = {}


def load_year(year: str) -> ElementTree | None:
    global cache
    try:
        return cache[year]
    except KeyError:
        pass
    try:
        # use a glob because the file name changed from "losung_free_YYYY.xml"
        # to "losungen free YYYY.xml" in 2011
        root = parse(glob(f'lib/losung*{year}.xml')[0])
    except (IndexError, IOError):
        # don't cache failure to allow for a newly appearing verse file
        return None
    cache[year] = root
    return root


def api_url(dt: date) -> str:
    return url_for('verse_date', y=dt.year, m=dt.month, d=dt.day)


def get_verse(dt: date) -> ApiResult:
    year = f'{dt.year:04}'
    if not (root := load_year(year)):
        return error(f"Losungen für Jahr {year} nicht vorhanden", 404)
    if (node := root.find(f'./Losungen[Datum="{dt.isoformat()}T00:00:00"]')) is None:
        return error(f"Vers für {dt} nicht gefunden‽", 404)

    prev = dt - oneday
    next = dt + oneday
    result: ApiResult = {n.tag.lower(): n.text for n in node.findall('*')}
    result.update({
        'datum': dt.isoformat(),
        'gestern': url_for_date(prev),
        'morgen': url_for_date(next) if dt < date.today() else None,
        '_links': {
            'self': api_url(dt),
            'prev': api_url(prev),
            'next': api_url(next)
        }
    })
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
