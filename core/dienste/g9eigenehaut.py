# -*- coding: utf-8 -*-
"""G9eigenehaut — selbst eingestellte und gespeicherte Häute als Hautsätze von Genesis 9 (18.10.2026).

Edgar, 18.10.2026: „Auch Button zum speichern der Neuen Haut, mit hautnamen, die soll dann auch in die Haut Combo box erscheinen" — „bei den einstellungen der Haut sollen
diese Regler kommen, darin auch Button zum speichern der neuen Haut". Eine eigene Haut ist ein REZEPT, kein Bild: der Hautsatz, auf dem sie aufbaut (`grund`), und was im
Browser im Shader auf ihm liegt — die Hautebenen (Hautton, Flecken, Relief …, ohne die grauen Haare), Glanz/Rauheit/Relief der Haut (`teilmaterial`) und die Texturmischung.
Gebacken wird nichts; die Bilder sind die des Grundsatzes.

    <eigene Daten>/haeute/<schluessel>.json        (`G9pfade.eigene_daten()` = 3DObjects/models/Genesis9 — nicht im Repo)
    {name, grund, hautebenen, teilmaterial, hautmischung, gespeichert, fassung}

Kennung `eigen:<schluessel>` (ASCII aus dem Namen, Umlaute umschrieben). Sie steht in der Hautauswahl (`praesets()`, das Rezept liegt dem Eintrag bei, der Browser legt es nach
dem Wechsel auf) und in gespeicherten Modellen wie jeder andere Hautsatz; für Bilder gibt der Server die des Grundsatzes (`bilder`). Wer auf einer eigenen Haut eine neue speichert,
bekommt den Grundsatz der ersten — nie eine Kette.
"""
import json
import logging
import math
import re
import unicodedata
from datetime import datetime

from Genesis9.hautpresets import G9hautpresets

logger = logging.getLogger('core')

__all__ = ['G9eigenehaut']


class G9eigenehaut:
    """Anbieter von Hautsätzen für `G9hautpresets` (`anbieten`) und die Ablage der Rezepte."""

    PRAEFIX = 'eigen:'
    FASSUNG = 1
    NAME_MAX = 60
    #: Höchstens so viele Werte je Abschnitt des Rezepts, Schlüssel höchstens so lang — ein Rezept ist klein.
    FELDER_MAX = 80
    SCHLUESSEL_MAX = 120
    _UMLAUTE = str.maketrans({'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue', 'ß': 'ss'})

    # ---------------------------------------------------------------- Ablage

    @staticmethod
    def ordner():
        from Genesis9.pfade import G9pfade
        return G9pfade.eigene_daten() / 'haeute'

    @classmethod
    def schluessel(cls, name):
        """Der ASCII-Schlüssel eines Namens (`Sommerhaut Ä` → `sommerhaut_ae`); ValueError, wenn nichts übrig bleibt."""
        roh = unicodedata.normalize('NFKD', str(name or '').translate(cls._UMLAUTE)).encode('ascii', 'ignore').decode('ascii')
        aus = re.sub(r'[^a-z0-9]+', '_', roh.lower()).strip('_')[:50]
        if not aus:
            raise ValueError('Der Name braucht mindestens einen Buchstaben oder eine Ziffer.')
        return aus

    @classmethod
    def name(cls, roh):
        """Der Anzeigename: getrimmt, Steuerzeichen weg, höchstens `NAME_MAX` Zeichen; ValueError bei leer."""
        name = re.sub(r'[\x00-\x1f\x7f]', '', str(roh or '')).strip()[:cls.NAME_MAX].strip()
        if not name:
            raise ValueError('Bitte einen Namen für die Haut angeben.')
        return name

    @classmethod
    def gehoert(cls, preset):
        return str(preset or '').startswith(cls.PRAEFIX)

    @classmethod
    def _pfad(cls, schluessel):
        return cls.ordner() / ('%s.json' % schluessel)

    @classmethod
    def rezept(cls, kennung):
        """Das Rezept zu `eigen:<schluessel>` — oder None (unbekannt, unlesbar)."""
        schluessel = str(kennung or '')[len(cls.PRAEFIX):] if cls.gehoert(kennung) else ''
        if not re.fullmatch(r'[a-z0-9_]{1,50}', schluessel):
            return None
        pfad = cls._pfad(schluessel)
        if not pfad.is_file():
            return None
        try:
            daten = json.loads(pfad.read_text(encoding='utf-8'))
        except (OSError, ValueError) as fehler:
            logger.warning('Eigene Haut %s unlesbar: %s', pfad, fehler)
            return None
        return daten if isinstance(daten, dict) else None

    # ------------------------------------------------------------ Anbieter

    @classmethod
    def eintrag(cls, schluessel, rezept):
        """Ein Eintrag der Hautauswahl, mit dem Rezept (ohne `grund` ist es eine Haut wie jede andere)."""
        return {'id': cls.PRAEFIX + schluessel, 'name': 'Eigene Haut · %s' % rezept.get('name', schluessel), 'geschlecht': 'eigen', 'vorschau': False,
                'rezept': {k: rezept.get(k) for k in ('name', 'grund', 'hautebenen', 'teilmaterial', 'hautmischung', 'gespeichert')}}

    @classmethod
    def praesets(cls):
        """`[{id, name, geschlecht, vorschau, rezept}]` — alle gespeicherten Häute, nach Namen."""
        ordner = cls.ordner()
        if not ordner.is_dir():
            return []
        aus = []
        for pfad in sorted(ordner.glob('*.json')):
            rezept = cls.rezept(cls.PRAEFIX + pfad.stem)
            if rezept is not None:
                aus.append(cls.eintrag(pfad.stem, rezept))
        return sorted(aus, key=lambda e: e['name'].lower())

    @classmethod
    def grund(cls, preset):
        """Der Hautsatz unter einer Kennung: bei `eigen:` der Grundsatz des Rezepts (eine Stufe), sonst die Kennung selbst."""
        if not cls.gehoert(preset):
            return str(preset or '')
        rezept = cls.rezept(preset) or {}
        grund = str(rezept.get('grund') or '')
        return '' if cls.gehoert(grund) else grund

    @classmethod
    def bilder(cls, preset):
        """Die Bilder des Grundsatzes (wie `G9hautpresets.haut`) — oder {}; leer heißt: der Server nimmt die Haut der Figur."""
        grund = cls.grund(preset)
        return G9hautpresets.haut(grund) if grund else {}

    # ------------------------------------------------------------ Speichern

    @classmethod
    def _zahlen(cls, roh, grenze=1000.0):
        """`{schluessel: zahl}` — nur endliche Zahlen, geklemmt, höchstens `FELDER_MAX` Einträge."""
        aus = {}
        for k, v in list((roh or {}).items())[:cls.FELDER_MAX] if isinstance(roh, dict) else []:
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
                continue
            aus[str(k)[:cls.SCHLUESSEL_MAX]] = max(-grenze, min(grenze, float(v)))
        return aus

    @classmethod
    def speichern(cls, name, grund, hautebenen=None, teilmaterial=None, hautmischung=None):
        """Das Rezept schreiben (gleicher Schlüssel = überschreiben) → `(eintrag, ueberschrieben)`. ValueError bei ungültigem Namen oder ohne Grundsatz."""
        name = cls.name(name)
        schluessel = cls.schluessel(name)
        grund = cls.grund(grund)
        if not grund:
            raise ValueError('Die Figur hat keinen benannten Hautsatz — bitte zuerst eine Haut in der Auswahl wählen.')
        rezept = {
            'name': name, 'grund': grund, 'fassung': cls.FASSUNG, 'gespeichert': datetime.now().isoformat(timespec='seconds'),
            'hautebenen': {k: round(v) for k, v in cls._zahlen(hautebenen).items()},
            'teilmaterial': cls._zahlen(teilmaterial, 10.0),
            'hautmischung': {k: v for k, v in cls._zahlen(hautmischung, 100.0).items() if v > 0},
        }
        ordner = cls.ordner()
        ordner.mkdir(parents=True, exist_ok=True)
        ziel = cls._pfad(schluessel)
        ueberschrieben = ziel.is_file()
        vorlaeufig = ziel.with_suffix('.neu')
        vorlaeufig.write_text(json.dumps(rezept, ensure_ascii=False, indent=1), encoding='utf-8')
        vorlaeufig.replace(ziel)
        logger.info('Eigene Haut gespeichert: %s (%s, Grund %s, %d Hautebenen)%s', name, ziel, grund, len(rezept['hautebenen']),
                    ' — überschrieben' if ueberschrieben else '')
        return cls.eintrag(schluessel, rezept), ueberschrieben


G9hautpresets.anbieten(G9eigenehaut)         # beim ersten Import als Anbieter von Hautsätzen eintragen
