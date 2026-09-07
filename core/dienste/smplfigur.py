# -*- coding: utf-8 -*-
u"""Smplfiguren — die Referenzkoerper von GarmentCode als Figur der Szene.

WARUM (Edgar, 06.09.2026: „keine experimente, baue erstmal das Online tool
nach!"): Das Online-Tool (garmentcode.ethz.ch, `upstream/gui/gui_pattern.py`)
drapiert auf `mean_all` — GarmentCodes eigenem Durchschnittskoerper — mit den
handvermessenen Massen aus `mean_all.yaml` und der Segmentierung
`ggg_body_segmentation.json`. Nichts wird gemessen. Genau diese Koerper
werden hier angeboten, `mean_all` voran; dazu die SMPL-Durchschnittskoerper
(`f_/m_smpl_average_A40`), fuer die GarmentCode ebenfalls Masse und eine
eigene Segmentierung (`smpl_vert_segmentation.json`) mitbringt.

Damit laeuft der GarmentCode-Reiter auf dieser Figur exakt so wie das Tool:
Schnitt aus den vorgegebenen Massen, Drapierung mit der zum Koerper
gehoerenden Segmentierung, keine Messung, keine Nachkorrektur. Was dabei
herauskommt, ist der Massstab fuer alles andere.

Die Koerper liegen im Upstream-Klon und werden nur gelesen.
"""

import logging
import os

logger = logging.getLogger('core')


class Smplfiguren:
    u"""Lesender Zugang zu GarmentCodes Referenzkoerpern."""

    #: Name -> Geschlecht, Segmentierung, Anzeige. `smpl` sagt, ob die
    #: Drapierung `smpl_vert_segmentation.json` braucht (SMPL-Topologie,
    #: 6.890 Punkte) oder `ggg_body_segmentation.json` (GarmentCodes eigenes
    #: Koerpermodell, 23.752 Punkte). Reihenfolge = Reihenfolge im Dialog.
    KOERPER = {
        'mean_all': {'geschlecht': 'female', 'smpl': False,
                     'anzeige': 'mean_all — Körper des Online-Tools'},
        'mean_female': {'geschlecht': 'female', 'smpl': False,
                        'anzeige': 'mean_female (GarmentCode)'},
        'mean_male': {'geschlecht': 'male', 'smpl': False,
                      'anzeige': 'mean_male (GarmentCode)'},
        'f_smpl_average_A40': {'geschlecht': 'female', 'smpl': True,
                               'anzeige': 'SMPL weiblich (Durchschnitt, A-Pose 40°)'},
        'm_smpl_average_A40': {'geschlecht': 'male', 'smpl': True,
                               'anzeige': 'SMPL männlich (Durchschnitt, A-Pose 40°)'},
    }

    @staticmethod
    def ordner():
        from GarmentCode.entwurf import Entwurf
        return os.path.join(Entwurf.REPO, 'assets', 'bodies')

    @classmethod
    def kennt(cls, name):
        from .smplvarianten import Smplvarianten
        return name in cls.KOERPER or Smplvarianten.vorhanden(name)

    @classmethod
    def ist_smpl(cls, name):
        u"""Braucht dieser Koerper die SMPL-Segmentierung?"""
        from .smplvarianten import Smplvarianten
        if Smplvarianten.ist_variante(name):
            return True          # Varianten sind SMPL-Netze, immer.
        return bool(cls.KOERPER.get(name, {}).get('smpl'))

    @classmethod
    def geschlecht(cls, name):
        from .smplvarianten import Smplvarianten
        if Smplvarianten.ist_variante(name):
            return Smplvarianten.geschlecht(name)
        return cls.KOERPER.get(name, {}).get('geschlecht', 'female')

    @classmethod
    def liste(cls):
        u"""Die verfuegbaren Koerper mit dem, was die Seite zum Anzeigen braucht."""
        aus = []
        for name, angaben in cls.KOERPER.items():
            obj = os.path.join(cls.ordner(), name + '.obj')
            yaml_datei = os.path.join(cls.ordner(), name + '.yaml')
            if not os.path.isfile(obj):
                continue
            aus.append({
                'name': name,
                'anzeige': angaben['anzeige'],
                'geschlecht': angaben['geschlecht'],
                'smpl': angaben['smpl'],
                'bytes': os.path.getsize(obj),
                'masse_vorhanden': os.path.isfile(yaml_datei),
            })
        return aus

    @classmethod
    def masse(cls, name):
        u"""Die vorgegebenen Masse des Koerpers (dict, Zentimeter)."""
        import yaml
        from .smplvarianten import Smplvarianten
        cls._pruefen(name)
        if Smplvarianten.ist_variante(name):
            return Smplvarianten.masse(name)
        with open(os.path.join(cls.ordner(), name + '.yaml'), 'r',
                  encoding='utf-8') as quelle:
            return yaml.safe_load(quelle)['body']

    @classmethod
    def netz(cls, name):
        u"""Punkte (Meter, Y oben — so wie GarmentCode und Three.js rechnen)
        und Dreiecke. Vierecke werden geteilt."""
        from GarmentCode.anziehen import Anziehen
        from .smplvarianten import Smplvarianten
        cls._pruefen(name)
        if Smplvarianten.ist_variante(name):
            return Smplvarianten.netz(name)
        punkte, dreiecke = Anziehen.netz_lesen(
            os.path.join(cls.ordner(), name + '.obj'), aus_garmentcode=False)
        return punkte, dreiecke

    @classmethod
    def _pruefen(cls, name):
        if not cls.kennt(name):
            raise ValueError('Unbekannter Referenzkoerper: %r' % (name,))
