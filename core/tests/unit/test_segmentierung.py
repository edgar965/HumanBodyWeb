# -*- coding: utf-8 -*-
u"""`Segmentierung`: welcher Vertex zu welchem Koerperteil zaehlt.

WARUM (07.09.2026): Die Zuordnung entscheidet ueber die Kollision waehrend
der Drapierung UND ueber jede Koerpermessung. Zwei Fehler darin trafen den
MAENNLICHEN Koerper, und beide sahen nach einer Eigenschaft der Figur aus,
nicht nach einem Fehler:

    1. 1.536 Vertices haengen am staerksten an `corrective_smooth_inv`,
       einem MB-Lab-Steuerknochen. Der benennt kein Koerperteil, also
       galten sie als RUMPF — 76 davon liegen in Armen und Beinen, die
       tiefsten bei z 0,507 m. Der tiefste Rumpfpunkt IST der Schritt:
       Er rutschte beim 183-cm-Mann von 0,88 auf 0,51 m, und mit ihm jede
       Messhoehe darueber. Gemessen wurde danach Brustumfang 307 cm,
       Taille 14,3 cm; fuenf Masse kamen nur noch aus der Baendigung.
    2. `data/humanBody_male` hat keine `materials.json`. Ohne
       Materialnamen bleibt `face_internal` LEER, und Zaehne, Zunge und
       Augen sind Kollisionsgeometrie — 6.213 Punkte im Kopf, an denen
       der Stoff haengenbleiben kann.

Geprueft wird beides an einem Kunstnetz mit bekannter Antwort und an den
echten Netzen. Der dritte Fall haelt die Annahme fest, auf der der
Namens-Rueckfall beruht: dass beide Netze dieselbe Materialreihenfolge
fuehren.
"""
import os

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from GarmentCode.segmentierung import Segmentierung


KNOCHEN = ['DEF-spine', 'DEF-thigh.L', 'DEF-upper_arm.R',
           'corrective_smooth_inv']


def netz(anzahl=4):
    u"""Ein Viereck je Vertex-Paar — Inhalt egal, nur die Form zaehlt."""
    faces = np.array([[0, 1, 2, 3]] * 2)
    return faces, np.array([0, 0])


class HilfsknochenTest(SimpleTestCase):
    u"""Ein Steuerknochen darf ein Koerperteil nicht ueberstimmen."""

    def _segmente(self, gewichte):
        faces, materialien = netz()
        return Segmentierung(faces, materialien, ['HB_Skin'],
                             {'bone_names': KNOCHEN, 'weights': gewichte},
                             len(gewichte)).segmente()

    def test_steuerknochen_ueberstimmt_das_bein_nicht(self):
        u"""Vertex 0: Steuerknochen 0,7, Oberschenkel 0,3 -> linkes Bein.

        Ohne den Fix gewinnt `corrective_smooth_inv`, `_knochenteil`
        liefert None, und der Punkt landet im Rumpf.
        """
        segmente = self._segmente([
            [(3, 0.7), (1, 0.3)],     # Steuerknochen stark, Bein schwach
            [(0, 1.0)],               # Wirbelsaeule -> Rumpf
            [(3, 0.9), (2, 0.1)],     # Steuerknochen, dahinter der Arm
            [(1, 1.0)],               # Oberschenkel -> Bein
        ])
        self.assertIn(0, segmente['left_leg'])
        self.assertIn(3, segmente['left_leg'])
        self.assertIn(2, segmente['right_arm'])
        self.assertIn(1, segmente['body'])

    def test_rumpfvertex_bleibt_im_rumpf(self):
        u"""Die Gegenprobe: Wer am staerksten an der Wirbelsaeule haengt,
        darf nicht ueber einen schwachen Armknochen zum Arm werden.

        Genau das waere passiert, haette man statt der Steuerknochen
        einfach jedes 'None' uebersprungen.
        """
        segmente = self._segmente([[(0, 0.9), (2, 0.1)]])
        self.assertIn(0, segmente['body'])
        self.assertNotIn(0, segmente['right_arm'])

    def test_ohne_echten_knochen_bleibt_die_wahl_wie_sie_war(self):
        u"""Haengt ein Vertex NUR an Steuerknochen, wird nichts erfunden:
        er zaehlt zum Rumpf, wie zuvor."""
        segmente = self._segmente([[(3, 1.0)]])
        self.assertIn(0, segmente['body'])


class MaterialRueckfallTest(SimpleTestCase):
    u"""Ohne `materials.json` darf `face_internal` nicht leer bleiben."""

    def _segmente(self, material_names):
        # Flaeche 0 traegt Material 8 (Zaehne), Flaeche 1 Material 0 (Haut).
        faces = np.array([[0, 1, 2, 3], [4, 5, 6, 7]])
        materialien = np.array([8, 0])
        gewichte = [[(0, 1.0)]] * 8
        return Segmentierung(faces, materialien, material_names,
                             {'bone_names': KNOCHEN, 'weights': gewichte},
                             8).segmente()

    def test_leere_namensliste_nutzt_die_bekannte_reihenfolge(self):
        segmente = self._segmente([])
        self.assertEqual(sorted(segmente['face_internal']), [0, 1, 2, 3])
        self.assertEqual(sorted(segmente['body']), [4, 5, 6, 7])

    def test_vorhandene_namen_gewinnen(self):
        u"""Wo Namen da sind, wird der Rueckfall nicht angefasst — hier
        heisst Material 8 anders, also ist nichts innen."""
        eigene = ['HB_Skin'] * 8 + ['HB_Irgendwas']
        segmente = self._segmente(eigene)
        self.assertEqual(segmente['face_internal'], [])


class EchteNetzeTest(SimpleTestCase):
    u"""Die Annahme hinter dem Rueckfall, an den echten Daten geprueft."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wurzel = str(settings.HUMANBODY_DATA_DIR)

    def _netzdaten(self, geschlecht):
        from core.dienste.charakterdaten import Charakterdaten
        return Charakterdaten.netzdaten(geschlecht)

    def test_materialreihenfolge_stimmt_in_beiden_netzen(self):
        u"""Fuer die Materialien 2 bis 8 — die inneren — muessen Flaechen-
        und Punktzahl in beiden Netzen uebereinstimmen.

        Darauf beruht `MATERIALIEN_RUECKFALL`: Das maennliche Netz bringt
        keine Namen mit, also wird die Reihenfolge des weiblichen
        angenommen. Laufen die Netze je auseinander, faellt dieser Test
        aus — und nicht erst die Kollision im Drapierlauf.
        """
        if not os.path.isdir(self.wurzel + '_male'):
            self.skipTest('keine maennliche Datenlage')
        zahlen = {}
        for geschlecht in ('female', 'male'):
            netzdaten = self._netzdaten(geschlecht)
            fm = np.asarray(netzdaten.face_materials)
            faces = np.asarray(netzdaten.faces)
            zahlen[geschlecht] = {
                nr: (int((fm == nr).sum()), int(len(np.unique(faces[fm == nr]))))
                for nr in range(2, 9)
            }
        for nr in range(2, 9):
            self.assertEqual(
                zahlen['female'][nr], zahlen['male'][nr],
                'Material %d (%s): weiblich %s, maennlich %s'
                % (nr, Segmentierung.MATERIALIEN_RUECKFALL[nr],
                   zahlen['female'][nr], zahlen['male'][nr]))

    def test_maennlicher_schritt_liegt_wo_ein_schritt_liegt(self):
        u"""Der tiefste Rumpfpunkt muss ueber der Koerpermitte liegen.

        Das ist die Probe auf den Steuerknochen-Fehler in echten Daten:
        Vorher lag der Schritt des 183-cm-Mannes bei 0,507 m — auf
        Kniehoehe, 28 % der Koerperhoehe.
        """
        from GarmentCode.dienst import GarmentcodeDienst
        from GarmentCode.koerperdienst import Garmentkoerper
        if not os.path.isdir(self.wurzel + '_male'):
            self.skipTest('keine maennliche Datenlage')
        punkte = GarmentcodeDienst.figurnetz('male', None, 'Male_Caucasian',
                                             None)
        if punkte is None:
            self.skipTest('kein maennliches Netz')
        punkte = np.asarray(punkte, dtype=np.float64)
        segmente = Garmentkoerper.segmente('male')
        if not segmente:
            self.skipTest('keine Skinning-Gewichte')
        rumpf = punkte[np.asarray(segmente['body'], dtype=int)]
        hoehe = float(punkte[:, 2].max() - punkte[:, 2].min())
        anteil = float(rumpf[:, 2].min() - punkte[:, 2].min()) / hoehe
        self.assertGreater(anteil, 0.40,
                           'Schritt bei %.0f %% der Koerperhoehe' % (anteil * 100))
        self.assertLess(anteil, 0.60,
                        'Schritt bei %.0f %% der Koerperhoehe' % (anteil * 100))

    def test_beide_netze_haben_inneres_gesicht(self):
        u"""`face_internal` darf in keiner Datenlage leer sein — sonst
        haengt der Stoff an Zaehnen und Zunge."""
        from GarmentCode.koerperdienst import Garmentkoerper
        for geschlecht in ('female', 'male'):
            if geschlecht == 'male' and not os.path.isdir(self.wurzel + '_male'):
                continue
            segmente = Garmentkoerper.segmente(geschlecht)
            if not segmente:
                continue
            self.assertGreater(len(segmente['face_internal']), 1000,
                               '%s: nur %d innere Punkte'
                               % (geschlecht, len(segmente['face_internal'])))


class GrundnetzTest(SimpleTestCase):
    u"""Das Grundnetz muss zur Bauart passen, nicht zur Datei.

    Bis zum 07.09.2026 stand in `_grundnetz` fest `vertices_tpose.npy` aus
    der WEIBLICHEN Datenlage. Eine maennliche Figur ohne Regler wurde
    damit am weiblichen Netz vermessen — 18.210 Punkte statt 17.996, bei
    Flaechen, deren hoechster Index 17.995 ist.
    """

    def test_je_bauart_die_eigene_punktzahl(self):
        from core.dienste.charakterdaten import Charakterdaten
        from GarmentCode.dienst import GarmentcodeDienst
        morphdaten = Charakterdaten.morphdaten()
        for bauart in ('Female_Caucasian', 'Male_Caucasian'):
            if bauart not in morphdaten.l1:
                continue
            erwartet = len(morphdaten.l1[bauart])
            netz = GarmentcodeDienst._grundnetz(
                Charakterdaten.geschlecht_zu(bauart), bauart)
            self.assertIsNotNone(netz, bauart)
            self.assertEqual(len(netz), erwartet, bauart)

    def test_maennlich_und_weiblich_sind_verschieden_lang(self):
        u"""Die Gegenprobe: Waeren beide gleich lang, koennte der Test
        oben auch mit der alten, festen Datei bestehen."""
        from core.dienste.charakterdaten import Charakterdaten
        morphdaten = Charakterdaten.morphdaten()
        if 'Male_Caucasian' not in morphdaten.l1:
            self.skipTest('keine maennliche Bauart')
        self.assertNotEqual(len(morphdaten.l1['Female_Caucasian']),
                            len(morphdaten.l1['Male_Caucasian']))
