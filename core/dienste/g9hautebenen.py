# -*- coding: utf-8 -*-
"""G9hautebenen — die Gebiete für Sommersprossen und Altersflecken als Karten der Genesis-9-Kacheln (17.10.2026).

Edgar, 17.10.2026: „Baue noch Hautebenen: Hautton, Sommersprossen, Altersflecken, graue Haare, Muskel- und Fettzeichnung." Die Punkte selbst zeichnet der Shader aus Rauschen
(Dichte, Größe, Kontrast sind Regler, Auflösung unbegrenzt); WO sie sitzen dürfen, steht in einem Bild je Kachel (`Genesis9haut.hautebenen`, ein Sampler):

    R   Sommersprossen-Gebiet     Körper: MB-Labs `frecklemask.png` (1024², HumanBody-UV), über denselben Weg wie die Verschiebung auf die Genesis-Kachel gelegt
                                  (`Bildmodellhautverschiebung.texel`); Gesicht: Nase, Wangen und Stirnrand aus den Landmarken (`G9gesichtsteile`) — MB-Labs Maske hat im Gesicht
                                  nur 0,04 (gemessen 17.10.2026: Kopf 0,04, Rumpf 0,45–0,49), die Gesichts-Gebiete sind GESETZT, nicht gemessen
    G   Altersflecken-Gebiet      GESETZT (kein System auf der Platte hat Altersflecken, `genesis9-alter.md` Tabelle 7): Handrücken und Unterarme außen, Stirn und
                                  Schläfen, Schultern/Décolleté nach oben gewandte Haut
    B   unbenutzt (0)

Je Kachel zusätzlich `meter_je_uv`: wie viele Meter eine UV-Einheit auf dieser Kachel misst (Median der Kantenlängen) — der Shader rechnet damit die Punktgröße von Millimetern
in UV um, sonst wären die Sommersprossen auf dem Kopf (kleine Kachelfläche) so groß wie das halbe Gesicht.

ABLAGE: `Genesis9/ablage/hautebenen_<geschlecht>_v<FASSUNG>_<kachel>.png` und `….json` — die Fassung steht im Namen (`artefakte-benennen.md`). Bau und Stand: `G9hautebenenablage`.
"""
import json
import logging
import os
import time

import numpy as np

from .g9hautfalten import G9hautfalten

logger = logging.getLogger('core')

__all__ = ['G9hautebenen']


class G9hautebenen(G9hautfalten):
    """`bauen()` rechnet alle Kacheln dieses Geschlechts und schreibt sie in die Ablage."""

    FASSUNG = 1
    OHNE_FALTEN = (1005,)                      # Nägel
    #: Der größte Wert der MB-Lab-Maske (168/255 weiblich, 153/255 männlich) wird 1.
    MASKE_MAX = {'female': 168.0 / 255.0, 'male': 153.0 / 255.0}
    #: Gesicht, Sommersprossen: (Teil, Radius m, Stärke) — gesetzt.
    GESICHT_SOMMER = (('nase', 0.022, 1.0), ('wange', 0.034, 0.85), ('stirn', 0.022, 0.35))
    #: Gesicht, Altersflecken: Stirn und Schläfen stark, Wangen schwach — gesetzt.
    GESICHT_ALTER = (('stirn', 0.030, 0.9), ('schlaefe', 0.030, 0.7), ('wange', 0.028, 0.35))
    #: Weichzeichnen der Karte (Pixel).
    GLAETTUNG_PX = 2.0

    @classmethod
    def stamm(cls, geschlecht):
        from Genesis9.pfade import G9pfade
        return G9pfade.ablage() / ('hautebenen_%s_v%d' % (geschlecht, cls.FASSUNG))

    # ------------------------------------------------------------- Quellen

    def _maske(self):
        """(1024, 1024) float — MB-Labs Sommersprossenmaske dieses Geschlechts, 0..1 (v = 0 unten wie `Hautverschiebung.abtasten`)."""
        from PIL import Image

        from .lippenmaske import Lippenmaske
        pfad = os.path.join(str(Lippenmaske.ordner()), 'human_%s_frecklemask.png' % self.geschlecht)
        return np.asarray(Image.open(pfad).convert('L'), dtype=np.float64) / 255.0

    @staticmethod
    def _glatt(t):
        """Smoothstep 0..1 (Anteile)."""
        t = np.clip(t, 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)

    @staticmethod
    def _gauss(abstand, radius):
        return np.exp(-(abstand / radius) ** 2)

    # ------------------------------------------------------------- Rechnen

    def felder(self, pos, normale, teil, uv, maske, gesicht):
        """`(sommer (n,), alter (n,))` — die beiden Gebiete je Texel; `teil` sind Nummern aus `G9koerperteile`."""
        from Genesis9.koerperteile import G9koerperteile
        from humanbody_core.hautverschiebung import Hautverschiebung
        from scipy.spatial import cKDTree

        nummer = G9koerperteile.NUMMER
        ist = lambda *namen: np.isin(teil, [nummer[n] for n in namen])           # noqa: E731
        kopf = ist('kopf')
        fk = np.clip(Hautverschiebung.abtasten(maske, uv) / self.MASKE_MAX[self.geschlecht], 0.0, 1.0)
        sommer = np.where(kopf, 0.0, fk * 0.9)
        alter = np.zeros(len(pos))
        seite = np.sign(pos[:, 0])
        aussen = self._glatt((normale[:, 0] * seite - 0.1) / 0.4)                # Handrücken/Außenseite des Arms: die Normale zeigt vom Körper weg
        hand = ist('l_hand', 'r_hand')
        arm = ist('l_unterarm', 'r_unterarm')
        alter[hand] = aussen[hand]
        alter[arm] = 0.7 * aussen[arm]
        sonne = self._glatt((normale[:, 1] - 0.3) / 0.5)                         # nach oben gewandte Haut
        schulter = ist('l_schulter', 'r_schulter', 'l_oberarm', 'r_oberarm', 'hals')
        alter[schulter] = 0.45 * sonne[schulter]
        rumpf = ist('rumpf')
        alter[rumpf] = 0.45 * sonne[rumpf] * self._glatt((pos[rumpf, 1] - 1.25) / 0.10)      # nur das Décolleté
        for name, radius, staerke in self.GESICHT_SOMMER:
            if name in gesicht:
                d, _i = cKDTree(gesicht[name]).query(pos[kopf])
                sommer[kopf] = np.maximum(sommer[kopf], staerke * self._gauss(d, radius))
        for name, radius, staerke in self.GESICHT_ALTER:
            if name in gesicht:
                d, _i = cKDTree(gesicht[name]).query(pos[kopf])
                alter[kopf] = np.maximum(alter[kopf], staerke * self._gauss(d, radius))
        return np.clip(sommer, 0.0, 1.0), np.clip(alter, 0.0, 1.0)

    def kachel(self, traeger, abtastung, nummer, grund):
        """`(bild (S, S, 3) uint8, meter_je_uv)` einer Kachel."""
        from scipy import ndimage

        kaefig, normalen, teil_je_punkt, maske, gesicht = grund
        drin, _lage_hb, uv, _abstand = traeger.texel(abtastung, nummer)
        _drin, ecken, anteile = abtastung.stellen(nummer)
        pos = np.einsum('nk,nkc->nc', anteile, kaefig[ecken])
        normale = np.einsum('nk,nkc->nc', anteile, normalen[ecken])
        normale /= np.maximum(np.linalg.norm(normale, axis=1, keepdims=True), 1e-9)
        fuehrend = ecken[np.arange(len(ecken)), anteile.argmax(1)]
        sommer, alter = self.felder(pos, normale, teil_je_punkt[fuehrend], uv, maske, gesicht)
        s = abtastung.seite
        karten = np.zeros((s, s, 3))
        karten[drin, 0], karten[drin, 1] = sommer, alter
        weg, (iy, ix) = ndimage.distance_transform_edt(~drin, return_indices=True)
        nah = (~drin) & (weg <= self.RAND_PX)
        karten[nah] = karten[iy[nah], ix[nah]]
        for k in range(2):
            karten[..., k] = ndimage.gaussian_filter(karten[..., k], self.GLAETTUNG_PX)
        lage = np.zeros((s, s, 3))
        lage[drin] = pos
        schritte = []
        for achse in (0, 1):
            zu = np.take(lage, np.arange(1, s), axis=achse)
            von = np.take(lage, np.arange(0, s - 1), axis=achse)
            beide = np.take(drin, np.arange(1, s), axis=achse) & np.take(drin, np.arange(0, s - 1), axis=achse)
            if beide.any():
                schritte.append(float(np.median(np.linalg.norm(zu - von, axis=2)[beide])))
        meter_je_uv = float(np.mean(schritte)) * s if schritte else 1.0
        bild = np.clip(karten * 255.0 + 0.5, 0, 255).astype(np.uint8)
        bild[~(drin | nah)] = 0
        return bild, meter_je_uv

    def bauen(self):
        """Alle Kacheln dieses Geschlechts in die Ablage; → die Liste (`{kachel: {meter_je_uv, …}}`, `sekunden`)."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.gesichtsteile import G9gesichtsteile
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile
        from Genesis9.texturabtastung import G9texturabtastung
        from PIL import Image

        t0 = time.perf_counter()
        abtastung = G9texturabtastung.holen(self.SEITE)
        netz = G9basisnetz.holen()
        kaefig = np.asarray(netz.punkte, dtype=np.float64)
        grund = (kaefig, np.asarray(netz.normalen(), dtype=np.float64), G9koerperteile.genesis_punkte(G9haut.holen()),
                 self._maske(), G9gesichtsteile.positionen(kaefig))
        if not grund[4]:
            logger.warning('Hautebenen: keine Landmarkentabelle — Gesichtsgebiete fehlen (G9netzlandmarken)')
        traeger = self._traeger()
        kacheln = {}
        for nummer in abtastung.kacheln:
            if int(nummer) in self.OHNE_FALTEN:
                continue
            bild, meter_je_uv = self.kachel(traeger, abtastung, nummer, grund)
            logger.info('Hautebenen %s Kachel %d: Sommersprossen max %d, Altersflecken max %d, %.3f m je UV (%.1f s)', self.geschlecht, nummer,
                        int(bild[..., 0].max()), int(bild[..., 1].max()), meter_je_uv, time.perf_counter() - t0)
            Image.fromarray(bild, 'RGB').save(self.bildpfad(self.geschlecht, nummer), 'PNG')
            kacheln[str(nummer)] = {'meter_je_uv': round(meter_je_uv, 4), 'sommer_max': int(bild[..., 0].max()), 'alter_max': int(bild[..., 1].max())}
        liste = {'geschlecht': self.geschlecht, 'fassung': self.FASSUNG, 'seite': self.SEITE, 'kacheln': kacheln,
                 'sekunden': round(time.perf_counter() - t0, 1)}
        ziel = self.listenpfad(self.geschlecht)
        vorlaeufig = ziel.with_suffix('.neu')
        vorlaeufig.write_text(json.dumps(liste), encoding='utf-8')
        vorlaeufig.replace(ziel)
        return liste
