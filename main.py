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

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from models import Losung


root_path = os.path.dirname(__file__)

class DateHandler(webapp.RequestHandler):

    def get(self, y, m, d):
        self.render(Losung(int(y), int(m), int(d)))

    def render(self, model):
        self.response.out.write(template.render(
            os.path.join(root_path, 'losung.html'), model
        ))

class TodayHandler(DateHandler):

    def get(self):
        self.render(Losung())


def main():
    application = webapp.WSGIApplication([
        ('/', TodayHandler),
        (r'^(\d{4})/(\d\d?)/(\d\d?)/$', DateHandler)
    ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
