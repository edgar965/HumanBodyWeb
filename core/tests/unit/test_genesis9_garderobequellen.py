# -*- coding: utf-8 -*-
u"""Bestandsschluessel der Garderobe-Ablage je Stueck (`G9garderobequellen`, 09.10.2026).

Edgar: „warum dauert der Modell Import von Blender so lange?" Der Schritt „Stuecke" eines Imports mit 10 Stuecken
brauchte 1.593 s. 676 s davon las die Garderobe nach jedem geschriebenen Stueck 149 Eintraege neu: Alle selbst
gebauten Stuecke liegen in EINEM Ordner (`Clothing/EIGEN`, ebenso `GC` und `MB`), und dieser Ordner stand im
Schluessel jedes einzelnen — ein neues Stueck veraltete die Ablage aller anderen.

Kunstdaten im Ordner `_wegwerf`, die eigene Bibliothek per `G9_EIGENE_BIBLIOTHEK` umgelenkt:

1. Ein neues Stueck im selben Herstellerordner aendert den Schluessel der anderen NICHT (EIGEN, GC und MB).
2. Seine eigenen Dateien aendern ihn: eine neue Vorschau, eine Variante mit dem Namensanfang (`<Name> f2`).
3. Ein anderer Name mit gleichem Anfang ohne Trenner (`Alphabet` zu `Alpha`) gehoert nicht dazu.
4. Ein Ordner, der kein Herstellerordner ist (Produktordner mit Presets), schluesselt weiter ueber den GANZEN
   Ordner.

Sabotage: `gemeinsam` immer False liefern -> Fall 1 rot; den Trenner (`' '`/`'.'`) weglassen -> Fall 3 rot;
`gemeinsam` immer True -> Fall 4 rot.

Gelaufen am 09.10.2026 (Gesamtlauf auf Ansage): gruen. Die Gegenprobe steht in
`ProjektTemp/_wegwerf/quellen_probe.py` (gelaufen).
"""
import os
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.garderobeeintrag import G9garderobeeintrag
from Genesis9.listenablage import G9listenablage
from Genesis9.pfade import G9pfade

WEGWERF = Path(__file__).resolve().parent / '_wegwerf'


def schreiben(pfad, inhalt='{}'):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(inhalt, encoding='utf-8')


class Garderobequellen(SimpleTestCase):

    def _schluessel(self, datei):
        return G9listenablage.schluessel(G9garderobeeintrag.quellen(datei))

    def _eigene_bibliothek(self):
        WEGWERF.mkdir(exist_ok=True)
        ordner = tempfile.TemporaryDirectory(dir=WEGWERF)
        self.addCleanup(ordner.cleanup)
        eigen = Path(ordner.name) / 'bibliothek'
        patch = mock.patch.dict(os.environ, {G9pfade.UMGEBUNG_EIGENE: str(eigen)})
        patch.start()
        self.addCleanup(patch.stop)
        return eigen / 'People' / 'Genesis 9' / 'Clothing'

    def test_1_ein_neues_stueck_aendert_den_schluessel_der_anderen_nicht(self):
        kleidung = self._eigene_bibliothek()
        for hersteller in ('EIGEN', 'GC', 'MB'):
            alpha = kleidung / hersteller / 'Alpha Hemd.duf'
            schreiben(alpha)
            schreiben(alpha.with_suffix('.png'), 'x')
            vorher = self._schluessel(alpha)
            schreiben(kleidung / hersteller / 'Gamma Rock.duf')
            schreiben(kleidung / hersteller / 'Gamma Rock.png', 'x')
            self.assertEqual(self._schluessel(alpha), vorher, hersteller)

    def test_2_die_eigenen_dateien_aendern_ihn(self):
        kleidung = self._eigene_bibliothek()
        alpha = kleidung / 'EIGEN' / 'Alpha Hemd.duf'
        schreiben(alpha)
        schreiben(alpha.with_suffix('.png'), 'x')
        vorher = self._schluessel(alpha)
        schreiben(alpha.with_suffix('.png'), 'xxxx')
        nach_vorschau = self._schluessel(alpha)
        self.assertNotEqual(nach_vorschau, vorher)
        schreiben(kleidung / 'EIGEN' / 'Alpha Hemd f2.duf')
        self.assertNotEqual(self._schluessel(alpha), nach_vorschau)

    def test_3_gleicher_anfang_ohne_trenner_gehoert_nicht_dazu(self):
        kleidung = self._eigene_bibliothek()
        alpha = kleidung / 'EIGEN' / 'Alpha Hemd.duf'
        schreiben(alpha)
        schreiben(kleidung / 'EIGEN' / 'Alpha Hemdchen.duf')
        schreiben(kleidung / 'EIGEN' / 'Alpha Hemd f2.duf')
        namen = [p.name for p in G9garderobeeintrag.quellen(alpha) if p.is_file()]
        self.assertEqual(namen, ['Alpha Hemd f2.duf', 'Alpha Hemd.duf'])

    def test_4_ein_produktordner_schluesselt_ueber_den_ganzen_ordner(self):
        kleidung = self._eigene_bibliothek()
        hemd = kleidung / 'Mein Produkt' / 'Hemd.duf'
        schreiben(hemd)
        vorher = self._schluessel(hemd)
        # kein Namensanfang, gehoert aber zum Produkt
        schreiben(kleidung / 'Mein Produkt' / 'Anderes Preset.duf')
        self.assertNotEqual(self._schluessel(hemd), vorher)
