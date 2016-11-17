#!/usr/bin/env python

import os
import jinja2
import webapp2

from models import Sporocilo

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *args, **kwargs):
        return self.response.out.write(*args, **kwargs)

    def render_str(self, template, **params):
        template = jinja_env.get_template(template)
        return template.render(params)

    def render(self, template, **kwargs):
        return self.write(self.render_str(template, **kwargs))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("hello.html")


class RezultatHandler(BaseHandler):
    def get(self):
        params = {}
        return self.render_template("vnos_podatkov.html", params=params)

    def post(self):
        pridobljeno_ime_priimek = self.request.get("ime_priimek")
        if pridobljeno_ime_priimek == "":
            pridobljeno_ime_priimek = "Anonymous"

        pridobljen_email = self.request.get("email")
        if pridobljen_email == "":
            pridobljen_email = "Not specified"

        pridobljeno_sporocilo = self.request.get("tekst")

        sporocilo = Sporocilo(ime_priimek=pridobljeno_ime_priimek, email=pridobljen_email,
                              tekst=pridobljeno_sporocilo)  # pripravi podatek
        sporocilo.put()  # shrani v bazo

        params = {"ime_priimek": pridobljeno_ime_priimek, "tekst": pridobljeno_sporocilo, "email": pridobljen_email}
        return self.render_template("vnos_podatkov.html", params=params)


class SeznamSporocilHandler(BaseHandler):
    def get(self):
        seznam = Sporocilo.query(Sporocilo.izbrisano == False).fetch()
        params={"seznam": seznam}
        return self.render_template("seznam_sporocil.html",params=params)


class ArhivSporocilHandler(BaseHandler):
    def get (self):
        seznam = Sporocilo.query(Sporocilo.izbrisano == True).fetch()
        params = {"seznam": seznam}
        return self.render_template("arhiv_sporocil.html", params=params)


class PosameznoSporociloHandler(BaseHandler):
    """Prikazi posamezno sporocilo glede na id sporocila"""
    def get(self, sporocilo_id):
        arhiv = ""
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        if sporocilo.izbrisano: arhiv = "obnovi"
        else:
            arhiv = "izbrisi"
        params = {"sporocilo": sporocilo, "arhiv": arhiv}
        return self.render_template("posamezno_sporocilo.html", params=params)


class UrediSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("uredi_sporocilo.html", params=params)

    def post(self, sporocilo_id):
        pridobljeno_ime_priimek = self.request.get("ime_priimek")
        if pridobljeno_ime_priimek == "":
            pridobljeno_ime_priimek = "Anonymous"

        pridobljen_email = self.request.get("email")
        if pridobljen_email == "":
            pridobljen_email = "Not specified"

        pridobljeno_sporocilo = self.request.get("tekst")

        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))  # pripravi podatek
        sporocilo.ime_priimek = pridobljeno_ime_priimek
        sporocilo.email = pridobljen_email
        sporocilo.tekst = pridobljeno_sporocilo
        sporocilo.put()  # shrani v bazo
        return self.redirect_to("seznam-sporocil")


class IzbrisiSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("izbrisi_sporocilo.html", params=params)

    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        sporocilo.izbrisano = True
        sporocilo.put()
        return self.redirect_to("seznam-sporocil")


class ObnoviSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("obnovi_sporocilo.html", params=params)

    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        sporocilo.izbrisano = False
        sporocilo.put()
        return self.redirect_to("seznam-sporocil")


class OdstraniSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("odstrani_sporocilo.html", params=params)

    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        sporocilo.key.delete()
        return self.redirect_to("seznam-sporocil")


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/rezultat', RezultatHandler),
    webapp2.Route('/seznam_sporocil', SeznamSporocilHandler, name="seznam-sporocil"),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', PosameznoSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/uredi', UrediSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/izbrisi', IzbrisiSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/obnovi', ObnoviSporociloHandler),
    webapp2.Route('/arhiv_sporocil', ArhivSporocilHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/odstrani', OdstraniSporociloHandler),
], debug=True)