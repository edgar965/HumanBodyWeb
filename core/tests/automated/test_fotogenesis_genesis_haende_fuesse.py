# -*- coding: utf-8 -*-
"""Hände und Füße der Genesis-Figur der Mesh-Methode (Jobseite, oberste Zeile, Feld 3) decken Hände und Füße im Foto — kein Finger woanders, keine Zehe aus der Socke.

WARUM: Edgar, 30.10.2026, mit einem Bild der Figur von schräg hinten (Lauf 2026.10.29.23.02): „hände - finger verdreht und kaputt“, „Füße vorne kaputt“. Nachgestellt
(`ProjektTemp/_wegwerf/fotogenesis/diag_genesis_ansicht.py`): im Rückenfoto 2.jpg sind die Finger gespreizt und gestreckt, an der Figur zu einer Kralle gebogen; vorn am Fuß stehen die
Zehen einzeln, im Foto ist die Socke glatt. Beides hat schon die geometrische Figur (`--geo`), die Genesis-Figur übernimmt es an der Haut Punkt für Punkt (`Hautgleich`).
Gemessen vorher mit diesem Maß (`diag_genesis_masse.py`, Raster 1:4, mm²): Hände fehlt/zuviel/Kerben 1.jpg links 397/1057/306, rechts 131/1520/79, 2.jpg links 1009/1231/290,
rechts 754/1135/235; Füße 1.jpg links 7/313/56, 4.jpg links 147/208/115, 3.jpg links 191/235/54, rechts 62/165/64.

Maß: `Fotogenesisteilflaeche` (Saum 1 mm frei, Kerben = was ein Schließen mit 5 mm an der Figur füllt und am Foto nicht). Grenzen (Setzung 30.10.2026, ein Fingerglied ~15 × 25 mm
≈ 400 mm²): Hand fehlt + zuviel ≤ 600 mm², Kerben ≤ 150 mm²; Fuß fehlt + zuviel ≤ 300 mm², Kerben ≤ 50 mm².

    manage.py test core.tests.automated.test_fotogenesis_genesis_haende_fuesse
"""
import numpy as np
from django.conf import settings
from django.test import SimpleTestCase
from scipy import ndimage

from .fotogenesis_figurprobe import Fotogenesisfigurprobe
from .fotogenesis_genesisansicht import Fotogenesisgenesisansicht
from .fotogenesis_teilflaeche import Fotogenesisteilflaeche


class FotogenesisGenesisHaendeFuesse(SimpleTestCase):
    databases = set()
    JOB = 'EdgarTrip'
    #: Teil: (fehlt + zuviel, Kerben) höchstens, mm²
    GRENZEN = {'haende': (600, 150), 'fuesse': (300, 50)}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.probe = Fotogenesisfigurprobe(settings.OBJECTS_ROOT, cls.JOB)
        cls.ansicht = Fotogenesisgenesisansicht(cls.probe) if cls.probe.figur and cls.probe.figur.get('genesis') else None

    def _mass(self):
        if self.ansicht is None or self.probe.training is None:
            self.skipTest('kein Lauf mit Genesis-Figur: training_figur.json ohne genesis')
        return Fotogenesisteilflaeche(self.ansicht)

    def _zu_viel(self, teil, werte):
        flaeche, kerbe = self.GRENZEN[teil]
        return [w for w in werte if w[3] + w[4] > flaeche or w[5] > kerbe]

    @staticmethod
    def _text(werte):
        return '; '.join('%s %s: Fläche %d, fehlt %d, zuviel %d, Kerben %d mm²' % w for w in werte)

    def _pruefen(self, teil):
        werte = self._mass().messen(teil)
        self.assertGreaterEqual(len(werte), 2, 'kaum ein Teil messbar: %s' % self._text(werte))
        schlecht = self._zu_viel(teil, werte)
        self.assertFalse(schlecht, 'Lauf %s, Grenzen %s mm² — über der Grenze: %s. Alle: %s' % (self.probe.figur['lauf'], self.GRENZEN[teil], self._text(schlecht),
                                                                                        self._text(werte)))

    def test_haende_wie_im_foto(self):
        self._pruefen('haende')

    def test_fuesse_wie_im_foto(self):
        self._pruefen('fuesse')

    def _person(self, _nr, f, r):
        h, w = r['stueck'].shape
        return self.ansicht.verkleinern(self.probe.klassen(f['datei']))[:h, :w] > 0

    def test_gegenprobe_foto_als_figur_besteht(self):
        mass = self._mass()
        for teil in self.GRENZEN:
            werte = mass.messen(teil, self._person)
            self.assertFalse(self._zu_viel(teil, werte), self._text(werte))

    def test_gegenprobe_finger_gekappt_faellt_durch(self):
        """Die Person des Fotos, an Händen und Füßen um 6 mm eingezogen (Finger und Zehen fehlen) — muss durchfallen."""
        mass = self._mass()

        def gekappt(nr, f, r):
            person = self._person(nr, f, r)
            n = int(round(6.0 / self.probe.mm_je_px(nr) * self.ansicht.m))
            k = self.ansicht.verkleinern(self.probe.klassen(f['datei']))[:person.shape[0], :person.shape[1]]
            teile = np.isin(k, self.probe.klassen_index('Left_Hand', 'Right_Hand', 'Left_Sock', 'Right_Sock', 'Left_Foot', 'Right_Foot'))
            return np.where(teile, ndimage.binary_erosion(person, iterations=n), person)
        for teil in self.GRENZEN:
            self.assertTrue(self._zu_viel(teil, mass.messen(teil, gekappt)), teil)
