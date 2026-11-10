# -*- coding: utf-8 -*-
"""Die geometrische Figur (Mesh-Erzeugung, Feld 2 der oberen Zeile der Jobseite) hat Augäpfel, und sie sitzen in den Augenhöhlen.

WARUM: Edgar, 29.10.2026 abends: „augen im mesh fehlen“ — der Käfig (Genesis-Netz) hat keine Augäpfel; die Genesis-Figur der Mesh-Methode bekam sie am 28.10.2026 (`Meshaugen`), die
geometrische Figur nicht: die Augenhöhlen waren leer und zeigten den Hintergrund (weiß). Seit 29.10.2026 abends schreibt `Trainingfigur` sie mit (`Figurfarben.mit_augen`).

Geprüft an training_figur.json: `augen` mit Dreiecken, Punkten je Foto und Farben; zwei Augäpfel (Zusammenhangskomponenten der Dreiecke) mit einem Abstand der Mitten von
AUGENABSTAND_MM; jede Mitte höchstens HOEHLE_MM vom nächsten Punkt der Figur; im Vorderfoto (das erste Foto) beide Augäpfel sichtbar und keiner mehr als VORSTEHEN_MM vor der
vordersten Stelle der Figur in seinem Umkreis (sie sitzen in der Höhle, nicht davor — die Nähe allein hielt eine Verschiebung um 30 mm nach vorn nicht auf: Nase und Brauen
liegen so nah).

    manage.py test core.tests.automated.test_fotogenesis_mesh_augen
"""
import numpy as np
from django.conf import settings
from django.test import SimpleTestCase
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from .fotogenesis_figurprobe import Fotogenesisfigurprobe


class FotogenesisMeshAugen(SimpleTestCase):
    databases = set()
    JOB = 'EdgarTrip'
    AUGENABSTAND_MM = (50.0, 75.0)
    HOEHLE_MM = 20.0
    #: der Augapfel darf im Vorderfoto höchstens so weit vor der vordersten Stelle der Figur im Umkreis (Lider, Brauen, Nasenwurzel) liegen
    UMKREIS_MM, VORSTEHEN_MM = 20.0, 5.0
    #: Gegenprobe: so weit vor das Gesicht geschoben (mm, Blickrichtung der Kamera des Vorderfotos) muss die Prüfung durchfallen
    VOR_MM = 30.0

    def _probe(self):
        p = Fotogenesisfigurprobe(settings.OBJECTS_ROOT, self.JOB)
        if p.figur is None:
            self.skipTest('kein Lauf: training_figur.json fehlt')
        a = p.figur.get('augen')
        self.assertTrue(a, 'Lauf %s: die geometrische Figur hat keine Augäpfel (`augen` fehlt in training_figur.json)' % p.figur.get('lauf'))
        for schluessel in ('dreiecke', 'farben', 'fotos'):
            self.assertTrue(a.get(schluessel), 'augen ohne %s' % schluessel)
        self.assertEqual(set(a['fotos']), set(p.figur['fotos']), 'Augäpfel nicht für jedes Foto')
        return p, a

    @staticmethod
    def kugeln(dreiecke, n):
        """(n,) Nummer des Augapfels je Punkt (Zusammenhang über die Dreiecke)."""
        k = np.concatenate([dreiecke[:, [0, 1]], dreiecke[:, [1, 2]], dreiecke[:, [2, 0]]])
        g = coo_matrix((np.ones(len(k)), (k[:, 0], k[:, 1])), shape=(n, n))
        return connected_components(g, directed=False)[1]

    def messen(self, p, a, vor_mm=0.0):
        """[Fehlertext] für das erste Foto (Vorderansicht); leer = in Ordnung."""
        nr, f = p.fotos()[0] if p.fotos() else next(iter(p.figur['fotos'].items()))
        tri = p.feld(a['dreiecke'], '<u4', 3).astype(np.int64)
        y = p.feld(a['fotos'][nr], '<f4', 3).astype(np.float64)
        k = f['kamera']
        blick = np.asarray(k['ziel']) - np.asarray(k['ort'])
        y = y - vor_mm / 1000 * blick / np.linalg.norm(blick)
        x = p.punkte(f)
        teil = self.kugeln(tri, len(y))
        mitten = [y[teil == i].mean(0) for i in np.unique(teil)]
        fehler = []
        if len(mitten) != 2:
            return ['%d Augäpfel statt 2' % len(mitten)]
        abstand = 1000 * np.linalg.norm(mitten[0] - mitten[1])
        if not self.AUGENABSTAND_MM[0] <= abstand <= self.AUGENABSTAND_MM[1]:
            fehler.append('Abstand der Mitten %.1f mm' % abstand)
        for i, m in enumerate(mitten):
            d = 1000 * np.sqrt(((x - m) ** 2).sum(1)).min()
            if d > self.HOEHLE_MM:
                fehler.append('Augapfel %d: %.1f mm bis zur Figur (Grenze %.0f)' % (i, d, self.HOEHLE_MM))
        if 'versatz_px' in k:
            alle = np.concatenate([x, y])
            uv, z = p.projektion(f, alle)
            sb = p.sichtbar(uv, z, f, np.concatenate([p.dreiecke, tri + len(x)]))[len(x):]
            mm = p.mm_je_px(nr) if p.training else 0.4
            for i in np.unique(teil):
                if not sb[teil == i].any():
                    fehler.append('Augapfel %d im Vorderfoto %s verdeckt' % (i, f['datei']))
                # vor dem Gesicht? Die vorderste Stelle des Augapfels gegen die vorderste Stelle der Figur in einem Kreis von UMKREIS_MM um seine Mitte im Bild
                ja = teil == i
                mitte = uv[len(x):][ja].mean(0)
                nah = np.sqrt(((uv[:len(x)] - mitte) ** 2).sum(1)) * mm <= self.UMKREIS_MM
                if nah.any():
                    vor = 1000 * (z[:len(x)][nah].min() - z[len(x):][ja].min())
                    if vor > self.VORSTEHEN_MM:
                        fehler.append('Augapfel %d steht %.1f mm vor dem Gesicht (Grenze %.0f)' % (i, vor, self.VORSTEHEN_MM))
        return fehler

    def test_augaepfel_sitzen_in_den_augenhoehlen(self):
        p, a = self._probe()
        fehler = self.messen(p, a)
        self.assertFalse(fehler, 'Lauf %s: %s' % (p.figur['lauf'], '; '.join(fehler)))

    def test_gegenprobe_vor_dem_gesicht_faellt_durch(self):
        p, a = self._probe()
        self.assertTrue(self.messen(p, a, self.VOR_MM), 'Augäpfel %d mm vor dem Gesicht, trotzdem in Ordnung' % self.VOR_MM)
