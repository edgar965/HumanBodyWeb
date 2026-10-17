# -*- coding: utf-8 -*-
u"""Edgars Ordner für die Daz-Posen (`G9poseneinteilung`, 17.10.2026).

Edgar: „mache alle vorhandenen Poses aus allen Modellen in Ordner bei Poses (auch
valkyrie …) … Funktionen zum Verschieben, Löschen der Poses in andere Ordner …,
Löschen, Umbenennen der Ordner auch". Die Daz-Bibliothek wird nie beschrieben
(`G9pfade`); die Einteilung liegt als JSON daneben — hier in einem Wegwerfordner.
Zusagen:

1. Ohne Datei steht jede Pose in ihrem Bibliotheksordner (`gruppe` als Pfad);
   Ausdrücke unter `Characters` und Formpresets stehen nicht im Reiter.
2. Verschieben in einen neuen Ordner merkt die Zuordnung; zurück in die Vorgabe räumt sie weg.
3. Ordner umbenennen nimmt jede Pose darunter mit — auch eine, die nur per Vorgabe dort stand —
   und weist einen vorhandenen Namen ab.
4. Ordner löschen blendet jede Pose darunter aus; die Eigenschaften-Liste (`anwenden`) lässt sie weg.
5. Ein untauglicher Pfad wird abgewiesen, ohne die Datei anzufassen.

Gegen den laufenden Server von Hand geprüft (17.10.2026, `ProjektTemp/_wegwerf/posenbaum_server.py`).
"""
import shutil
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.poseneinteilung import G9poseneinteilung

from core.projekt_temp import ProjektTemp

VALKYRIE = r'People\Genesis 9\Poses\Daz Originals\Space Valkyrie Poses'
KATALOG = {
    'svp_sit': {'id': 'svp_sit', 'name': 'Sit', 'art': 'pose', 'gruppe': 'Space Valkyrie Poses · Base',
                'datei': VALKYRIE + r'\Base\CDI SVP Sit.duf'},
    'svp_stand': {'id': 'svp_stand', 'name': 'Stand', 'art': 'pose', 'gruppe': 'Space Valkyrie Poses · Base',
                  'datei': VALKYRIE + r'\Base\CDI SVP Stand.duf'},
    'svp_fear': {'id': 'svp_fear', 'name': 'Fear', 'art': 'ausdruck', 'gruppe': 'Space Valkyrie Poses',
                 'datei': VALKYRIE + r'\Expressions\CDI SVE Fear.duf'},
    'ursula_lacht': {'id': 'ursula_lacht', 'name': 'Lacht', 'art': 'ausdruck', 'gruppe': 'Ursula 9',
                     'datei': r'People\Genesis 9\Characters\P3D\Ursula 9\Expressions\Lacht.duf'},
    'ursula_body': {'id': 'ursula_body', 'name': 'Ursula Body', 'art': 'form', 'gruppe': 'Ursula 9',
                    'datei': r'People\Genesis 9\Characters\P3D\Ursula 9\Ursula Body Apply.duf'},
}


class Genesis9PoseneinteilungTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self._temp = ProjektTemp.ordner(prefix='g9posen_')
        self.datei = Path(self._temp) / 'posen_einteilung.json'
        self._patch = mock.patch.object(G9poseneinteilung, 'datei', classmethod(lambda cls: self.datei))
        self._patch.start()

    def tearDown(self):
        self._patch.stop()
        shutil.rmtree(self._temp, ignore_errors=True)

    def _ordner(self):
        return {e['id']: o for o, e in G9poseneinteilung.eintraege(KATALOG)}

    def test_vorgabe_ist_der_bibliotheksordner(self):
        self.assertEqual(self._ordner(), {'svp_sit': 'Space Valkyrie Poses/Base',
                                          'svp_stand': 'Space Valkyrie Poses/Base',
                                          'svp_fear': 'Space Valkyrie Poses'})
        self.assertFalse(self.datei.exists())

    def test_verschieben_und_zurueck(self):
        G9poseneinteilung.verschieben(KATALOG['svp_sit'], 'Kampf / Sitzen')
        self.assertEqual(self._ordner()['svp_sit'], 'Kampf/Sitzen')
        self.assertEqual(G9poseneinteilung.laden()['zuordnung'], {'svp_sit': 'Kampf/Sitzen'})
        G9poseneinteilung.verschieben(KATALOG['svp_sit'], 'Space Valkyrie Poses/Base')
        self.assertEqual(G9poseneinteilung.laden()['zuordnung'], {})

    def test_ordner_umbenennen_nimmt_alle_darunter_mit(self):
        G9poseneinteilung.ordner_anlegen('Space Valkyrie Poses/Leer')
        neu = G9poseneinteilung.ordner_umbenennen('Space Valkyrie Poses', 'Valkyrie', KATALOG)
        self.assertEqual(neu, 'Valkyrie')
        self.assertEqual(self._ordner(), {'svp_sit': 'Valkyrie/Base', 'svp_stand': 'Valkyrie/Base',
                                          'svp_fear': 'Valkyrie'})
        self.assertEqual(G9poseneinteilung.laden()['ordner'], ['Valkyrie/Leer'])
        G9poseneinteilung.ordner_anlegen('Kampf')
        with self.assertRaises(ValueError):
            G9poseneinteilung.ordner_umbenennen('Valkyrie', 'Kampf', KATALOG)

    def test_ordner_loeschen_blendet_aus(self):
        self.assertEqual(G9poseneinteilung.ordner_loeschen('Space Valkyrie Poses/Base', KATALOG), 2)
        self.assertEqual(self._ordner(), {'svp_fear': 'Space Valkyrie Poses'})
        gruppen = [{'gruppe': 'Space Valkyrie Poses · Base',
                    'eintraege': [{'id': 'svp_sit', 'name': 'Sit'}, {'id': 'svp_stand', 'name': 'Stand'}]}]
        self.assertEqual(G9poseneinteilung.anwenden(gruppen, KATALOG), [])

    def test_untaugliche_pfade(self):
        for pfad in ('', '   ', '/', 'a\\b', 'x' * 61, 'a/\x07'):
            with self.assertRaises(ValueError, msg=repr(pfad)):
                G9poseneinteilung.ordner_anlegen(pfad)
        self.assertFalse(self.datei.exists())
