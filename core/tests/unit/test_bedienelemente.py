# -*- coding: utf-8 -*-
u"""Kein Knopf ohne Hörer — auf keiner Seite.

DER AUFTRAG (Edgar, 09.09.2026): „das ist echt mühsam, ein bug nach dem
Anderen, kannst du nicht alles durchtesten, jeden Button und testen ob der das
tut was er soll?"

Vollständig beantworten lässt sich das nicht mechanisch: Ob ein Knopf das
RICHTIGE tut, weiss nur, wer die Sache kennt. Ob er ÜBERHAUPT etwas tut, ist
dagegen am Quelltext zu entscheiden — und genau daran lag der Befund desselben
Tages: Der Farbwähler der Schuhe schrieb ins Material und sonst nirgends.

Der Lauf über alle zwanzig Seiten dauert 0,40 s und findet 184 Bedienelemente
allein auf der Szene-Seite. Was er meldet, steht unten als AUSNAHMEN — mit
Datum und Grund. Ein NEUES stummes Element macht diesen Test rot.

Die Prüflogik steht in `_bedienelemente.py`; ihre drei Fehlalarm-Filter sind
dort belegt.
"""
from django.conf import settings
from django.test import SimpleTestCase

from ._bedienelemente import Bedienelemente

WURZEL = settings.BASE_DIR
BEISPIEL = WURZEL.joinpath('core', 'tests', 'unit', 'beispiele', 'bedienung')

# Bekannte stumme Bedienelemente: Kennung → warum sie (noch) dastehen.
#
# KEIN FREIBRIEF. Wer hier etwas einträgt, hat es angesehen; wer eines
# behebt, nimmt es heraus — `test_die_ausnahmeliste_ist_aktuell` hält beides
# fest, damit die Liste nicht zum Deckel über neuen Befunden wird.
AUSNAHMEN = {
    'smooth-sigma': u'Szene, Reiter Animation: Der Glättungsbereich hat nie '
                    u'einen Hörer bekommen (gefunden 09.09.2026). Die '
                    u'Funktion gibt es im BVH-Studio '
                    u'(`bvh_studio/werkzeug_glaettung.js`, dort '
                    u'`tool-smooth-*`), in der Szene nicht.',
    'smooth-apply': u'dasselbe — der Knopf „Smooth" tut nichts.',
    'smooth-reset': u'dasselbe — der Knopf „Reset" tut nichts.',
    'tool-ground-method': u'BVH-Studio: Auswahlfeld „Bodenmethode" ohne '
                          u'Leser (gefunden 09.09.2026).',
}


def _pruefer(wurzel=None):
    return Bedienelemente(wurzel or WURZEL)


class KunstbeispielTest(SimpleTestCase):
    u"""Die Gegenprobe: Findet der Prüfer das Tote — und schweigt er über die
    drei Wege, ein Element wirklich zu bedienen?

    Ohne diesen Fall wäre nicht zu unterscheiden, ob eine leere Befundliste
    „alles in Ordnung" heisst oder „der Prüfer ist blind geworden".
    """

    databases = []

    def setUp(self):
        self.stumm = [k for k, _, _ in _pruefer(BEISPIEL).ohne_hoerer('probe.html')]

    def test_der_tote_knopf_wird_gefunden(self):
        self.assertIn('probe-ohne-hoerer', self.stumm)

    def test_ein_woertlicher_hoerer_zaehlt(self):
        self.assertNotIn('probe-mit-hoerer', self.stumm)

    def test_ein_delegierter_hoerer_ueber_die_klasse_zaehlt(self):
        self.assertNotIn('probe-ueber-klasse', self.stumm)

    def test_eine_zusammengesetzte_kennung_zaehlt(self):
        u"""`${vorsilbe}-rauheit` — sonst meldete der Prüfer allein auf der
        Szene-Seite über sechzig lebende Regler als tot."""
        self.assertNotIn('probe-mit-vorsilbe-rauheit', self.stumm)

    def test_ein_formularfeld_braucht_kein_skript(self):
        u"""`name="…"` wird serverseitig im POST gelesen."""
        self.assertNotIn('probe-pfad', self.stumm)

    def test_genau_ein_befund(self):
        self.assertEqual(len(self.stumm), 1, self.stumm)


class AlleSeitenTest(SimpleTestCase):

    databases = []

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        pruefer = _pruefer()
        cls.befunde = {}
        for seite in pruefer.seiten():
            for kennung, art, vorlage in pruefer.ohne_hoerer(seite):
                cls.befunde[kennung] = (art, seite, vorlage)

    def test_kein_neues_stummes_bedienelement(self):
        neu = {k: v for k, v in self.befunde.items() if k not in AUSNAHMEN}
        self.assertEqual(
            neu, {},
            u'Bedienelemente ohne jeden Hörer — entweder verdrahten oder mit '
            u'Begründung in AUSNAHMEN eintragen: %s' % sorted(neu))

    def test_die_ausnahmeliste_ist_aktuell(self):
        u"""Was behoben ist, gehört aus der Liste heraus.

        Eine Ausnahmeliste, die mehr führt als es Befunde gibt, deckt
        irgendwann einen echten zu — dieselbe Sorte Falle wie ein rot
        stehen gelassener Konformitätstest.
        """
        erledigt = [k for k in AUSNAHMEN if k not in self.befunde]
        self.assertEqual(erledigt, [],
                         u'nicht mehr stumm, also aus AUSNAHMEN nehmen: %s'
                         % erledigt)

    def test_die_szene_seite_wird_wirklich_geprueft(self):
        u"""Ein Prüfer, der nichts findet, weil er nichts liest, meldet grün.

        Genau das ist am 07.09.2026 beim `assetCreator`-Umzug beinahe
        passiert (`Humanbodybaum.fehlende()` gibt es deswegen).
        """
        pruefer = _pruefer()
        namen = pruefer.kette('scene_config.html')
        self.assertGreater(len(namen), 10, namen)
        self.assertGreater(len(pruefer.elemente(namen)), 150)
