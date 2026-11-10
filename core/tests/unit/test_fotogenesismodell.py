# -*- coding: utf-8 -*-
"""„Als Modell speichern“ von Foto-Genesis (`Fotogenesismodell`, 31.10.2026) — die Quelle ist der Ordner des Jobs, der Rest ist der Weg von Mesh-Genesis (`Meshgenesistestmodell`).

1. Die Unterklasse liest Ordner, Form und Hautkacheln aus `<Job>/figur/` (`Fotogenesisfigur`), Mesh-Genesis behält seine eigene Quelle (keine Kacheln ohne „Haut b“).
2. Die Kachel-Adresse der Figur (`/api/fotogenesis/<job>/figur/<g>/bild/1001.jpg?t=…`) löst `Texturquelle` auf die Datei auf — nur so kopiert `Modelltexturen.sichern` sie neben
   das Modell (der erste Speicherlauf am 31.10.2026 ließ die Adressen in den Job zeigen); andere Bilder des Jobs nicht.
3. `starten` verlangt `ki.json` im Ordner der Stücke.

Kunstjob unter `ProjektTemp/pruefungen` (`Pruefablage`), `Fotogenesisfigur.ordner` umgelenkt; kein Prozess wird gestartet.
Sabotage-Gegenprobe (31.10.2026): `FIGUR_FOTOGENESIS` in `Texturquelle.pfad` übersprungen → `test_kacheladresse_loest_auf_die_datei_auf` rot.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from core.daten.texturquelle import Texturquelle
from core.dienste.fotogenesisfigur import Fotogenesisfigur
from core.dienste.fotogenesismodell import Fotogenesismodell
from core.dienste.meshgenesistestmodell import Meshgenesistestmodell

from ._pruefablage import Pruefablage


class FotogenesismodellTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.job = Path(tempfile.mkdtemp(prefix='fotogenesismodell_', dir=Pruefablage.wurzel()))
        self.addCleanup(shutil.rmtree, self.job, ignore_errors=True)
        figur = self.job / 'figur'
        (figur / 'form_maennlich' / 'anzeige').mkdir(parents=True)
        (figur / 'form_maennlich' / 'anzeige' / 'netz.npz').write_bytes(b'npz')
        (figur / 'form_maennlich' / 'modell.json').write_text(json.dumps({'figur': {'figur': 'masculine', 'regler': {'a': 0.5}}}), encoding='utf-8')
        (figur / 'haut_maennlich').mkdir()
        for name in ('1001.jpg', '1002.jpg', 'm1.jpg'):
            (figur / 'haut_maennlich' / name).write_bytes(b'\xff\xd8kachel')
        (figur / 'kleider_maennlich').mkdir()
        self.figur = figur
        umlenken = mock.patch.object(Fotogenesisfigur, 'ordner', classmethod(lambda cls, kennung: figur if kennung == 'kunstjob' else None))
        umlenken.start()
        self.addCleanup(umlenken.stop)

    def test_quelle_ist_der_ordner_des_jobs(self):
        self.assertEqual(Fotogenesismodell.geschlecht('kunstjob'), 'maennlich')
        self.assertEqual(Fotogenesismodell.ordner('kunstjob', 'maennlich'), self.figur / 'kleider_maennlich')
        self.assertIsNone(Fotogenesismodell.ordner('kunstjob', 'unbekannt'))
        self.assertEqual(Fotogenesismodell.form('kunstjob', 'maennlich')['figur']['regler'], {'a': 0.5})
        kacheln = Fotogenesismodell.kacheln('kunstjob', 'maennlich')
        self.assertEqual(sorted(kacheln), ['1001', '1002'])
        self.assertTrue(kacheln['1001'].startswith('/api/fotogenesis/kunstjob/figur/maennlich/bild/1001.jpg?t='))
        self.assertIsNone(Meshgenesistestmodell.kacheln('kunstjob', 'maennlich'))

    def test_kacheladresse_loest_auf_die_datei_auf(self):
        adresse = Fotogenesismodell.kacheln('kunstjob', 'maennlich')['1002']
        self.assertEqual(Texturquelle.pfad(adresse), self.figur / 'haut_maennlich' / '1002.jpg')
        self.assertIsNone(Texturquelle.pfad('/api/fotogenesis/kunstjob/figur/maennlich/bild/m1.jpg'))          # nur Kacheln 10??.jpg
        self.assertIsNone(Texturquelle.pfad('/api/fotogenesis/anderer/figur/maennlich/bild/1001.jpg'))

    def test_starten_verlangt_die_stuecke(self):
        antwort, status = Fotogenesismodell.starten('kunstjob', 'maennlich', 'Probe')
        self.assertEqual(status, 404)
        self.assertIn('error', antwort)
