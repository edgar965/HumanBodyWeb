# -*- coding: utf-8 -*-
"""Kleidermodellbau — ein `ModellMitKleidern` als Netze: Körper, Kleider, Haar (30.09.2026, „2D3D Kleider").

Gebaut wird über DENSELBEN Weg wie die Bühne: `G9garderobeapi._kleid` je Stück, `G9kleidmischbau` für die
Mischung der Kleider, `G9haarmischbau` für die des Haars — mit dem Rumpf, den der Browser schicken würde (die
Stellung als `regler`, die Werte des Sammeleintrags als `regler_stueck`, die getragenen Stücke als `getragen`).
Die rohen Netze fängt der Eingriff `vor_antwort` ab; was der Mischbau neu kodiert, wird aus den Netzfeldern
zurückgelesen. So sieht die Iteration genau das, was später auf der Bühne steht.

Ergebnis je Teil: `{punkte (N, 3), dreiecke (T, 3), farbe (3,), haut {knochen, index, gewicht}, art, sorte}`
in der Lage der Bühne (Meter, Y oben, Füße auf 0). Der Körper kommt als erstes Teil (Käfigstufe 0 an den
UV-Nähten geteilt, wie `G9figurrigglb`); seine Haut trägt die Daz-Knochen wie die der Stücke, damit
`G9tanzhaut` alles gleich häutet.

Die Farbe eines Stücks ist das Mittel seiner Textur (`G9kleidfarbe.farben`), getönt mit der Umfärbung des
Modells — flach je Stück, weil die Note Farbflächen vergleicht (`Iterationsnote`).

Läuft im Arbeitsprozess (python14 mit Django), nie im Server: Die Stufe wird hier auf den Käfig gesetzt
(`Netzstufenwahl`), sonst rechnete jede Runde die Unterteilung der Bühne mit.
"""

import logging

import numpy as np
from django.http import HttpResponse

logger = logging.getLogger('core')

__all__ = ['Kleidermodellbau']


class Kleidermodellbau:
    """`teile(modell)` → Liste der Teile; `glb(teile, pfad)`."""

    #: Haut der Figur, wenn keine Kachel gelesen wird (sRGB 0…1) — wie `Genesishaarrender.HAUT`.
    HAUT = (0.82, 0.68, 0.60)
    STUFE = 0

    def __init__(self, stellung, stufe=STUFE):
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.formung import G9formung
        from Genesis9.haut import G9haut

        from .netzstufenwahl import Netzstufenwahl
        Netzstufenwahl._gewaehlt.set(int(stufe))
        self.stellung = dict(stellung or {})
        self.formung = G9formung(self.stellung)
        self.boden = float(self.formung.boden())
        stufe0 = G9basisnetz.netzstufe(0)
        self._ursprung = np.asarray(stufe0.ursprung, dtype=np.int64)
        self._dreiecke = np.asarray(stufe0.dreiecke, dtype=np.int64)
        self._haut = G9haut.holen().fuer(self._ursprung)
        self._koerper = None

    # --------------------------------------------------------------- Körper

    def koerper(self):
        if self._koerper is None:
            punkte = np.asarray(self.formung.punkte(), dtype=np.float64) - np.array([0.0, self.boden, 0.0])
            self._koerper = {'punkte': punkte[self._ursprung], 'dreiecke': self._dreiecke,
                             'farbe': np.asarray(self.HAUT), 'haut': self._haut, 'art': 'koerper',
                             'sorte': 'koerper'}
        return self._koerper

    # --------------------------------------------------------------- Stücke

    @staticmethod
    def _feld(wert, typ=None):
        """Ein Netzfeld (oder Liste) zurück zu NumPy."""
        roh = getattr(wert, 'rohdaten', None)
        if roh is not None:
            return np.frombuffer(roh, dtype=np.dtype(wert.typ))
        return np.asarray(wert, dtype=typ)

    @classmethod
    def _haut_aus(cls, teil):
        h = teil.get('hautgewichte')
        if not h or not h.get('knochen'):
            return None
        index = cls._feld(h['skin_indices']).reshape(-1, 4).astype(np.int64)
        gewicht = cls._feld(h['skin_weights']).reshape(-1, 4).astype(np.float64)
        if h.get('kodierung') == 'u16u8':
            gewicht = gewicht / 255.0
        return {'knochen': list(h['knochen']), 'index': index, 'gewicht': gewicht}

    @staticmethod
    def _farbe(netze, toenung):
        from Genesis9.kleidfarbe import G9kleidfarbe
        farben = []
        for netz in netze:
            try:
                farben.append(np.asarray(G9kleidfarbe.farben(netz), dtype=np.float64).mean(axis=0))
            except (OSError, ValueError, KeyError, TypeError) as fehler:   # ohne Textur: Haut
                logger.debug('Kleidermodellbau: Farbe nicht lesbar (%s)', fehler)
        grund = np.mean(farben, axis=0) if farben else np.asarray(Kleidermodellbau.HAUT)
        return np.clip(grund * 2.0 * np.asarray(toenung), 0.0, 1.0)

    def _rumpf(self, modell, kennung, werte, rang):
        return {'regler': self.stellung, 'regler_stueck': dict(werte), 'getragen': modell.getragene(),
                'rang': rang}

    def _kleidung(self, modell):
        from Genesis9.kleidgenerisch import G9kleidgenerisch
        from Genesis9.koerpernetz import G9koerpernetz
        from Genesis9.netzstufe import G9netzstufe

        from ..api.g9figur import G9figur
        from ..api.g9garderobe import G9garderobeapi
        from .g9kleidmischbau import G9kleidmischbau
        rumpf = self._rumpf(modell, modell.KLEIDUNG, modell.kleidung, 0)
        folge, uebergang = G9kleidgenerisch.mischung_aufloesen(modell.KLEIDUNG, rumpf['regler_stueck'])
        if not folge:
            return []
        roh = {}

        def kleid(kennung, eintrag, r, vor_antwort=None):
            def sammeln(nummer, netz):
                roh.setdefault(kennung, []).append(netz)
                return vor_antwort(nummer, netz) if vor_antwort else netz
            return G9garderobeapi._kleid(kennung, eintrag, r, vor_antwort=sammeln)

        if len(folge) > 1:
            rumpf = dict(rumpf, regler_stueck=G9kleidgenerisch.ohne_textur(rumpf['regler_stueck']))
            koerper = lambda: G9koerpernetz(G9figur.formung(rumpf, {}), stufen=G9netzstufe.browser()).bindungsflaeche()  # noqa: E731
            aus = G9kleidmischbau.antwort(rumpf, kleid, modell.KLEIDUNG, folge, uebergang, koerper)
        else:
            kennung, _anteil, regler = folge[0]
            from Genesis9.garderobe import G9garderobe
            aus = kleid(kennung, G9garderobe.eintrag(kennung) or {}, dict(rumpf, regler_stueck=regler))
            if not isinstance(aus, HttpResponse):
                for teil in aus.get('teile') or []:
                    teil['sorte'] = kennung
        return self._teile(aus, roh, 'kleidung', np.asarray(self._hex(modell.farben['kleidung'])))

    def _haar(self, modell):
        from ..api.g9garderobe import G9garderobeapi
        from .g9haarmischbau import G9haarmischbau
        if not modell.frisuren():
            return []
        rumpf = self._rumpf(modell, modell.HAAR, modell.haar, 1)
        roh = {}

        def kleid(kennung, eintrag, r, vor_antwort=None):
            def sammeln(nummer, netz):
                roh.setdefault(kennung, []).append(netz)
                return vor_antwort(nummer, netz) if vor_antwort else netz
            return G9garderobeapi._kleid(kennung, eintrag, r, vor_antwort=sammeln)

        aus = G9haarmischbau.antwort(rumpf, kleid)
        return self._teile(aus, roh, 'haar', np.asarray(self._hex(modell.farben['haar'])))

    def _teile(self, aus, roh, art, toenung):
        if isinstance(aus, HttpResponse):
            raise RuntimeError('%s: %s' % (art, getattr(aus, 'content', b'')[:300].decode('utf-8', 'replace')))
        farben = {sorte: self._farbe(netze, toenung) for sorte, netze in roh.items()}
        teile = []
        for teil in aus.get('teile') or []:
            if teil is None or not teil.get('vertex_count'):
                continue
            punkte = self._feld(teil['vertices'], np.float32).reshape(-1, 3).astype(np.float64)
            dreiecke = self._feld(teil['faces'], np.uint32).reshape(-1, 3).astype(np.int64)
            if not len(dreiecke):
                continue                           # Stranghaar (Linien) rendert nicht
            sorte = teil.get('sorte') or art
            teile.append({'punkte': punkte, 'dreiecke': dreiecke, 'farbe': farben.get(sorte, toenung),
                          'haut': self._haut_aus(teil), 'art': art, 'sorte': sorte})
        return teile

    @staticmethod
    def _hex(text):
        roh = str(text or '').lstrip('#')
        if len(roh) != 6:
            return (0.5, 0.5, 0.5)
        return tuple(int(roh[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    def teile(self, modell):
        """Körper, Kleider, Haar — in dieser Reihenfolge."""
        return [self.koerper()] + self._kleidung(modell) + self._haar(modell)

    # ------------------------------------------------------------------ GLB

    @staticmethod
    def glb(teile, pfad, punkte_je_teil=None):
        """Alle Teile als GLB mit flachen Farben (`punkte_je_teil`: andere Punkte, etwa gehäutet)."""
        import trimesh
        szene = trimesh.Scene()
        for i, t in enumerate(teile):
            punkte = t['punkte'] if punkte_je_teil is None else punkte_je_teil[i]
            netz = trimesh.Trimesh(vertices=np.asarray(punkte, dtype=np.float64),
                                   faces=np.asarray(t['dreiecke'], dtype=np.int64), process=False)
            rgb = [int(round(float(c) * 255)) for c in np.asarray(t['farbe'])[:3]]
            netz.visual = trimesh.visual.ColorVisuals(
                netz, vertex_colors=np.tile(np.array([*rgb, 255], dtype=np.uint8), (len(netz.vertices), 1)))
            szene.add_geometry(netz, node_name='%s_%d' % (t.get('sorte') or t.get('art'), i))
        pfad.parent.mkdir(parents=True, exist_ok=True)
        szene.export(str(pfad))
        return pfad
