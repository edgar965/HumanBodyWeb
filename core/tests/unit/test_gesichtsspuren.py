# -*- coding: utf-8 -*-
"""Jeder Weg durch `Gesichtsformen` liefert denselben Datensatz.

DER BEFUND (02.09.2026, Code Review)
====================================
Beim Umbau auf `Bewegungsspuren` (01.09.2026) wurden zwei der drei
Rückgaben in `face_blendshapes.py` umgestellt — die dritte nicht. Der
Zweig für die leere Ausdrucksreihe gab weiter ein Wörterbuch zurück::

    fc = len(expression_frames)
    if fc == 0:
        return {'duration': 0, 'times': [], 'tracks': {},
                'frame_count': 0, 'mapped_bones': []}

Wer das Ergebnis an `merge_retargeted` weiterreicht, bekommt
``AttributeError: 'dict' object has no attribute 'tracks'`` — genau die
Sorte Fehler, gegen die der Datensatz eingeführt wurde. Kein Werkzeug
sieht ihn: Die Form stimmt ja, es ist nur der falsche Typ, und
`Gesichtsformen` wird heute aus HumanBodyWeb nirgends gerufen. Er wäre
beim ersten Gesichtsdurchlauf ohne Bilder aufgeschlagen.

WAS GEPRÜFT WIRD
================
Alle drei Wege (leer, gefüllt, Altformat) geben `Bewegungsspuren`, und
das leere Ergebnis lässt sich mischen, ohne zu werfen. Der letzte Punkt
ist der eigentliche: Er prüft nicht den Typ, sondern dass der Weg
durchläuft.
"""
from django.test import SimpleTestCase

from humanbody_core.skeleton.bewegungsspuren import Bewegungsspuren
from humanbody_core.skeleton.face_blendshapes import Gesichtsformen
from humanbody_core.skeleton.retarget.zusammenfuegen import merge_retargeted


#: Zehn SMPL-X-Ausdruckswerte je Bild — die Form, die SMPLest-X liefert.
EIN_BILD = [0.0] * 10


class JederWegLiefertDenDatensatz(SimpleTestCase):
    """Leer, gefüllt und Altformat geben dieselbe Sorte Ergebnis."""

    def test_eine_leere_ausdrucksreihe_gibt_bewegungsspuren(self):
        raus = Gesichtsformen.expression_to_bone_tracks([], fps=30.0)
        self.assertIsInstance(raus, Bewegungsspuren)

    def test_das_leere_ergebnis_hat_keine_bilder(self):
        raus = Gesichtsformen.expression_to_bone_tracks([], fps=30.0)
        self.assertEqual(raus.frame_count, 0)
        self.assertEqual(raus.tracks, {})

    def test_eine_gefuellte_reihe_gibt_bewegungsspuren(self):
        raus = Gesichtsformen.expression_to_bone_tracks([EIN_BILD] * 4,
                                                        fps=30.0)
        self.assertIsInstance(raus, Bewegungsspuren)
        self.assertEqual(raus.frame_count, 4)

    def test_das_altformat_gibt_bewegungsspuren(self):
        raus = Gesichtsformen.blendshapes_to_bone_tracks(
            {'blendshape_names': ['jawOpen'], 'frames': []})
        self.assertIsInstance(raus, Bewegungsspuren)

    def test_jeder_weg_traegt_alle_sechs_felder(self):
        for reihe in ([], [EIN_BILD] * 2):
            raus = Gesichtsformen.expression_to_bone_tracks(reihe, fps=30.0)
            self.assertEqual(sorted(raus.als_dict()),
                             sorted(Bewegungsspuren.FELDER),
                             'Reihe mit %d Bildern' % len(reihe))


class EinLeeresGesichtBrichtDasMischenNicht(SimpleTestCase):
    """Der Fall, an dem der Befund wirklich hing.

    Nicht der Typ ist das Ziel dieser Prüfung, sondern der Durchlauf:
    Vor der Reparatur warf `Spurenmischer` hier `AttributeError`.
    """

    @staticmethod
    def koerper(bilder=3):
        """Eine Körperaufnahme, wie sie aus dem Retarget käme."""
        return Bewegungsspuren(
            duration=bilder / 30.0,
            times=[i / 30.0 for i in range(bilder)],
            tracks={'DEF-spine': [0.0, 0.0, 0.0, 1.0] * bilder},
            frame_count=bilder,
            mapped_bones=['DEF-spine'],
        )

    def test_ein_leeres_gesicht_laesst_sich_mischen(self):
        gemischt = merge_retargeted(self.koerper(),
                                    Gesichtsformen.expression_to_bone_tracks(
                                        [], fps=30.0))
        self.assertIsInstance(gemischt, Bewegungsspuren)

    def test_der_koerper_bleibt_dabei_vollstaendig(self):
        gemischt = merge_retargeted(self.koerper(bilder=5),
                                    Gesichtsformen.expression_to_bone_tracks(
                                        [], fps=30.0))
        self.assertEqual(gemischt.frame_count, 5)
        self.assertIn('DEF-spine', gemischt.tracks)

    def test_ein_woerterbuch_wuerde_hier_werfen(self):
        """Die Gegenprobe: Mit dem alten Rückgabewert bricht es.

        Ohne sie könnte die Prüfung oben grün melden, weil `mischen`
        Wörterbücher irgendwann doch verträgt — dann prüft sie nichts
        mehr.
        """
        altes_ergebnis = {'duration': 0, 'times': [], 'tracks': {},
                          'frame_count': 0, 'mapped_bones': []}
        with self.assertRaises(AttributeError):
            merge_retargeted(self.koerper(), altes_ergebnis)
