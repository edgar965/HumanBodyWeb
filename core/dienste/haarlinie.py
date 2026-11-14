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

import torch
from KoerperKI_alle.torchfeld import Torchfeld

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
    #: Feinraster der Haarlinie: so viele Zellen je 5°-Feld und Richtung (4 → 1,25°). Auf dem 5°-Raster war der Rand um das Ohr eine Treppe aus Feldern von 9 mm Seite (Edgar, 07.10.2026: „das Haar ist sehr eckig um die Ohren").
    FEIN = 4
    #: Um jeden Hautpunkt des Ohrs wächst im Umkreis von so vielen Grad kein Haar (Scheiben, nicht Felder: der Rand um das Ohr ist rund) …
    OHR_ABSTAND = 7.0
    #: … und die Haarlinie als Ganzes wird mit dieser Gauß-Breite (Grad) gerundet: die Ecken an Schläfe, Koteletten und Gesichtsrand werden Bögen. Gesehen am Herrenhaar des Auftrags `2026.10.07.17.45.25`
    #: (`ProjektTemp/_wegwerf/edgar/haar_ansicht.py`, Seitenansicht): bei 3° blieb die Stufe an der Schläfe (Gesichtsrand bei 62° Azimut, Kotelettengrenze bei 8°) fast rechteckig, bei 6° noch ein Absatz über dem Ohr, bei 9° eine
    #: glatte S-Kurve; 8° ist der Mittelweg (Annahme nach Sicht, kein Maß).
    RUNDUNG = 8.0

    @classmethod
    def _felder(cls, v, r, hoehe, breite):
        """Zeile und Spalte des Felds je Richtung (`Haarklemme`: Azimut von +z nach +x, Höhenwinkel von der Waagerechten)."""
        az = Torchfeld.degrees(Torchfeld.arctan2(v[:, 0], v[:, 2])) % 360.0
        el = Torchfeld.degrees(Torchfeld.arcsin(Torchfeld.clip(v[:, 1] / Torchfeld.maximum(r, 1e-12), -1.0, 1.0)))
        zeile = Torchfeld.clip(Torchfeld.astype((el + 90.0) * hoehe / 180.0, torch.int64), 0, hoehe - 1)
        spalte = Torchfeld.clip(Torchfeld.astype(az * breite / 360.0, torch.int64), 0, breite - 1)
        return zeile, spalte

    @classmethod
    def ohrfelder(cls, netz, mitte, hoehe, breite):
        """Bool (hoehe, breite): Felder mit Ohr — Hautpunkte mit Gewicht auf `l_ear`/`r_ear`, geschlossen und um `OHR_RAND` Felder erweitert (Azimut umlaufend). Leer ohne Ohrknochen in der Haut."""
        from KoerperKI_alle.kartenbild import Kartenbild as ndimage
        haut = (netz or {}).get('haut') or {}
        namen = [str(n) for n in haut.get('knochen') or []]
        ohren = [i for i, n in enumerate(namen) if n in ('l_ear', 'r_ear')]
        felder = torch.zeros((hoehe, breite), dtype=torch.bool, device='cuda')
        if not ohren:
            return felder
        index = Torchfeld.feld(haut['index']).reshape(-1, 4)
        gewicht = Torchfeld.feld(haut['gewicht'], dtype=torch.float64).reshape(-1, 4)
        w = sum((gewicht * (index == i)).sum(axis=1) for i in ohren)
        punkte = Torchfeld.feld(netz['punkte'], dtype=torch.float64)
        m = w >= cls.OHR_GEWICHT
        if not m.any():
            return felder
        v = punkte[m] - Torchfeld.feld(mitte, dtype=torch.float64)
        zeile, spalte = cls._felder(v, Torchfeld.linalg_norm(v, dim=1), hoehe, breite)
        felder[zeile, spalte] = True
        rand = cls.OHR_RAND + 2
        z = Torchfeld.pad(felder, ((rand, rand), (rand, rand)), mode='wrap')
        eins = torch.ones((3, 3), dtype=torch.bool, device='cuda')
        z = ndimage.binary_closing(z, eins, iterations=2)
        z = ndimage.binary_dilation(z, eins, iterations=cls.OHR_RAND)
        return z[rand:-rand, rand:-rand]

    @classmethod
    def nacken(cls, el, az):
        """Bool (hoehe, breite): unterhalb des Nackenrands, der von `UNTEN_MITTE` (hinten) zu `UNTEN_SEITE` (an den Ohren) ansteigt — glatt (Hermite)."""
        abstand = Torchfeld.abs(az - 180.0)[None, :]
        t = Torchfeld.clip(abstand / cls.NACKEN_BREITE, 0.0, 1.0)
        rand = cls.UNTEN_MITTE + (cls.UNTEN_SEITE - cls.UNTEN_MITTE) * t * t * (3.0 - 2.0 * t)
        return el <= rand

    @classmethod
    def ohrpunkte(cls, netz, mitte):
        """`(M, 3)` Einheitsvektoren vom Kopfmittelpunkt zu den Hautpunkten des Ohrs (Gewicht auf `l_ear`/`r_ear` ab `OHR_GEWICHT`) — leer ohne Ohrknochen in der Haut."""
        haut = (netz or {}).get('haut') or {}
        namen = [str(n) for n in haut.get('knochen') or []]
        ohren = [i for i, n in enumerate(namen) if n in ('l_ear', 'r_ear')]
        if not ohren:
            return torch.zeros((0, 3), dtype=torch.float64, device='cuda')
        index = Torchfeld.feld(haut['index']).reshape(-1, 4)
        gewicht = Torchfeld.feld(haut['gewicht'], dtype=torch.float64).reshape(-1, 4)
        w = sum((gewicht * (index == i)).sum(axis=1) for i in ohren)
        v = Torchfeld.feld(netz['punkte'], dtype=torch.float64)[w >= cls.OHR_GEWICHT] - Torchfeld.feld(mitte, dtype=torch.float64)
        return v / Torchfeld.maximum(Torchfeld.linalg_norm(v, dim=1, keepdim=True), 1e-12)

    @classmethod
    def rund(cls, grob, netz, mitte):
        """`(bereich, zelle)` — der Haarbereich (`grob`: Bool (hoehe, breite) auf dem 5°-Raster, OHNE Ohr: `ausschluss(…, mit_ohr=False)`) auf dem Feinraster (`FEIN`, `zelle` Grad je Zelle), das Ohr als Scheiben
        von `OHR_ABSTAND` Grad um seine Hautpunkte herausgenommen, das Ganze mit `RUNDUNG` Grad gerundet. Azimut umlaufend."""
        from KoerperKI_alle.kartenbild import Kartenbild as ndimage

        hoehe, breite = grob.shape
        fein = ndimage.zoom(Torchfeld.astype(grob, torch.float64), cls.FEIN, order=1, mode='grid-wrap', grid_mode=True) > 0.5
        zelle = 180.0 / fein.shape[0]
        ohr = cls.ohrpunkte(netz, mitte)
        if len(ohr):
            el = Torchfeld.radians((Torchfeld.arange(fein.shape[0]) + 0.5) * zelle - 90.0)[:, None]
            az = Torchfeld.radians((Torchfeld.arange(fein.shape[1]) + 0.5) * zelle)[None, :]
            richtung = Torchfeld.stack([Torchfeld.cos(el) * Torchfeld.sin(az), Torchfeld.sin(el) * torch.ones_like(az), Torchfeld.cos(el) * Torchfeld.cos(az)], axis=-1).reshape(-1, 3)     # wie `_felder`: Azimut von +z nach +x
            kleinster = torch.zeros(len(richtung), dtype=torch.float64, device='cuda')
            for anfang in range(0, len(richtung), 8000):
                kleinster[anfang:anfang + 8000] = Torchfeld.amax(richtung[anfang:anfang + 8000] @ ohr.T, dim=1)
            nah = (kleinster >= Torchfeld.cos(Torchfeld.radians(cls.OHR_ABSTAND))).reshape(fein.shape)
            fein = fein & ~nah
        sigma = cls.RUNDUNG / zelle
        return ndimage.gaussian_filter(Torchfeld.astype(fein, torch.float64), sigma, mode=('nearest', 'wrap')) > 0.5, zelle

    @classmethod
    def ausschluss(cls, netz, mitte, roh, mit_ohr=True):
        """`(ausgeschlossen, kotelett)`, beide Bool (hoehe, breite) — `ausgeschlossen`: hier wächst kein Haar (Gesicht, Ohr, Nacken); `kotelett`: Felder der Koteletten, die das Netzhaar `roh` (NaN = kein Netzhaar)
        mit genug Haar belegt, also Haar sein dürfen, auch wenn die Abdeckung Lücken hat. `mit_ohr=False`: das Ohr bleibt draußen (die Haarkappe nimmt es als runde Scheiben auf dem Feinraster, `rund`)."""
        hoehe, breite = roh.shape
        feld = 180.0 / hoehe
        el = ((Torchfeld.arange(hoehe) + 0.5) * feld - 90.0)[:, None]
        az = (Torchfeld.arange(breite) + 0.5) * (360.0 / breite)
        von_vorn = Torchfeld.minimum(az, 360.0 - az)[None, :]
        ohr = cls.ohrfelder(netz, mitte, hoehe, breite)
        if ohr.any():
            vorn = float(torch.where(ohr, von_vorn, 360.0).min())      # der vordere Rand des Ohrs (von vorn gezählt)
        else:
            vorn = 100.0                                            # ohne Ohrknochen: ein Ohr mittig an der Seite annehmen
        gesicht = (von_vorn <= cls.GESICHT_AZ) & (el < cls.GESICHT_EL)
        zone = (von_vorn > cls.GESICHT_AZ) & (von_vorn <= vorn) & (el >= cls.KOTELETT_EL) & (el < cls.GESICHT_EL)
        kotelett = torch.zeros(roh.shape, dtype=torch.bool, device='cuda')
        if zone.any() and float((~Torchfeld.isnan(roh))[zone].mean()) >= cls.KOTELETT_ANTEIL:
            kotelett = zone
        unter = (von_vorn > cls.GESICHT_AZ) & (von_vorn <= vorn) & (el < cls.KOTELETT_EL)      # unter den Koteletten: Wange und Kiefer
        return gesicht | unter | (ohr if mit_ohr else False) | cls.nacken(el, az), kotelett
