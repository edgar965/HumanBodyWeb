# -*- coding: utf-8 -*-
"""Blendimporteinstellungen — was der Dialog „Modell importieren" für eine .blend fragt, mit Edgars Vorgaben.

Edgar (08.10.2026), die Entscheidungen zum Import von „cute girl", die beim nächsten Mal als Vorgabe dastehen sollen:

    datei       „die letzte blender Datei (mit der aktuellsten Version)" → aus dem Ordner die .blend mit der höchsten
                Fassungsnummer im Namen (`Blendimportquelle`)
    name        „name wie der Ordner"
    augen       „Die Originalaugen auf Genesis übertragen, aber einstellbar / ersetzbar" → `original` | `genesis`
    textur      „geringe Auflösung im Browser, mit Strg+Alt+H umschaltbar auf die höchste" → gebacken mit
                `kachel_px` je Kachel; der Browser bekommt `browser_px`, Strg+Alt+H die volle Kachel

Gemerkt werden die zuletzt benutzten Werte (samt Pfad) in `<OBJECTS_ROOT>/blendimport/einstellungen.json`; jeder Wert
wird gegen den Katalog geprüft, Unbekanntes fällt auf die Vorgabe (wie `Meshfiguroptionen.pruefen`).
"""

import json
import logging
import os

from ..daten.blendimportablage import Blendimportablage

logger = logging.getLogger('core')

__all__ = ['Blendimporteinstellungen']


class Blendimporteinstellungen:
    DATEI = 'einstellungen.json'

    KATALOG = [
        {'schluessel': 'pfad', 'titel': 'Ordner oder .blend', 'art': 'text', 'vorgabe': '',
         'hinweis': 'Ein Ordner: die .blend mit der höchsten Fassungsnummer im Namen. Die Texturen dürfen neben der '
                    'Datei liegen (nicht gepackt) — deshalb ein Pfad und kein Hochladen.'},
        {'schluessel': 'name', 'titel': 'Name', 'art': 'wahl', 'vorgabe': 'ordner',
         'werte': [('ordner', 'Wie der Ordner'), ('datei', 'Wie die Datei (ohne Fassung)')]},
        {'schluessel': 'umposen', 'titel': 'Haltung', 'art': 'wahl', 'vorgabe': 'rig',
         'werte': [('rig', 'Mit dem Rig in die Genesis-Haltung bringen (Knochenkarte)'),
                   ('aus', 'Haltung der Datei lassen')],
         'hinweis': 'Körper, Kleider und Haar stehen dann wie Genesis in A-Haltung; „Mesh to 3D" muss die Haltung nicht '
                    'mehr schätzen. Nur für Auto-Rig Pro; ein anderes Rig wird übersprungen.'},
        {'schluessel': 'augen', 'titel': 'Augen', 'art': 'wahl', 'vorgabe': 'original',
         'werte': [('original', 'Originalaugen auf die Genesis-Augen übertragen'),
                   ('genesis', 'Genesis-Augen (Irisfarbe aus dem Modell)')],
         'hinweis': 'Das Augenbild liegt als eigene Datei beim Modell; die Augenwahl der Figur bleibt bedienbar.'},
        {'schluessel': 'kachel_px', 'titel': 'Hautkacheln (volle Auflösung)', 'art': 'wahl', 'vorgabe': '8192',
         'werte': [('2048', '2048 px'), ('4096', '4096 px'), ('8192', '8192 px (höchste)')],
         'hinweis': 'So groß wird jede der vier Haut-Kacheln (Kopf, Rumpf, Beine, Arme) gebacken — sichtbar mit '
                    'Strg+Alt+H. Die Nägel bleiben Genesis, damit der Nagellack wirkt. Das Original hat 8192 px; mit '
                    '8192 geht beim Backen nichts verloren.'},
        {'schluessel': 'browser_px', 'titel': 'Hautkacheln im Browser', 'art': 'wahl', 'vorgabe': '2048',
         'werte': [('1024', '1024 px'), ('2048', '2048 px'), ('4096', '4096 px')],
         'hinweis': 'Ohne Strg+Alt+H lädt der Browser diese verkleinerte Fassung.'},
        {'schluessel': 'normalen_grenze', 'titel': 'Normalen säubern ab', 'art': 'wahl', 'vorgabe': '50',
         'werte': [('35', '35° (streng)'), ('50', '50° (Vorgabe)'), ('70', '70° (nur grobe Fehltreffer)'),
                   ('aus', 'Nicht säubern')],
         'hinweis': 'Gebackene Normalen, die stärker von der Figur abweichen, gelten als falscher Strahltreffer (so '
                    'entstand ein weißer Fleck im Dekolleté) und werden flach. An cute girl gemessen bei 50°: 0,8–2,8 % '
                    'der Texel je Kachel; ab 8 % warnt der Import.'},
        {'schluessel': 'basis', 'titel': 'Grundfigur', 'art': 'wahl', 'vorgabe': 'feminine',
         'werte': [('feminine', 'Genesis 9 Feminine'), ('masculine', 'Genesis 9 Masculine'),
                   ('neutral', 'Genesis 9 (neutral)')]},
        {'schluessel': 'stuecke', 'titel': 'Kleider und Haar', 'art': 'wahl', 'vorgabe': 'an',
         'werte': [('an', 'Als eigene Stücke in die Genesis-Bibliothek'), ('aus', 'Nur die Figur')]},
    ]

    @classmethod
    def pfad(cls):
        return Blendimportablage.wurzel() / cls.DATEI

    @classmethod
    def eintrag(cls, schluessel):
        for e in cls.KATALOG:
            if e['schluessel'] == schluessel:
                return e
        raise KeyError(schluessel)

    @classmethod
    def pruefen(cls, roh):
        roh = roh if isinstance(roh, dict) else {}
        aus = {}
        for e in cls.KATALOG:
            wert = roh.get(e['schluessel'], e['vorgabe'])
            if e['art'] == 'text':
                wert = str(wert or '').strip().strip('"').strip("'").strip()[:1000]
            elif str(wert) not in [w for w, _ in e['werte']]:
                wert = e['vorgabe']
            aus[e['schluessel']] = str(wert)
        return aus

    @classmethod
    def laden(cls):
        """Die gemerkten Werte (geprüft) — ohne Datei die Vorgaben."""
        try:
            roh = json.loads(cls.pfad().read_text(encoding='utf-8'))
        except FileNotFoundError:
            roh = {}
        except (OSError, ValueError):
            logger.warning('Blender-Import: %s nicht lesbar — Vorgaben', cls.pfad(), exc_info=True)
            roh = {}
        return cls.pruefen(roh)

    @classmethod
    def speichern(cls, werte):
        """Geprüft ablegen und zurückgeben (bei jedem Start eines Imports)."""
        werte = cls.pruefen({**cls.laden(), **(werte if isinstance(werte, dict) else {})})
        cls.pfad().parent.mkdir(parents=True, exist_ok=True)
        neben = cls.pfad().with_suffix('.json.neu')
        neben.write_text(json.dumps(werte, ensure_ascii=False, indent=1), encoding='utf-8')
        os.replace(neben, cls.pfad())
        return werte

    @classmethod
    def katalog(cls):
        """`{optionen: [...], werte: {...}}` für den Dialog — Werte der Auswahl als `{wert, text}`."""
        optionen = []
        for e in cls.KATALOG:
            feld = {k: v for k, v in e.items() if k != 'werte'}
            if e['art'] == 'wahl':
                feld['werte'] = [{'wert': w, 'text': t} for w, t in e['werte']]
            optionen.append(feld)
        return {'optionen': optionen, 'werte': cls.laden()}
