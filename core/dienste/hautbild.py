# -*- coding: utf-8 -*-
"""Hautbild — die Hauttextur einer Figur als EIN Bild, mit gezeichneter Braue.

WARUM (Edgar, 17.09.2026: „baue: der pyrender-Film (er hat weder Textur noch
Augen/Wimpern)"): Der Browser mischt die Braue je Bildpunkt im Hautshader
(`gemeinsam/brauenhaut.js`) über die Albedo oder die Hautfarbe. Der Film
(`TheatreJS/ModelPhysik/filmhaut.py`) hat keinen eigenen Shader — er bekommt
hier dasselbe Ergebnis als fertiges Bild: Grund (Albedo ohne gemalte Brauen,
getönt wenn eine Hautfarbe gesetzt ist — sonst die Farbe der Körperart als
Fläche), darauf das Brauenfenster aus `Brauendecal`, gemischt wie im Shader
(`mix(haut, braue.rgb, braue.a)`).

Die Reglerfelder heißen wie im Browser (`Brauenhaut.FELDER`): Meterwerte
werden in Millimeter umgerechnet (`test_hautbild` vergleicht die Tabelle mit
der JS-Quelle). Nur lesen: die MB-Lab-Texturen bleiben unangetastet, die
Retusche liegt unter `media/hauttexturen/`.
"""

import re

import numpy as np

from .brauenbogen import Brauenbogen
from .brauendecal import Brauendecal
from .brauenretusche import Brauenretusche
from .lippenmaske import Lippenmaske


class Hautbild:
    """`Hautbild.bild(details, body_type)` → (H, W, 3) uint8, sRGB."""

    #: Kantenlänge der Fläche ohne Albedo — so groß wie die MB-Lab-Albedo,
    #: damit die Braue (~540 px breit im Fenster) dieselbe Schärfe hat.
    GROESSE = 2048
    #: Die wählbaren Albedos (`Hauttextur.WAHL` ohne die leere Wahl).
    ALBEDO = re.compile(r'^hum_[fm]_(afro|asian|cauc|latino)$')
    #: Detailfeld → (Regler des Zeichners, Faktor) — Spiegel von
    #: `Brauenhaut.FELDER` in `gemeinsam/brauenhaut.js`.
    BRAUENFELDER = {
        'brauen': ('farbe', 1),
        'brauen_staerke': ('haar_laenge', 1),
        'brauen_dicke': ('dicke', 1),
        'brauen_dichte': ('dichte', 1),
        'brauen_bogen_laenge': ('laenge', 1),
        'brauen_deckkraft': ('deckkraft', 1),
        'brauen_lage': ('lage', 1000),
        'brauen_hoehe_innen': ('hoehe_innen', 1000),
        'brauen_hoehe_aussen': ('hoehe_aussen', 1000),
        'brauen_woelbung': ('woelbung', 1000),
    }
    #: Die Farben der Körperart sind linear (`MorphData.SKIN_COLORS`); der
    #: Browser hebt sie mit 1/2,2 an (`gemeinsam/hautfarbe.js`).
    GAMMA = 1 / 2.2
    ERSATZ_ETHNIE = 'Caucasian'
    HEX = re.compile(r'^#[0-9a-fA-F]{6}$')

    # --------------------------------------------------------------- Regler

    @classmethod
    def geschlecht(cls, body_type):
        return 'male' if str(body_type or '').lower().startswith('male') else 'female'

    @classmethod
    def regler(cls, details):
        """Die Zeichnerregler aus den Detailfeldern — wie `Brauenhaut.abfrage`."""
        roh = {}
        for feld, (name, faktor) in cls.BRAUENFELDER.items():
            wert = (details or {}).get(feld)
            if wert is None or wert == '':
                continue
            roh[name] = round(float(wert) * faktor, 2) if isinstance(wert, (int, float)) else wert
        return Brauendecal.regler(roh)

    # ---------------------------------------------------------------- Grund

    @classmethod
    def ethnie(cls, body_type):
        teile = str(body_type or '').split('_')
        return '_'.join(teile[1:]) if len(teile) > 1 else cls.ERSATZ_ETHNIE

    @classmethod
    def hautfarbe(cls, details, body_type):
        """(r, g, b) 0..255: die gesetzte Hautfarbe, sonst die der Körperart."""
        farbe = (details or {}).get('haut')
        if isinstance(farbe, str) and cls.HEX.match(farbe):
            return cls.rgb(farbe)
        from humanbody_core import MorphData

        tabelle = MorphData.SKIN_COLORS
        linear = tabelle.get(cls.ethnie(body_type)) or tabelle[cls.ERSATZ_ETHNIE]
        return tuple(int(round(255 * float(c) ** cls.GAMMA)) for c in linear)

    @staticmethod
    def rgb(hex_farbe):
        return tuple(int(hex_farbe[i : i + 2], 16) for i in (1, 3, 5))

    @classmethod
    def albedo(cls, details):
        """Pfad der MB-Lab-Albedo zum Detail `haut_textur`, oder None."""
        name = str((details or {}).get('haut_textur') or '')
        if not cls.ALBEDO.match(name):
            return None
        pfad = Lippenmaske.ordner() / ('%s_albedo.png' % name)
        return pfad if pfad.is_file() else None

    @classmethod
    def toenen(cls, bild, farbe):
        """Albedo mal Hautfarbe, linear wie in Three.js (`color` × `map`)."""
        lin = (np.asarray(bild, dtype=np.float32) / 255.0) ** 2.2
        ton = (np.asarray(farbe, dtype=np.float32) / 255.0) ** 2.2
        return np.clip(255 * (lin * ton) ** (1 / 2.2), 0, 255).astype(np.uint8)

    @classmethod
    def grund(cls, details, body_type):
        """Albedo ohne gemalte Brauen (getönt, wenn eine Hautfarbe gesetzt
        ist) — oder die Farbe der Körperart als Fläche."""
        from PIL import Image

        farbe = cls.hautfarbe(details, body_type)
        pfad = cls.albedo(details)
        if pfad is None:
            return np.full((cls.GROESSE, cls.GROESSE, 3), farbe, dtype=np.uint8)
        with Image.open(Brauenretusche.fuer(pfad)) as bild:
            roh = np.asarray(bild.convert('RGB'))
        if (details or {}).get('haut'):
            return cls.toenen(roh, farbe)
        return roh

    # ---------------------------------------------------------------- Braue

    @classmethod
    def mit_brauen(cls, grund, geschlecht, regler):
        """Das Brauenfenster in den Grund gemischt — Bildzeile 0 ist oben,
        v = 1 auch (wie `Lippenmaske.aus_uvs`); das Decal ist bereits so
        gezeichnet (`Brauendecal.zeichnen`: Zeile 0 = v1)."""
        from PIL import Image

        u0, v0, u1, v1 = Brauenbogen.laden(geschlecht)['fenster']
        hoehe, breite = grund.shape[:2]
        x0, x1 = int(round(u0 * breite)), int(round(u1 * breite))
        y0, y1 = int(round((1 - v1) * hoehe)), int(round((1 - v0) * hoehe))
        with Image.open(Brauendecal.bild(geschlecht, regler)) as decal:
            braue = np.asarray(
                decal.convert('RGBA').resize((x1 - x0, y1 - y0), Image.LANCZOS), dtype=np.float32
            )
        alpha = braue[..., 3:4] / 255.0
        fenster = grund[y0:y1, x0:x1].astype(np.float32)
        aus = np.array(grund)
        aus[y0:y1, x0:x1] = np.clip(fenster * (1 - alpha) + braue[..., :3] * alpha, 0, 255).astype(np.uint8)
        return aus

    @classmethod
    def bild(cls, details, body_type):
        """Grund plus Braue für diese Figur."""
        return cls.mit_brauen(cls.grund(details, body_type), cls.geschlecht(body_type), cls.regler(details))
