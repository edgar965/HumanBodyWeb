# -*- coding: utf-8 -*-
"""Die Sperre fremder `meta.*`-Werte im Katalog — sie lässt die Formen durch.

WARUM (30.09.2026): `Katalog.entwurf` verwirft seit dem 25.09. jeden `meta.*`-Wert,
der weder zur Vorgabe des Stücks noch zu einer seiner Formen gehört (Edgar: „ich
baue eine Hose für SMPL-X, es wird aber ein Kleid gebaut" — der Client schickte
den Kern der Kleid-Form an die Hose). Die Prüfung sah aber nur Bausteinnamen, nie
`None`: Die Form „Höschen" setzt `meta.upper: None` („kein Oberteil"), und das
wurde mitverworfen. Ergebnis: Die Unterwäsche baute unter dem Namen Höschen einen
BH mit Bund (`torso`-Panels, Bund an der Taille statt an der Hüfte) — fünf rote
LongRunner-Tests, kein Fehler im Log außer einer Warnzeile.

Sabotage-Gegenprobe: in `Katalog._meta_erlaubt` wieder `Formpresets.varianten`
statt `metawerte` lesen -> Fall 1 rot. Die Sperre selbst (Fall 2) wird rot, wenn man
sie ausbaut.
"""

from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.assets()
from GarmentCode.formpresets import Formpresets  # noqa: E402
from GarmentCode.katalog import Katalog  # noqa: E402


class KatalogMetasperreTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _meta(entwurf):
        return {feld: entwurf['meta'][feld]['v'] for feld in ('upper', 'wb', 'bottom')}

    def test_jede_form_setzt_ihre_bausteine_auch_das_keins(self):
        """Mit den Werten einer Form gebaut ist das Stück genau diese Form —
        `None` eingeschlossen (Höschen: kein Oberteil)."""
        for stueck, formen in Formpresets.FORMEN.items():
            for form in formen:
                soll = {feld: form['werte'][pfad] for feld, pfad in
                        (('upper', 'meta.upper'), ('wb', 'meta.wb'), ('bottom', 'meta.bottom'))
                        if pfad in form['werte']}
                ist = self._meta(Katalog.entwurf(stueck, form['werte']))
                for feld, wert in soll.items():
                    self.assertEqual(ist[feld], wert, (stueck, form['schluessel'], feld))

    def test_das_hoeschen_ist_der_slip_ohne_oberteil(self):
        entwurf = Katalog.entwurf('unterwaesche', Formpresets.werte('form_hoeschen'))
        self.assertEqual(self._meta(entwurf),
                         {'upper': None, 'wb': 'StraightWB', 'bottom': 'Briefs'})

    def test_fremde_bausteine_bleiben_draussen(self):
        """Der Fall vom 25.09.: die Kleid-Form an der Hose, `Pants` an der
        Unterwäsche (keine Form dort setzt sie)."""
        hose = Katalog.entwurf('hose', {'meta.bottom': 'PencilSkirt', 'meta.upper': 'FittedShirt'})
        self.assertEqual(self._meta(hose), {'upper': None, 'wb': 'StraightWB', 'bottom': 'Pants'})
        unterwaesche = Katalog.entwurf('unterwaesche', {'meta.bottom': 'Pants'})
        self.assertIsNone(self._meta(unterwaesche)['bottom'])
        # Ein „keins", das keine Form der Hose setzt, bleibt ebenfalls draussen.
        self.assertEqual(self._meta(Katalog.entwurf('hose', {'meta.bottom': None}))['bottom'], 'Pants')
