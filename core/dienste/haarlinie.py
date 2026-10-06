# -*- coding: utf-8 -*-
"""Haarlinie — wo am Kopf Haar wächst und wo nicht: Gesicht, Koteletten, Ohr und Nacken der Haarkappe (05.10.2026).

Edgar (Auftrag 2026.10.04.21.41.43, Iteration 1): „Haar ist eine Linie über den Ohren, ist nicht so im Bild, in der Vorlage ist das nicht so." Die Haarkappe (`Haarkappe`) hatte die Haarlinie aus der Abdeckung des
Netzhaars und zwei ANNAHMEN: bis Azimut 122° von vorn wächst unter 10° Höhenwinkel kein Haar, hinten reicht es bis −38°. Gemessen am Auftrag (`ProjektTemp/_wegwerf/edgar/ohr_knochen.py`, Hautpunkte um den Ohrknochen,
Radius über 0,095 m): das Ohr der Figur liegt im Azimut 79–135° und Höhenwinkel −41…+15°. Die Annahme schnitt also mitten durch das Ohr — oben 5° zu tief, hinten 13° zu früh —, und aus der Haarlinie über Schläfe und Ohr
(Azimut 40–122°) wurde ein Lineal bei 10°, dahinter eine senkrechte Klippe bis in den Nacken (Bild: eine harte Kante, ein Helm mit Visier). Im Foto setzt sich das Haar vor dem Ohr als Koteletten nach unten fort, schmiegt
sich über dem Ohr an dessen Rand und läuft hinter dem Ohr in den Nacken, der zu den Ohren hin ansteigt.

Hier steht die Haarlinie als Regeln, die an der FIGUR hängen statt an festen Winkeln:
  * **Ohr** — die Felder (5°), in denen Hautpunkte mit Gewicht auf den Ohrknochen `l_ear`/`r_ear` liegen (`OHR_GEWICHT`), plus ein Feld Luft: das Haar folgt dem Rand des Ohrs, wo immer es liegt;
  * **Gesicht** — vorn bis `GESICHT_AZ` kein Haar unter `GESICHT_EL` (Wange, Bartschatten, Schläfe); darüber entscheidet der Haaransatz des Netzhaars;
  * **Koteletten** — zwischen Gesicht und Ohr wächst Haar bis `KOTELETT_EL` herab, wenn das Netzhaar dort Haar zeigt (`KOTELETT_ANTEIL` der Felder), sonst nicht;
  * **Nacken** — der untere Rand liegt in der Mitte bei `UNTEN_MITTE` und steigt zu den Ohren hin auf `UNTEN_SEITE` (glatt über `NACKEN_BREITE`): ein runder Nacken statt einer Geraden.

`ausschluss(...)` gibt die Felder ohne Haar; `Haarkappe._linienfeld` zieht sie von der Abdeckung des Netzhaars ab.
"""

import numpy as np

__all__ = ['Haarlinie']


class Haarlinie:
    #: Hautgewicht auf dem Ohrknochen, ab dem ein Punkt zum Ohr zählt (0,5 fand nur den Kern: el −31…−0,4°, az 104–119°; der Rand des Ohrs hat kleine Gewichte).
    OHR_GEWICHT = 0.15
    #: Felder Luft um das Ohr.
    OHR_RAND = 1
    #: (Azimut von vorn bis, Höhenwinkel darüber das Netzhaar entscheidet): Gesicht, Wange, Bart, Schläfe.
    GESICHT_AZ = 62.0
    GESICHT_EL = 30.0
    #: Sigma (Felder) der Glättung der Haarfläche: rundet die Treppe der 5°-Felder an Ohr, Schläfe und Koteletten.
    GLAETTEN = 1.0
    #: Koteletten wachsen bis hierher herab (Höhenwinkel), Annahme: im Seitenfoto enden sie auf der Höhe der Ohroberkante (Ohr: −41…+15°), nicht an der Ohrmitte; Haar nur, wenn das Netzhaar dort mindestens `KOTELETT_ANTEIL` Haarfelder hat.
    KOTELETT_EL = 8.0
    KOTELETT_ANTEIL = 0.2
    #: Unterer Rand des Haars im Nacken (Höhenwinkel): Mitte, Seite (an den Ohren), Breite des Anstiegs (Grad Azimut um den Nacken).
    UNTEN_MITTE = -38.0
    UNTEN_SEITE = -24.0
    NACKEN_BREITE = 85.0

    @classmethod
    def _felder(cls, v, r, hoehe, breite):
        """Zeile und Spalte des Felds je Richtung (`Haarklemme`: Azimut von +z nach +x, Höhenwinkel von der Waagerechten)."""
        az = np.degrees(np.arctan2(v[:, 0], v[:, 2])) % 360.0
        el = np.degrees(np.arcsin(np.clip(v[:, 1] / np.maximum(r, 1e-12), -1.0, 1.0)))
        zeile = np.clip(((el + 90.0) * hoehe / 180.0).astype(int), 0, hoehe - 1)
        spalte = np.clip((az * breite / 360.0).astype(int), 0, breite - 1)
        return zeile, spalte

    @classmethod
    def ohrfelder(cls, netz, mitte, hoehe, breite):
        """Bool (hoehe, breite): Felder mit Ohr — Hautpunkte mit Gewicht auf `l_ear`/`r_ear`, geschlossen und um `OHR_RAND` Felder erweitert (Azimut umlaufend). Leer ohne Ohrknochen in der Haut."""
        from scipy import ndimage
        haut = (netz or {}).get('haut') or {}
        namen = [str(n) for n in haut.get('knochen') or []]
        ohren = [i for i, n in enumerate(namen) if n in ('l_ear', 'r_ear')]
        felder = np.zeros((hoehe, breite), dtype=bool)
        if not ohren:
            return felder
        index = np.asarray(haut['index']).reshape(-1, 4)
        gewicht = np.asarray(haut['gewicht'], dtype=np.float64).reshape(-1, 4)
        w = sum((gewicht * (index == i)).sum(axis=1) for i in ohren)
        punkte = np.asarray(netz['punkte'], dtype=np.float64)
        m = w >= cls.OHR_GEWICHT
        if not m.any():
            return felder
        v = punkte[m] - np.asarray(mitte, dtype=np.float64)
        zeile, spalte = cls._felder(v, np.linalg.norm(v, axis=1), hoehe, breite)
        felder[zeile, spalte] = True
        rand = cls.OHR_RAND + 2
        z = np.pad(felder, ((rand, rand), (rand, rand)), mode='wrap')
        eins = np.ones((3, 3), dtype=bool)
        z = ndimage.binary_closing(z, eins, iterations=2)
        z = ndimage.binary_dilation(z, eins, iterations=cls.OHR_RAND)
        return z[rand:-rand, rand:-rand]

    @classmethod
    def nacken(cls, el, az):
        """Bool (hoehe, breite): unterhalb des Nackenrands, der von `UNTEN_MITTE` (hinten) zu `UNTEN_SEITE` (an den Ohren) ansteigt — glatt (Hermite)."""
        abstand = np.abs(az - 180.0)[None, :]
        t = np.clip(abstand / cls.NACKEN_BREITE, 0.0, 1.0)
        rand = cls.UNTEN_MITTE + (cls.UNTEN_SEITE - cls.UNTEN_MITTE) * t * t * (3.0 - 2.0 * t)
        return el <= rand

    @classmethod
    def ausschluss(cls, netz, mitte, roh):
        """`(ausgeschlossen, kotelett)`, beide Bool (hoehe, breite) — `ausgeschlossen`: hier wächst kein Haar (Gesicht, Ohr, Nacken); `kotelett`: Felder der Koteletten, die das Netzhaar `roh` (NaN = kein Netzhaar)
        mit genug Haar belegt, also Haar sein dürfen, auch wenn die Abdeckung Lücken hat."""
        hoehe, breite = roh.shape
        feld = 180.0 / hoehe
        el = ((np.arange(hoehe) + 0.5) * feld - 90.0)[:, None]
        az = (np.arange(breite) + 0.5) * (360.0 / breite)
        von_vorn = np.minimum(az, 360.0 - az)[None, :]
        ohr = cls.ohrfelder(netz, mitte, hoehe, breite)
        if ohr.any():
            vorn = float(np.where(ohr, von_vorn, 360.0).min())      # der vordere Rand des Ohrs (von vorn gezählt)
        else:
            vorn = 100.0                                            # ohne Ohrknochen: ein Ohr mittig an der Seite annehmen
        gesicht = (von_vorn <= cls.GESICHT_AZ) & (el < cls.GESICHT_EL)
        zone = (von_vorn > cls.GESICHT_AZ) & (von_vorn <= vorn) & (el >= cls.KOTELETT_EL) & (el < cls.GESICHT_EL)
        kotelett = np.zeros(roh.shape, dtype=bool)
        if zone.any() and float((~np.isnan(roh))[zone].mean()) >= cls.KOTELETT_ANTEIL:
            kotelett = zone
        unter = (von_vorn > cls.GESICHT_AZ) & (von_vorn <= vorn) & (el < cls.KOTELETT_EL)      # unter den Koteletten: Wange und Kiefer
        return gesicht | unter | ohr | cls.nacken(el, az), kotelett
