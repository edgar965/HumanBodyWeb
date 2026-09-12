# -*- coding: utf-8 -*-
u"""Modellvorlagen — die Modellnamen ohne die Szenen.

WARUM (12.09.2026, Befund `testdeckung`): Die Klasse ist der EINE Ort für
eine Liste, die vorher zweimal wörtlich im Code stand — und deren Witz die
Ausnahme ist: `*.json` findet auch `.scene.json`, und eine Szene ist als
Vorgabemodell unbrauchbar. Genau diese Ausnahme prüft hier ein Fall; fällt
sie weg (Sabotage: `if not f.name.endswith(cls.SZENE)` entfernen), wird
`test_szenen_stehen_nicht_in_der_liste` rot.

Die Umleitung des Modellordners wird mitgeprüft (Regel `test-isolation`):
Der Testordner führt genau die hier angelegten Dateien; kämen die echten
Modelle aus `HumanBody/data/models` durch, stünde dort mehr.

Aufruf: python manage.py test core.tests.unit.test_modellvorlagen
"""
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from core.dienste.modellvorlagen import Modellvorlagen
from ._pruefablage import Pruefablage


class ModellvorlagenTest(SimpleTestCase):
    databases = set()

    def _mit_ordner(self, dateien):
        u"""Ein Modellordner mit genau diesen Dateien, als Kontextverwalter."""
        ablage = Pruefablage.ordner('modellvorlagen_')
        ordner = Path(ablage.__enter__())
        self.addCleanup(ablage.__exit__, None, None, None)
        for name in dateien:
            (ordner / name).write_text('{}', encoding='utf-8')
        umschaltung = override_settings(HUMANBODY_MODELS_DIR=str(ordner))
        umschaltung.enable()
        self.addCleanup(umschaltung.disable)
        return ordner

    def test_die_umleitung_greift(self):
        ordner = self._mit_ordner(['Probe.json'])
        self.assertEqual(Modellvorlagen.ordner(), ordner)
        self.assertEqual(Modellvorlagen.namen(), ['Probe'])

    def test_szenen_stehen_nicht_in_der_liste(self):
        self._mit_ordner(['Zimmer.scene.json', 'Female1.json', 'Rig2.json',
                          'Notiz.txt'])
        self.assertEqual(Modellvorlagen.namen(), ['Female1', 'Rig2'])

    def test_die_liste_ist_sortiert(self):
        # Sortiert werden `Path`-Objekte — unter Windows ohne Groß/Klein,
        # also wie der Explorer, nicht wie `sorted(str)` (dort käme `C` zuerst).
        self._mit_ordner(['b.json', 'a.json', 'C.json'])
        self.assertEqual(Modellvorlagen.namen(), ['a', 'b', 'C'])

    def test_ein_fehlender_ordner_gibt_eine_leere_liste(self):
        ordner = self._mit_ordner([])
        fehlend = ordner / 'gibt_es_nicht'
        with override_settings(HUMANBODY_MODELS_DIR=str(fehlend)):
            self.assertEqual(Modellvorlagen.namen(), [])

    def test_die_szenenendung_ist_die_des_studios(self):
        # `Studioprojekte.SZENE` schreibt die Dateien, `Modellvorlagen.SZENE`
        # filtert sie — laufen die beiden auseinander, landen Szenen in der
        # Modellauswahl.
        from core.api.studio_projekt import Studioprojekte
        self.assertEqual(Modellvorlagen.SZENE, Studioprojekte.SZENE)
