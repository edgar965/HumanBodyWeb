# -*- coding: utf-8 -*-
u"""`Koerperabstand.radial` und `.gerichtet` — und was sie unterscheidet.

WARUM DIESER TEST EXISTIERT (31.08.2026)
----------------------------------------
`_push_outside_body` stand in drei Dateien mit drei verschiedenen
Parameterlisten, und sieben Module in HumanBodyWeb importierten den Namen
— mal aus `humanbody_core.cloth`, mal aus `GarmentFitter.fitter`. Ein
Name mit Unterstrich, den sieben fremde Module holen, ist nicht privat,
sondern unbenannt.

Zusammengelegt sind die Verfahren NICHT: Sie rechnen wirklich
verschieden. Sie heißen jetzt nur so, dass man beim Lesen merkt, welches
man vor sich hat. Dieser Test hält den Unterschied fest — sonst
verschwindet er beim nächsten Aufräumen still, und ein eingeklemmter
Vertex bleibt fortan im Körper stecken statt zur Seite auszuweichen.

Der entscheidende Fall ist die ENTARTETE RICHTUNG: Stoff- und
Körperpunkt fallen zusammen, es gibt kein „nach außen" mehr.

    radial     weicht waagerecht von der Körperachse weg aus
    gerichtet  setzt die Länge auf 1,0 — der Punkt bleibt praktisch liegen

Aufruf:  python manage.py test core.tests.unit.test_koerperabstand
"""
import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.koerperabstand import Koerperabstand  # noqa: E402


class EntarteteRichtungTest(SimpleTestCase):
    u"""Der Fall, in dem sich die beiden Verfahren wirklich unterscheiden."""

    #: Ein Körperpunkt, seitlich von der Achse (x=0,3) — damit „weg von der
    #: Achse" eine Richtung hat.
    KOERPER = np.array([[0.3, 0.0, 1.0]])

    def test_radial_weicht_zur_seite_aus(self):
        u"""Stoffpunkt liegt EXAKT auf dem Körperpunkt: keine Richtung."""
        stoff = self.KOERPER.copy()
        raus = Koerperabstand.radial(stoff, self.KOERPER, mindestabstand=0.01)
        self.assertGreater(float(np.linalg.norm(raus - stoff)), 0.0,
                           'radial hat den eingeklemmten Punkt nicht bewegt')

    def test_gerichtet_laesst_ihn_praktisch_liegen(self):
        u"""Dasselbe mit `gerichtet` — hier bleibt der Punkt stecken.

        Das ist kein Fehler dieses Tests, sondern der belegte Unterschied.
        Wer die beiden Verfahren eines Tages zusammenlegt, muss diese
        Entscheidung treffen und sieht hier, dass es eine gibt.
        """
        stoff = self.KOERPER.copy()
        raus = Koerperabstand.gerichtet(stoff, self.KOERPER,
                                        mindestabstand=0.01)
        self.assertAlmostEqual(float(np.linalg.norm(raus - stoff)), 0.0,
                               places=9)


class RadialTest(SimpleTestCase):

    KOERPER = np.array([[0.0, 0.0, 0.0]])

    def test_punkt_im_koerper_kommt_auf_den_mindestabstand(self):
        stoff = np.array([[0.001, 0.0, 0.0]])
        raus = Koerperabstand.radial(stoff, self.KOERPER, mindestabstand=0.01)
        self.assertAlmostEqual(float(np.linalg.norm(raus[0])), 0.01, places=9)

    def test_punkt_weit_draussen_bleibt_unangetastet(self):
        stoff = np.array([[0.5, 0.0, 0.0]])
        raus = Koerperabstand.radial(stoff, self.KOERPER, mindestabstand=0.01)
        np.testing.assert_allclose(raus, stoff, atol=0)

    def test_die_richtung_bleibt_erhalten(self):
        u"""Geschoben wird auf der Verbindungslinie, nicht irgendwohin."""
        stoff = np.array([[0.002, 0.002, 0.0]])
        raus = Koerperabstand.radial(stoff, self.KOERPER, mindestabstand=0.02)
        self.assertAlmostEqual(float(raus[0, 0]), float(raus[0, 1]), places=9)
        self.assertAlmostEqual(float(raus[0, 2]), 0.0, places=9)


class GerichtetTest(SimpleTestCase):

    KOERPER = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    NORMALEN = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])

    def test_mit_normalen_wird_nur_das_fehlende_stueck_geschoben(self):
        u"""Defizit statt Sollwert — sonst werden gewölbte Stellen flach.

        Zwei Punkte, verschieden tief drin: Nach dem Schieben müssen
        beide GENAU auf dem Mindestabstand liegen, ihre Differenz
        zueinander bleibt dabei erhalten, weil jeder um sein eigenes
        Defizit steigt.
        """
        stoff = np.array([[0.0, 0.0, 0.001], [1.0, 0.0, 0.004]])
        raus = Koerperabstand.gerichtet(stoff, self.KOERPER,
                                        mindestabstand=0.01,
                                        normalen=self.NORMALEN)
        np.testing.assert_allclose(raus[:, 2], [0.01, 0.01], atol=1e-9)
        # x und y bleiben unberührt — geschoben wird nur entlang z.
        np.testing.assert_allclose(raus[:, :2], stoff[:, :2], atol=0)

    def test_mit_normalen_bleibt_ein_punkt_ueber_der_marke_liegen(self):
        stoff = np.array([[0.0, 0.0, 0.5]])
        raus = Koerperabstand.gerichtet(stoff, self.KOERPER,
                                        mindestabstand=0.01,
                                        normalen=self.NORMALEN)
        np.testing.assert_allclose(raus, stoff, atol=0)

    def test_mit_normalen_zaehlt_der_abstand_ENTLANG_der_normale(self):
        u"""Weit weg in x, aber knapp über der Fläche: gilt als zu nah.

        Das ist der Unterschied zum euklidischen Maß — ein Punkt 40 cm
        neben dem Körper, aber nur 1 mm über seiner Oberfläche, steckt in
        der Fläche und muss heraus.
        """
        stoff = np.array([[0.5, 0.0, 0.001]])
        raus = Koerperabstand.gerichtet(stoff, self.KOERPER,
                                        mindestabstand=0.01,
                                        normalen=self.NORMALEN)
        self.assertAlmostEqual(float(raus[0, 2]), 0.01, places=9)

    def test_ohne_normalen_wird_radial_geschoben(self):
        stoff = np.array([[0.001, 0.0, 0.0]])
        raus = Koerperabstand.gerichtet(stoff, np.array([[0.0, 0.0, 0.0]]),
                                        mindestabstand=0.01)
        self.assertAlmostEqual(float(np.linalg.norm(raus[0])), 0.01, places=9)


class EinzigeFassungTest(SimpleTestCase):
    u"""Der Name darf nicht wieder in die Bibliotheken zurückwandern."""

    def test_kein_push_outside_body_mehr_in_den_bibliotheken(self):
        from pathlib import Path

        import humanbody_core

        wurzel = Path(humanbody_core.__file__).parent.parent
        treffer = []
        for unter in ('humanbody_core', 'assetCreator'):
            for pfad in (wurzel / unter).rglob('*.py'):
                if '__pycache__' in pfad.parts or 'PhotoToTexture' in pfad.parts:
                    continue
                for nummer, zeile in enumerate(
                        pfad.read_text(encoding='utf-8',
                                       errors='replace').splitlines(), 1):
                    if zeile.startswith('def _push_outside_body('):
                        treffer.append('%s:%d' % (pfad.name, nummer))
        self.assertEqual(treffer, [],
                         '`_push_outside_body` steht wieder in den Bibliotheken')
