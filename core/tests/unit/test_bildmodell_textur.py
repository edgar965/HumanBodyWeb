# -*- coding: utf-8 -*-
"""Der Bereich „Textur": Liste der Bilder, Bildtypen-Vorgaben beim Upload, Schritt `textur` (19.09.2026).

Edgar: „Mach mir ganz unten einen Bereich nur für Textur … einen Button zum
Anpassen, wenn ich ein Bild mit einer Textur entfernt habe … wenn ich die
Bilder auswähle / abwähle, hinzufüge." Ohne Bibliothek, ohne Schätzer:

1. `Bildmodelltextur.liste`: je Bild gewählt/möglich/Grund/Kamera — ein
   gerendertes Testfallbild mit bekannter Kamera (`kamera_bekannt`), ein Bild
   mit Rig über das Rig (seit 20.09. gegen das Modell selbst, kein Schätzer-
   Netz mehr), ein Nebenbild ohne Teil ist nicht möglich (Grund), Nutzung
   „nur Form" ebenso, Videos fehlen.
2. `Bildmodellbildtypen.vorgaben_pruefen`: nur eben hochgeladene Dateien, nur
   bekannte Werte; die Sichtung übernimmt die Vorgabe (`optionen.bildtypen`) für
   einen neuen und einen nie von Hand gestellten Eintrag, nicht für einen manuellen.
3. `Bildmodelloptionen`: der Schritt `textur` steht zwischen `vorschau` und
   `speichern`, die Vorgabe der Textur ist `foto`, `BLEIBEN` kennt die
   gezogenen Linien (die gingen beim ersten Start verloren).
4. `Bildmodellfototextur.bilder`: nur projizierbare Bilder (Kamera bekannt, Rig,
   Gesichtspunkte oder Hände); Nebenbilder ohne Teil bleiben draußen. `_eintrag`
   rechnet die Browserkamera in die OpenCV-Kamera um (Zuschnitt verschiebt den
   Hauptpunkt) und gibt die Teilnummern eines Nebenbilds mit.
"""

import unittest

from django.test import override_settings

from core.daten.bildmodellablage import Bildmodellablage
from core.dienste.bildmodellbildtypen import Bildmodellbildtypen as T
from core.dienste.bildmodellfototextur import Bildmodellfototextur
from core.dienste.bildmodelloptionen import Bildmodelloptionen
from core.dienste.bildmodellsichtung import Bildmodellsichtung
from core.dienste.bildmodelltextur import Bildmodelltextur

from ._pruefablage import Pruefablage

SMPLX = {'backend': 'smplest_x', 'posed_vertices_path': 'v_posed.npy', 'cam_focal': [5000, 5000],
         'processed_bbox': [0, 0, 100, 100]}
HAUT = {'hautton': [180, 130, 100], 'tauglich': True, 'anteil': 0.5, 'maske_px': 900}


def _bilder():
    return [
        {'datei': 'vorn.jpg', 'kategorie': 'koerper', 'ansicht': 'vorne', 'gewicht': 1.0, 'textur': HAUT,
         'schaetzung': SMPLX, 'rigs': {'yolo': {'punkte': []}}},
        {'datei': 'hinten.jpg', 'kategorie': 'koerper', 'ansicht': 'hinten', 'gewicht': 1.0, 'textur': HAUT,
         'schaetzung': SMPLX, 'kasten': [100, 0, 1100, 1600], 'breite': 1000, 'hoehe': 1600,
         'kamera_bekannt': {'matrix': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0.9, 3.0, 1],
                            'figur': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                            'fov': 30.0, 'breite': 1200, 'hoehe': 1600}},
        {'datei': 'gesicht.jpg', 'kategorie': 'neben', 'teil': 'gesicht', 'gewicht': 0.0, 'nutzung': 'textur',
         'textur': dict(HAUT, tauglich=False, grund='kein Hauptbild'),
         'rigs': {'openpifpaf': {'punkte': []}}},
        {'datei': 'detail.jpg', 'kategorie': 'neben', 'gewicht': 0.0, 'textur': dict(HAUT, tauglich=False),
         'rigs': {'yolo': {'punkte': []}}},
        {'datei': 'form.jpg', 'kategorie': 'koerper', 'ansicht': 'seite', 'gewicht': 1.0, 'nutzung': 'form',
         'textur': HAUT, 'schaetzung': SMPLX},
        {'datei': 'ohne.jpg', 'kategorie': 'kopf', 'ansicht': 'vorne', 'gewicht': 1.0, 'textur': HAUT},
        {'datei': 'dreh.mp4', 'video': True, 'kategorie': 'video', 'gewicht': 1.0, 'textur': HAUT},
    ]


class _Job:
    kennung = 'pruef'

    def __init__(self, bilder, optionen=None):
        self.bilder = bilder
        self.optionen = optionen or {}
        self.ergebnis = {}


class _Ablage:
    @staticmethod
    def zuschnitt():
        from pathlib import Path
        return Path('A:/pruef/zuschnitt')


class TexturlisteTest(unittest.TestCase):
    def test_1_liste(self):
        liste = {e['datei']: e for e in Bildmodelltextur.liste(_bilder())}
        self.assertNotIn('dreh.mp4', liste)
        self.assertEqual((liste['vorn.jpg']['gewaehlt'], liste['vorn.jpg']['kamera']), (True, 'rig'))
        self.assertEqual(liste['hinten.jpg']['kamera'], 'bekannt')
        self.assertEqual((liste['gesicht.jpg']['gewaehlt'], liste['gesicht.jpg']['kamera']), (True, 'rig'))
        self.assertFalse(liste['detail.jpg']['moeglich'])
        self.assertIn('Körperteil', liste['detail.jpg']['grund'])
        self.assertFalse(liste['form.jpg']['moeglich'])
        self.assertIn('Nur Form', liste['form.jpg']['grund'])
        self.assertEqual(liste['ohne.jpg']['kamera'], 'keine')

    def test_2_vorgaben_und_sichtung(self):
        roh = '{"a.jpg": {"neben": "neben/gesicht", "nutzung": "textur", "haupt": "quatsch"}, ' \
              '"fremd.jpg": {"nutzung": "textur"}, "b.jpg": "kaputt"}'
        self.assertEqual(T.vorgaben_pruefen(roh, ['a.jpg', 'b.jpg']),
                         {'a.jpg': {'neben': 'neben/gesicht', 'nutzung': 'textur'}})
        self.assertEqual(T.vorgaben_pruefen('nicht json', ['a.jpg']), {})
        self.assertEqual(T.vorgaben_pruefen('', ['a.jpg']), {})
        with Pruefablage.ordner('bm_textur_') as ordner, override_settings(OBJECTS_ROOT=ordner):
            a = Bildmodellablage('pruef')
            a.anlegen()
            job = _Job([{'datei': 'alt_z1.jpg', 'quelle': 'alt.jpg', 'kategorie': 'koerper', 'gewicht': 1.0,
                         'manuell': True},
                        {'datei': 'frei_z1.jpg', 'quelle': 'frei.jpg', 'kategorie': 'koerper',
                         'gewicht': 1.0}])
            kamera = {'matrix': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0.9, 3.0, 1], 'fov': 30.0,
                      'breite': 1200, 'hoehe': 1600}
            typen = {'a.jpg': {'neben': 'neben/gesicht', 'nutzung': 'textur'},
                     'alt.jpg': {'neben': 'neben/haende', 'kamera': kamera},
                     'frei.jpg': {'neben': 'neben/haende'}}
            s = Bildmodellsichtung(job, a, {'bildtypen': typen})
            s._uebernehmen([{'datei': 'a_z1.jpg', 'quelle': 'a.jpg', 'kategorie': 'kopf', 'gewicht': 1.0},
                            {'datei': 'alt_z1.jpg', 'quelle': 'alt.jpg', 'kategorie': 'koerper',
                             'gewicht': 1.0},
                            {'datei': 'frei_z1.jpg', 'quelle': 'frei.jpg', 'kategorie': 'koerper',
                             'gewicht': 1.0}])
            nach = {b['datei']: b for b in job.bilder}
            neu = nach['a_z1.jpg']
            self.assertEqual((neu['kategorie'], neu['teil'], neu['nutzung']), ('neben', 'gesicht', 'textur'),
                             'Vorgabe für die neue Datei')
            self.assertTrue(neu['manuell'])
            self.assertEqual(nach['alt_z1.jpg']['kategorie'], 'koerper', 'von Hand gestellt: bleibt')
            self.assertEqual(nach['alt_z1.jpg']['kamera_bekannt']['fov'], 30.0, 'die Kamera gilt trotzdem')
            self.assertNotIn('kamera_bekannt', nach['frei_z1.jpg'])
            self.assertEqual(nach['frei_z1.jpg']['teil'], 'haende', 'nie von Hand gestellt: Vorgabe greift')

    def test_3_schritt_und_bleiben(self):
        reihe = Bildmodelloptionen.REIHENFOLGE
        self.assertEqual(reihe[reihe.index('vorschau') + 1], 'textur')
        self.assertEqual(reihe[-1], 'speichern')
        self.assertEqual(Bildmodelloptionen.vorgaben()['textur'], 'foto')
        self.assertIn('proportionen_linien', Bildmodelloptionen.BLEIBEN)
        self.assertIn('bildtypen', Bildmodelloptionen.BLEIBEN)

    def test_4_fototextur_bilder_und_eintrag(self):
        job = _Job(_bilder())
        job.ergebnis = {'anpassung': {'regler': {'Height': 0.4}}, 'rest': {'regler': 'eigen:pruef'}}
        ft = Bildmodellfototextur(job, _Ablage(), {})
        self.assertEqual([b['datei'] for b in ft.bilder()], ['vorn.jpg', 'hinten.jpg', 'gesicht.jpg'])
        self.assertEqual(ft.stellung(), {'Height': 0.4, 'eigen:pruef': 1.0})
        e = ft._eintrag(job.bilder[1])
        self.assertEqual((e['kamera']['cx'], e['kamera']['cy']), (500.0, 800.0),
                         'Zuschnitt verschiebt den Hauptpunkt')
        self.assertAlmostEqual(e['kamera']['t'][2], 3.0)
        self.assertNotIn('teile', e)
        g = ft._eintrag(job.bilder[2])
        self.assertNotIn('kamera', g)
        self.assertEqual(g['teile'], [0], 'Gesicht → Kopf')
        job.bilder[1].pop('kamera_bekannt')
        self.assertEqual([b['datei'] for b in ft.bilder()], ['vorn.jpg', 'gesicht.jpg'],
                         'ohne Kamera und Rig draußen')
