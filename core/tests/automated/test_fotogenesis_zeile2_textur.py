# -*- coding: utf-8 -*-
"""Zeile 2 der Jobseite (gerechnete Figur → Genesis-Modell, Feld 3): die Textur stimmt mit den Fotos
überein — Arme, Beine, Hände wie die Haut im Foto, Kleidung wie die Kleidung — und das Genesis-Modell der
Zeile 2 ist VIEL besser als das der Zeile 1 (Mesh-Methode).

WARUM: Edgar, 02.11.2026, mit einem Bild der Seite EdgarTrip--gpu0: „genesie modell in zeile 2 ist
Katastrophal“; zu Zeile 1: „Textur beine / arme ist kaputt, saum T-short und hose … erzeuge [testcases],
Die müssen rot sein“; „das Genesis modell muss viel besser sein als die erste Zeile“. Ursache der
Katastrophe: der Kettenlauf 2026.11.01.19.51 „ab kopf“ rechnete die Einpassung neu (Formrest 11,13 mm) —
Kamera und Figur passten nicht mehr zu den Fotos, das Oberteil bekam 86 % seiner Farbe aus der Vorlage.

Maß: `Fotogenesisbildmass` auf dem Rendering der Seite (`<Job>/abnahme/seite_<nr>.png`, im Chrome
`window.__fotogenesis.seitenbilder()`) für die Textur-Tests; der Vergleich mit Zeile 1 liest seit 02.11.2026
abends das Maß der Kette (`abnahme/bildmass.json`, beide Zeilen mit demselben Raster auf der Karte —
`_kette`). Gemessen 02.11.2026
(`ProjektTemp/_wegwerf/ergaenzung/zeile2_mass_diag.py`): Zeile 1 Arme 1,9 % falsch / 6 Zellen, Beine 0,8 %
/ 3; Zeile 2 nach 19.51 Arme 13,5 % / 24, alle Gruppen 194 Zellen; Zeile 2 im Stand port2 (17:33) Arme 4,6
% / 12, Hose 13,2 % / 31.
„Viel besser“ (Setzung): in Summe über alle Gruppen höchstens VIEL_BESSER so viele abweichende Pixel
(falsch gefärbt oder leer, wo das Foto die Gruppe zeigt, oder über die Person hinaus) und Fehlerzellen wie
Zeile 1. Seit 02.11.2026 nachmittags zählt der Überstand mit (`Fotogenesisbildmass` „ueber“): Zeile 2 ragte mit dem
Oberteil 4.680 px über die Schultern hinaus, und kein Test sah es (`_wegwerf/ergaenzung/ueberstand_diag.py`).

    manage.py test core.tests.automated.test_fotogenesis_zeile2_textur
    FOTOGENESIS_TESTJOB=EdgarTrip--<probe> manage.py test …      # einen Probejob (`nurfotos_probejob.py`) prüfen
"""
import os

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from .fotogenesis_bildmass import Fotogenesisbildmass
from .fotogenesis_figurprobe import Fotogenesisfigurprobe
from .fotogenesis_genesisansicht import Fotogenesisgenesisansicht
from .fotogenesis_zeile2 import Fotogenesiszeile2


class FotogenesisZeile2Textur(SimpleTestCase):
    databases = set()
    JOB = os.environ.get('FOTOGENESIS_TESTJOB', 'EdgarTrip')
    HAUT = ('arme', 'beine', 'haende')
    VIEL_BESSER = 0.5
    #: so viele Pixel muss das Maß mindestens prüfen (EdgarTrip: ~700.000 je Zeile über vier Fotos)
    MINDEST_PX = 10000

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.probe = Fotogenesisfigurprobe(settings.OBJECTS_ROOT, cls.JOB)
        cls.zeile2 = Fotogenesiszeile2(settings.OBJECTS_ROOT, cls.JOB)
        cls.ansicht = None
        cls._erg = {}

    def _pruefbar(self):
        if self.probe.figur is None or self.probe.training is None or not self.zeile2.kameras:
            self.skipTest('kein Lauf: training_figur.json, training.json oder kameras.json fehlt')
        alt = self.zeile2.veraltet()
        self.assertFalse(alt, 'Renderings der Seite fehlen oder sind älter als die Figur (%s) — im Chrome '
                              'window.__fotogenesis.seitenbilder() auf /foto-genesis/test/%s/'
                         % (', '.join(alt), self.JOB.lower()))

    def _zeile2(self, nr, f, form):
        return self.zeile2.bild(f['datei'], form)

    def _zeile1(self, nr, f, form):
        r = type(self).ansicht.rastern(nr, f)
        h, w = form
        return r['farbe'][:h, :w], (r['stueck'] >= 0)[:h, :w]

    def _messen(self, zeile):
        if zeile not in self._erg:
            self._pruefbar()
            if zeile == 1:
                type(self).ansicht = Fotogenesisgenesisansicht(self.probe)
            bilder = self._zeile1 if zeile == 1 else self._zeile2
            self._erg[zeile] = Fotogenesisbildmass(self.probe, bilder).messen()
        # nichts gemessen ist kein Erfolg (02.11.2026: am Probejob fand die Probe keine Fotosegmente, alle Tests grün bei 0 Pixeln)
        geprueft = sum(s['geprueft'] for s in self._erg[zeile]['gruppen'].values())
        self.assertGreater(geprueft, self.MINDEST_PX, 'Zeile %d: nur %d Pixel geprüft — Fotosegmente oder Bilder fehlen' % (zeile, geprueft))
        return self._erg[zeile]

    @staticmethod
    def _text(erg, gruppen=None):
        g = {k: v for k, v in erg['gruppen'].items() if gruppen is None or k in gruppen}
        zellen = [z for z in erg['zellen'] if gruppen is None or z[1] in gruppen]
        je = ', '.join('%s %.1f %% falsch (%d px), leer %d px, über %d px'
                       % (k, 100 * v['anteil'], v['falsch'], v['leer'], v['ueber']) for k, v in g.items())
        erste = '; '.join('%s %s bei %s px Anteil %.2f %d mm²' % z for z in zellen[:8])
        return '%s; %d Zellen: %s' % (je, len(zellen), erste)

    def test_seitenbilder_zeigen_die_jetzige_figur(self):
        self._pruefbar()

    def test_textur_arme_beine_haende_wie_die_haut_im_foto(self):
        erg = self._messen(2)
        self.assertFalse([z for z in erg['zellen'] if z[1] in self.HAUT], self._text(erg, self.HAUT))

    def test_textur_kleidung_haar_gesicht_wie_im_foto(self):
        erg = self._messen(2)
        andere = [g for g in erg['gruppen'] if g not in self.HAUT]
        self.assertFalse([z for z in erg['zellen'] if z[1] in andere], self._text(erg, andere))

    def _kette(self):
        """Das Maß der Kette für beide Zeilen (`<Job>/abnahme/bildmass.json`, Stufe „bildmass“,
        `KoerperKI_Fotos.Bildmass` auf der Karte): beide Figuren mit DEMSELBEN Raster (Pixelmitten).
        Seit 02.11.2026 abends statt Seite (Zeile 2) gegen `Fotogenesisgenesisansicht` (Zeile 1): dessen Raster
        zählt jedes Pixel, das ein dicht abgetastetes Dreieck berührt, und macht Zeile 1 so rund ein halbes
        Pixel dicker — gemessen an EdgarTrip--versatz Lauf s: leer Zeile 1 3.704 (numpy) gegen 6.632 (Karte),
        Zeile 2 Seite 7.469 gegen Karte 8.474 (`ProjektTemp/_wegwerf/ergaenzung/bildmass_versatz_s.log`,
        `test_s.log`). Dasselbe Maß auf denselben Seitenbildern rechnet auf der Karte bitgleich zum numpy-Maß
        (14.414 Pixel, 30 Zellen, `ergaenzung/bildmass_gegenprobe.py`)."""
        datei = self.probe.ordner / 'abnahme' / 'bildmass.json'
        if not datei.is_file():
            self.skipTest('kein Maß der Kette: abnahme/bildmass.json fehlt (Stufe bildmass der Kette)')
        self.assertGreaterEqual(datei.stat().st_mtime, self.zeile2.figur_zeit(),
                                'abnahme/bildmass.json ist älter als die Figur — Stufe bildmass neu rechnen')
        import json
        erg = json.loads(datei.read_text(encoding='utf-8'))
        for zeile in ('zeile1', 'zeile2'):
            self.assertTrue(erg.get(zeile), 'bildmass.json ohne %s' % zeile)
            geprueft = sum(s['geprueft'] for s in erg[zeile]['gruppen'].values())
            self.assertGreater(geprueft, self.MINDEST_PX, '%s: nur %d Pixel geprüft' % (zeile, geprueft))
        return erg['zeile1'], erg['zeile2']

    def test_zeile2_viel_besser_als_zeile1(self):
        e1, e2 = self._kette()
        ab = {z: sum(s['falsch'] + s['leer'] + s['ueber'] for s in e['gruppen'].values())
              for z, e in ((1, e1), (2, e2))}
        text = 'Zeile 1: %s\nZeile 2: %s' % (self._text(e1), self._text(e2))
        self.assertLessEqual(ab[2], self.VIEL_BESSER * ab[1], 'abweichende Pixel Zeile 2 %d, Zeile 1 %d\n%s'
                             % (ab[2], ab[1], text))
        n1, n2 = len(e1['zellen']), len(e2['zellen'])
        self.assertLessEqual(n2, self.VIEL_BESSER * n1, 'Fehlerzellen Zeile 2 %d, Zeile 1 %d\n%s'
                             % (n2, n1, text))

    def _foto_als_bild(self, farbe_von=None, breiter_px=0):
        """Gegenproben: das Foto selbst als Bild der Figur (Person = Figur); `farbe_von(foto, klassen)`
        färbt um, `breiter_px` bläht die Figur um so viele Pixel des Maßstabs auf."""
        from scipy import ndimage
        mass = Fotogenesisbildmass(self.probe, None)

        def bild(nr, f, form):
            foto, kl, person = mass.foto(f)
            figur = ndimage.binary_dilation(person, iterations=breiter_px) if breiter_px else person
            return (foto if farbe_von is None else farbe_von(foto, kl)), figur
        mass.bilder = bild
        return mass.messen()

    def test_gegenprobe_das_foto_selbst_besteht(self):
        self._pruefbar()
        erg = self._foto_als_bild()
        self.assertFalse(erg['zellen'], self._text(erg))
        self.assertEqual(sum(s['ueber'] for s in erg['gruppen'].values()), 0, self._text(erg))

    def test_gegenprobe_aufgeblaehte_figur_ragt_ueber(self):
        """Die Person um 6 Pixel (≈ 40 mm bei 1,6 mm je Fotopixel und Maßstab 0,25) aufgebläht — der
        Überstand muss zählen (bis 02.11.2026 zählte er nirgends)."""
        self._pruefbar()
        erg = self._foto_als_bild(breiter_px=6)
        self.assertGreater(sum(s['ueber'] for s in erg['gruppen'].values()), self.MINDEST_PX, self._text(erg))

    def test_gegenprobe_arme_in_hemdfarbe_fallen_durch(self):
        """Die Arme in der Farbe des Oberteils (wie die dunklen Streifen an den Armen der Zeile 1 im
        Profil) — muss in der Gruppe arme durchfallen."""
        self._pruefbar()
        arme = self.probe.klassen_index(*Fotogenesisbildmass.GRUPPEN['arme'])
        hemd = self.probe.klassen_index(*Fotogenesisbildmass.GRUPPEN['oberteil'])

        def faerben(foto, kl):
            aus = foto.copy()
            aus[np.isin(kl, arme)] = np.median(foto[np.isin(kl, hemd)], axis=0)
            return aus
        erg = self._foto_als_bild(faerben)
        self.assertTrue([z for z in erg['zellen'] if z[1] == 'arme'], self._text(erg))
