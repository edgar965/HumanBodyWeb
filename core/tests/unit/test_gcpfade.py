# -*- coding: utf-8 -*-
u"""Zwei Quellen für denselben Ort — und sie müssen gleich bleiben.

WARUM (08.09.2026, Umzug der Kleidungsdienste nach `Assets/`)
=============================================================
`Assets/GarmentCode/pfade.Gcpfade` rechnet seine Verzeichnisse aus der
eigenen Lage; `ui/settings/pfade.py` führt dieselben Orte als
`ASSETS_ROOT` und `HUMANBODY_DATA_DIR` weiter. Das ist bewusst so — das
Paket soll ohne Django laufen, die Settings behalten ihre Namen für
Language-Server, `local_settings` und die Nur-Lesen-Prüfung.

Zwei Quellen für denselben Ort laufen auseinander, ohne dass es jemand
merkt: Wer `HUMANBODY_DATA_DIR` in `local_settings` umbiegt, misst danach
an einem anderen Netz, als er drapiert. Dieselbe Prüfung hält seit dem
07.09.2026 `Mhpfade` gegen `MAKEHUMAN_ROOT` (`test_mhpfade.py`).

Und die `.parents`-Kette selbst wird geprüft: Sie ist genau die Falle,
die beim Verschieben einer Datei um eine Ebene stumm woanders hinzeigt
(`~/.claude/rules/projektpfade.md`).
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from GarmentCode.pfade import Gcpfade


class GcpfadeGegenSettings(SimpleTestCase):

    databases = []

    def test_assets_ist_dieselbe_wurzel(self):
        self.assertEqual(Gcpfade.assets(), Path(str(settings.ASSETS_ROOT)))

    def test_arbeitswurzel_ist_tools_root(self):
        self.assertEqual(Gcpfade.wurzel(), Path(str(settings.TOOLS_ROOT)))

    def test_humanbody_daten_weiblich(self):
        self.assertEqual(Gcpfade.humanbody_daten('female'),
                         Path(str(settings.HUMANBODY_DATA_DIR)))

    def test_humanbody_daten_maennlich(self):
        u"""Der männliche Ordner heisst `humanBody_male` — bis zum
        07.09.2026 wurde er durch Anhängen von `_male` an die Zeichenkette
        gebildet. Das steht jetzt an einer Stelle statt an dreien."""
        self.assertEqual(Gcpfade.humanbody_daten('male'),
                         Path(str(settings.HUMANBODY_DATA_DIR) + '_male'))

    def test_das_paket_liegt_unter_assets(self):
        self.assertEqual(Gcpfade.PAKET,
                         Path(str(settings.ASSETS_ROOT)) / 'GarmentCode')

    def test_messreihen_liegen_neben_dem_paket(self):
        u"""Die YAML-Reihen der Hilfeseite. Fehlt der Ordner, zeigt die
        Seite eine leere Tabelle — und die liest sich wie „alles gut"."""
        self.assertTrue(Gcpfade.messreihen().is_dir(),
                        u'%s fehlt' % Gcpfade.messreihen())

    def test_die_kette_wuerde_eine_falsche_ebene_melden(self):
        u"""GEGENPROBE: Zeigt die Wurzel woanders hin, muss `wurzel()`
        werfen statt still ein leeres Verzeichnis zu liefern."""
        class Verschoben(Gcpfade):
            WURZEL = Path(str(settings.ASSETS_ROOT))   # eine Ebene zu tief

        with self.assertRaises(RuntimeError):
            Verschoben.wurzel()
