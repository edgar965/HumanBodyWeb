# -*- coding: utf-8 -*-
"""Die Textur der geometrischen Figur (Mesh-Erzeugung, Feld 2 der oberen Zeile der Jobseite) stammt von der Person, nicht vom Hintergrund der Fotos.

WARUM: Edgar, 29.10.2026 abends, mit einem Bild der Figur (Lauf 2026.10.29.21.00): „testcase für textur in der Mesherzeugung und fixen (z.B. handtextur ist falsch)“ — weiße
Fingerspitzen, ein weißer Fleck an der Wölbung zwischen den Beinen. `Trainingfigur` färbte ohne Personenmasken: wo ein Punkt der Figur im Foto neben der Person lag, holte er den
Hintergrund. Gemessen mit diesem Maß (`ProjektTemp/_wegwerf/ai2d3d/diag_textur_hintergrund.py`): 866 Punkte, die schlimmsten Zellen an den Händen in 2.jpg (146, 116 Punkte) und
1.jpg (129, 87, 82), dazu an den Füßen in 1.jpg.

Maß: `Ai2d3dtexturmass` (Punkt sichtbar deutlich neben der Person, seine Farbe dem Hintergrund dort näher als jeder eigenen Farbe auf der Person); Fehler = eine Zelle von 60 mm mit
mindestens 5 solchen Punkten.

    manage.py test core.tests.automated.test_ai2d3d_mesh_textur
"""
import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from .ai2d3d_figurprobe import Ai2d3dfigurprobe
from .ai2d3d_texturmass import Ai2d3dtexturmass


class Ai2d3dMeshTextur(SimpleTestCase):
    databases = set()
    JOB = 'EdgarTrip'

    def _probe(self):
        p = Ai2d3dfigurprobe(settings.OBJECTS_ROOT, self.JOB)
        if p.figur is None or p.training is None:
            self.skipTest('kein Lauf: training_figur.json oder training.json fehlt')
        self.assertTrue(p.figur.get('farben'), 'Lauf %s ohne Farben' % p.figur.get('lauf'))
        self.assertTrue(p.fotos(), 'Lauf %s: keine Kamera mit versatz_px — form_direkt.py … --aus=%s neu ausgeben' % (p.figur.get('lauf'), p.figur.get('lauf')))
        return p, p.feld(p.figur['farben'], 'u1', 3).astype(np.int64)

    @staticmethod
    def _text(erg):
        return '%d Punkte mit Hintergrundfarbe; Zellen: %s' % (erg['punkte'], '; '.join('%s bei %s px %d Punkte' % z for z in erg['zellen'][:8]))

    def test_keine_hintergrundfarbe_auf_der_figur(self):
        p, farben = self._probe()
        erg = Ai2d3dtexturmass(p).messen(farben)
        self.assertFalse(erg['zellen'], 'Lauf %s — %s' % (p.figur['lauf'], self._text(erg)))

    def test_gegenprobe_hintergrund_eingefaerbt_faellt_durch(self):
        """Dieselben Farben, nur wo ein Punkt im ersten Foto deutlich neben der Person liegt, die Farbe des Fotos dort (= der alte Fehler)."""
        p, farben = self._probe()
        mass = Ai2d3dtexturmass(p)
        datei, (_uv, _sb, foto, _innen, daneben, _mm) = next(iter(mass._je_foto().items()))
        n = len(farben)
        falsch = np.where(daneben[:n, None], foto[:n], farben)
        erg = mass.messen(falsch)
        self.assertTrue(erg['zellen'], 'Hintergrund aus %s eingefärbt, trotzdem keine Zelle — %s' % (datei, self._text(erg)))
