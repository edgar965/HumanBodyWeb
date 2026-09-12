# -*- coding: utf-8 -*-
u"""Effektquellen — was die Seite „Effekte" zur Auswahl stellt.

BVH-DATEIEN: die fertigen Auftraege von „Process Videos" — nur die, deren
Gelenke der Retargeter kennt (SMPL-Namen der 3D-Pipelines). MocapNET-BVHs
(2D-Pipelines, 165 Gelenke) stehen mit dabei, aber abgewaehlt, mit dem
Grund: Eine leere Liste saehe aus wie „nichts verarbeitet".

KLEIDER: die `.mhclo`-Dateien unter `garment_library/dresses` — der
MakeHuman-Bestand, den MPFB an die Figur anpasst.

MODELLE: die gespeicherten Figuren der Szene (`Modellvorlagen`), fuer die
Pipeline „HumanBody-Figur (DEF-Skelett)" — je Modell Koerpertyp, Stuecke
und Frisur, damit der Dialog zeigt, was man bekommt.

FORMAT: je BVH das Format, das der Retarget der Web-App erkennt
(`Skeleton.detect_format`) — die Figur-Pipeline nimmt alles Erkannte, auch
MocapNET; die Blender-Pipeline nur SMPL-Namen (`passt`).
"""
import os
from pathlib import Path

from django.conf import settings

from effekte.bvhnamen import Bvhnamen
from effekte.figur.modellfigur import Modellfigur
from ..dienste.modellvorlagen import Modellvorlagen
from ..models import BVHJob

__all__ = ['Effektquellen']


class Effektquellen:

    ENDUNG_KLEID = '.mhclo'
    HOECHSTENS = 60

    # -------------------------------------------------------------- BVH

    @classmethod
    def bvh_dateien(cls):
        u"""Fertige Auftraege mit BVH, neueste zuerst; `passt` sagt, ob der
        Retargeter die Gelenke kennt."""
        eintraege = []
        auftraege = (BVHJob.objects.filter(status='complete')
                     .exclude(bvh_file='').order_by('-created_at')[:cls.HOECHSTENS])
        for job in auftraege:
            pfad = str(job.bvh_file)
            if not os.path.isfile(pfad):
                continue
            namen = Bvhnamen.lesen(pfad)
            unbekannt = namen.unbekannte()
            eintraege.append({
                'pfad': pfad,
                'name': os.path.basename(pfad),
                'auftrag': job.name,
                'pipeline': job.get_pipeline_display(),
                'bilder': namen.bilder(),
                'bildrate': namen.bildrate(),
                'format': cls.format(namen.gelenke()),
                'passt': not unbekannt,
                'grund': ('' if not unbekannt else
                          '%d unbekannte Gelenke (%s …)' % (len(unbekannt), unbekannt[0])),
                'vorgewaehlt': False,
            })
        # Der neueste passende ist vorgewaehlt — so steht der Ausgabevorschlag
        # sofort da, statt erst nach einem Klick.
        for eintrag in eintraege:
            if eintrag['passt']:
                eintrag['vorgewaehlt'] = True
                break
        return eintraege

    @staticmethod
    def format(gelenke):
        u"""Name des erkannten BVH-Formats (CMU, SMPL, MOCAPNET …) oder ''."""
        from humanbody_core.skeleton import Skeleton
        bauart = Skeleton.detect_format(list(gelenke))
        return getattr(bauart, 'FORMAT', '') or '' if bauart else ''

    # ----------------------------------------------------------- Kleider

    @classmethod
    def kleider(cls):
        ordner = Path(settings.EFFEKTE_KLEIDER_DIR)
        if not ordner.is_dir():
            return []
        eintraege = []
        for unter in sorted(p for p in ordner.iterdir() if p.is_dir()):
            for datei in sorted(unter.glob('*' + cls.ENDUNG_KLEID)):
                eintraege.append({'pfad': str(datei), 'name': unter.name,
                                  'titel': cls.titel(unter.name)})
                break
        return eintraege

    @staticmethod
    def titel(name):
        return name.replace('_', ' ')

    # ----------------------------------------------------------- Modelle

    @classmethod
    def modelle(cls):
        u"""Die gespeicherten Modelle der Szene, mit dem, was der Film daraus
        macht: Koerpertyp, GarmentCode-Stuecke, Frisur."""
        eintraege = []
        for name in Modellvorlagen.namen():
            pfad = Modellvorlagen.pfad(name)
            try:
                modell = Modellfigur(str(pfad))
            except (OSError, ValueError):
                continue
            beschreibung = modell.beschreibung()
            beschreibung['name'] = name
            beschreibung['stuecke'] = [s for s in beschreibung['stuecke'] if s]
            eintraege.append(beschreibung)
        return eintraege
