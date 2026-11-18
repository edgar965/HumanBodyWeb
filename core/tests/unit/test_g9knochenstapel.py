# -*- coding: utf-8 -*-
"""Genesis 9: die gestapelte Knochenrechnung (`G9knochenstapel`, 18.11.2026) an Kunstdaten — in torch auf der Karte (Regel torch-statt-numpy).

Ohne Daz-Bibliothek. Fälle:
1. Reihenfolge wie die frühere Schleife: Figur zuerst, ein Kind vor seinem Elternteil in `roh`
   kommt nach ihm; ein Knochen mit unbekanntem Elternteil hängt an der Figur.
2. Drehung um die Knochenachsen: der lineare Teil eines gedrehten Knochens ist O · E · Oᵀ
   (`G9knochenmatrizen._drehung`, die Rechnung je Knochen); sein Kind erbt die Drehung.
3. Häutung mit einem Knochen ohne Matrix: Einheit, der Punkt bleibt (wie bis 18.11.2026).

Erwartete Gegenproben (nicht gelaufen): Ebenen nach Rohfolge statt Tiefe → Fall 1 rot;
Drehung nur E statt O·E·Oᵀ → Fall 2 rot; fehlender Knochen auf Zeile 0 statt Einheit → Fall 3 rot.
Ohne Karte übersprungen (die Rechnung legt ihre Felder auf `cuda`).
"""
import unittest

import torch
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.knochenmatrizen import G9knochenmatrizen  # noqa: E402
from Genesis9.knochenstapel import G9knochenstapel  # noqa: E402

KARTE = 'cuda'


def feld(werte):
    """Zahlen, Liste oder Tensor → float64 auf der Karte."""
    if isinstance(werte, torch.Tensor):
        return werte.detach().to(KARTE, torch.float64)
    return torch.tensor(werte, dtype=torch.float64, device=KARTE)


def knochen(name, eltern, kopf, erbt=False, orientation=None, reihenfolge='XYZ'):
    k = {'name': name, 'eltern': eltern, 'kopf': feld(kopf), 'schwanz': feld(kopf) - feld([0.0, 10.0, 0.0]),
         'erbt': erbt, 'reihenfolge': reihenfolge}
    if orientation is not None:
        k['orientation'] = feld(orientation)
    return k


def skelett():
    """`l_thigh` steht VOR seinem Elternteil `pelvis`; `fremd` hat ein Elternteil, das es nicht gibt."""
    return [
        knochen('l_thigh', 'pelvis', [10.0, 90.0, 0.0]),
        knochen('hip', None, [0.0, 100.0, 0.0], erbt=True),
        knochen('pelvis', 'hip', [0.0, 100.0, 0.0], orientation=[0.0, 30.0, 0.0], reihenfolge='YZX'),
        knochen('fremd', 'gibt_es_nicht', [0.0, 50.0, 0.0]),
    ]


class Haut:
    def __init__(self, knochen, index, gewicht):
        self.knochen, self.index, self.gewicht = knochen, index, gewicht


def gleich(ist, soll, atol):
    torch.testing.assert_close(feld(ist), feld(soll), atol=atol, rtol=0.0)


@unittest.skipUnless(torch.cuda.is_available(), 'ohne Karte: die Knochenrechnung legt ihre Felder auf cuda')
class Knochenstapel(SimpleTestCase):
    def test_1_reihenfolge_und_unbekanntes_elternteil(self):
        roh = skelett()
        plan = G9knochenstapel.plan(roh, 'Genesis9')
        self.assertEqual(plan.namen, ['Genesis9', 'hip', 'pelvis', 'l_thigh', 'fremd'])
        posen = {'Genesis9': {'translation/y': 5.0}, 'hip': {'translation/y': 10.0}}
        m = G9knochenmatrizen(posen, roh=roh).matrizen()
        self.assertEqual(list(m), plan.namen)
        # `fremd` folgt nur der Figur (5 cm), nicht der Hüfte (10 cm).
        gleich(feld(m['fremd'])[:3, 3], [0.0, 5.0, 0.0], atol=1e-9)
        gleich(feld(m['l_thigh'])[:3, 3], [0.0, 15.0, 0.0], atol=1e-9)

    def test_2_drehung_um_die_knochenachsen_wie_je_knochen(self):
        roh = skelett()
        km = G9knochenmatrizen({'pelvis': {'rotation/x': 30.0, 'rotation/z': -12.0}}, roh=roh)
        m = km.matrizen()
        soll = feld(km._drehung(roh[2], 'pelvis'))
        gleich(feld(m['pelvis'])[:3, :3], soll, atol=1e-12)
        gleich(feld(m['l_thigh'])[:3, :3], soll, atol=1e-12)          # das Kind erbt die Drehung
        # Das Gelenk des Beckens bleibt stehen (Drehpunkt), das des Oberschenkels dreht um das Becken.
        kopf = feld(m['pelvis']) @ feld([0.0, 100.0, 0.0, 1.0])
        gleich(kopf[:3], [0.0, 100.0, 0.0], atol=1e-9)
        knie = feld(m['l_thigh']) @ feld([10.0, 90.0, 0.0, 1.0])
        soll_knie = soll @ feld([10.0, -10.0, 0.0]) + feld([0.0, 100.0, 0.0])
        gleich(knie[:3], soll_knie, atol=1e-9)

    def test_3_haeutung_mit_knochen_ohne_matrix(self):
        km = G9knochenmatrizen({'Genesis9': {'scale/general': 2.0}}, roh=skelett())
        index = torch.tensor([[0, 0, 0, 0], [1, 0, 0, 0]], dtype=torch.int64, device=KARTE)
        gewicht = feld([[1.0, 0, 0, 0], [1.0, 0, 0, 0]])
        punkte = feld([[0.3, 0.4, 0.5], [0.0, 0.95, 0.0]])
        neu = feld(km.anwenden(punkte, Haut(['unbekannt', 'hip'], index, gewicht)))
        gleich(neu[0], punkte[0], atol=1e-12)
        gleich(neu[1], punkte[1] * 2.0, atol=1e-9)
