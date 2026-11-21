# -*- coding: utf-8 -*-
"""Hautbackenkernbau — die CUDA-Kerne des lokalen Backers (`hautbackenkerne_cu/`) übersetzen und laden (21.11.2026, Edgar: „Warp überall raus“).

Bis dahin rund 65 Warp-Kerne in diesem Paket (Rastern, Strahlen, Kontext, Bild, Knoten, Closure, Ausgabe). `-fmad=true` wie Warps Vorgabe; die Rechnungen in Warps Form
(`wp17.cuh`). Der Strahl auf den Körper: `Assets/kartenkoepfe/kartenstrahl.cuh` über GarmentCodes `Dreiecksbaum` (beide Köpfe gehen in den Fingerabdruck).
Bauweg `Kernruf`: DLL in `ProjektTemp/xpbdkerne/<Fingerabdruck>/hautbackenkerne.dll`, gerufen über ctypes auf dem Strom von torch.
Felder: vec2/vec3/vec4 als (n, 2|3|4) float32, Dreiecke (m, 3) int32, Bilder (h, w, 3) uint8 — zusammenhängend auf der Karte.
"""
import os
import sys

if r'A:\3DTools' not in sys.path:
    sys.path.append(r'A:\3DTools')
from Assets.GarmentCode.xpbdtorch.kernruf import Kernruf  # noqa: E402

__all__ = ['Hautbackenkernbau']

P, I, F = Kernruf.P, Kernruf.I, Kernruf.F
GARMENT = os.path.join(r'A:\3DTools', 'Assets', 'GarmentCode', 'flaechen_cu')
KOPFORDNER = os.path.join(r'A:\3DTools', 'Assets', 'kartenkoepfe')


class Hautbackenkernbau(Kernruf):
    QUELLEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hautbackenkerne_cu')
    NAME = 'hautbackenkerne'
    SCHALTER = Kernruf.SCHALTER + ('-I', GARMENT, '-I', KOPFORDNER)
    KOEPFE = (os.path.join(GARMENT, 'abfrage.cuh'), os.path.join(GARMENT, 'wpmath.cuh'), os.path.join(KOPFORDNER, 'kartenstrahl.cuh'))
    #: Argumente nach dem Strom wie in den `extern "C"`-Köpfen der .cuh-Dateien
    FUNKTIONEN = {
        # hautbackenkern.cuh
        'hb_rastern': [I, P, P, I, F, F, P, P],
        'hb_schiessen': [I] + [P] * 10 + [F, F, P, P, P],
        'hb_erweitern': [I, I, P, P, P, I, P, P],
        'hb_holen': [I] + [P] * 7,
        'hb_schreiben_farbe': [I, P, P, P],
        'hb_schreiben_rauheit': [I, P, P, P],
        'hb_schreiben_normale': [I] + [P] * 8,
        'hb_nullen': [I, P, F, P, P],
        'hb_korrektur_noetig': [I] + [P] * 5,
        'hb_rueckdrehen': [I, P, P, P],
        'hb_f_zu_v': [I, P, P],
        'hb_c_zu_f': [I, P, F, F, F, P],
        'hb_v_zu_f': [I, P, P],
        'hb_packen': [I, P, P],
        # hautkontextkern.cuh
        'hb_geometrie': [I] + [P] * 12,
        'hb_differenzial': [I] + [P] * 8 + [I] + [P] * 3,
        'hb_differenzial_uv': [I] + [P] * 10,
        'hb_attribut2': [I] + [P] * 11,
        'hb_attribut4': [I] + [P] * 11,
        'hb_normale_unnormiert': [I] + [P] * 7,
        'hb_glatt_je_treffer': [I] + [P] * 3,
        'hb_tangente_interpoliert': [I] + [P] * 7,
        'hb_verteilen_vec3': [I] + [P] * 3,
        # hauttexturkern.cuh
        'hb_abtasten': [I, P, I, I, P, I, I, I, I, P],
        # hautclosurekern.cuh
        'hb_normale_mittel': [I] + [P] * 19 + [I] + [P] * 4 + [I] * 3 + [P] * 9,
        # hautknotenaus.cuh
        'hb_farbattribut': [I, P, P, P, I, F, P, P, P],
        'hb_bild_trennen': [I, P, P, P],
        'hb_uv_koordinate': [I, P, P, P, I, F, P],
        'hb_bereich_zahl': [I] + [P] * 6 + [I, I, P],
        'hb_bereich_vektor': [I] + [P] * 6 + [I, I, P],
        'hb_klemmen': [I, P, P, P, I, P],
        'hb_bump': [I] + [P] * 8 + [F, I, P],
        'hb_hsv': [I] + [P] * 6,
        'hb_helligkeit': [I] + [P] * 4,
        'hb_gamma': [I] + [P] * 3,
        'hb_invertieren': [I] + [P] * 3,
        'hb_abbilden': [I, P, P, P, P, I, P],
        'hb_mathe': [I, P, P, P, I, I, P],
        'hb_vektor_mathe': [I, P, P, P, P, I, P, P],
        'hb_mix_farbe': [I, P, P, P, I, I, I, P],
        'hb_mix_alt': [I, P, P, P, I, I, P],
        'hb_mix_zahl': [I, P, P, P, I, P],
        'hb_mix_vektor': [I, P, P, P, I, P],
        'hb_mix_vektor_ungleich': [I, P, P, P, I, P],
        'hb_normalkarte': [I] + [P] * 9 + [I, P],
        'hb_normalkarte_fest': [I, P, P, P, P, I, P],
        'hb_rampe': [I, P, P, I, I, P, P],
        'hb_kurven': [I, P, P, P, F, F, I, I, P],
        'hb_kurve': [I, P, P, P, F, F, I, I, P],
        'hb_farbe_trennen': [I, P, I, P, P, P],
        'hb_farbe_zusammen': [I, P, P, P, I, P],
        'hb_trennen_xyz': [I] + [P] * 4,
        'hb_zusammen_xyz': [I] + [P] * 4,
    }
    _dll = None

    @classmethod
    def lauf(cls, name, *args):
        u"""`rufen` auf dem Strom der Karte 0 (der Backer rechnet auf einer Karte)."""
        import torch
        with torch.cuda.device(0):
            cls.rufen(name, *args)
