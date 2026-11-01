# -*- coding: utf-8 -*-
"""Die Genesis-Figur der Mesh-Methode (Jobseite, oberste Zeile, Feld 3) trägt jedes Kleidungsstück des Fotos als eigenes Stück — Oberteil, Unterteil, Socken.

WARUM: Edgar, 30.10.2026, mit einem Bild der Figur von schräg hinten (Lauf 2026.10.29.23.02): „Unterhose nicht erkannt (stattdessen T-Shirt an der Stelle gebaut)“ — „die du erst
per testcase feststellen sollst und dann so lange rechnen sollst bis sie weg sind“. Die Figur hatte EINE Hülle `kleid` über allem, was im Foto Kleidung war; Sapiens2 unterscheidet
im Foto aber Oberteil (`Upper_Clothing`) und Unterteil (`Lower_Clothing`). Gemessen vorher mit diesem Maß (`ProjektTemp/_wegwerf/ai2d3d/diag_genesis_masse.py`): 654 von 654 Zellen
falsch (Oberteil 505, Unterteil 91, Socken 58) — keine Art hatte ein eigenes Stück.

Maß: `Ai2d3dkleidungmass` — je Foto gerastert, Zellen von 40 mm: füllt eine Art im Foto mindestens 40 % der Zelle, muss die Figur auf mindestens der Hälfte dieser Pixel das Stück
dieser Art zeigen. Flächen einer Art, die die anderen Fotos nicht bestätigen (Sapiens2 nennt im Profil Flecken auf Schienbein und Socke „Lower_Clothing“), zählen nicht.

    manage.py test core.tests.automated.test_ai2d3d_genesis_kleidung
"""
import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from .ai2d3d_figurprobe import Ai2d3dfigurprobe
from .ai2d3d_genesisansicht import Ai2d3dgenesisansicht
from .ai2d3d_kleidungmass import Ai2d3dkleidungmass


class Ai2d3dGenesisKleidung(SimpleTestCase):
    databases = set()
    JOB = 'EdgarTrip'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.probe = Ai2d3dfigurprobe(settings.OBJECTS_ROOT, cls.JOB)
        cls.ansicht = Ai2d3dgenesisansicht(cls.probe) if cls.probe.figur and cls.probe.figur.get('genesis') else None

    def _mass(self):
        if self.ansicht is None or self.probe.training is None:
            self.skipTest('kein Lauf mit Genesis-Figur: training_figur.json ohne genesis')
        self.assertTrue(self.probe.fotos(), 'Lauf %s ohne Kamera mit versatz_px' % self.probe.figur.get('lauf'))
        return Ai2d3dkleidungmass(self.ansicht)

    @staticmethod
    def _text(erg):
        zahl = {}
        for datei, art, _m, _a in erg['zellen']:
            zahl[(datei, art)] = zahl.get((datei, art), 0) + 1
        return 'Zellen je Art %s; falsch: %s; erste: %s; nicht bestätigt: %s' % (
            erg['arten'], zahl, '; '.join('%s %s bei %s px getroffen %.2f' % z for z in erg['zellen'][:6]),
            '; '.join('%s %s %d mm² bei %s px %.2f' % u for u in erg['uneinig'] if u[2] > 1000))

    def test_jede_kleidungsart_des_fotos_ist_ein_eigenes_stueck(self):
        mass = self._mass()
        erg = mass.messen()
        self.assertTrue(erg['arten'], 'keine Kleidung in den Fotos gefunden')
        self.assertFalse(erg['zellen'], 'Lauf %s, Stücke %s — %s' % (self.probe.figur['lauf'], self.ansicht.namen, self._text(erg)))

    def _foto_als_figur(self, mass, tausch=None):
        """Stücke je Pixel = die Arten des Fotos (Namen-Index wie die Ansicht); `tausch` {Art: Art} vertauscht."""
        namen = ['koerper', *mass.ARTEN]

        def stueck(_nr, f, r):
            st = np.zeros(r['stueck'].shape, dtype=np.int64)
            k = self.ansicht.verkleinern(self.probe.klassen(f['datei']))[:st.shape[0], :st.shape[1]]
            for art, kl in mass.ARTEN.items():
                st[np.isin(k, self.probe.klassen_index(*kl))] = namen.index((tausch or {}).get(art, art))
            return st
        return mass.messen(stueck, namen)

    def test_gegenprobe_foto_als_figur_besteht(self):
        mass = self._mass()
        erg = self._foto_als_figur(mass)
        self.assertFalse(erg['zellen'], self._text(erg))

    def test_gegenprobe_unterhose_als_oberteil_faellt_durch(self):
        mass = self._mass()
        erg = self._foto_als_figur(mass, {'unterteil': 'oberteil'})
        self.assertTrue(any(art == 'unterteil' for _d, art, _m, _a in erg['zellen']), self._text(erg))

    def test_gegenprobe_die_groesste_flaeche_jeder_art_ist_bestaetigt(self):
        """Der Filter gegen Flecken darf das Kleidungsstück selbst nie verwerfen: die größte Fläche jeder Art im Foto bestätigen die anderen Fotos."""
        from scipy import ndimage
        mass = self._mass()
        verworfen = []
        for nr, f in self.probe.fotos():
            r = self.ansicht.rastern(nr, f)
            _foto, weg = mass.foto_arten(nr, f, r['stueck'].shape)
            k = self.ansicht.verkleinern(self.probe.klassen(f['datei']))[:r['stueck'].shape[0], :r['stueck'].shape[1]]
            for art, namen in mass.ARTEN.items():
                marke, zahl = ndimage.label(np.isin(k, self.probe.klassen_index(*namen)))
                if zahl:
                    groesste = np.bincount(marke.ravel())[1:].max() * (self.probe.mm_je_px(nr) / self.ansicht.m) ** 2
                    verworfen += [u for u in weg if u[1] == art and u[2] >= int(groesste)]
        self.assertFalse(verworfen, 'größte Fläche einer Art nicht bestätigt: %s' % verworfen)
