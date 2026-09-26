# -*- coding: utf-8 -*-
u"""`Netzstufenwahl` — der Keks `netzstufen` (Strg+Alt+H) wählt die Stufe je Browser.

1. `aus_cookies`: 1–3 gelten, alles andere (fehlt, leer, 0, 4, Text) ist None.
2. Die Middleware setzt die Wahl für die Dauer der Anfrage und nimmt sie
   danach zurück — sonst gälte sie unter Daphne (ein Faden) für den nächsten.
3. `Netzqualitaet.stufen_browser()` nimmt die Wahl vor der Einstellung.
4. Drahtformat: Middleware eingetragen; der Kanal liest `scope['cookies']`
   und gibt `stufen=` weiter; `ui/asgi.py` hängt die `CookieMiddleware` an;
   beide Figurseiten richten die Taste ein.

Sabotage-Gegenprobe: `finally: reset` weg → Fall 2 rot („danach None").
"""
from pathlib import Path

from django.conf import settings
from django.test import RequestFactory, SimpleTestCase

from core.dienste.netzqualitaet import Netzqualitaet
from core.dienste.netzstufenwahl import Netzstufenwahl


class DerKeks(SimpleTestCase):

    def test_nur_eins_bis_drei_gelten(self):
        for keks, soll in ((None, None), ({}, None), ({'netzstufen': ''}, None),
                           ({'netzstufen': '3'}, 3), ({'netzstufen': '1'}, 1),
                           ({'netzstufen': '0'}, None), ({'netzstufen': '4'}, None),
                           ({'netzstufen': 'x'}, None), ({'andere': '3'}, None)):
            self.assertEqual(Netzstufenwahl.aus_cookies(keks), soll, keks)


class DieMiddleware(SimpleTestCase):

    def test_wahl_gilt_waehrend_der_anfrage_und_danach_nicht(self):
        gesehen = []

        def ansicht(request):
            gesehen.append(Netzstufenwahl.gewaehlt())
            return 'antwort'

        anfrage = RequestFactory().get('/api/character/mesh/')
        anfrage.COOKIES['netzstufen'] = '3'
        self.assertEqual(Netzstufenwahl(ansicht)(anfrage), 'antwort')
        self.assertEqual(gesehen, [3])
        self.assertIsNone(Netzstufenwahl.gewaehlt(), 'danach None')

    def test_wahl_geht_vor_der_einstellung(self):
        alt = Netzqualitaet._werte
        Netzqualitaet._werte = {'unterteilung_browser': 2, 'unterteilung_film': 3,
                                'haut_verschiebung': True}
        try:
            gesehen = []
            Netzstufenwahl(lambda r: gesehen.append(Netzqualitaet.stufen_browser()))(
                RequestFactory().get('/'))
            self.assertEqual(gesehen, [2], 'ohne Keks die Einstellung')
            marke = Netzstufenwahl._gewaehlt.set(3)
            try:
                self.assertEqual(Netzqualitaet.stufen_browser(), 3)
                self.assertEqual(Netzqualitaet.stufen_film(), 3, 'der Film bleibt')
            finally:
                Netzstufenwahl._gewaehlt.reset(marke)
        finally:
            Netzqualitaet._werte = alt


class DasDrahtformat(SimpleTestCase):

    def _quelle(self, *teile):
        return Path(settings.BASE_DIR).joinpath(*teile).read_text(encoding='utf-8')

    def test_middleware_eingetragen(self):
        self.assertIn('core.dienste.netzstufenwahl.Netzstufenwahl', settings.MIDDLEWARE)

    def test_kanal_liest_den_keks_und_gibt_die_stufe_weiter(self):
        kanal = self._quelle('core', 'consumers.py')
        self.assertIn("Netzstufenwahl.aus_cookies(self.scope.get('cookies'))", kanal)
        self.assertEqual(kanal.count('stufen=self._stufen'), 2,
                         'Vorladen UND Nachladen je Geschlecht')
        self.assertIn('CookieMiddleware(URLRouter(', self._quelle('ui', 'asgi.py'))

    def test_beide_figurseiten_richten_die_taste_ein(self):
        for teile in (('static', 'viewer', 'viewer', 'index.js'),
                      ('static', 'viewer', 'charakter', 'boot.js')):
            self.assertIn('Netzstufe.einrichten(', self._quelle(*teile), teile)
