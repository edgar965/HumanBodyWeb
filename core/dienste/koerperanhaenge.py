# -*- coding: utf-8 -*-
"""Koerperanhaenge — Augäpfel, Mund (Zähne, Zunge), Wimpern und Brauen als Teile einer Runde von „2D3D Kleider"
(02.10.2026).

Befund der ersten Prüfung mit Kopftafel (Runde 15, Auftrag 2026.10.01.20.10.04): Die Augen waren schwarze Löcher. Der
Körper der Runde (`Koerpertextur.teil`) ist das Genesis-Grundnetz OHNE die Anhänge — Augäpfel, Wimpern, Brauen sind bei
Genesis eigene Netze (`G9anhang`), die Bühne hängt sie an (`Engine2d3dKleiderstandmodell` → `Standmodellglb.anhaenge`), die
Runde nie. Jede Runde wurde also mit leeren Augenhöhlen gerendert und benotet.

Wie im Standmodell: die durchsichtigen Schichten (`Standmodellglb.DURCHSICHTIG`: Tränenfilm, Hornhaut) fallen weg — sie
deckten opak die Iris zu —, Brauen und Wimpern in der Haarfarbe (`Brauenfarbe`). Je Formung und Haarfarbe einmal je
Prozess gebaut (`_vorrat`).
"""

import json
from pathlib import Path

import numpy as np

__all__ = ['Koerperanhaenge']


class Koerperanhaenge:
    TOENUNG = (0.5, 0.5, 0.5)            # Faktor = Daz-Farbe × 2 × Tönung (`Kleidermodellbau._textur`) → Daz-Farbe
    _vorrat = {}

    @classmethod
    def teile(cls, bau, modell=None):
        """Die Anhänge zur Formung von `bau` (`Kleidermodellbau`) im Teileformat — `art` 'koerper' NACH dem Körper:
        wer den Körper sucht, nimmt das erste Teil dieser Art; Farbnote und Netznote zählen sie zum Körper. Brauen und
        Wimpern in der Haarfarbe von `modell` (`ModellMitKleidern`)."""
        haarfarbe = (getattr(modell, 'farben', None) or {}).get('haar')
        schluessel = json.dumps([bau.formung.morphwerte(), haarfarbe], sort_keys=True, default=str)
        if schluessel not in cls._vorrat:
            cls._vorrat.clear()                      # eine Formung je Lauf: kein Wachsen über Runden
            cls._vorrat[schluessel] = cls._bauen(bau, haarfarbe)
        gemalt = cls.brauen_gemalt(getattr(bau, 'kacheln', None))
        return [t for t in cls._vorrat[schluessel] if not (gemalt and t.get('sorte') == cls.BRAUEN)]

    #: Sorte des Brauenteils (`anhang_<schluessel>`) und Name der Kopfkachel mit Fotohaut (`Koerperfotoprojektion`, Kachel 1001).
    BRAUEN = 'anhang_brauen'
    FOTOKOPF = 'hautfoto_1001'

    @classmethod
    def brauen_gemalt(cls, kacheln):
        """True, wenn die Kopfkachel (1001) Fotohaut trägt (`kacheln`: `{kachel: Pfad}`): Die Brauen sind dann mit dem Gesicht aus dem Foto gemalt (buschig, grau, an der Stelle der Landmarken), die Geometrie-Brauen
        (dünn, in der Haarfarbe) weichen im Bild davon ab — Edgar, 06.10.2026: „Augenbrauen … ganz anders als im Mesh". Ohne Fotohaut im Kopf bleiben sie."""
        pfad = (kacheln or {}).get(1001)
        return bool(pfad) and Path(str(pfad)).name.startswith(cls.FOTOKOPF)

    @classmethod
    def _bauen(cls, bau, haarfarbe):
        from Genesis9.charaktere import G9charaktere
        from Genesis9.koerpernetz import G9koerpernetz

        from .brauenfarbe import Brauenfarbe
        from .kleidermodellbau import Kleidermodellbau
        from .standmodellglb import Standmodellglb
        netz = {'anhaenge': G9koerpernetz(bau.formung, G9charaktere.eintrag('basis'), anhaenge=True,
                                          stufen=0).nur_anhaenge()}
        if haarfarbe:
            Brauenfarbe().anwenden(netz, haarfarbe)
        aus = []
        for a in netz['anhaenge']:
            dreiecke = np.asarray(a['dreiecke'], dtype=np.int64).reshape(-1, 3)
            stuecke, gruppen, ab = [], [], 0
            for g in a.get('gruppen') or []:
                anzahl = int(g.get('index_anzahl') or 0) // 3
                if anzahl < 1 or str(g.get('name', '')).startswith(Standmodellglb.DURCHSICHTIG):
                    continue
                von = int(g['index_ab']) // 3
                stuecke.append(dreiecke[von:von + anzahl])
                gruppen.append(dict(g, index_ab=3 * ab, index_anzahl=3 * anzahl))
                ab += anzahl
            if not stuecke or a.get('uv') is None:
                continue
            for g in gruppen:                   # Wimpern: Maske ohne Farbbild (Runde 16: hautfarbene Lidkarten)
                b = g.get('bilder') or {}
                if b.get('alpha') and not b.get('albedo'):
                    g['bilder'] = dict(b, albedo=cls._einfarbig(b.get('farbe')), farbe=[1.0, 1.0, 1.0])
            textur = Kleidermodellbau._textur(gruppen, {g['name']: g.get('bilder') or {} for g in gruppen},
                                              cls.TOENUNG)
            aus.append({'punkte': np.asarray(a['punkte'], dtype=np.float64), 'dreiecke': np.concatenate(stuecke),
                        'farbe': np.asarray(Kleidermodellbau.HAUT), 'haut': a.get('haut'), 'art': 'koerper',
                        'sorte': 'anhang_%s' % a.get('schluessel'), 'uv': np.asarray(a['uv'], dtype=np.float64)
                        .reshape(-1, 2), 'normalen': a.get('normalen'), 'gruppen': gruppen, 'textur': textur,
                        'toenung': cls.TOENUNG})
        return aus

    @staticmethod
    def _einfarbig(farbe):
        """Ein 4 × 4-Bild in `farbe` (rgb 0…1) als Bibliothekspfad — `Kleidermodellbau._textur` verwirft die Textur
        eines Teils ohne ein einziges Farbbild, die Maske der Wimpern ginge mit verloren."""
        from Genesis9.kleidtexturen import G9kleidtexturen
        from PIL import Image
        rgb = [int(round(255 * min(max(float(c), 0.0), 1.0))) for c in (list(farbe or [])[:3] or [0.1, 0.1, 0.1])]
        name = 'einfarbig_%02x%02x%02x.png' % tuple(rgb)
        ordner = G9kleidtexturen.ordner() / G9kleidtexturen.KOMPONIERT
        if not (ordner / name).is_file():
            ordner.mkdir(parents=True, exist_ok=True)
            Image.new('RGB', (4, 4), tuple(rgb)).save(ordner / name)
        return G9kleidtexturen.BILDPFAD + G9kleidtexturen.KOMPONIERT + '/' + name
