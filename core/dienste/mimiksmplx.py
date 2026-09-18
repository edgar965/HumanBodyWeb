# -*- coding: utf-8 -*-
"""Mimiksmplx — `static/mimik/smplx_basis.json` aus MB-Lab und dem SMPL-X-Modell.

Edgar, 16.09.2026: „Mimik auch auf SMPL-X." Was `manage.py mimik_vorbereiten`
fuer die DEF-Knochen in `basis.json` legt, liegt fuer SMPL-X hier als
Verschiebungsfeld je Einheit — gerechnet von `SMPL/xmimik.py` (Landmarken,
Zylinderebene, Thin-Plate-Spline). Dieser Dienst sammelt nur die Zutaten:
HumanBody-Ruhenetz und Hautgewichte, DEF-Skelett, MB-Lab-Einheiten, das
weibliche SMPL-X-Modell (die Topologie ist bei allen Geschlechtern dieselbe,
die Felder gelten fuer alle SMPL-X-Koerper des Studios).
"""

import json

import numpy as np

__all__ = ['Mimiksmplx']


class Mimiksmplx:
    DATEI = 'smplx_basis.json'
    #: Das Modell, an dem die Felder gerechnet werden.
    GESCHLECHT = 'female'

    @classmethod
    def vorhanden(cls):
        from .smplxrig import Smplxrig

        return Smplxrig.vorhanden(cls.GESCHLECHT)

    @classmethod
    def uebertrag(cls, einheiten, daten):
        """Der fertige `Smplxmimik` — `daten` ist der HumanBody-Datenordner."""
        from humanbody_core.mimik.kopflandmarken import Kopflandmarken
        from SMPL.xkopf import SmplxKopf
        from SMPL.xmimik import Smplxmimik

        from .smplxrig import Smplxrig

        punkte = np.load(str(daten / 'vertices_tpose.npy')).astype(np.float64)
        drei = np.column_stack([punkte[:, 0], punkte[:, 2], -punkte[:, 1]])
        with open(daten / 'skin_weights_base.json', encoding='utf-8') as datei:
            haut = json.load(datei)
        with open(daten / 'def_skeleton.json', encoding='utf-8') as datei:
            skelett = json.load(datei)
        quelle = Kopflandmarken(drei, haut, skelett, einheiten, np.load(str(daten / 'faces.npy')))
        ziel = SmplxKopf.aus_modell(Smplxrig.koerper(cls.GESCHLECHT), Smplxrig.ordner())
        return Smplxmimik(quelle, ziel)

    @classmethod
    def schreiben(cls, einheiten, daten, ziel):
        """Die Datei anlegen; Rueckgabe: Bericht des Uebertrags plus Zahlen."""
        uebertrag = cls.uebertrag(einheiten, daten)
        felder = uebertrag.felder(einheiten)
        with open(ziel / cls.DATEI, 'w', encoding='utf-8') as datei:
            json.dump(felder, datei, separators=(',', ':'))
        bericht = uebertrag.bericht()
        bericht['einheiten'] = len(felder)
        bericht['punkte'] = max((len(r['i']) for e in felder.values() for r in e.values()), default=0)
        return bericht
