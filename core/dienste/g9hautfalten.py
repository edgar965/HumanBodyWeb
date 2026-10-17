# -*- coding: utf-8 -*-
"""G9hautfalten — HumanBodys Altersfalten als Normalenkarten der Genesis-9-Kacheln (17.10.2026).

WARUM (Edgar, 17.10.2026: „baue die Runzeln und Hautfalten"): Der Sammelregler „Alter" (`Genesis9/alter.py`) stellt
Morphs, die Haut bleibt glatt. HumanBody (MB-Lab) legt dagegen eine Verschiebungstextur auf die Haut, deren G-Kanal die
Falten des Alters sind (`human_<geschlecht>_displacement.png`: Halsringe, Augenfalten, Brust; Wert = R + alter·(G − 0,5)
…, ±5 mm bei Stärke 0,01 m — `humanbody_core/hautverschiebung.py`). Genesis' Kanten sind auf Stufe 1 3,3 mm lang
(`ProjektTemp/_wegwerf/alter/kantenlaenge.py`): eine Falte von 1 mm Tiefe ist dort keine Geometrie, nur Licht. Darum hier
eine NORMALENKARTE je UDIM-Kachel — der Browser legt sie als weitere Schicht über die Hautnormale (`Genesis9haut.falten`),
das Gewicht ist der Alterswert.

WIE: Die Zuordnung Texel → HumanBody-UV ist die der Bildmodell-Verschiebung (`Bildmodellhautverschiebung.texel`:
Texel → Käfiglage → HumanBody-Lage über die Paarung → nächster Punkt der HumanBody-Dreiecke desselben Körperteils →
UV der Ecken). Aus dem G-Kanal wird die Höhe in Metern ((G − 0,5) · 0,01 m = Wert bei Alter 1), je Texel die
Kantenlänge in Metern aus den Lagen der Nachbartexel, und die Normale aus der Steigung — die Falte hat also die Tiefe
und Breite, die HumanBody ihr gibt, nicht eine geratene Stärke. Weiblich und männlich je mit eigener Paarung und eigenem
Bild (wie `G9alter`: die Grundfigur im Rumpf wählt).

ABLAGE: `Genesis9/ablage/hautfalten_<geschlecht>_v<FASSUNG>_<kachel>.png` und `….json` (Kachel, Seite, Steigung) —
die Fassung steht im Namen (`artefakte-benennen.md`). Fehlt die Liste, gibt es kein Ergebnis (`G9hautfaltenablage`).
"""
import json
import logging
import time

import numpy as np

from .bildmodellhautverschiebung import Bildmodellhautverschiebung

logger = logging.getLogger('core')

__all__ = ['G9hautfalten']


class G9hautfalten:
    """`bauen(geschlecht)` rechnet alle Kacheln und schreibt sie in die Ablage."""

    #: Bei Änderungen an Rechnung oder Format erhöhen — die Dateinamen tragen sie. 2: Alpha = Furchentiefe; 3: Nähte der Übertragung flach (beides 17.10.2026).
    FASSUNG = 3
    #: FURCHEN (Alpha, 17.10.2026 — Edgar: „am Anschlag ist das ein etwa 50 jähriger Mann"): Die Normalen allein zeigen eine Falte nur im Streiflicht; in der
    #: Furche fehlt das Licht, das ein echtes Relief verschattet. Alpha = wie tief der Texel unter seiner Umgebung liegt (Weichzeichnen mit `HOEHLE_SIGMA_M`),
    #: `HOEHLE_VOLL_M` tief = 255. Gemessen am Bild (`ProjektTemp/_wegwerf/alter/falten_vorzeichen.py`): G − 0,5 ist meist positiv (Wülste, p99 +2,4 mm, 22 % unter 0) —
    #: das Vorzeichen allein taugt nicht, die örtliche Tiefe schon. Beide Maße gesetzt, nicht gemessen.
    HOEHLE_SIGMA_M = 0.0025
    HOEHLE_VOLL_M = 0.0008
    #: Kachelseite (Pixel). Die Quelle hat 2048² für den ganzen Körper; 1024² je Kachel verliert nichts.
    SEITE = 1024
    #: Der Rand der Inseln wird so weit nach außen gezogen, dass das Filtern keine flache Normale hereinzieht.
    RAND_PX = 6
    #: Weichzeichnen der Höhe vor der Steigung (Pixel): die Zuordnung Texel → HumanBody-UV ist nicht glatter als ein Pixel.
    GLAETTUNG_PX = 1.0
    #: Größte Steigung (Tangens) — 45°; die Quelle hat darüber nur Ausreißer an Nähten.
    STEIGUNG_MAX = 1.0
    #: Eine Kachel mit kleinerer 99-%-Steigung hat keine Falten und bekommt kein Bild.
    STEIGUNG_MIN = 0.01
    #: Die Nagelkachel (Finger- und Zehennägel) bekommt nie Falten: in der weiblichen Paarung landen ihre Texel auf Finger- und Zehenfalten der Quelle (p99 0,19, männlich 0,008) —
    #: Nägel mit Runzeln wären falsch.
    OHNE_FALTEN = (1005,)

    def __init__(self, geschlecht):
        self.geschlecht = 'male' if str(geschlecht).lower().startswith('m') else 'female'

    # ------------------------------------------------------------- Ablage

    @classmethod
    def stamm(cls, geschlecht):
        from Genesis9.pfade import G9pfade
        return G9pfade.ablage() / ('hautfalten_%s_v%d' % (geschlecht, cls.FASSUNG))

    @classmethod
    def bildpfad(cls, geschlecht, kachel):
        stamm = cls.stamm(geschlecht)
        return stamm.with_name('%s_%d.png' % (stamm.name, int(kachel)))

    @classmethod
    def listenpfad(cls, geschlecht):
        stamm = cls.stamm(geschlecht)
        return stamm.with_name(stamm.name + '.json')

    # ------------------------------------------------------------- Rechnen

    def _traeger(self):
        traeger = Bildmodellhautverschiebung({}, self.SEITE)
        traeger.GESCHLECHT = self.geschlecht          # die Paarung und das Bild dieses Geschlechts
        return traeger

    @staticmethod
    def _quelle(geschlecht):
        """(H, W) float32 — der G-Kanal des Datenbilds, 0,5 = keine Verschiebung."""
        from .verschiebungstextur import Verschiebungstextur
        return Verschiebungstextur.datenbild(geschlecht)[..., 1]

    def hoehe_und_mass(self, traeger, abtastung, nummer, quelle):
        """`(drin, hoehe (S, S) m, kante_x (S, S) m, kante_y (S, S) m)` einer Kachel; außerhalb der Inseln bis `RAND_PX` fortgesetzt."""
        from humanbody_core.hautverschiebung import Hautverschiebung
        from scipy import ndimage

        drin, pos, uv, _abstand = traeger.texel(abtastung, nummer)
        s = abtastung.seite
        hoehe = np.zeros((s, s))
        hoehe[drin] = (Hautverschiebung.abtasten(quelle, uv) - Hautverschiebung.MITTE) * Hautverschiebung.STAERKE
        lage = np.zeros((s, s, 3))
        lage[drin] = pos
        uvbild = np.zeros((s, s, 2))
        uvbild[drin] = uv
        weg, (iy, ix) = ndimage.distance_transform_edt(~drin, return_indices=True)
        nah = (~drin) & (weg <= self.RAND_PX)
        hoehe[nah] = hoehe[iy[nah], ix[nah]]
        kante_x = self._kante(lage, drin, 1)
        kante_y = self._kante(lage, drin, 0)
        self.naht = self._naht(uvbild, drin, hoehe, kante_x, kante_y)
        return drin | nah, hoehe, kante_x, kante_y

    #: NÄHTE (17.10.2026, zweiter Durchgang — im Chrome gesehen: helle und dunkle Striche von den Augenwinkeln zum Kiefer, an Schläfe und Nasenrücken, schon in Fassung 1):
    #: Wo die HumanBody-UV zwischen Nachbartexeln springt (Inselgrenze, der nächste HB-Punkt liegt auf einer anderen Insel) oder die Höhe steiler als `SPRUNG_STEIGUNG`
    #: wird, ist die Steigung keine Falte, sondern eine Naht der Übertragung — dort bleibt die Karte flach (`NAHT_PX` breit). `UV_SPRUNG` = so viele mittlere UV-Schritte.
    UV_SPRUNG = 12.0
    SPRUNG_STEIGUNG = 0.8
    NAHT_PX = 3

    def _naht(self, uvbild, drin, hoehe, kante_x, kante_y):
        u"""(S, S) bool — Texel an einer Naht der Übertragung (siehe `UV_SPRUNG`)."""
        from scipy import ndimage

        sprung = np.zeros(drin.shape, dtype=bool)
        for achse in (0, 1):
            d = np.linalg.norm(np.diff(uvbild, axis=achse), axis=2)
            beide = np.logical_and(np.take(drin, np.arange(1, drin.shape[achse]), axis=achse), np.take(drin, np.arange(0, drin.shape[achse] - 1), axis=achse))
            if not beide.any():
                continue
            grenze = self.UV_SPRUNG * max(float(np.median(d[beide])), 1e-9)
            stelle = beide & (d > grenze)
            if achse == 0:
                sprung[1:] |= stelle
                sprung[:-1] |= stelle
            else:
                sprung[:, 1:] |= stelle
                sprung[:, :-1] |= stelle
        steigung_y, steigung_x = np.gradient(hoehe)
        steil = np.hypot(steigung_x / np.maximum(kante_x, 1e-6), steigung_y / np.maximum(kante_y, 1e-6)) > self.SPRUNG_STEIGUNG
        return ndimage.binary_dilation((sprung | steil) & drin, iterations=self.NAHT_PX)

    @staticmethod
    def _kante(lage, drin, achse):
        """(S, S) Meter je Pixel entlang `achse` — aus den Nachbartexeln, wo beide in der Insel liegen, sonst vom nächsten gültigen."""
        from scipy import ndimage

        zu = np.take(lage, np.arange(2, lage.shape[achse]), axis=achse)
        von = np.take(lage, np.arange(0, lage.shape[achse] - 2), axis=achse)
        mass = np.linalg.norm(zu - von, axis=2) / 2.0
        gut = np.take(drin, np.arange(2, lage.shape[achse]), axis=achse) & np.take(drin, np.arange(0, lage.shape[achse] - 2), axis=achse)
        gut &= np.take(drin, np.arange(1, lage.shape[achse] - 1), axis=achse)
        voll = np.zeros(drin.shape)
        gueltig = np.zeros(drin.shape, dtype=bool)
        innen = [slice(None), slice(None)]
        innen[achse] = slice(1, -1)
        voll[tuple(innen)] = mass
        gueltig[tuple(innen)] = gut & (mass > 1e-6)
        if not gueltig.any():
            return np.full(drin.shape, 1e-3)
        _w, (iy, ix) = ndimage.distance_transform_edt(~gueltig, return_indices=True)
        return voll[iy, ix]

    def normalen(self, hoehe, kante_x, kante_y):
        """(S, S, 3) uint8 — Tangentenraum, OpenGL (Y = +v = im Bild nach oben), flach = (128, 128, 255)."""
        from scipy import ndimage

        glatt = ndimage.gaussian_filter(hoehe, self.GLAETTUNG_PX)
        steigung_y, steigung_x = np.gradient(glatt)               # Meter Höhe je Pixel
        sx = np.clip(steigung_x / np.maximum(kante_x, 1e-6), -self.STEIGUNG_MAX, self.STEIGUNG_MAX)
        sy = np.clip(steigung_y / np.maximum(kante_y, 1e-6), -self.STEIGUNG_MAX, self.STEIGUNG_MAX)
        naht = getattr(self, 'naht', None)
        if naht is not None and naht.shape == sx.shape:
            sx[naht] = 0.0
            sy[naht] = 0.0
        # Bildzeilen laufen nach unten, v nach oben: dh/dv = −sy → n_y = −dh/dv = +sy.
        n = np.dstack([-sx, sy, np.ones_like(sx)])
        n /= np.linalg.norm(n, axis=2, keepdims=True)
        return np.clip((n * 0.5 + 0.5) * 255.0 + 0.5, 0, 255).astype(np.uint8), np.hypot(sx, sy)

    def hoehle(self, hoehe, kante_x, drin):
        u"""(S, S) uint8 — die Furchentiefe für den Alpha-Kanal (siehe `HOEHLE_SIGMA_M`): wie weit der Texel unter seiner Umgebung liegt, `HOEHLE_VOLL_M` = 255."""
        from scipy import ndimage

        mass = float(np.median(kante_x[drin])) if drin.any() else 1e-3
        glatt = ndimage.gaussian_filter(hoehe, self.GLAETTUNG_PX)
        umgebung = ndimage.gaussian_filter(hoehe, max(1.0, self.HOEHLE_SIGMA_M / max(mass, 1e-6)))
        tiefe = np.clip((umgebung - glatt) / self.HOEHLE_VOLL_M, 0.0, 1.0)
        naht = getattr(self, 'naht', None)
        if naht is not None and naht.shape == tiefe.shape:
            tiefe[ndimage.binary_dilation(naht, iterations=self.NAHT_PX)] = 0.0     # an der Naht keine Furche
        return (tiefe * 255.0 + 0.5).astype(np.uint8)

    def bauen(self):
        """Alle Kacheln dieses Geschlechts in die Ablage; → die Liste (`{kachel: {steigung_p99, steigung_mittel}}`, `sekunden`)."""
        from Genesis9.texturabtastung import G9texturabtastung
        from PIL import Image

        t0 = time.perf_counter()
        abtastung = G9texturabtastung.holen(self.SEITE)
        traeger, quelle = self._traeger(), self._quelle(self.geschlecht)
        kacheln = {}
        for nummer in abtastung.kacheln:
            if int(nummer) in self.OHNE_FALTEN:
                continue
            gueltig, hoehe, kx, ky = self.hoehe_und_mass(traeger, abtastung, nummer, quelle)
            bild, steigung = self.normalen(hoehe, kx, ky)
            drin = abtastung.stellen(nummer)[0]
            bild = np.dstack([bild, self.hoehle(hoehe, kx, drin)])          # RGBA: Normale + Furchentiefe
            bild[~gueltig] = (128, 128, 255, 0)
            p99 = float(np.percentile(steigung[drin], 99)) if drin.any() else 0.0
            logger.info('Hautfalten %s Kachel %d: Steigung p99 %.3f, Mittel %.4f, Naht %.1f %% (%.1f s)', self.geschlecht, nummer, p99,
                        float(steigung[drin].mean()) if drin.any() else 0.0, float(self.naht[drin].mean() * 100) if drin.any() else 0.0,
                        time.perf_counter() - t0)
            if p99 < self.STEIGUNG_MIN:
                continue
            Image.fromarray(bild, 'RGBA').save(self.bildpfad(self.geschlecht, nummer), 'PNG')
            kacheln[str(nummer)] = {'steigung_p99': round(p99, 4), 'steigung_mittel': round(float(steigung[drin].mean()), 5)}
        liste = {'geschlecht': self.geschlecht, 'fassung': self.FASSUNG, 'seite': self.SEITE, 'kacheln': kacheln,
                 'sekunden': round(time.perf_counter() - t0, 1)}
        ziel = self.listenpfad(self.geschlecht)
        vorlaeufig = ziel.with_suffix('.neu')
        vorlaeufig.write_text(json.dumps(liste), encoding='utf-8')
        vorlaeufig.replace(ziel)                    # die Liste kommt zuletzt: sie sagt „fertig"
        return liste
