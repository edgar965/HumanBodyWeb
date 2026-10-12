# -*- coding: utf-8 -*-
"""Meshfigurfrisurstueck — EINE Frisur der Garderobe auf der angepassten Figur, für die Frisurwahl.

Dieselbe Rechnung wie die Antwort an den Browser (`G9stueckteile.zusatz` + `G9folger.punkte_zu`): Vorgaben
des Presets, darüber der Stil, darüber die Regler; ein Stil mit Knochen (Eirgrid: Länge) dreht und skaliert
die eigenen Knochen. Punkte in Metern, Y oben, Füße auf 0 — die Lage der Figur in der Bühne, in der auch das
Haar des Netzes liegt (`Meshfigurhaar.objekt`). Ohne Lagenrechnung gegen andere Stücke (die Figur trägt in
„Mesh to 3D" nichts) und ohne Stufe: verglichen wird der Käfig.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurfrisurstueck']


class Meshfigurfrisurstueck:
    #: Stilarten, die eine Frisur formen (`G9garderobeeintrag.ARTEN`); „pose" dreht nur Zöpfe.
    STILARTEN = ('stil', 'laenge')
    HOECHSTENS_STILE = 8

    def __init__(self, kennung, formung):
        from Genesis9.garderobe import G9garderobe

        self.kennung = kennung
        self.eintrag = G9garderobe.eintrag(kennung) or {}
        self.formung = formung
        self.hoch = np.array([0.0, float(formung.boden()), 0.0])
        self.teile = G9garderobe.teile(kennung)

    @property
    def name(self):
        return self.eintrag.get('name') or self.kennung

    def stile(self):
        """`[None, {id, name, art}, …]` — ohne Stil zuerst, dann die formenden Stile des Stücks."""
        stile = [s for s in self.eintrag.get('stile') or [] if s.get('art') in self.STILARTEN]
        return [None] + stile[: self.HOECHSTENS_STILE]

    def grenzen(self):
        return {r['name']: (float(r['min']), float(r['max'])) for r in self.eintrag.get('regler') or []}

    def _zusatz(self, stil, regler=None):
        """`(zusatz, knochen)` wie `G9folger.punkte_zu` sie braucht: Vorgaben des Presets, darüber der Stil, darüber die Regler."""
        from Genesis9.garderobe import G9garderobe

        werte, knochen = G9garderobe.stilwerte(self.kennung, [stil['id']] if stil else [])
        zusatz = dict(self.eintrag.get('vorgaben') or {})
        zusatz.update(werte)
        zusatz.update(regler or {})
        return zusatz, knochen

    def teilpunkte(self, stil=None, regler=None):
        """`[(Nᵢ, 3)]` je Teil — die Form, die `G9haarachsen.anwenden` braucht (es rechnet je Netz)."""
        zusatz, knochen = self._zusatz(stil, regler)
        return [f.punkte_zu(self.formung, zusatz, drehung=knochen, lage=lage) - self.hoch
                for f, lage in self.teile]

    def punkte(self, stil=None, regler=None):
        """(N, 3) alle Teile hintereinander."""
        return np.vstack(self.teilpunkte(stil, regler))

    def deltas(self, stil, namen):
        """`{regler: (N, 3)}` Wirkung bei Wert 1 über dem Stil — Daz-Morphe sind linear. Direkt auf den Punkten des Morphs (`Meshfigurfrisurdeltas`, 12.10.2026: Eirgrid 51 s → Sekunden); was dieser Weg nicht
        kann (Prop, Passform, ein Kanal, den auch der Körper stellt), rechnet wie bisher die volle Differenz."""
        grund = self.punkte(stil)
        schnell = self._schnell(stil)
        aus = {}
        for n in namen:
            delta = schnell.delta(n) if schnell is not None else None
            aus[n] = delta if delta is not None else self.punkte(stil, {n: 1.0}) - grund
        return grund, aus

    def _schnell(self, stil):
        """`Meshfigurfrisurdeltas` zum Grundstand dieses Stils — `None`, wenn die Herleitung nicht gilt oder die Vorbereitung scheitert (der Aufrufer rechnet dann dicht)."""
        from .meshfigurfrisurdeltas import Meshfigurfrisurdeltas

        try:
            zusatz, knochen = self._zusatz(stil)
            schnell = Meshfigurfrisurdeltas(self.formung, self.teile, zusatz, knochen)
            return schnell if schnell.moeglich() else None
        except Exception:  # noqa: BLE001 — die dichte Rechnung ist der sichere Weg; hier nur Zeit gespart
            logger.exception('Frisur %s: schnelle Reglerwirkung nicht vorbereitet', self.kennung)
            return None

    def kleidung(self, stil, regler, farbe):
        """Der Eintrag für `figur.kleidung` eines Modells — dieselbe Form wie „Modell speichern" der Szene
        (`Genesis9Modell.kleidung`, `Genesis9lagen.stilliste`)."""
        stil_id, stile = '', {}
        if stil:
            if stil.get('art') == 'stil':
                stil_id = stil['id']
            else:
                stile[stil['art']] = stil['id']
        return {'variante': '', 'stil': stil_id, 'stile': stile, 'regler': dict(regler or {}), 'farbe': farbe,
                'gruppenfarben': {}, 'griff': False, 'knochen': bool(self.eintrag.get('eigene_knochen'))}
