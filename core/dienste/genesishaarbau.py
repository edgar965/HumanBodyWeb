# -*- coding: utf-8 -*-
"""Genesishaarbau — aus einem Wertesatz der Iterationen die Punkte der Frisur (30.09.2026).

Der eine Schritt zwischen `Haarparameter` (Zahlen) und `Genesishaarrender` (Bilder): Welche Frisur ist an,
wie stehen ihre Morphs, wie ihre fünf Formachsen? Gebaut wird mit denselben Klassen, die auch die Bühne und
die Frisurwahl von „Mesh to 3D" benutzen (`Meshfigurfrisurstueck` → `G9folger.punkte_zu`, dazu
`G9haarachsen`) — es gibt keinen zweiten Weg, eine Frisur auf eine Figur zu setzen.

**Daz-Morphe sind linear** (`Haar/frisurregler.py`: Punkte(w) = Punkte(0) + Σ wᵢ · Δᵢ). Ein Kandidat kostet
deshalb keine neue Projektion, sondern eine Summe: `deltas()` rechnet die Wirkung jedes Reglers EINMAL je
Frisur (der teure Teil), danach ist jeder weitere Wertesatz eine Matrixmultiplikation. Die Iterationen
schlagen je Runde `kandidaten` Wertesätze vor — ohne diesen Vorrat wäre jeder davon ein voller Neubau.

Die Lage ist die der Bühne: Meter, Y oben, Füße auf 0 (`Meshfigurfrisurstueck`).
"""

import logging

import numpy as np

from .haarparameter import Haarparameter

logger = logging.getLogger('core')

__all__ = ['Genesishaarbau']


class Genesishaarbau:
    """`punkte(werte)` → (N, 3) der getragenen Frisur; `farbe(werte)`; `kleidung(werte)`."""

    def __init__(self, formung):
        """`formung`: die Stellung der Grundfigur (`G9formung`) — dieselbe, auf der die Figur steht."""
        self.formung = formung
        self._stuecke = {}
        self._vorrat = {}
        self._laengen = {}

    # ------------------------------------------------------------- Frisur

    def stueck(self, kennung):
        from .meshfigurfrisurstueck import Meshfigurfrisurstueck
        if kennung not in self._stuecke:
            self._stuecke[kennung] = Meshfigurfrisurstueck(kennung, self.formung)
        return self._stuecke[kennung]

    def _deltas(self, kennung):
        """(Grundpunkte, {schluessel: (N, 3)}) — einmal je Frisur, danach kostet ein Kandidat eine Summe."""
        if kennung in self._vorrat:
            return self._vorrat[kennung]
        stueck = self.stueck(kennung)
        namen = [k for k in Haarparameter.schema()
                 if k.startswith('%s.%s' % (kennung, Haarparameter.MORPH))]
        kanaele = {k: k.split(Haarparameter.MORPH, 1)[1] for k in namen}
        teilpunkte = stueck.teilpunkte()
        self._laengen[kennung] = [len(p) for p in teilpunkte]
        grund = np.vstack(teilpunkte)
        deltas = {}
        for schluessel, kanal in kanaele.items():
            try:
                deltas[schluessel] = stueck.punkte(None, {kanal: 1.0}) - grund
            except (OSError, ValueError, KeyError) as fehler:
                logger.warning('Haarbau %s: Regler %s übersprungen (%s)', kennung, kanal, fehler)
        deltas.update(self._achsendeltas(kennung, stueck, grund))
        self._vorrat[kennung] = (grund, deltas)
        return self._vorrat[kennung]

    def _achsendeltas(self, kennung, stueck, grund):
        """Die fünf Formachsen als Deltas auf denselben Punkten — über `G9haarachsen.anwenden`, das
        je Teilnetz rechnet (ein mehrteiliges Haar hat je Teil einen eigenen Deltasatz)."""
        from Genesis9.haarachsen import G9haarachsen
        if not G9haarachsen.vorhanden(kennung):
            return {}
        kaefige = stueck.teilpunkte()
        aus = {}
        for achse, _anzeige, _methode in G9haarachsen.KANAELE:
            neu = G9haarachsen.anwenden(kennung, stueck.teile, kaefige, {achse: 1.0})
            aus['%s.%s%s' % (kennung, Haarparameter.ACHSE, achse)] = np.vstack(neu) - grund
        return aus

    def dreiecke(self, kennung):
        """Die Dreiecke aller Teile, auf die gestapelten Punkte umnummeriert (`punkte` stapelt sie
        in derselben Reihenfolge) — oder None bei einem Netz ohne Flächen (Stranghaar)."""
        self._deltas(kennung)                       # füllt die Teillängen
        versatz, alle = 0, []
        for (folger, _lage), anzahl in zip(self.stueck(kennung).teile, self._laengen[kennung],
                                           strict=True):
            dreiecke = np.asarray(getattr(folger, 'dreiecke', None), dtype=np.int64)
            if dreiecke.size:
                alle.append(dreiecke.reshape(-1, dreiecke.shape[-1]) + versatz)
            versatz += anzahl
        return np.vstack(alle) if alle else None

    def punkte(self, werte):
        """(N, 3) der getragenen Frisur in der Lage der Bühne — oder None, wenn keine an ist."""
        kennung = Haarparameter.getragene(werte)
        if not kennung:
            return None, None
        grund, deltas = self._deltas(kennung)
        punkte = grund.copy()
        for schluessel, delta in deltas.items():
            wert = float((werte or {}).get(schluessel, 0.0) or 0.0)
            if abs(wert) > 1e-6:
                punkte += wert * delta
        return kennung, punkte

    # -------------------------------------------------------------- Farbe

    @staticmethod
    def farbe(werte):
        """Die Umfärbung als `#rrggbb` (sRGB) — wie `Meshfigurfrisur.farbe`."""
        kanaele = []
        for kanal in 'rgb':
            try:
                kanaele.append(float((werte or {}).get('farbe.haar.%s' % kanal, 0.0) or 0.0))
            except (TypeError, ValueError):
                kanaele.append(0.0)
        return '#%02x%02x%02x' % tuple(int(round(min(1.0, max(0.0, k)) * 255)) for k in kanaele)

    def kleidung(self, werte):
        """Der Eintrag für `figur.kleidung` eines Modells — die getragene Frisur mit ihren Reglern."""
        kennung = Haarparameter.getragene(werte)
        if not kennung:
            return {}
        vorn = '%s.%s' % (kennung, Haarparameter.MORPH)
        regler = {k.split(Haarparameter.MORPH, 1)[1]: float(v)
                  for k, v in (werte or {}).items() if k.startswith(vorn)}
        from Genesis9.haarachsen import G9haarachsen
        for achse, _anzeige, _methode in G9haarachsen.KANAELE:
            wert = float((werte or {}).get('%s.%s%s' % (kennung, Haarparameter.ACHSE, achse), 0.0) or 0.0)
            if abs(wert) > 1e-6:
                regler['%s%s' % (G9haarachsen.PRAEFIX, achse)] = wert
        return {kennung: self.stueck(kennung).kleidung(None, regler, self.farbe(werte))}
