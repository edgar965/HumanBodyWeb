# -*- coding: utf-8 -*-
u"""Smplvarianten — SMPL-Koerper anderer Form, so abgelegt, wie GarmentCode
sie zum Drapieren braucht.

WARUM (Edgar, 06.09.2026: „5 Testfälle für das Fitting mit unterschiedlichen
SMPL Modellen"): GarmentCode liefert nur die Durchschnittskoerper. Eine
Variante entsteht hier aus dem SMPL-Modell des Projekts (`smplkoerper.py`:
Blendshapes + A-Haltung 40 Grad, gegen den A40-Koerper des Tools geprueft)
und bekommt ihre Masse RELATIV zur Tool-YAML (`smplmasse.py`).

Abgelegt wird in `GarmentCode/koerper/smpl/`: `<name>.obj` (Meter, Y oben —
GarmentCodes Lage, nichts gedreht), `<name>.yaml` und daneben die
`smpl_vert_segmentation.json` des Tools. `PathCofig(smpl_body=True)` findet
dort alles. Der Name traegt Geschlecht und einen Fingerabdruck der Betas.
"""

import hashlib
import json
import logging
import os
import shutil

import numpy as np
from django.conf import settings

logger = logging.getLogger('core')


class Smplvarianten:
    u"""Erzeugt, benennt und legt SMPL-Varianten ab."""

    #: Woher das SMPL-Modell kommt (VideoToBVH/models/smpl).
    MODELLE = str(settings.SMPL_MODELS_DIR)

    #: Der Durchschnittskoerper des Tools je Geschlecht — er traegt die YAML.
    DURCHSCHNITT = {'female': 'f_smpl_average_A40', 'male': 'm_smpl_average_A40'}

    _modelle = {}
    _erzeugt = {}

    @staticmethod
    def ordner():
        from GarmentCode.koerperablage import Koerperablage
        return os.path.join(Koerperablage.ORDNER, 'smpl')

    @classmethod
    def name(cls, geschlecht, betas):
        b = np.zeros(10)
        betas = np.asarray(betas or [], dtype=np.float64)
        b[:min(10, len(betas))] = betas[:10]
        rohbytes = np.round(b, 3).astype(np.float32).tobytes()
        kennung = hashlib.sha1(rohbytes).hexdigest()[:12]
        return 'smpl_%s_%s' % (geschlecht[0], kennung)

    @classmethod
    def ist_variante(cls, name):
        return str(name).startswith('smpl_')

    # ------------------------------------------------------------- erzeugen

    @classmethod
    def modell(cls, geschlecht):
        from GarmentCode.smplkoerper import Smplkoerper
        if geschlecht not in cls._modelle:
            cls._modelle[geschlecht] = Smplkoerper.laden(geschlecht, cls.MODELLE)
        return cls._modelle[geschlecht]

    @classmethod
    def erzeugen(cls, geschlecht, betas):
        u"""Koerper, Masse und Ablage einer Variante.

        Rueckgabe: {name, ordner, geschlecht, betas, punkte (Meter, Y oben),
        dreiecke, hoehe, masse, herkunft}.
        """
        from GarmentCode.koerperablage import Koerperablage
        from GarmentCode.smplmasse import Smplmasse
        from .smplfigur import Smplfiguren

        name = cls.name(geschlecht, betas)
        if name in cls._erzeugt:
            return cls._erzeugt[name]

        modell = cls.modell(geschlecht)
        v = modell.a40(betas)
        v_avg = modell.a40(None)
        seg_datei = os.path.join(Smplfiguren.ordner(), 'smpl_vert_segmentation.json')
        with open(seg_datei, 'r', encoding='utf-8') as quelle:
            seg = json.load(quelle)
        yaml_avg = Smplfiguren.masse(cls.DURCHSCHNITT[geschlecht])
        # Die Armlaenge kommt aus den SMPL-Gelenken, nicht aus der YAML: dort
        # stehen 80 cm bei 165 cm Koerpergroesse (siehe Smplkoerper.armlaenge).
        masse, herkunft = Smplmasse(seg).relativ(
            v, v_avg, yaml_avg, zusatz={'arm_length': modell.armlaenge(betas)})

        ordner = cls.ordner()
        os.makedirs(ordner, exist_ok=True)
        ziel_seg = os.path.join(ordner, 'smpl_vert_segmentation.json')
        if not os.path.isfile(ziel_seg):
            shutil.copy(seg_datei, ziel_seg)
        if not os.path.isfile(os.path.join(ordner, name + '.obj')):
            # Koerperablage rechnet Projekt -> GarmentCode; die Punkte hier
            # SIND schon GarmentCode-Lage, also erst hin, damit sie zurueck
            # genau so landen.
            Koerperablage(name, Smplmasse.projekt(v), modell.faces,
                          ordner=ordner).ablegen(masse)
        daten = {
            'name': name, 'ordner': ordner, 'geschlecht': geschlecht,
            'betas': [float(x) for x in (betas or [])],
            'punkte': v, 'dreiecke': modell.faces,
            'hoehe': float(v[:, 1].max() - v[:, 1].min()),
            'masse': masse, 'herkunft': herkunft,
        }
        cls._erzeugt[name] = daten
        logger.info('SMPL-Variante %s: %s, Betas %s, %.1f cm, Taille %.0f cm',
                    name, geschlecht, daten['betas'], daten['hoehe'] * 100,
                    masse.get('waist', 0))
        return daten

    @classmethod
    def aus_reglern(cls, geschlecht, groesse=0.0, fuelle=0.0):
        u"""Der Weg, den das Bedienfeld geht: zwei Regler statt zehn Betas.

        Die Umrechnung samt der je Geschlecht verschiedenen Vorzeichen steht
        in `GarmentCode/smplform.py` — dort auch, warum sie gemessen und
        nicht geraten ist.
        """
        from GarmentCode.smplform import Smplform
        return cls.erzeugen(geschlecht, Smplform.betas(geschlecht, groesse, fuelle))

    @classmethod
    def masse(cls, name):
        u"""Die abgelegten Masse einer Variante (aus ihrer YAML)."""
        import yaml
        pfad = os.path.join(cls.ordner(), name + '.yaml')
        with open(pfad, 'r', encoding='utf-8') as quelle:
            return yaml.safe_load(quelle)['body']

    @classmethod
    def netz(cls, name):
        u"""Punkte (Meter, Y oben) und Dreiecke einer abgelegten Variante."""
        from GarmentCode.anziehen import Anziehen
        return Anziehen.netz_lesen(os.path.join(cls.ordner(), name + '.obj'),
                                   aus_garmentcode=False)

    @classmethod
    def geschlecht(cls, name):
        u"""Das Geschlecht steckt im Namen (`smpl_m_…` / `smpl_f_…`)."""
        kurz = str(name).split('_')[1:2]
        return 'male' if kurz and kurz[0] == 'm' else 'female'

    @classmethod
    def vorhanden(cls, name):
        return (cls.ist_variante(name)
                and os.path.isfile(os.path.join(cls.ordner(), name + '.obj')))
