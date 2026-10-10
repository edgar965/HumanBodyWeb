# -*- coding: utf-8 -*-
"""Schammessung — die Messung der Scham, die bei JEDEM Import läuft (10.10.2026).

Edgar: „mach kein Raten und Bildvergleich, sondern Messungen, so wie wir es einen Tag lang gemacht haben … Mach das auch bei dem Importprozess", „für jeden Importprozess [werden] bei der
Scham Messungen durchgeführt", „diesen Importprozess in einer Klasse festschreiben und IMMER aufrufen". Das ist diese Klasse. Aufrufer: `Dazgeograft.bauen` (Daz-Geograft, auch das an eine
Blender-Scham angepasste) und `Blendimportstuecke.scham_stueck` (Blender-, OBJ- und FBX-Import); die Farbe am Ring kommt dort nach dem Schritt „haut" (`Schammessungablage`).

Gemessen wird in vier Klassen, alle in mm / Farbwerten 0–255, Definitionen in deren Docstrings:

    `Schammessunggeometrie`   Form: Original → Modell je Zone, Tiefenkarte mit Mittelschnitt und Querprofilen, Stück → Original, Spiegelabstand
    `Schammessungnaht`        Naht: Rand → Ring, Normalenwinkel am Ring
    `Schammessungtextur`      Textur: Farbe am Ring gegen die Haut daneben, Farbe gegen das Original
    `Schammessungrahmen`      das gemeinsame Koordinatensystem und die Zonen

`abweichungen` nennt, was über den Schwellen unten liegt. Die Schwellen sind SETZUNGEN (kein Messwert), außer wo vermerkt; wer sie ändert, belegt es mit einer Messung. Ein Fehler der Messung bricht
den Import nie ab (`sicher`), steht aber im Bericht und im Log.
"""
import json
import logging

import numpy as np

from .schammessungzeilen import Schammessungzeilen

logger = logging.getLogger('core')

__all__ = ['Schammessung']


class Schammessung:
    #: Form: Original → Modell darf im Median höchstens so weit (mm) und bei p90 höchstens so weit abweichen (Setzung; das Nachformen des alten Stücks erreichte 0,14 / 1,1 mm, 08.10.2026).
    FORM_MEDIAN_MM, FORM_P90_MM = 1.0, 3.0
    #: Tiefenkarte: mittlerer Betrag des Unterschieds (mm), Setzung.
    TIEFE_MEDIAN_MM = 1.0
    #: Naht: größter Abstand Rand ↔ Ring (mm); der Bau legt den Rand auf die Ringecken (gemessen 0,000 mm, 09.10.2026).
    RAND_MAX_MM = 0.1
    #: Farbe am Ring: größter Leuchtdichte-Unterschied Stück ↔ Haut (Prozent); im Browser gerendert wurden 4 % gemessen (09.10.2026).
    LEUCHTDICHTE_PROZENT = 4.0
    #: Farbe gegen das Original: größter mittlerer Kanalunterschied (Setzung).
    ORIGINAL_FARBE_MITTEL = 12.0
    #: Die Haut und das Original werden im Kasten ums Stück plus so viel (m) zugeschnitten.
    UMKREIS_M = 0.04

    def __init__(self, punkte, dreiecke, uv_ecken, figur, loch, vorgabe=None, farbe_pfad=None, kachelbild=None):
        """`punkte`, `dreiecke`, `uv_ecken (T,3,2)`: das Stück nach der Naht; `figur`: `{punkte, dreiecke, uv, kachel}` (Stufe 1); `loch`: `{dreiecke, ring, ring_punkte[, ring_d]}` (oder None);
        `vorgabe`: `{punkte, dreiecke[, farbe_an, teil]}` — das Original (`teil`: nur der Teil, den die Figur nicht trägt); `farbe_pfad`: Farbbild des Stücks; `kachelbild(k)`: Pfad der Hautkachel `k`."""
        self.punkte = np.asarray(punkte, dtype=np.float64)
        self.dreiecke = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        self.uv_ecken = np.asarray(uv_ecken, dtype=np.float64)
        self.figur, self.loch, self.vorgabe = figur, loch, vorgabe
        self.farbe_pfad, self.kachelbild = farbe_pfad, kachelbild

    # ------------------------------------------------------------ Aufruf

    @classmethod
    def sicher(cls, ordner=None, **angaben):
        """Messen, ohne dass ein Fehler den Import beendet → Bericht (bei Fehler `{'fehler': Text}`); mit `ordner` wird `messung.json` dort abgelegt."""
        try:
            messung = cls(**angaben)
            bericht = messung.messen()
            for zeile in messung.zeilen(bericht):
                logger.info('Schammessung: %s', zeile)
            if ordner is not None:
                ordner.mkdir(parents=True, exist_ok=True)
                (ordner / 'messung.json').write_text(json.dumps(bericht, ensure_ascii=False, indent=1), encoding='utf-8')
            return bericht
        except Exception as fehler:  # noqa: BLE001 — die Messung darf den Import nie beenden; Grund steht im Log und im Bericht
            logger.exception('Schammessung gescheitert')
            return {'fehler': '%s: %s' % (type(fehler).__name__, str(fehler)[:300])}

    @classmethod
    def sicher_farbe(cls, **angaben):
        """Nur die Farbe am Ring, wenn die Hautkacheln erst nach dem Stück da sind (Blender-Import: Schritt „haut") — wie `sicher` ohne Wurf → Bericht."""
        try:
            messung = cls(**angaben)
            bericht = messung.farbe_am_ring()
            for zeile in Schammessungzeilen.zeilen({'stueck': {'punkte': len(messung.punkte), 'dreiecke': len(messung.dreiecke)}, 'farbe_am_ring': bericht, 'abweichungen': messung.abweichungen({'farbe_am_ring': bericht})}):
                logger.info('Schammessung: %s', zeile)
            return bericht
        except Exception as fehler:  # noqa: BLE001 — wie `sicher`
            logger.exception('Schammessung (Farbe am Ring) gescheitert')
            return {'fehler': '%s: %s' % (type(fehler).__name__, str(fehler)[:300])}

    def farbe_am_ring(self):
        from .schammessungnaht import Schammessungnaht
        from .schammessungtextur import Schammessungtextur

        f = self.figur
        sichtbar = np.ones(len(f['dreiecke']), dtype=bool)
        if self.loch:
            sichtbar[np.asarray(self.loch['dreiecke'], dtype=np.int64)] = False
        ring = np.asarray((self.loch or {}).get('ring', np.zeros((0, 3))), dtype=np.float64)
        rand = Schammessungnaht(self.punkte, self.dreiecke, ring, np.zeros_like(ring)).rand
        return Schammessungtextur.am_ring(rand, self.punkte, self.dreiecke, self.uv_ecken, Schammessungtextur.bild(self.farbe_pfad), f, sichtbar, self.kachelbild)

    def messen(self):
        import trimesh

        from .schammessunggeometrie import Schammessunggeometrie
        from .schammessungnaht import Schammessungnaht
        from .schammessungrahmen import Schammessungrahmen
        from .schammessungtextur import Schammessungtextur

        f = self.figur
        fp, fd = np.asarray(f['punkte'], dtype=np.float64), np.asarray(f['dreiecke'], dtype=np.int64)
        sichtbar = np.ones(len(fd), dtype=bool)
        if self.loch:
            sichtbar[np.asarray(self.loch['dreiecke'], dtype=np.int64)] = False
        lo, hi = self.punkte.min(axis=0) - self.UMKREIS_M, self.punkte.max(axis=0) + self.UMKREIS_M
        haut = self._zuschneiden(fp, fd[sichtbar], lo, hi)
        stueck = trimesh.Trimesh(self.punkte, self.dreiecke, process=False)
        modell = trimesh.util.concatenate([haut, stueck])
        ring_normalen = np.asarray(trimesh.Trimesh(fp, fd[sichtbar], process=False).vertex_normals)
        aus = {'stueck': {'punkte': int(len(self.punkte)), 'dreiecke': int(len(self.dreiecke))}}
        if self.loch:
            ring_punkte = np.asarray(self.loch['ring_punkte'], dtype=np.int64)
            rahmen = Schammessungrahmen.von_ring(fp, ring_normalen, ring_punkte, self.punkte)
            naht = Schammessungnaht(self.punkte, self.dreiecke, self.loch['ring'], ring_normalen[ring_punkte], self.loch.get('ring_d'))
            aus['naht'] = naht.messen()
            rand = naht.rand
        else:
            aus['naht'] = {'hinweis': 'Stück ohne Naht (kein Loch in der Haut)'}
            tief = np.asarray(haut.vertices)[np.unique(haut.faces)]
            nah = np.argsort(np.linalg.norm(tief - self.punkte.mean(axis=0), axis=1))[:50]
            rahmen = Schammessungrahmen(self.punkte.mean(axis=0), np.asarray(haut.vertex_normals)[np.unique(haut.faces)[nah]].mean(axis=0), self.punkte)
            rand, naht = np.zeros((0, 3)), None
        vorgabe, original = self._vorgabe(lo, hi, haut)
        geometrie = Schammessunggeometrie(rahmen, stueck, modell, vorgabe, original, rand)
        aus['geometrie'] = geometrie.messen()
        farbe = Schammessungtextur.bild(self.farbe_pfad)
        aus['farbe_am_ring'] = Schammessungtextur.am_ring(rand, self.punkte, self.dreiecke, self.uv_ecken, farbe, f, sichtbar, self.kachelbild)
        aus['farbe_gegen_original'] = Schammessungtextur.gegen_original(rahmen, self.punkte, self.dreiecke, self.uv_ecken, farbe,
                                                                        (self.vorgabe or {}).get('farbe_an'), geometrie.abstand_stueck)
        aus['abweichungen'] = self.abweichungen(aus)
        return aus

    def _vorgabe(self, lo, hi, haut):
        """`(vorgabe, original)` als `trimesh.Trimesh`: die zugeschnittene Vorgabe und das Original für Strahlen (bei einer Teil-Vorgabe samt sichtbarer Haut)."""
        import trimesh

        if not self.vorgabe:
            return None, None
        vorgabe = self._zuschneiden(np.asarray(self.vorgabe['punkte'], dtype=np.float64), np.asarray(self.vorgabe['dreiecke'], dtype=np.int64), lo, hi)
        if not len(vorgabe.faces):
            return None, None
        return vorgabe, (trimesh.util.concatenate([vorgabe, haut]) if self.vorgabe.get('teil') else vorgabe)

    @staticmethod
    def _zuschneiden(punkte, dreiecke, lo, hi):
        """Die Dreiecke, deren Mitte im Kasten `lo … hi` liegt, ohne ungenutzte Punkte."""
        import trimesh

        mitte = punkte[dreiecke].mean(axis=1)
        netz = trimesh.Trimesh(punkte, dreiecke[((mitte >= lo) & (mitte <= hi)).all(axis=1)], process=False)
        netz.remove_unreferenced_vertices()
        return netz

    # ------------------------------------------------------------ Urteil

    def abweichungen(self, m):
        """Texte zu allem, was über den Schwellen liegt (leer = alles innerhalb)."""
        a = []
        g = m.get('geometrie') or {}
        o = (g.get('original_zu_modell') or {}).get('gesamt')
        if o and (o['median'] > self.FORM_MEDIAN_MM or o['p90'] > self.FORM_P90_MM):
            a.append('Form: Original → Modell Median %.2f / p90 %.2f mm (Schwelle %.1f / %.1f)' % (o['median'], o['p90'], self.FORM_MEDIAN_MM, self.FORM_P90_MM))
        t = (g.get('tiefenkarte') or {}).get('betrag')
        if t and t['median'] > self.TIEFE_MEDIAN_MM:
            a.append('Tiefenkarte: mittlerer Unterschied %.2f mm (Schwelle %.1f)' % (t['median'], self.TIEFE_MEDIAN_MM))
        n = m.get('naht') or {}
        for schluessel in ('rand_zu_ring_mm', 'ring_zu_rand_mm'):
            if n.get(schluessel) and n[schluessel]['max'] > self.RAND_MAX_MM:
                a.append('Naht: %s größter Wert %.2f mm (Schwelle %.1f)' % (schluessel, n[schluessel]['max'], self.RAND_MAX_MM))
        for band in (m.get('farbe_am_ring') or {}).get('baender', []):
            if band.get('n') and abs(band['leuchtdichte_prozent']) > self.LEUCHTDICHTE_PROZENT:
                a.append('Farbe am Ring, Band %s mm: Leuchtdichte %+.1f %% gegen die Haut (Schwelle %.0f %%)' % (band['band_mm'], band['leuchtdichte_prozent'], self.LEUCHTDICHTE_PROZENT))
        c = m.get('farbe_gegen_original') or {}
        if c.get('mittel') is not None and c['mittel'] > self.ORIGINAL_FARBE_MITTEL:
            a.append('Farbe gegen Original: mittlerer Unterschied %.1f (Schwelle %.0f)' % (c['mittel'], self.ORIGINAL_FARBE_MITTEL))
        return a

    @staticmethod
    def zeilen(m):
        """Der Bericht als lesbare Zeilen (Log, Befehlsausgabe)."""
        return Schammessungzeilen.zeilen(m)
