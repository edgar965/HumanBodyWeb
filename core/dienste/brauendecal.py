# -*- coding: utf-8 -*-
"""Brauendecal — die Augenbraue als Zeichnung fürs Brauenfenster der Haut.

Edgar, 16.09.2026 (Konzept A, `Docu/konzepte/2026-09-16_augenbrauen.md`):
„meinetwegen kann ich die auch aus der Textur nehmen, aber dann sollen die
auch anpassbar sein!" Die Braue liegt in der Haut — aber nicht in der
2048²-Albedo (dort 90 × 12 px), sondern als eigene Karte NUR für das
Brauenfenster (`Brauenbogen.fenster`, hier `BREITE` px breit: ~10 px je mm).
Der Hautshader (`gemeinsam/brauenhaut.js`) mischt sie an der Stelle ein; die
Braue folgt den Morphs, weil sie an den UVs hängt.

Gezeichnet werden HÄRCHEN entlang der Mittellinie der MB-Lab-Braue
(`Brauenbogen`): Dichte (Härchen je Braue), Länge des Bogens (innen fest,
nach außen), Dicke (Bogenbreite, innen breiter als außen), Höhe innen/außen
und Wölbung (Versatz des Bogens in mm), Lage (alles höher/tiefer),
Härchenlänge, Farbe mit Varianz, Deckkraft. Die Richtung der Härchen dreht
von innen (steil nach oben) nach außen (flach, leicht fallend), jedes Haar
ist leicht gebogen, verjüngt sich und blendet an der Spitze aus — das nimmt
die „Hecke" (60 gleiche Streifen) weg. Deterministisch: gleiche Regler,
gleiches Bild (Zufall mit festem Keim je Seite).

Gezeichnet in `S`-facher Auflösung und mit Lanczos verkleinert (weiche
Kanten); die Fläche ist vorab in der Brauenfarbe gefüllt (Alpha 0), damit
die Verkleinerung an den Rändern keine dunklen Säume mischt. Ablage je
Reglerstand unter `media/hauttexturen/brauen/` (Projekt, nicht System-Temp).
"""

import hashlib
import json
import logging
import math

import numpy as np

from .brauenbogen import Brauenbogen

logger = logging.getLogger('core')


class Brauendecal:
    FASSUNG = 2
    BREITE = 2048
    S = 3
    ORDNER = Brauenbogen.ORDNER / 'brauen'

    #: Regler mit Vorgabe; mm-Werte in Millimetern, Faktoren um 1, Deckkraft 0..1.
    VORGABE = {
        'farbe': '#3a2a1e',
        'hoehe_innen': 0.0,
        'hoehe_aussen': 0.0,
        'woelbung': 0.0,
        'lage': 0.0,
        'laenge': 1.0,
        'dicke': 1.0,
        'dichte': 1.0,
        'haar_laenge': 1.0,
        'deckkraft': 1.0,
    }
    GRENZEN = {
        'hoehe_innen': (-15, 15),
        'hoehe_aussen': (-15, 15),
        'woelbung': (-8, 10),
        'lage': (-20, 20),
        'laenge': (0.25, 3.0),
        'dicke': (0.25, 3.0),
        'dichte': (0.25, 3.0),
        'haar_laenge': (0.25, 3.0),
        'deckkraft': (0.0, 1.0),
    }
    #: Bogenbreite innen/außen (mm), Härchen je Braue, Haarlänge innen/außen (mm),
    #: Strichbreite Ansatz/Spitze (mm), Winkel zur Tangente innen/Mitte/außen (°).
    BOGEN_MM = (4.5, 2.0)
    HAARE = 220
    HAAR_MM = (6.5, 4.0)
    STRICH_MM = (0.35, 0.10)
    WINKEL = (70.0, 30.0, -5.0)
    SEGMENTE = 8
    #: Alpha je Segment von der Wurzel zur Spitze (Anteil).
    AUSBLENDEN = (1, 1, 1, 1, 1, 0.75, 0.5, 0.25)
    #: Die Enden laufen aus: über diesen Anteil des Bogens (je Ende) wachsen
    #: Haarlänge und Dichte von ENDE_LAENGE bzw. ENDE_DICHTE auf 1.
    ENDE_ANTEIL = 0.18
    ENDE_LAENGE = 0.45
    ENDE_DICHTE = 0.35

    # --------------------------------------------------------------- Regler

    @classmethod
    def regler(cls, roh):
        """Regler aus einer Abfrage (Zeichenketten erlaubt), geklemmt."""
        aus = dict(cls.VORGABE)
        for name, (unten, oben) in cls.GRENZEN.items():
            if name in roh:
                try:
                    aus[name] = min(oben, max(unten, float(roh[name])))
                except TypeError, ValueError:
                    logger.warning('Brauenregler %s unlesbar: %r', name, roh[name])

        farbe = str(roh.get('farbe', aus['farbe'])).lower()
        if len(farbe) == 7 and farbe[0] == '#' and all(c in '0123456789abcdef' for c in farbe[1:]):
            aus['farbe'] = farbe
        return aus

    @classmethod
    def kennung(cls, geschlecht, regler):
        text = json.dumps(
            [
                cls.FASSUNG,
                Brauenbogen.FASSUNG,
                geschlecht,
                {k: (round(v, 2) if isinstance(v, float) else v) for k, v in sorted(regler.items())},
            ]
        )
        return hashlib.sha1(text.encode()).hexdigest()[:12]

    #: Figurarten mit eigenem Brauenbogen (25.09.2026: SMPL-X, `Smplxdetaildienst`).
    QUELLEN = ('smplx',)

    @classmethod
    def bogen(cls, geschlecht, quelle=''):
        """Der Brauenbogen der Figurart — HumanBody (MB-Lab-Albedo) oder SMPL-X."""
        if quelle == 'smplx':
            from .smplxdetaildienst import Smplxdetaildienst

            return Smplxdetaildienst.bogen(geschlecht)
        return Brauenbogen.laden(geschlecht)

    @classmethod
    def bild(cls, geschlecht, regler, quelle=''):
        """Pfad der PNG für diesen Reglerstand — aus der Ablage oder frisch.

        `quelle` 'smplx' zeichnet auf den Brauenbogen der SMPL-X-UV; der Name
        trägt sie dann vorn (HumanBody-Namen bleiben wie sie waren)."""
        geschlecht = 'male' if geschlecht == 'male' else 'female'
        quelle = quelle if quelle in cls.QUELLEN else ''
        cls.ORDNER.mkdir(parents=True, exist_ok=True)
        # Die SMPL-X-Karte haengt am Brauenbogen DIESER Fassung (`Smplxdetails.FASSUNG`,
        # artefakte-benennen) — sonst laege nach einem neuen Bogen die alte Braue.
        praefix = ''
        if quelle == 'smplx':
            from SMPL.xdetails import Smplxdetails

            praefix = 'smplx%d_' % Smplxdetails.FASSUNG
        name = '%s%s_%s.png' % (praefix, geschlecht, cls.kennung(geschlecht, regler))
        ziel = cls.ORDNER / name
        if not ziel.is_file():
            bogen = cls.bogen(geschlecht, quelle)
            cls.zeichnen(bogen, regler).save(ziel)
            logger.info('Brauendecal %s: %s', geschlecht, ziel.name)
        return ziel

    # ------------------------------------------------------------- Zeichnen

    @classmethod
    def zeichnen(cls, bogen, regler):
        """Das Fensterbild: je Braue ein kleiner Ausschnitt in `S`-facher
        Auflösung, verkleinert und eingesetzt — das ganze Fenster zu zeichnen
        kostete 13 s, so sind es 0,2 s."""
        from PIL import Image

        u0, v0, u1, v1 = bogen['fenster']
        px_je_uv = cls.BREITE / (u1 - u0)
        px_je_mm = px_je_uv / bogen['mm_je_uv']
        hoehe = int(round((v1 - v0) * px_je_uv))
        farbe = cls._rgb(regler['farbe'])
        bild = Image.new('RGBA', (cls.BREITE, hoehe), farbe + (0,))
        for nummer, seite in enumerate(('links', 'rechts')):
            if seite not in bogen:
                continue
            linie = np.array([[(u - u0) * px_je_uv, (v1 - v) * px_je_uv] for u, v in bogen[seite]])
            striche = cls.haare(linie, px_je_mm, regler, farbe, np.random.default_rng(1000 + nummer))
            teil, ecke = cls.ausschnitt(striche, farbe)
            bild.paste(teil, ecke, teil)
        return bild

    @classmethod
    def ausschnitt(cls, striche, farbe):
        """Eine Braue als kleines RGBA-Bild plus seine linke obere Ecke."""
        from PIL import Image, ImageDraw

        alle = np.concatenate([p for p, _b, _r in striche])
        rand = 4
        x0, y0 = np.floor(alle.min(axis=0)).astype(int) - rand
        x1, y1 = np.ceil(alle.max(axis=0)).astype(int) + rand
        x0, y0 = max(0, x0), max(0, y0)
        breite, hoehe = x1 - x0, y1 - y0
        gross = Image.new('RGBA', (breite * cls.S, hoehe * cls.S), farbe + (0,))
        zeichner = ImageDraw.Draw(gross)
        # Spitzen zuerst, Ansätze zuletzt: das dichtere Alpha gewinnt.
        for segment in range(cls.SEGMENTE - 1, -1, -1):
            for punkte, breiten, rgba in striche:
                a = (punkte[segment] - (x0, y0)) * cls.S
                b = (punkte[segment + 1] - (x0, y0)) * cls.S
                zeichner.line(
                    [tuple(a), tuple(b)],
                    fill=rgba[segment],
                    width=max(1, int(round(breiten[segment] * cls.S))),
                )
        return gross.resize((breite, hoehe), Image.LANCZOS), (int(x0), int(y0))

    @classmethod
    def haare(cls, linie, px_je_mm, regler, farbe, rng):
        """Die Striche einer Braue: `[(punkte (SEGMENTE+1, 2), breiten, rgba je
        Segment)]` — `linie` in Bildpixeln von innen nach außen."""
        laengen = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(linie, axis=0), axis=1))])
        gesamt = laengen[-1]
        t_linie = laengen / gesamt

        def punkt(s):
            if s <= 1:
                return np.array([np.interp(s, t_linie, linie[:, 0]), np.interp(s, t_linie, linie[:, 1])])
            return linie[-1] + tangente(1.0) * (s - 1) * gesamt

        def tangente(s):
            i = min(len(linie) - 2, max(0, int(np.searchsorted(t_linie, min(s, 1.0)) - 1)))
            d = linie[i + 1] - linie[i]
            return d / (np.linalg.norm(d) or 1.0)

        def normale(s):
            t = tangente(s)
            n = np.array([-t[1], t[0]])
            return n if n[1] < 0 else -n  # „oben" = kleinere Bildzeile

        anzahl = max(2, int(round(cls.HAARE * regler['dichte'] * regler['laenge'])))
        striche = []
        for k in range(anzahl):
            s = (k + rng.uniform(0.15, 0.85)) / anzahl * regler['laenge']
            s_form = min(1.0, s / max(regler['laenge'], 1e-6))
            # Die Enden laufen aus (Edgar, 17.09.2026: „am Rand noch etwas
            # krank"): innen standen lange, steile Haare einzeln wie ein
            # Besen, außen hingen die letzten als dünne Fransen. Im ENDE_ANTEIL
            # an beiden Enden werden die Haare kürzer und dünner gesät.
            ende = min(1.0, min(s_form, 1.0 - s_form) / cls.ENDE_ANTEIL)
            if rng.uniform() > cls.ENDE_DICHTE + (1 - cls.ENDE_DICHTE) * ende:
                continue
            versatz = (
                regler['lage']
                + regler['hoehe_innen'] * (1 - s_form)
                + regler['hoehe_aussen'] * s_form
                + regler['woelbung'] * math.sin(math.pi * s_form)
            )
            breite_mm = regler['dicke'] * np.interp(s_form, [0, 1], cls.BOGEN_MM)
            quer = rng.normal(0, 0.5) * breite_mm / 2
            n = normale(s)
            wurzel = punkt(s) + n * (versatz + quer) * px_je_mm
            winkel = np.interp(s_form, [0, 0.45, 1], cls.WINKEL) + rng.normal(0, 7)
            richtung = cls._drehen(tangente(s), n, winkel)
            laenge = (
                np.interp(s_form, [0, 1], cls.HAAR_MM)
                * regler['haar_laenge']
                * (1 + rng.normal(0, 0.18))
                * (cls.ENDE_LAENGE + (1 - cls.ENDE_LAENGE) * ende)
            ) * px_je_mm
            spitze = cls._drehen(richtung, n, -25.0)
            steuer = wurzel + richtung * laenge * 0.55
            ende = wurzel + spitze * laenge
            tt = np.linspace(0, 1, cls.SEGMENTE + 1)[:, None]
            punkte = (1 - tt) ** 2 * wurzel + 2 * (1 - tt) * tt * steuer + tt**2 * ende
            breiten = np.interp(np.linspace(0, 1, cls.SEGMENTE), [0, 1], cls.STRICH_MM) * px_je_mm
            hell = 1 + rng.normal(0, 0.10)
            rgb = tuple(int(min(255, max(0, c * hell))) for c in farbe)
            rgba = [
                rgb + (int(round(255 * regler['deckkraft'] * cls.AUSBLENDEN[i])),)
                for i in range(cls.SEGMENTE)
            ]
            striche.append((punkte, breiten, rgba))
        return striche

    @staticmethod
    def _drehen(richtung, normale, grad):
        """`richtung` um `grad` zur `normale` hin drehen (positiv = zur Normalen)."""
        a = math.radians(grad)
        return richtung * math.cos(a) + normale * math.sin(a)

    @staticmethod
    def _rgb(hex_farbe):
        return tuple(int(hex_farbe[i : i + 2], 16) for i in (1, 3, 5))
