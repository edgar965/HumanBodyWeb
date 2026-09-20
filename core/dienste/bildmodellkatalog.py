# -*- coding: utf-8 -*-
"""Bildmodellkatalog — die Felder je Schritt mit ihren Alternativen.

Aus `Bildmodelloptionen` herausgelöst (19.09.2026, die Datei stand bei 337
Zeilen): hier steht NUR die Tabelle — je Schritt `(feld, name, [(wert, name,
erklärung)], vorgabe)` — und die Verfügbarkeit der Schätzer, die
`Bildmodelloptionen.katalog()` daran hängt (`photo_analyzer.get_all_status()`,
GVHMR-Wurzel). Ein Schätzer ohne Gewichte steht ausgegraut mit Grund.
Die Felder der Sichtung liegen in `Bildmodellsichtungskatalog`, die von Zielnetz und
Textur in `Bildmodellzielkatalog` (20.09.2026, die Datei stand bei 295 Zeilen).
"""

import logging
import os

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellpersonkatalog import Bildmodellpersonkatalog
from .bildmodellsichtungskatalog import Bildmodellsichtungskatalog
from .bildmodellzielkatalog import Bildmodellzielkatalog

logger = logging.getLogger('core')

__all__ = ['Bildmodellkatalog']


class Bildmodellkatalog:
    _zustand = None

    FELDER = {
        'sichtung': Bildmodellsichtungskatalog.FELDER,
        'schaetzung': [
            (
                'koerper',
                'Körperschätzer',
                [
                    ('gvhmr', 'GVHMR (Standvideo je Bild)',
                     'SMPL-X mit Rig und Weltlage je Körper-Hauptbild; Häkchen „Verwenden" in der Tabelle; '
                     '~60 s je Bild beim ersten Mal, danach liest der Lauf das Ergebnis'),
                    ('smplest_x', 'SMPLest-X', 'SMPL-X aus jedem Hauptbild; 8-GB-Modell, ~45 s Laden'),
                    ('pymafx', 'PyMAF-X', 'SMPL-X mit FLAME-Gesichtsform; braucht den openpifpaf-Detektor'),
                    ('hmr2', 'HMR 2.0', 'SMPL (Körper); Gesicht neutral'),
                    ('mediapipe', 'MediaPipe-Ausgleich', 'Nur Längenverhältnisse aus 33 Landmarken'),
                    ('keiner', 'Keiner', 'Nur die Grundfigur'),
                ],
                'smplest_x',
            ),
            (
                'gesicht',
                'Gesichtsform',
                [
                    ('pymafx_flame', 'FLAME aus PyMAF-X', '100 Formparameter des Gesichts'),
                    ('keiner', 'Aus dem Körperschätzer', 'Kopf aus den 10 Körperparametern'),
                ],
                'keiner',
            ),
            (
                'silhouette',
                'Silhouettenabgleich',
                [
                    ('aus', 'Wie geschätzt', ''),
                    ('messen', 'Nur messen', 'Deckung der SMPLest-X-Silhouette mit der Personenmaske'),
                    (
                        'an',
                        'Form an die Maske',
                        'Betas je Bild nachgestellt — Ursula-Probe: Käfig 9,75 → 10,9 mm, nicht besser',
                    ),
                ],
                'aus',
            ),
            (
                'video',
                'Drehvideo',
                [
                    ('gvhmr', 'GVHMR', 'Eine SMPL-X-Form je Video (Vorstufe + Demo; 125 Bilder in 85 s)'),
                    ('keiner', 'Videos übergehen', ''),
                ],
                'gvhmr',
            ),
            (
                'mischung',
                'Mehrere Hauptbilder',
                [
                    ('haupt', 'Nur die Hauptbilder',
                     'Nur die in der zweiten Box markierten Hauptbilder (vorn/hinten/seitlich) bauen den '
                     'Körper, der Kopf kommt vom Kopf-Hauptbild; ohne Markierung die ersten zwei '
                     'Körperzeilen der Tabelle (Edgar, 20.09.2026)'),
                    ('median', 'Median', 'Je Parameter der mittlere Wert — unempfindlich gegen Ausreißer'),
                    ('mittel', 'Gewichtetes Mittel', 'Gewicht je Bild aus der Sichtung'),
                    ('bestes', 'Nur das beste Bild', 'Das Bild mit dem höchsten Gewicht und Zuversicht'),
                ],
                'haupt',
            ),
        ],
        'ziel': Bildmodellzielkatalog.FELDER,
        'anpassung': [
            (
                'reglersatz',
                'Reglersatz',
                [
                    ('proportionen', 'Proportionen', '19 Proportionsregler'),
                    (
                        'charaktere',
                        'Proportionen + Charaktere',
                        'dazu Figur-, Körper- und Kopfregler der installierten Charaktere',
                    ),
                    ('alle', 'Alle Formregler', 'dazu die Asymmetrie-Regler als Links-Rechts-Paare'),
                ],
                'charaktere',
            ),
            (
                'kopffit',
                'Kopf-Fit',
                [
                    ('an', 'Gesichtsregler auf den FLAME-Kopf',
                     'Zweite Stufe nur auf den Kopfpunkten: Kopfregler des Satzes (mit „200 Plus '
                     'Genesis 9 Edition": Brauen, Wangen, Nase, Mund, Kinn, Ohren, Kopfform), '
                     'Körper bleibt wie gestellt (20.09.2026)'),
                    ('aus', 'Aus', 'Nur die Körperstufe — der Kopf bleibt Grundfigur/Charaktermischung'),
                ],
                'an',
            ),
            (
                'basis',
                'Grundfigur',
                [
                    ('auto', 'Aus den Bildern', 'Feminine oder Masculine nach Schulter-Hüft-Verhältnis'),
                    ('feminine', 'Base Feminine', ''),
                    ('masculine', 'Base Masculine', ''),
                    ('keine', 'Genesis 9 Basis', 'Androgyne Grundfigur'),
                ],
                'auto',
            ),
            (
                'daempfung',
                'Dämpfung',
                [
                    ('gering', 'Gering (0,02)', 'Viele Regler dürfen anschlagen'),
                    ('mittel', 'Mittel (0,1)', ''),
                    ('stark', 'Stark (0,5)', 'Wenige Regler, näher an der Grundfigur'),
                ],
                'gering',
            ),
            (
                'gelenke',
                'Gelenke',
                [
                    ('an', 'Gelenke mitziehen', 'Beinlänge, Schulterbreite aus den SMPL-X-Gelenken'),
                    ('aus', 'Nur Oberfläche', ''),
                ],
                'an',
            ),
            (
                'nebenbilder',
                'Handaufnahmen',
                [
                    ('aus', 'Nur Hauptbilder', ''),
                    (
                        'haende',
                        'Fingerlänge aus den Händen',
                        'Mittelfinger zu Handfläche (MediaPipe) → Fingers Length; unsicher: ±0,24 je Hand',
                    ),
                ],
                'aus',
            ),
        ],
        'rest': [
            (
                'restmorph',
                'Restmorph',
                [
                    ('an', 'Rest als Eigenmorph', 'Was die Regler nicht erreichen, wird ein eigener Morph'),
                    ('aus', 'Nur Regler', ''),
                ],
                'an',
            ),
            (
                'glaettung',
                'Glättung',
                [
                    ('wenig', 'Wenig (3 Schritte)', ''),
                    ('mittel', 'Mittel (6 Schritte)', ''),
                    ('viel', 'Viel (12 Schritte)', ''),
                ],
                'mittel',
            ),
        ],
        'textur': Bildmodellzielkatalog.TEXTUR,
        'speichern': [
            (
                'modell',
                'Modell',
                [
                    (
                        'an',
                        'Unter dem Auftragsnamen speichern',
                        'data/models/<Name>.json, in Szene und Studio ladbar',
                    ),
                    ('aus', 'Nicht speichern', 'Nur im Auftrag ansehen'),
                ],
                'an',
            ),
        ],
    }

    @classmethod
    def verfuegbarkeit(cls):
        """`{(feld, wert): (verfügbar, grund)}` — Schätzer nach ihren Gewichten."""
        if cls._zustand is not None:
            return cls._zustand
        aus = {}
        try:
            with Wrapperpfad():
                from photo_analyzer import get_all_status

                stand = get_all_status()
        except Exception as fehler:  # noqa: BLE001
            logger.warning('Foto-Backends nicht abfragbar: %s', fehler)
            stand = {}
        for name in ('smplest_x', 'pymafx', 'hmr2', 'mediapipe'):
            s = stand.get(name) or {}
            aus[('koerper', name)] = (
                bool(s.get('available')),
                '' if s.get('available') else str(s.get('info') or 'nicht eingerichtet'),
            )
        aus[('gesicht', 'pymafx_flame')] = aus[('koerper', 'pymafx')]
        aus[('video', 'gvhmr')] = cls._gvhmr()
        aus[('koerper', 'gvhmr')] = aus[('video', 'gvhmr')]
        cls._zustand = aus
        return aus

    @staticmethod
    def _gvhmr():
        """GVHMR liegt neben den Foto-Backends: Wurzel, Startskript, Gewichte."""
        try:
            with Wrapperpfad():
                from gvhmrlauf import Gvhmrlauf

                wurzel = Gvhmrlauf.WURZEL
                gewichte = os.path.join(wurzel, 'inputs', 'checkpoints', 'gvhmr')
                if not os.path.isdir(wurzel):
                    return (False, 'GVHMR nicht eingelagert')
                if not os.path.isfile(Gvhmrlauf.SKRIPT):
                    return (False, 'gvhmr_vorhersage.py fehlt')
                if not os.path.isdir(gewichte):
                    return (False, 'GVHMR-Gewichte fehlen (inputs/checkpoints/gvhmr)')
        except Exception as fehler:  # noqa: BLE001
            return (False, str(fehler))
        return (True, '')

    @classmethod
    def vergessen(cls):
        cls._zustand = None
        Bildmodellpersonkatalog.vergessen()
