# -*- coding: utf-8 -*-
"""Bildmodellkopfkatalog — die Felder des Schritts „Kopf" und die Verfügbarkeit der Verfahren.

Edgar (22.09.2026): „Mach eine eigene Pipeline für den Kopf, wo ich FLAME und KeenTools
FaceBuilder auswählen kann, FLAME mit MICA und was es sonst noch gibt, und mehrere Fotos
auswählen kann für den Kopf." — und danach: „mach FaceBuilder OHNE Handarbeit im Blender,
automatisch, ggf. minimale Handarbeit in unserem UI." Der Schritt `kopf` (`Bildmodellkopf`)
liegt zwischen Schätzung und Zielnetz; sein Ergebnis ist immer ein FLAME-Kopf (5.023 Punkte),
damit Zielnetz und Kopf-Fit unverändert weiterlaufen.

    kopfverfahren   mica          FLAME aus MICA (ArcFace → 300 Formparameter, metrisch;
                                  `_run_mica.py`, python10, ~8 s je Bild nach dem Laden)
                    mehrbild      Automatischer Ersatz für FaceBuilder: EIN FLAME-Kopf,
                                  gleichzeitig an ALLE gewählten Fotos angepasst
                                  (`_run_flame_mehrbild.py`: insightface-Gesichtspunkte je
                                  Foto, Bündelausgleichung mit schwacher Perspektive) — kein
                                  Blender, keine Pins; am besten mit mehreren Ansichten
                    pymafx_flame  FLAME aus PyMAF-X (wie der frühere Knopf „Kopf (FLAME)")
                    keiner        kein eigener Kopf; der Kopf kommt aus den Körperparametern
    kopfmischung    mittel        mehrere Fotos bei `mica`/`pymafx_flame`: Mittel der
                                  Formparameter bzw. der ausgerichteten Punkte
                    erstes        nur das erste gewählte Foto (ohne Wirkung bei `mehrbild` —
                                  das nutzt immer alle gewählten Fotos gemeinsam)

Die Fotos wählt das Häkchen „Kopf" je Bild (`kopf_an`, `Bildmodellbildtypen.stellen`) — die
einzige Handarbeit, die bleibt; ohne Häkchen die Kopf-Hauptbilder, dann alle Kopfbilder außer
der Rückansicht.
"""
import os

from ..daten.wrapperpfad import Wrapperpfad

__all__ = ['Bildmodellkopfkatalog']


class Bildmodellkopfkatalog:
    FELDER = [
        (
            'kopfverfahren',
            'Kopfverfahren',
            [
                ('mica', 'FLAME aus MICA',
                 'Metrische Kopfform aus dem Gesicht (ArcFace → 300 FLAME-Parameter); mehrere Fotos '
                 'werden gemittelt; ~8 s je Bild'),
                ('mehrbild', 'Mehrbild-Anpassung (automatisch, ohne Blender)',
                 'FLAME wird automatisch an die erkannten Gesichtspunkte ALLER gewählten Fotos '
                 'gemeinsam angepasst — der Ersatz für KeenTools FaceBuilder, ohne Blender und ohne '
                 'Pins von Hand. Am besten mit mehreren Ansichten (vorn + Seite), ~1–2 min'),
                ('pymafx_flame', 'FLAME aus PyMAF-X',
                 '100 Formparameter des Gesichts aus dem Körperschätzer — wie der frühere Knopf „Kopf (FLAME)"'),
                ('keiner', 'Aus dem Körperschätzer', 'Kein eigener Kopf; Kopf aus den 10 Körperparametern'),
            ],
            'mica',
        ),
        (
            'kopfmischung',
            'Mehrere Kopffotos',
            [
                ('mittel', 'Mittel der Köpfe', 'Formparameter (MICA) bzw. ausgerichtete Punkte (PyMAF-X) gemittelt'),
                ('erstes', 'Nur das erste Foto', 'Das erste gewählte Foto in Tabellenreihenfolge'),
            ],
            'mittel',
        ),
    ]

    #: Was MICA zusätzlich braucht (relativ zu `VideoToBVH/MICA`) — Mehrbild kommt ohne aus.
    MICA_GEWICHTE = ('data', 'pretrained', 'mica.tar')
    FLAME_MODELL = ('data', 'FLAME2020', 'generic_model.pkl')
    INSIGHTFACE = os.path.join(os.path.expanduser('~'), '.insightface', 'models', 'antelopev2')

    @classmethod
    def mica_ordner(cls):
        return os.path.join(os.path.dirname(Wrapperpfad.pfad()), 'MICA')

    @classmethod
    def verfuegbarkeit(cls, pymafx):
        """`{(feld, wert): (verfügbar, grund)}` — `pymafx` ist der Stand des Körperschätzers."""
        aus = {('kopfverfahren', 'pymafx_flame'): pymafx}
        ordner = cls.mica_ordner()
        if not os.path.isdir(ordner):
            fehlt_flame2020 = 'MICA nicht eingelagert (VideoToBVH/MICA)'
            aus[('kopfverfahren', 'mica')] = (False, fehlt_flame2020)
            aus[('kopfverfahren', 'mehrbild')] = (False, fehlt_flame2020)
            return aus
        flame2020_da = os.path.isfile(os.path.join(ordner, *cls.FLAME_MODELL))
        insightface_da = os.path.isdir(cls.INSIGHTFACE)
        # `mehrbild` braucht nur FLAME2020 (das Kopfmodell) und insightface (Gesichtspunkte) —
        # kein MICA-Netz.
        fehlt = ([] if flame2020_da else [os.path.join(*cls.FLAME_MODELL)]) \
            + ([] if insightface_da else ['~/.insightface/models/antelopev2'])
        aus[('kopfverfahren', 'mehrbild')] = (not fehlt, ('fehlt: ' + ', '.join(fehlt)) if fehlt else '')
        # `mica` zusätzlich das Netz selbst.
        fehlt_mica = fehlt + ([] if os.path.isfile(os.path.join(ordner, *cls.MICA_GEWICHTE))
                              else [os.path.join(*cls.MICA_GEWICHTE)])
        aus[('kopfverfahren', 'mica')] = (not fehlt_mica, ('fehlt: ' + ', '.join(fehlt_mica)) if fehlt_mica else '')
        return aus
