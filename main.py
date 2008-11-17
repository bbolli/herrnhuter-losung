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

import re, datetime, os
import wsgiref.handlers
from xml.etree import cElementTree as ElementTree

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from django.utils.html import escape

root_path = os.path.dirname(__file__)
oneday = datetime.timedelta(days=1)


class Verse(db.Model):
    date = db.DateProperty(required=True)
    year = db.IntegerProperty(required=True)
    verse_text = db.TextProperty(required=True)
    verse_verse = db.StringProperty(required=True)
    teach_text = db.TextProperty(required=True)
    teach_verse = db.StringProperty(required=True)
    sunday_name = db.StringProperty()

    def prepare(self):
        self.yesterday = self.date - oneday
        if self.date < datetime.date.today():
            self.tomorrow = self.date + oneday
        return self


class DateHandler(webapp.RequestHandler):

    def get(self, y, m, d):
        self.render(datetime.date(int(y), int(m), int(d)))

    def render(self, date):
        verses = Verse.all().filter('date =', date).fetch(1)
        if len(verses) != 1:
            self.error(404)
            self.response.out.write('Not found')
            return
        self.response.out.write(template.render(
            os.path.join(root_path, 'verse.html'), {'verse': verses[0].prepare()}
        ))


class TodayHandler(DateHandler):

    def get(self):
        self.render(datetime.date.today())


class LoadHandler(webapp.RequestHandler):
    file_template = os.path.join(root_path, 'lib', 'losung_free_%s.xml')

    def get(self, year):
        old = Verse.all().filter('year =', year)
        for verse in old:
            verse.delete()
        self.response.out.write('<code>%d old verses deleted.</code><br>\n' % old.count())
        fn = self.file_template % year
        verses = ElementTree.parse(fn)
        for e in verses.findall('Losungen'):
            d = e.findtext('Datum')     # assumes ISO format
            y = int(d[:4])
            Verse(
                date = datetime.date(y, int(d[5:7]), int(d[8:10])), year = y,
                verse_text = _textverse(e.findtext('Losungstext')),
                verse_verse = e.findtext('Losungsvers'),
                teach_text = _textverse(e.findtext('Lehrtext')),
                teach_verse = e.findtext('Lehrtextvers'),
                sunday_name = e.findtext('Sonntag')
            ).put()
        self.response.out.write('<code>File %s loaded.</code>' % fn)

speak_re = re.compile(r'/(.+?:)/')
strong_re = re.compile(r'#(.+?)#')

def _textverse(t):
    t = escape(t)
    t = speak_re.sub(r'<em>\1</em>', t)
    t = strong_re.sub(r'<strong>\1</strong>', t)
    return t


def main():
    application = webapp.WSGIApplication([
        ('/', TodayHandler),
        (r'/(\d{4})[/-](\d\d?)[/-](\d\d?)$', DateHandler),
        (r'/load/(\d{4})', LoadHandler),
    ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
