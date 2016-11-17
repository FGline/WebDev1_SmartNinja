from google.appengine.ext import ndb

class Sporocilo(ndb.Model):
    ime_priimek = ndb.StringProperty()
    email = ndb.StringProperty()
    tekst = ndb.TextProperty()
    nastanek = ndb.DateTimeProperty(auto_now_add =True)
    izbrisano = ndb.BooleanProperty(default=False)