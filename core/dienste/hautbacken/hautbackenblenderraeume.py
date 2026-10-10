# -*- coding: utf-8 -*-
"""Hautbackenblenderraeume — Blenders Lnor-Räume (`CornerNormalSpace`) der Fächer und die Dekodierung der eigenen Normalen (`custom_normal`, INT16_2D).

Blender v5.2.2, `mesh_normals.cc` (gelesen 10.10.2026): `corner_fan_space_define` und `corner_space_custom_data_to_normal`. Die gespeicherten Werte sind zwei Winkelanteile
(alpha um `vec_ortho`, beta um `vec_lnor`) RELATIV zur automatischen Normale des Fächers; mit neuen Punkten ändern sich Normale, Referenzkante und Referenzwinkel, die Rohdaten
bleiben — und Blender liest daraus eine neue Normale. Genau das ist hier nachgebaut.

Ein Raum ist ein Wörterbuch aus (F,3)-/(F,)-float32-Feldern: `lnor`, `ref`, `ortho`, `alpha`, `beta`.
Ungültiger Raum (Referenz- oder Gegenkante fast parallel zur Normale): Blender gibt `ref_alpha = ref_beta = 0` zurück und lässt die übrigen Felder bei 0 (`CornerNormalSpace{}`) —
auch `vec_lnor`; die Dekodierung liefert dann `vec_lnor`, also den NULLvektor. So steht es im Quelltext; hier genauso übernommen.
"""

import numpy as np

from .hautbackenblendermathe import Hautbackenblendermathe as M

__all__ = ['Hautbackenblenderraeume']

SHRT_MAX = np.float32(32767.0)


class Hautbackenblenderraeume:
    @staticmethod
    def definieren(lnor, vec_ref, vec_other, alpha_kanten=None):
        """`corner_fan_space_define` für F Fächer zugleich. `alpha_kanten`: (F,) Mittel der Winkel aller Fächerkanten zur Normale oder NaN, wo der Fächer nur eine Ecke hat."""
        dtp_ref = M.punkt(vec_ref, lnor)
        dtp_other = M.punkt(vec_other, lnor)
        ungueltig = (np.abs(dtp_ref) >= M.TRIGO) | (np.abs(dtp_other) >= M.TRIGO)
        alpha_zwei = (M.acos_naeherung(dtp_ref) + M.acos_naeherung(dtp_other)) / np.float32(2.0)
        alpha = alpha_zwei if alpha_kanten is None else np.where(np.isnan(alpha_kanten), alpha_zwei, alpha_kanten)
        ref = M.normalisieren(vec_ref - lnor * dtp_ref[:, None])
        ortho = M.normalisieren(M.kreuz(lnor, ref))
        andere = M.normalisieren(vec_other - lnor * dtp_other[:, None])
        dtp = M.punkt(ref, andere)
        beta = M.acos_naeherung(dtp)
        beta = np.where(M.punkt(ortho, andere) < M.NULL, M.PI2 - beta, beta)
        beta = np.where(dtp < M.TRIGO, beta, M.PI2)
        raum = {'lnor': lnor.copy(), 'ref': ref, 'ortho': ortho, 'alpha': alpha.astype(np.float32), 'beta': beta.astype(np.float32)}
        for name in ('lnor', 'ref', 'ortho'):
            raum[name][ungueltig] = 0.0
        raum['alpha'][ungueltig] = 0.0
        raum['beta'][ungueltig] = 0.0
        return raum

    @staticmethod
    def dekodieren(raum, daten):
        """`corner_space_custom_data_to_normal`: `daten` (F,2) int16-Werte (je Fächer der Mittelwert) → (F,3) float32 (nicht normalisiert, wie in Blender)."""
        d0 = daten[:, 0].astype(np.float32)
        d1 = daten[:, 1].astype(np.float32)
        nichts = (daten[:, 0] == 0) | (raum['alpha'] == 0.0) | (raum['beta'] == 0.0)
        alphafac = d0 / SHRT_MAX
        alpha = np.where(alphafac > M.NULL, raum['alpha'], M.PI2 - raum['alpha']) * alphafac
        betafac = d1 / SHRT_MAX
        sin_alpha = Hautbackenblenderraeume._sinf(alpha)
        beta = np.where(betafac > M.NULL, raum['beta'], M.PI2 - raum['beta']) * betafac
        aus = raum['lnor'] * Hautbackenblenderraeume._cosf(alpha)[:, None]
        # betafac == 0: nur die Referenzrichtung mit sin(alpha); sonst Referenz- und Orthogonalrichtung mit sin(alpha)·cos/sin(beta)
        nur_ref = betafac == M.NULL
        f_ref = np.where(nur_ref, sin_alpha, sin_alpha * Hautbackenblenderraeume._cosf(beta))
        aus = aus + raum['ref'] * f_ref[:, None]
        mit_beta = ~nur_ref
        if mit_beta.any():
            aus[mit_beta] = aus[mit_beta] + raum['ortho'][mit_beta] * (sin_alpha * Hautbackenblenderraeume._sinf(beta))[mit_beta, None]
        aus[nichts] = raum['lnor'][nichts]
        return aus.astype(np.float32)

    @staticmethod
    def _sinf(x):
        """`sinf` wie die C-Bibliothek: auf float64 gerechnet und auf float32 gerundet. Numpys eigenes float32-`sin` weicht um 1 ulp ab (gemessen 10.10.2026: bitgleich 96,6 % → 99,95 %)."""
        return np.sin(x.astype(np.float64)).astype(np.float32)

    @staticmethod
    def _cosf(x):
        return np.cos(x.astype(np.float64)).astype(np.float32)
