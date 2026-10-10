# -*- coding: utf-8 -*-
"""Hautbackenblendermathe — die Gleitkomma-Bausteine von Blenders Normalenrechnung, Schritt für Schritt in float32 und in Blenders Reihenfolge.

Übernommen aus dem Quelltext von Blender v5.2.2 (gelesen 10.10.2026, `ProjektTemp/_wegwerf/hautbacken_normalen/quelle/`):
  * `dot`: `math::dot` (BLI_math_vector.hh) — `a0*b0`, dann `+= a1*b1`, `+= a2*b2`, von links.
  * `normalisieren`: `math::normalize` (BLI_math_vector.hh `normalize_and_get_length`) — Länge² > 1e-35, danach `v / sqrt(Länge²)` (DIVISION je Komponente);
    sonst der Nullvektor. Das benutzen die Punktnormalen, die Fächer und die Lnor-Räume.
  * `normalisieren_c`: `normalize_v3` (math_vector_inline.cc `normalize_v3_v3_length`) — Länge² > 1e-35, danach `a * (1.0f / sqrtf(d))` (Multiplikation mit dem
    Kehrwert; das andere Rundungsverhalten). Das benutzt nur `normal_calc_ngon` (Flächennormale, Newell).
  * `acos_naeherung`: `math::safe_acos_approx` (BLI_math_base.hh): die Näherung mit „denormal crush", Fehler bis 4,5e-5 — kein echtes arccos.
  * `kreuz`: `math::cross`.
  * `gruppensumme`: die Schleife `vert_normal += …` über die Polygone eines Punkts, in der Reihenfolge der Gruppe.
Alles auf float32-Feldern: ein float64 irgendwo würde die Rundung ändern.
"""

import numpy as np

__all__ = ['Hautbackenblendermathe']

F32 = np.float32


class Hautbackenblendermathe:
    EINS = F32(1.0)
    NULL = F32(0.0)
    SCHWELLE_LAENGE = F32(1.0e-35)
    PI = F32(np.pi)
    PI2 = F32(np.pi) * F32(2.0)
    #: `LNOR_SPACE_TRIGO_THRESHOLD (1.0f - 1e-4f)` in float32.
    TRIGO = F32(1.0) - F32(1e-4)
    _K = (F32(1.5707963267), F32(-0.213300989), F32(0.077980478), F32(-0.02164095))

    @staticmethod
    def punkt(a, b):
        return a[:, 0] * b[:, 0] + a[:, 1] * b[:, 1] + a[:, 2] * b[:, 2]

    @classmethod
    def kreuz(cls, a, b):
        return np.stack([a[:, 1] * b[:, 2] - a[:, 2] * b[:, 1],
                         a[:, 2] * b[:, 0] - a[:, 0] * b[:, 2],
                         a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]], axis=1)

    @classmethod
    def normalisieren(cls, v):
        """`math::normalize` — (n,3) float32."""
        laenge2 = cls.punkt(v, v)
        gut = laenge2 > cls.SCHWELLE_LAENGE
        laenge = np.sqrt(np.where(gut, laenge2, cls.EINS))
        aus = v / laenge[:, None]
        aus[~gut] = 0.0
        return aus

    @classmethod
    def normalisieren_c(cls, v):
        """`normalize_v3` — `(normalisiert, Länge)`; Länge 0 bei zu kleinem Vektor (dann Nullvektor)."""
        d = cls.punkt(v, v)
        gut = d > cls.SCHWELLE_LAENGE
        d = np.sqrt(np.where(gut, d, cls.EINS))
        faktor = cls.EINS / d
        aus = v * faktor[:, None]
        aus[~gut] = 0.0
        return aus, np.where(gut, d, cls.NULL)

    @classmethod
    def acos_naeherung(cls, x):
        """`math::safe_acos_approx(x)` für ein float32-Feld."""
        k0, k1, k2, k3 = cls._K
        f = np.abs(x)
        m = np.where(f < cls.EINS, cls.EINS - (cls.EINS - f), cls.EINS)
        a = np.sqrt(cls.EINS - m) * (k0 + m * (k1 + m * (k2 + m * k3)))
        return np.where(x < cls.NULL, cls.PI - a, a)

    @classmethod
    def gruppensumme(cls, werte, anfang):
        """Summe je Gruppe, sequentiell in Gruppenreihenfolge, von 0 beginnend: `werte` (E,3) float32, `anfang` (G+1) Offsets → (G,3) float32."""
        anzahl = np.diff(anfang)
        summe = np.zeros((len(anzahl), 3), dtype=np.float32)
        if len(werte) == 0:
            return summe
        for k in range(int(anzahl.max())):
            aktiv = np.flatnonzero(anzahl > k)
            summe[aktiv] += werte[anfang[aktiv] + k]
        return summe
