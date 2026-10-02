# -*- coding: utf-8 -*-
u"""Bart und Haarlänge der Runden (01.10.2026 abends) — Kunstdaten, keine Grafikkarte, keine Garderobe.

1. `G9haargenerisch.anteile`/`mischung`: ein Bart (`…_beard`) zählt nicht in die Normierung — Frisur 1,0 + Bart 1,0
   bleiben beide 1,0, die Frisur bleibt Hauptsorte (Kappe), der Bart steht hinten.
2. `IterationHaare.bart`: zeigt die Bartzone Haar, kommt der Bart dazu und wird umgefärbt; ohne Befund nichts; beim
   Frisurwechsel (`haar_nur` setzt alle Sorten auf 0) kommt er im selben Rezept wieder; `getragen` ist nie der Bart.
3. `Rundenauswahl.pflicht`: die Bartzeile gilt als belegt.
4. `IterationHaare.laenge`: steht der Haarabstand über vier Runden mit verschiedenen Längen auf ±2 mm, kein Schritt mehr.
5. `Teilmasken.messen`: neun Teile, jeder bekommt genau sein Pixel — vorher trug der 7. die Kennfarbe des ersten.
6. `G9kleidtexturen._flach_hell`: Helligkeit der hellsten bildlosen Gruppe (Bart: Daz-Grundton), Gruppen mit Bild
   zählen nicht — unter `grau` kommt sie auf `GRAU_MITTEL`, der Bart wird grau statt schwarz.
7. `IterationHaare.farbe`: graues Foto (Buntheit < 0,15) → Tönung ohne Stich (#916e6d → #757575); braunes bleibt bunt.
8. `Rundenauswahl`: ein Farbschritt 0,0002 über der besten Note gilt (Rauschen), 0,01 darüber nicht; die abgeschaltete
   Haar-Fototextur wird zurückgenommen, und die Zeile ist Pflicht.

Sabotage: `G9haargenerisch.ZUSATZ = '_nie'` → Fall 1 rot; `PFLICHT_HAAR = ()` → Fall 3 rot; die Stillstandsprüfung in
`laenge` entfernen → Fall 4 rot.
"""
import sys

from django.conf import settings
from django.test import SimpleTestCase

sys.path.insert(0, str(settings.BASE_DIR.parent))
sys.path.insert(0, str(settings.BASE_DIR.parent / '2d3DIterationen'))

from iterationen2d3d.iterationhaare import IterationHaare  # noqa: E402
from iterationen2d3d.rundenauswahl import Rundenauswahl  # noqa: E402


class _Modell:
    SORTE = 'sorte.'
    BILD = 'bild.'
    EIGEN = 'eigen.'
    HAAR_VORGABE = 'kin_hair'

    def __init__(self, haar):
        self.haar = dict(haar)
        self.farben = {'haar': '#808080'}


class BartHaarlaengeTest(SimpleTestCase):
    databases = set()

    def test_1_bart_ausserhalb_der_normierung(self):
        from Genesis9.haargenerisch import G9haargenerisch as H
        frisuren = [{'id': 'kin_hair'}, {'id': 'mavick_hair'}, {'id': 'mavick_beard'}]
        alt = H.__dict__['frisuren']
        H.frisuren = classmethod(lambda cls: frisuren)
        try:
            werte = {'sorte.kin_hair': 0.0, 'sorte.mavick_hair': 1.0, 'sorte.mavick_beard': 1.0}
            self.assertEqual(H.anteile(werte), {'mavick_hair': 1.0, 'mavick_beard': 1.0})
            self.assertEqual([(k, a) for k, a, _r in H.mischung(werte)], [('mavick_hair', 1.0), ('mavick_beard', 1.0)])
        finally:
            H.frisuren = alt

    def test_2_bart_aus_dem_befund(self):
        grund = {'sorte.kin_hair': 0.0, 'sorte.mavick_hair': 1.0, 'mavick_hair.bild.grau': 1.0}
        befund = {'zubehoer': {'bart': True}}
        aufrufe = IterationHaare(_Modell(grund), befund, kandidaten=['mavick_hair']).bart()
        self.assertEqual(aufrufe, ["m.haar_anteil('mavick_beard', 1.0)", "m.haar_umfaerben('mavick_beard')"])
        self.assertEqual(IterationHaare(_Modell(grund), {}).bart(), [])
        mit = dict(grund, **{'sorte.mavick_beard': 1.0, 'mavick_beard.bild.grau': 1.0})
        self.assertEqual(IterationHaare(_Modell(mit), befund).getragen(), 'mavick_hair')
        self.assertEqual(IterationHaare(_Modell(mit), befund).bart(), [])
        self.assertEqual(IterationHaare(_Modell(mit), befund).bart(neu=True), ["m.haar_anteil('mavick_beard', 1.0)"])
        anders = dict(mit, **{'sorte.mavick_hair': 0.0, 'sorte.toulouse_hair': 1.0})
        wechsel = IterationHaare(_Modell(anders), befund, kandidaten=['mavick_hair']).aufrufe()
        self.assertEqual(wechsel[0], "m.haar_nur('mavick_hair')")
        self.assertIn("m.haar_anteil('mavick_beard', 1.0)", wechsel)

    def test_3_bart_ist_pflicht(self):
        self.assertTrue(Rundenauswahl.pflicht(["m.haar_anteil('mavick_beard', 1.0)"]))
        self.assertFalse(Rundenauswahl.pflicht(["m.haar_anteil('toulouse_hair', 0.3)"]))

    def test_4_laenge_ruht_bei_stillstand(self):
        haar = {'sorte.mavick_hair': 1.0, 'mavick_hair.achse.laenge': 0.2}
        befund = {'teile': {'mavick_hair': {'art': 'haar', 'pixel': 400, 'netz_abs_mm': 30.6}}}
        verlauf = [{'frisur': 'mavick_hair', 'laenge': lg, 'haar_mm': mm}
                   for lg, mm in ((0.15, 30.62), (0.35, 30.58), (0.25, 30.59), (0.2, 30.6))]
        self.assertEqual(IterationHaare(_Modell(haar), befund, verlauf).laenge(), [])
        bewegt = [dict(r, haar_mm=r['haar_mm'] - 3 * i) for i, r in enumerate(verlauf)]
        self.assertTrue(IterationHaare(_Modell(haar), befund, bewegt).laenge())

    def test_5_teilmasken_ohne_doppelte_kennfarbe(self):
        import numpy as np
        from iterationen2d3d.teilmasken import Teilmasken
        anzahl = 9                                      # mehr Teile als Kennfarben: zwei Blöcke

        def kennbild(farben, _block):                  # Teil i liegt in Pixel i (eine Zeile)
            bild = np.asarray([farben], dtype=np.float32) * 0.8
            return bild, np.ones((1, anzahl), dtype=bool)

        masken = Teilmasken.messen(anzahl, kennbild)
        for i, m in enumerate(masken):
            self.assertEqual(np.flatnonzero(m[0]).tolist(), [i])
        self.assertEqual(len(set(Teilmasken.farben(7))), 7)

    def test_6_grau_normiert_bildlose_gruppen_je_sorte(self):
        from Genesis9.kleidtexturen import G9kleidtexturen
        bart = {'Hair1': {'alpha': 'MBtr.jpg', 'farbe': [0.2118, 0.1843, 0.1216]}}
        self.assertAlmostEqual(G9kleidtexturen._flach_hell(bart), 0.2118 * 0.2126 + 0.1843 * 0.7152 + 0.1216 * 0.0722)
        mit_bild = dict(bart, Cap={'albedo': 'x.jpg', 'farbe': [1.0, 1.0, 1.0]})     # Gruppen mit Bild zählen nicht
        self.assertAlmostEqual(G9kleidtexturen._flach_hell(mit_bild), G9kleidtexturen._flach_hell(bart))
        self.assertIsNone(G9kleidtexturen._flach_hell({'Cap': {'albedo': 'x.jpg'}}))

    def test_7_graues_haar_ohne_farbstich(self):
        haar = {'sorte.mavick_hair': 1.0, 'mavick_hair.bild.grau': 1.0}
        teil = {'art': 'haar', 'pixel': 400, 'foto_farbe': [0.347, 0.313, 0.310], 'render_farbe': [0.37, 0.34, 0.33]}
        m = _Modell(haar)
        m.farben['haar'] = '#916e6d'
        self.assertEqual(IterationHaare(m, {'teile': {'mavick_hair': teil}}).farbe(), ["m.haar_farbe('#757575')"])
        braun = dict(teil, foto_farbe=[0.35, 0.25, 0.18])                       # buntes Haar behält seinen Ton
        self.assertEqual(IterationHaare._neutral(braun['foto_farbe']), [0.35, 0.25, 0.18])

    def test_8_farbschritt_im_rauschen_und_fototextur_zuruecknehmen(self):
        a = Rundenauswahl()
        a.nach_runde(1, 0.4094, [])
        self.assertEqual(a.nach_runde(2, 0.4096, ["m.haar_farbe('#757575')"])[0], 'besser')
        self.assertEqual(a.nach_runde(3, 0.4200, ["m.haar_farbe('#808080')"])[0], 'verworfen')
        haar = {'sorte.mavick_hair': 1.0, 'mavick_hair.bild.foto_j1': 1.0}
        zeilen = IterationHaare(_Modell(haar), {}).fototextur()
        self.assertEqual(zeilen, ["m.bild_wert('haar', 'mavick_hair', 'foto_j1', 0.0)"])
        self.assertTrue(Rundenauswahl.pflicht(zeilen))
