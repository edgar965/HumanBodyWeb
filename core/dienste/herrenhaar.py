# -*- coding: utf-8 -*-
"""Herrenhaar — ein eigenes Kurzhaar für einen normalen Herrenschnitt, aus den Fotos angepasst (05.10.2026).

Edgar (Auftrag 2026.10.04.21.41.43, Iteration 1): „Beim Haar auch Texturprobleme, und Probleme in den Strähnen, oben scheint ein anderes Haar als unten. Vielleicht machst du dir ein Haarmodell als eigenes Modell, es scheint,
dass du ‚Randy' nimmst, der schwer anpassbar ist. Vielleicht erzeugst du ein Haar, das für einen normalen mittelalten Mann gedacht ist, der einen normalen Haarschnitt hat?" Gesehen in Iteration 1 (Kopfbild): Die Frisur der
Garderobe (Mavick Hair Style, für ein ganz anderes Aussehen gebaut) bestand aus Haarkarten, deren Deckkraftbilder KEIN Weg des Renders liest (`Mitsubamaterial`: die Karten stehen als undurchsichtige Klumpen) — oben dunkle
Fetzen, an den Seiten verschmierte Streifen, darunter eine Kappe aus Rauschen: zwei verschiedene Haare in einem Kopf.

Hier wächst das Haar selbst: Wurzeln auf der Kopfhaut (`Haarkappe.hautschnitt`, dasselbe Stück Haut, das die Haarlinie schneidet), je Wurzel eine Strähne als Band (`Haarband`) in einer Wuchsrichtung (`Haarwuchs`), so lang und
so dick, wie die Hülle des Fotohaars es dort zeigt (`Haarkappe.dicke_bei`): Die Spitzen liegen auf 70–100 % (außen) bzw. 30–70 % (innen) der Dicke, das Band steigt an der Wurzel an und legt sich an den Kopf — der Umriss ist der des
Fotohaars, die Fläche aus Strähnen. Darunter liegt die Haarkappe in dunklerem Ton (Wurzelschatten), darüber die Strähnen in `GRUPPEN` Helligkeiten um die Haarfarbe der Fotos (salzgrau statt Einheitsgrau; weniger Spreizung bei
dunklem, buntem Haar). Dichte und Länge laufen an der Haarlinie aus, die Linie selbst ist leicht unregelmäßig (Rauschfeld) — keine Kante wie mit dem Lineal.

Es sind ANNAHMEN über „normales" Haar (Wirbel, Wuchsrichtung, Spreizung der Helligkeiten, Streifenbreite), keine Messungen an diesem Auftrag; gemessen wird die Wirkung am Foto (Haarabgleich, Haarfarbe im Kopfbild).

    teile = Herrenhaar(ablage, netz).teile(rgb)      # [Kappe, Strähnengruppen …] wie `Kleidermodellbau.teile`, None ohne Hülle des Fotohaars
"""

import logging

import numpy as np

from .haarband import Haarband
from .haarkappe import Haarkappe
from .haarlaenge import Haarlaenge
from .haarwuchs import Haarwuchs

logger = logging.getLogger('core')

__all__ = ['Herrenhaar']


class Herrenhaar:
    #: Zählt hoch, wenn sich das Haar bei gleicher Eingabe ändert (gehört in die Fassung des Standmodells).
    #: 3 (07.10.2026): runde Haarlinie um die Ohren (`Haarkappe` 7); die Länge der Strähnen (und mit ihr die Dicke) ist je Höhe am Kopf wählbar: unten an Schläfen und Nacken, oben an der Kopfdecke (`Haarlaenge`).
    VERSION = 3
    SORTE = 'herrenhaar'
    #: Wurzeln je cm² Kopfhaut (am Testauftrag knapp 30.000 Strähnen) und Obergrenze.
    DICHTE_CM2 = 45.0
    HOECHSTENS = 60000
    #: Punkte je Strähne (Wurzel … Spitze) und Halbbreite des Bands an Wurzel und Spitze (m): eine Strähne ist ein Büschel von einigen Haaren, im Kopfbild (0,66 mm je Bildpunkt) rund 2 Bildpunkte breit.
    PUNKTE = 4
    BREITE_M = (0.00075, 0.00035)
    #: Die Länge der Strähne entlang des Kopfes (Bogenlänge ab der Wurzel) wählt `Haarlaenge`: ein Herrenschnitt ist an den Seiten und im Nacken kurz und wird nach oben zum Scheitel hin länger (Edgar, 07.10.2026: „kürzer
    #: seitlich (nach oben länger werdend) und hinten auch kürzer, wird dann länger wenn es zum Scheitel geht" — und: unten und oben als Regler, dazwischen interpoliert). Die Dicke der Kappe und der Strähnen folgt ihr.
    #: Die Spitze liegt über der Haarlinie mindestens so viele Grad (`_bis_zur_linie`).
    LINIE_ABSTAND = 1.0
    #: Anteil der Strähnen, deren Spitze innen liegt, und die Höhe der Spitzen als Anteil der Dicke (innen/außen) — beide ÜBER der Kappe (`KAPPE_DICKE`).
    INNEN = 0.35
    SPITZE_INNEN = (0.80, 0.92)
    SPITZE_AUSSEN = (0.92, 1.0)
    #: Das Band liegt so weit über der Haut (m), mindestens.
    ABSTAND_M = 0.0006
    #: Über der Hülle des Fotohaars steht höchstens so viel (m).
    UEBER_HUELLE_M = 0.003
    #: Unregelmäßigkeit der Haarlinie (Grad) und Auslauf der Dichte über der Linie.
    LINIE_GRAD = 2.5
    #: Helligkeiten der Strähnengruppen (Faktor um 1) bei voller Spreizung und ihre Anteile; Spreizung je Haar siehe `spreizung`.
    GRUPPEN = ((-0.45, 0.18), (-0.22, 0.27), (0.0, 0.25), (0.25, 0.20), (0.55, 0.10))
    #: Wie sehr die Helligkeit benachbarter Strähnen zusammenhängt (0 = Zufall, 1 = Rauschfeld): wenig — meliertes Haar ist fein gemischt, keine dunklen Flecken.
    GRUPPE_RAUSCHEN = 0.2
    #: Die Kappe darunter trägt diesen Anteil der Haarfarbe (Wurzelschatten); die Strähnen darüber gleichen es so aus, dass das Mittel die Haarfarbe trifft.
    KAPPE_ANTEIL = 0.8
    #: Anteil der Kappendicke an der Dicke des Haars (die Kappe liegt unter den Strähnen).
    KAPPE_DICKE = 0.75
    #: Die Röhren rendern im Mittel so viel dunkler als ihre Farbe (Mitsuba, Selbstverschattung der Strähnen): gemessen 05.10.2026 im Kopfbild gegen die Fotos, Fenster vorn/hinten/Seite 0,86–0,94, im Mittel 0,90.
    HELL = 1.11
    SAMEN = 7

    def __init__(self, ablage, netz, ansatz=0.0, laenge=None):
        """`ansatz`: Grad, um die der Haaransatz vorn angehoben wird (`Haaransatz`, Rezept `haar_ansatz`). `laenge`: eine `Haarlaenge` (unten/oben in cm, Rezept `haar_laenge`, Option `iterationen.haar_laenge_*`) — ohne die Vorgabe."""
        self.laenge = laenge or Haarlaenge()
        self.kappe = Haarkappe(ablage, netz, ansatz, dicke_faktor=self.laenge.dickefaktor)
        self.netz = netz

    # ------------------------------------------------------------------ Farbe

    @classmethod
    def spreizung(cls, rgb):
        """0,25 … 0,7: wie stark die Helligkeiten der Strähnen streuen — grau (unbunt, mittelhell) meliert stark, dunkles braunes Haar kaum."""
        c = np.asarray(rgb[:3], dtype=np.float64)
        sat = (c.max() - c.min()) / max(float(c.max()), 1e-6)
        grau = 1.0 - min(sat / 0.35, 1.0)
        return float(np.clip(0.25 + 0.45 * grau * min(float(c.max()) / 0.25, 1.0), 0.25, 0.7))

    @classmethod
    def farben(cls, rgb):
        """`(kappe, [(rgb, anteil) je Gruppe])` — die Strähnenfarben im Mittel (nach Anteilen) gleich der Haarfarbe `rgb` abzüglich der Kappe, die Kappe `KAPPE_ANTEIL` davon."""
        rgb = np.clip(np.asarray(rgb[:3], dtype=np.float64) * cls.HELL, 0.0, 1.0)
        s = cls.spreizung(rgb)
        faktoren = np.array([1.0 + d * s for d, _a in cls.GRUPPEN])
        anteile = np.array([a for _d, a in cls.GRUPPEN])
        faktoren = faktoren / float((faktoren * anteile).sum() / anteile.sum())      # Mittel nach Anteilen = 1
        kappe = rgb * cls.KAPPE_ANTEIL
        # sichtbar sind Strähnen und Kappe etwa im Verhältnis 70 : 30 — die Strähnen tragen den Rest, damit das Mittel stimmt
        sicht = 0.7
        streifen = np.clip((rgb - (1.0 - sicht) * kappe) / sicht, 0.0, 1.0)
        return kappe, [(np.clip(streifen * f, 0.0, 1.0), float(a)) for f, a in zip(faktoren, anteile)]

    # ------------------------------------------------------------------ Kopf

    def _hautkarte(self, klemme):
        """Radius der Haut je Richtungsfeld (m), lückenlos — der Höhenstand, über dem die Strähnen liegen."""
        p = np.asarray(self.netz['punkte'], dtype=np.float64)
        v = p - klemme.mitte
        r = np.linalg.norm(v, axis=1)
        nah = r < Haarkappe.REICHWEITE
        hoehe, breite = klemme.roh.shape
        karte = np.full((hoehe, breite), np.nan)
        zeile = np.clip(((np.degrees(np.arcsin(np.clip(v[nah, 1] / r[nah], -1.0, 1.0))) + 90.0) * hoehe / 180.0).astype(int), 0, hoehe - 1)
        spalte = np.clip((np.degrees(np.arctan2(v[nah, 0], v[nah, 2])) % 360.0 * breite / 360.0).astype(int), 0, breite - 1)
        np.fmax.at(karte, (zeile, spalte), r[nah])
        return Haarkappe._fuellen(karte, sigma=0.8)                        # noqa: SLF001 — dieselbe Füllung wie die Hülle

    def _wurzeln(self, schnitt, zufall):
        """Wurzeln auf den Dreiecken der Kopfhaut (nach Fläche): `(punkt (N, 3), ecke (N,))` — `ecke` ist der Eckpunkt (Index in die Reihen von `schnitt`) mit dem größten Anteil, von dem Haut und Gewichte kommen."""
        haut_p = schnitt[0].reshape(-1, 3, 3)
        flaeche = 0.5 * np.linalg.norm(np.cross(haut_p[:, 1] - haut_p[:, 0], haut_p[:, 2] - haut_p[:, 0]), axis=1)
        n = int(min(self.HOECHSTENS, round(float(flaeche.sum()) * 1.0e4 * self.DICHTE_CM2)))
        wahl = zufall.choice(len(flaeche), size=n, p=flaeche / flaeche.sum())
        w = zufall.dirichlet((1.0, 1.0, 1.0), size=n)
        punkt = (haut_p[wahl] * w[:, :, None]).sum(axis=1)
        return punkt, 3 * wahl + np.argmax(w, axis=1)

    def _bis_zur_linie(self, punkt, u0, t, r0, dicke, lauf):
        """Die Länge jeder Strähne so weit kürzen, dass ihre Spitze noch über der Haarlinie liegt (Halbierungssuche, 6 Schritte): Haar hängt nicht über die Linie hinaus — am Nacken und an den Koteletten standen sonst
        lange Fransen unter der Kappe."""
        unten, oben = np.zeros(len(lauf)), np.ones(len(lauf))
        for _ in range(6):
            mitte = 0.5 * (unten + oben)
            winkel = (lauf * mitte / np.maximum(r0 + 0.5 * dicke, 1e-3))[:, None]
            spitze = self.kappe._lage()[0].mitte + (u0 * np.cos(winkel) + t * np.sin(winkel)) * (r0 + 0.5 * dicke)[:, None]   # noqa: SLF001
            drin = self.kappe.dicke_bei(spitze)[1] > self.LINIE_ABSTAND
            unten, oben = np.where(drin, mitte, unten), np.where(drin, oben, mitte)
        return lauf * unten

    def _strahlen(self, klemme, karte, huelle, punkt, zufall):
        """Alle Strähnen: `(reihen (S, K, 3), aussen (S, K, 3), breite (S, K), behalten (N,))` — `behalten` sagt, welche Wurzeln eine Strähne tragen (Haarlinie, Dichte)."""
        dicke, grad, v, r0 = self.kappe.dicke_bei(punkt)
        u0 = v / r0[:, None]
        el = np.degrees(np.arcsin(np.clip(u0[:, 1], -1.0, 1.0)))                                    # Höhenwinkel der Wurzel am Kopf: danach richtet sich die Länge
        rau = Haarwuchs.rauschen(u0, self.SAMEN + 31)
        grad = grad + self.LINIE_GRAD * Haarwuchs.rauschen(u0, self.SAMEN + 32)
        rand = Haarkappe._weich(grad / Haarkappe.RAND_GRAD)                 # noqa: SLF001 — 0 an der Linie, 1 ab `RAND_GRAD` Grad darüber
        behalten = (grad > 0.0) & (zufall.random(len(punkt)) < 0.6 + 0.4 * rand)
        k = self.PUNKTE
        tau = np.linspace(0.0, 1.0, k)[None, :]
        innen = zufall.random(len(punkt)) < self.INNEN
        spitze = dicke * np.where(innen, zufall.uniform(*self.SPITZE_INNEN, len(punkt)), zufall.uniform(*self.SPITZE_AUSSEN, len(punkt)))
        # Die gewählte Länge (`Haarlaenge`) ist die mittlere: ±15 % nach Rauschfeld und ±15 % nach Zufall; ganz an der Haarlinie 80 % davon (die Dichte läuft dort ohnehin aus, `behalten`).
        lauf = self.laenge.laenge(el) * (0.85 + 0.30 * (rau + 1.0) / 2.0) * zufall.uniform(0.85, 1.15, len(punkt)) * (0.8 + 0.2 * rand)
        t = Haarwuchs.laufrichtung(u0, self.SAMEN)
        lauf = self._bis_zur_linie(punkt, u0, t, r0, dicke, lauf)
        winkel = lauf[:, None] * tau / np.maximum(r0 + 0.5 * dicke, 1e-3)[:, None]                  # Bogen entlang der Kugel um den Kopfmittelpunkt
        richtung = u0[:, None, :] * np.cos(winkel)[..., None] + t[:, None, :] * np.sin(winkel)[..., None]
        flach = richtung.reshape(-1, 3)
        eins = np.ones(len(flach))
        haut_r = klemme._grenze_je_punkt(flach, eins, karte).reshape(len(punkt), k)               # noqa: SLF001
        haut_w = klemme._grenze_je_punkt(u0, np.ones(len(u0)), karte)                              # noqa: SLF001
        grund = haut_r + (r0 - haut_w)[:, None]                                                    # die Wurzel liegt genau auf der Haut des Netzes
        radius = grund + spitze[:, None] * (1.0 - (1.0 - tau) ** 2)
        radius = np.minimum(radius, klemme._grenze_je_punkt(flach, eins, huelle).reshape(len(punkt), k) + self.UEBER_HUELLE_M)   # noqa: SLF001
        kappe = Haarkappe.RAND_DICKE + (dicke - Haarkappe.RAND_DICKE) * self.KAPPE_DICKE                 # die Kappe darunter: die Strähnen liegen immer darüber, sonst verschwänden sie in ihr
        radius = np.maximum(radius, grund + (kappe + self.ABSTAND_M)[:, None] * np.minimum(tau * 3.0, 1.0))
        radius[:, 0] = r0
        reihen = klemme.mitte + richtung * radius[..., None]
        breite = self.BREITE_M[0] + (self.BREITE_M[1] - self.BREITE_M[0]) * tau * np.ones((len(punkt), 1))
        return reihen, richtung, breite, behalten, u0, rau

    # ------------------------------------------------------------------ Teile

    def teile(self, rgb):
        """`[Kappe, Strähnengruppe …]` — Teile (`art` 'haar') in der Form von `Kleidermodellbau.teile`; None ohne Hülle des Fotohaars oder ohne Kopfhaut über der Haarlinie."""
        schnitt = self.kappe.hautschnitt()
        if schnitt is None:
            return None
        klemme, huelle, _linie = self.kappe._lage()                                             # noqa: SLF001
        zufall = np.random.default_rng(self.SAMEN)
        karte = self._hautkarte(klemme)
        punkt, ecke = self._wurzeln(schnitt, zufall)
        reihen, aussen, breite, behalten, u0, rau = self._strahlen(klemme, karte, huelle, punkt, zufall)
        reihen, aussen, breite, ecke, rau = reihen[behalten], aussen[behalten], breite[behalten], ecke[behalten], rau[behalten]
        if not len(reihen):
            return None
        kappenfarbe, gruppen = self.farben(rgb)
        teile = []
        kappe = self.kappe.teil(kappenfarbe, anteil=self.KAPPE_DICKE)
        if kappe is not None:
            kappe['dreiecke'] = np.asarray(kappe['dreiecke'], dtype=np.int64).reshape(-1, 3)
            teile.append(kappe)
        # Gruppe je Strähne: ein Rauschfeld mit etwas Zufall, nach Rang auf die Anteile verteilt — Strähnen derselben Gegend gleichen sich, wie Locken unterschiedlich hell
        wert = self.GRUPPE_RAUSCHEN * rau + (1.0 - self.GRUPPE_RAUSCHEN) * zufall.uniform(-1.0, 1.0, len(rau))
        rang = np.argsort(np.argsort(wert)) / max(len(wert) - 1, 1)
        grenzen = np.cumsum([a for _c, a in gruppen]) / sum(a for _c, a in gruppen)
        gruppe = np.minimum(np.searchsorted(grenzen, rang, side='left'), len(gruppen) - 1)
        haut = self.netz['haut']
        index, gewicht = schnitt[2], schnitt[3]
        k = self.PUNKTE
        for g, (farbe, _anteil) in enumerate(gruppen):
            wahl = np.flatnonzero(gruppe == g)
            if not len(wahl):
                continue
            punkte, dreiecke = Haarband.roehren(reihen[wahl], aussen[wahl], breite[wahl])
            je = ecke[wahl][Haarband.eckpunkte(len(wahl), k, 3)]
            teile.append({'art': 'haar', 'sorte': '%s_%d' % (self.SORTE, g), 'punkte': punkte, 'dreiecke': dreiecke, 'farbe': tuple(float(c) for c in farbe),
                          'haut': {'knochen': haut['knochen'], 'index': index[je], 'gewicht': gewicht[je]}, 'uv': None, 'normalen': None, 'gruppen': [],
                          'toenung': np.ones(3), 'textur': []})
        logger.info('Herrenhaar: %d Strähnen (%d Dreiecke) in %d Gruppen, Spreizung %.2f, Kappe %s', len(reihen), len(reihen) * 6 * (k - 1), len(teile) - (1 if kappe else 0), self.spreizung(rgb),
                    'ja' if kappe is not None else 'nein')
        return teile

    @classmethod
    def fingerabdruck(cls, ablage, laenge=None):
        """Gehört in die Fassung des Standmodells: Version dieses Haars, der Wuchsfelder, der gewählten Länge (`Haarlaenge`) und der Kappe samt der Quelle der Hülle — None ohne Quelle."""
        kappe = Haarkappe.fingerabdruck(ablage)
        return None if kappe is None else [cls.VERSION, kappe, cls.DICHTE_CM2, Haarwuchs.WIRBEL, Haarwuchs.NACH_HINTEN, (laenge or Haarlaenge()).fingerabdruck()]
