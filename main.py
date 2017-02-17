import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment (loader = jinja2.FileSystemLoader (template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str (self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

  def render (self, template, **kw):
    self.write(self.render_str(template, **kw))

class Blog(db.Model):  #creates an intity
  title = db.StringProperty(required = True) #constraint, won't let you not enter a title
  blog = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True) #set created at current time when blog is created
  #all this in google docs for datastore

class MainPage(Handler):
  def render_base(self, title="", blog="", error=""):

    blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")

    self.render("base.html", title=title, blog=blog, error=error, blogs=blogs)


  def get (self):
    self.render_base()


class NewPost(Handler):
    def render_newpost(self, title="", blog="", error=""):
        self.render("newpost.html", title=title, blog=blog, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get('title')
        blog = self.request.get('blog')

        if title and blog:
            a = Blog(title = title, blog = blog)
            a.put()

            self.redirect("/base/%s" % str(a.key().id()))
        else:
            error = "We need a title and an entry."
            self.render_newpost(title, blog, error)


class ViewPost(Handler):
    def render_front(self, title="", blog="", error="", blogs=""):
        #Having LIMIT 5 here makes no difference, but the variable 'entries' is required.
        entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC")
        self.render("viewpost.html", title = title, blog = blog, error = error, entries=entries, id = id)

	int_id = Blog.get_by_id( int(id) )
    def get(self, id):
        single_entry = Blog.get_by_id(int(id))
        if single_entry:
            self.render("viewpost.html", title = single_entry.title, blog = single_entry.blog)
        else:
            error = "Not right."
            self.render("viewpost.html", error = error)


app = webapp2.WSGIApplication([('/', MainPage),
                                ("/newpost", NewPost),
                                webapp2.Route('/base/<id:\d+>', ViewPost)],
                                debug = True)
