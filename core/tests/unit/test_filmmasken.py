# -*- coding: utf-8 -*-
u"""`Filmmasken` und `Feinkoerper`: Der Server-Videoweg rendert die Haut
unter dem Stoff nicht — und zwar am SICHTBAREN Netz.

Am Kunstkörper (Zylinder mit anliegendem Rohr): Der Körper bekommt eine
Maske und einen gekürzten Index, das Rohr (allein) keine; beim Rendern
wandern die verdeckten Ecken nach innen, die Dreiecke sind die gekürzten.
Dazu `Feinkoerper`: Trägt ein Teil einen Unterteiler, kommen Ruhe und Bild
aus `subdivide(...)`, sonst aus der Bahn selbst; die Bildablage fällt,
wenn die Bahn ersetzt wird (Physik).

Und die Verdrahtung am Quelltext: `filmlauf.py` reicht das feine Netz
weiter, `filmrender.py` rendert über `Filmmasken.gerendert`, die
Stoffgrenze der Physik läuft gegen den Feinkörper.
"""
import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from ._kunstkoerper import Kunstkoerper


def _pfad(name):
    return settings.BASE_DIR / 'TheatreJS' / 'ModelPhysik' / name


def _modul(name):
    import importlib
    import sys
    ordner = str(settings.BASE_DIR / 'TheatreJS' / 'ModelPhysik')
    if ordner not in sys.path:
        sys.path.insert(0, ordner)
    return importlib.import_module(name)


class _Haut:
    def __init__(self, punkte, bilder=2):
        self.punkte = np.asarray(punkte, dtype=np.float64)
        self.folge = np.array([self.punkte + np.array([0.0, 0.001 * k, 0.0])
                               for k in range(bilder)])


class _Unterteiler:
    u"""Verdoppelt nichts — schiebt nur um 1 mm, damit man den Weg sieht."""
    def subdivide(self, basis):
        return np.asarray(basis) + np.array([0.001, 0.0, 0.0])


class FilmmaskenTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.fm = _modul('filmmasken')
        self.fk = _modul('feinkoerper')
        kp, kt = Kunstkoerper.zylinder(0.10, 0.0, 1.0, 51, 36)
        sp, st = Kunstkoerper.zylinder(0.102, 0.30, 0.70, 41, 36)
        self.koerper = {'name': u'Koerper', 'haut': _Haut(kp), 'dreiecke': kt}
        self.rohr = {'name': u'rohr', 'haut': _Haut(sp), 'dreiecke': st}

    def test_koerper_bekommt_maske_und_gekuerzten_index(self):
        bericht = self.fm.Filmmasken.anwenden([self.koerper, self.rohr])
        self.assertEqual([b[0] for b in bericht], [u'Koerper'])
        self.assertGreater(int(self.koerper['maske'].sum()), 500)
        self.assertLess(len(self.koerper['dreiecke_sichtbar']), len(self.koerper['dreiecke']))
        self.assertNotIn('maske', self.rohr)
        punkte, dreiecke, normalen = self.fm.Filmmasken.gerendert(self.koerper, 1)
        self.assertEqual(len(dreiecke), len(self.koerper['dreiecke_sichtbar']))
        maske = self.koerper['maske']
        r = np.linalg.norm(punkte[:, [0, 2]], axis=1)
        self.assertTrue(np.allclose(r[maske], 0.10 - 0.010, atol=1e-6))
        self.assertTrue(np.allclose(r[~maske], 0.10, atol=1e-6))
        self.assertEqual(normalen.shape, punkte.shape)

    def test_feinkoerper_ohne_unterteiler_ist_die_bahn(self):
        F = self.fk.Feinkoerper
        self.assertFalse(F.hat(self.koerper))
        self.assertIs(F.ruhe(self.koerper), self.koerper['haut'].punkte)
        self.assertIs(F.dreiecke(self.koerper), self.koerper['dreiecke'])
        self.assertTrue(np.array_equal(F.bild(self.koerper, 1), self.koerper['haut'].folge[1]))

    def test_feinkoerper_mit_unterteiler_folgt_der_bahn(self):
        F = self.fk.Feinkoerper
        teil = dict(self.koerper, unterteiler=_Unterteiler(), fein_dreiecke=self.koerper['dreiecke'])
        ruhe = F.ruhe(teil)
        self.assertTrue(np.allclose(ruhe[:, 0], teil['haut'].punkte[:, 0] + 0.001))
        bild = F.bild(teil, 1)
        self.assertTrue(np.allclose(bild[:, 1], teil['haut'].folge[1][:, 1]))
        # Bahn ersetzt (wie nach der Physik): der alte Eintrag gilt nicht mehr.
        teil['haut'].folge = teil['haut'].folge + np.array([0.0, 0.0, 0.5])
        self.assertTrue(np.allclose(F.bild(teil, 1)[:, 2], teil['haut'].folge[1][:, 2]))

    def test_verdrahtung_im_film(self):
        lauf = _pfad('filmlauf.py').read_text(encoding='utf-8')
        self.assertIn('figurfein=fein', lauf)
        self.assertIn('Charakterdaten.unterteiler(geschlecht)', lauf)
        render = _pfad('filmrender.py').read_text(encoding='utf-8')
        self.assertIn('Filmmasken.gerendert(teil, nummer)', render)
        self.assertNotIn('import trimesh', render)
        physik = _pfad('filmphysik.py').read_text(encoding='utf-8')
        self.assertIn('Stoffgrenze(Feinkoerper.bild(koerper, nummer)', physik)
        film = _pfad('hbfilm.py').read_text(encoding='utf-8')
        self.assertIn('Filmmasken.anwenden(self.teile, self.melder)', film)
        grenze = _pfad('stoffgrenze.py').read_text(encoding='utf-8')
        # Wicklung ueber das Volumen, nicht die Mehrheit (kippte in Posen).
        self.assertIn("np.einsum('ij,ij->i', a, np.cross(b, c)).sum()", grenze)
