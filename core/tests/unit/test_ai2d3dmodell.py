# -*- coding: utf-8 -*-
"""„Als Modell speichern“ von 2d-3d-AI (`Ai2d3dmodell`, 31.10.2026) — die Quelle ist der Ordner des Jobs, der Rest ist der Weg von Mesh3D-AI (`Mesh3daitestmodell`).

1. Die Unterklasse liest Ordner, Form und Hautkacheln aus `<Job>/figur/` (`Ai2d3dfigur`), Mesh3D-AI behält seine eigene Quelle (keine Kacheln ohne „Haut b“).
2. Die Kachel-Adresse der Figur (`/api/2d3dai/<job>/figur/<g>/bild/1001.jpg?t=…`) löst `Texturquelle` auf die Datei auf — nur so kopiert `Modelltexturen.sichern` sie neben
   das Modell (der erste Speicherlauf am 31.10.2026 ließ die Adressen in den Job zeigen); andere Bilder des Jobs nicht.
3. `starten` verlangt `ki.json` im Ordner der Stücke.

Kunstjob unter `ProjektTemp/pruefungen` (`Pruefablage`), `Ai2d3dfigur.ordner` umgelenkt; kein Prozess wird gestartet.
Sabotage-Gegenprobe (31.10.2026): `FIGUR_2D3DAI` in `Texturquelle.pfad` übersprungen → `test_kacheladresse_loest_auf_die_datei_auf` rot.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from core.daten.texturquelle import Texturquelle
from core.dienste.ai2d3dfigur import Ai2d3dfigur
from core.dienste.ai2d3dmodell import Ai2d3dmodell
from core.dienste.mesh3daitestmodell import Mesh3daitestmodell

from ._pruefablage import Pruefablage


class Ai2d3dmodellTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.job = Path(tempfile.mkdtemp(prefix='ai2d3dmodell_', dir=Pruefablage.wurzel()))
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
        umlenken = mock.patch.object(Ai2d3dfigur, 'ordner', classmethod(lambda cls, kennung: figur if kennung == 'kunstjob' else None))
        umlenken.start()
        self.addCleanup(umlenken.stop)

    def test_quelle_ist_der_ordner_des_jobs(self):
        self.assertEqual(Ai2d3dmodell.geschlecht('kunstjob'), 'maennlich')
        self.assertEqual(Ai2d3dmodell.ordner('kunstjob', 'maennlich'), self.figur / 'kleider_maennlich')
        self.assertIsNone(Ai2d3dmodell.ordner('kunstjob', 'unbekannt'))
        self.assertEqual(Ai2d3dmodell.form('kunstjob', 'maennlich')['figur']['regler'], {'a': 0.5})
        kacheln = Ai2d3dmodell.kacheln('kunstjob', 'maennlich')
        self.assertEqual(sorted(kacheln), ['1001', '1002'])
        self.assertTrue(kacheln['1001'].startswith('/api/2d3dai/kunstjob/figur/maennlich/bild/1001.jpg?t='))
        self.assertIsNone(Mesh3daitestmodell.kacheln('kunstjob', 'maennlich'))

    def test_kacheladresse_loest_auf_die_datei_auf(self):
        adresse = Ai2d3dmodell.kacheln('kunstjob', 'maennlich')['1002']
        self.assertEqual(Texturquelle.pfad(adresse), self.figur / 'haut_maennlich' / '1002.jpg')
        self.assertIsNone(Texturquelle.pfad('/api/2d3dai/kunstjob/figur/maennlich/bild/m1.jpg'))          # nur Kacheln 10??.jpg
        self.assertIsNone(Texturquelle.pfad('/api/2d3dai/anderer/figur/maennlich/bild/1001.jpg'))

    def test_starten_verlangt_die_stuecke(self):
        antwort, status = Ai2d3dmodell.starten('kunstjob', 'maennlich', 'Probe')
        self.assertEqual(status, 404)
        self.assertIn('error', antwort)
