import urllib
import cgi

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import os
from google.appengine.ext.webapp import template

class Listem(db.Model):
    """Models an individual Listick entry with an author, content, and date."""
    author = db.StringProperty()
    listName = db.StringProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)


def listick_key(guestbook_name=None):
    """Constructs a Datastore key for a Listick entity with guestbook_name."""
    return db.Key.from_path('Listick', guestbook_name or 'default_guestbook')


class MainPage(webapp.RequestHandler):
    def get(self):
        if users.get_current_user():
            user_name = users.get_current_user().nickname()
        else:
            user_name = "global"
        listick_name = self.request.get('listick_name')
        greetings_query = Listem.all().ancestor(
            listick_key(user_name)).order('-date')
        listicks = greetings_query.fetch(1000)

        specificList = []

        for listick in listicks:
            if listick.listName == listick_name:
                specificList.append(listick)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'listicks': specificList,
            'url': url,
            'url_linktext': url_linktext,
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


class Listick(webapp.RequestHandler):
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each userList is in
        # the same entity group. Queries across the single entity group will be
        # consistent. However, the write rate to a single entity group should
        # be limited to ~1/second.

        user_name = "global"
        listick_name = self.request.get('listick_name')
        
        if users.get_current_user():
            user_name = users.get_current_user().nickname()
            
        userList = Listem(parent=listick_key(user_name))

        if users.get_current_user():
            userList.author = users.get_current_user().nickname()

        userList.content = self.request.get('content')
        userList.listName = listick_name
        userList.put()

        self.redirect('/?' + urllib.urlencode({'listick_name': listick_name}))

class ListLister(webapp.RequestHandler):
    def get(self):
        if users.get_current_user():
            user_name = users.get_current_user().nickname()
        else:
            user_name = "global"
        greetings_query = Listem.all().ancestor( 
            listick_key(user_name)).order('date')
        listicks = greetings_query.fetch(1000)

        listSet = set()
        
        for listick in listicks:
            listSet.add(listick.listName)

        self.response.out.write(listSet)

application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/sign', Listick),
  ('/getLists', ListLister)
], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == '__main__':
    main()