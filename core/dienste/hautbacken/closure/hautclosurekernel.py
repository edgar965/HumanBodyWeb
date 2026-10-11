# -*- coding: utf-8 -*-
"""Hautclosurekernel — die gebackene Normale, die Cycles aus den Closures des Principled BSDF bildet (`surface_shader_average_normal`: `normalize(Σ sc->N · |average(sc->weight)|)`).

Je Texel nach `svm_node_closure_bsdf` / `principled_bsdf_emission` (`kernel/svm/closure.h`, Blender v5.2.2): die Schichten Sheen → Lack (Coat) → Metall → Glanz → Untergrundstreuung/Diffus, jede mit ihrem
Gewicht (`closure_layering_weight`: was die obere Schicht übrig lässt, aus den Albedo-Tabellen), der Energieerhaltung der Multi-Scatter-Verteilung (`microfacet_ggx_preserve_energy`) und der Normale,
die sie bekommt: Diffus und Sheen die geglättete Normale `N`, alle Glanz-Closures `maybe_ensure_valid_specular_reflection(N)` (`hautclosurefunktionen.ensure_valid_specular_reflection`).

Dazu die Transmission (nicht dünnwandig: ein Glas-Closure, Multi-GGX mit den Glas-Tabellen) und die verbundene Coat-Normale (`coat_n`).
Nicht im Kern (der Aufrufer `Hautclosure` meldet es und lässt die Texel dann unverändert): Thin Wall, Dünnfilm, Mehrfach-Principled.
Die Tangente zählt nur als Schalter (`tang_gueltig`: der Eingang „Anisotropic" ist verbunden oder >= Schwelle — dann ist auch ein unverbundener Tangent-Eingang gültig): sie ändert
`alpha_x`/`alpha_y` (Anisotropie), nicht die Gewichte; die Albedo-Tabellen lesen `(alpha_x · alpha_y)^(1/4)`, das sich erst ändert, wenn `saturate(alpha_x)` klemmt (Rauheit 1).
"""

import warp as wp

from ..hautfunktionen import safe_normalize3, safe_sqrtf, saturatef
from .hautclosurefunktionen import (
    F0_from_ior,
    closure_layering_weight,
    fresnel_dielectric_Fss,
    fresnel_f82_Fss,
    fresnel_f82tint_B,
    ggx_darkening,
    glass_darkening,
    inverse_lerp,
    ior_from_F0,
    lookup_table_read_2D,
    schlick_s_ior,
)

__all__ = ['normale_mittel']

CUTOFF = 1.0e-5          # CLOSURE_WEIGHT_CUTOFF (kernel/types.h)
BSSRDF_MIN_RADIUS = 1.0e-8


@wp.func
def _mittel(a: wp.vec3) -> float:
    return (a[0] + a[1] + a[2]) / 3.0


@wp.func
def _null_hoch(a: wp.vec3) -> wp.vec3:
    """`closure_sample_weight`: negative Gewichte gibt es nicht."""
    return wp.vec3(wp.max(a[0], 0.0), wp.max(a[1], 0.0), wp.max(a[2], 0.0))


@wp.func
def _gueltig(ng: wp.vec3, i: wp.vec3, n: wp.vec3) -> wp.vec3:
    """`maybe_ensure_valid_specular_reflection` → `ensure_valid_specular_reflection` (`bsdf_util.h`): hebt `n` zur Flächennormale, wenn die Spiegelung unter die Fläche fiele."""
    if n[0] == ng[0] and n[1] == ng[1] and n[2] == ng[2]:
        return n
    r = 2.0 * wp.dot(n, i) * n - i
    iz = wp.dot(i, ng)
    threshold = wp.min(0.9 * iz, 0.01)
    if wp.dot(ng, r) >= threshold:
        return n
    x = n - wp.dot(n, ng) * ng
    laenge = wp.length(x)
    if laenge != 0.0:
        x = x * (1.0 / laenge)
    else:
        x = n
    ix = wp.dot(i, x)
    a = ix * ix + iz * iz
    b = 2.0 * (a + iz * threshold)
    c = (threshold + iz) * (threshold + iz)
    nz2 = float(0.0)
    if ix < 0.0:
        nz2 = 0.25 * (b + safe_sqrtf(b * b - 4.0 * a * c)) / a
    else:
        nz2 = 0.25 * (b - safe_sqrtf(b * b - 4.0 * a * c)) / a
    return safe_sqrtf(1.0 - nz2) * x + safe_sqrtf(nz2) * ng


@wp.kernel
def normale_mittel(n_in: wp.array(dtype=wp.vec3), ng_a: wp.array(dtype=wp.vec3), n_glatt: wp.array(dtype=wp.vec3), rueck: wp.array(dtype=wp.int32),
                   basis: wp.array(dtype=wp.vec3), metallisch: wp.array(dtype=wp.float32), rauheit: wp.array(dtype=wp.float32), ior_a: wp.array(dtype=wp.float32),
                   spec_stufe: wp.array(dtype=wp.float32), spec_tint: wp.array(dtype=wp.vec3), aniso: wp.array(dtype=wp.float32),
                   sheen_g: wp.array(dtype=wp.float32), sheen_r: wp.array(dtype=wp.float32), sheen_t: wp.array(dtype=wp.vec3),
                   coat_g: wp.array(dtype=wp.float32), coat_r: wp.array(dtype=wp.float32), coat_i: wp.array(dtype=wp.float32), coat_t: wp.array(dtype=wp.vec3),
                   coat_n: wp.array(dtype=wp.vec3), coat_n_verbunden: int, trans_g: wp.array(dtype=wp.float32),
                   sss_g: wp.array(dtype=wp.float32), sss_radius: wp.array(dtype=wp.vec3), sss_skala: wp.array(dtype=wp.float32),
                   multi_ggx: int, tang_gueltig: int, korrektur_an: int,
                   ggx_E: wp.array(dtype=wp.float32), ggx_Eavg: wp.array(dtype=wp.float32), ggx_s_ior: wp.array(dtype=wp.float32), sheen_ltc: wp.array(dtype=wp.float32),
                   glass_E: wp.array(dtype=wp.float32), glass_Eavg: wp.array(dtype=wp.float32), glass_inv_E: wp.array(dtype=wp.float32), glass_inv_Eavg: wp.array(dtype=wp.float32),
                   aus: wp.array(dtype=wp.vec3)):
    i = wp.tid()
    ng = ng_a[i]
    nsd = n_glatt[i]                                       # sd->N
    wi = nsd
    if rueck[i] != 0:
        wi = -nsd                                          # `wi = -ray.D` ist die geglättete Normale vor der Rückseiten-Umkehr
    n = safe_normalize3(n_in[i])
    if n[0] == 0.0 and n[1] == 0.0 and n[2] == 0.0:
        n = nsd                                            # safe_normalize_fallback(N, sd->N)
    gueltig = n                                            # `maybe_ensure_valid_specular_reflection`: ohne `SD_USE_BUMP_MAP_CORRECTION` bleibt die Normale
    if korrektur_an != 0:
        gueltig = _gueltig(ng, wi, n)
    eins = wp.vec3(1.0, 1.0, 1.0)
    schicht = eins                                         # `weight` der Schichtung (mix_weight = 1)
    summe = wp.vec3(0.0, 0.0, 0.0)

    # Alpha kommt hier nicht vor: `principled_bsdf_emission` skaliert bei Alpha < 1 alle Schichten mit Alpha (`weight *= alpha`) - das ändert die Richtung nicht - und legt eine Transparent-Closure
    # an (Gewicht 1 - Alpha, `bsdf->N = sd->N`). Die geht NICHT in die Mittelung ein: Beim Backen setzt `Integrator::device_update` `FILTER_CLOSURE_TRANSPARENT` (`scene/integrator.cpp`,
    # `bake_manager->get_baking()`), und `surface_shader_prepare_closures` macht daraus - VOR `film_write_data_passes` - `CLOSURE_HOLDOUT_ID`. Dieser Typ liegt hinter
    # `CLOSURE_BSSRDF_RANDOM_WALK_SKIN_ID`, `CLOSURE_IS_BSDF_OR_BSSRDF` zählt ihn also nicht mehr (alles Blender v5.2.2). Gemessen: Mix Shader aus Diffuse und Transparent, die Normale bleibt die des Diffuse
    # (`ProjektTemp/_wegwerf/cycles_vergleich/transparent_probe.py`), und im Zoo (`glanz_alpha_*`). Unter Alpha 0,5 schreibt Cycles den Normal-Pass gar nicht (`Hautalpha`).

    # Die Coat-Normale: ein unverbundener „Coat Normal" hängt Cycles an den Geometry-Knoten (`ShaderGraph::default_inputs`, `LINK_NORMAL` → Ausgang „Normal" = `sd->N`) — das ist die geglättete
    # Normale OHNE Normalenkarte/Bump, nicht das `N` des Principled. Verbunden (`coat_n_verbunden`): der Wert des Graphen, `safe_normalize_fallback(coat_normal, sd->N)`.
    nc = nsd
    if coat_n_verbunden != 0:
        nc = safe_normalize3(coat_n[i])
        if nc[0] == 0.0 and nc[1] == 0.0 and nc[2] == 0.0:
            nc = nsd
    lack_normale = nc                                      # `maybe_ensure_valid_specular_reflection(sd, coat_normal)`
    if korrektur_an != 0:
        lack_normale = _gueltig(ng, wi, nc)

    # ---- Sheen: die oberste Schicht; Normale = normalize(mix(N, coat_normal, saturate(coat_weight))), `mix(a, b, t) = a + t * (b - a)`
    sheen_w = wp.max(sheen_g[i], 0.0)
    coat_w = wp.max(coat_g[i], 0.0)
    if sheen_w > CUTOFF:
        w_s = _null_hoch(sheen_w * wp.cw_mul(_null_hoch(sheen_t[i]), schicht))
        if _mittel(w_s) >= CUTOFF:
            cm = saturatef(coat_g[i])
            n_s = safe_normalize3(n + cm * (nc - n))
            rau = wp.clamp(saturatef(sheen_r[i]), 1.0e-3, 1.0)
            cos_ni = wp.dot(n_s, wi)
            a = lookup_table_read_2D(sheen_ltc, cos_ni, rau, 0, 32, 32)
            albedo = lookup_table_read_2D(sheen_ltc, cos_ni, rau, 2 * 32 * 32, 32, 32)
            if not (wp.abs(a) < 1.0e-5 or albedo < 1.0e-5):
                w_s = w_s * albedo                         # bsdf->weight *= albedo
                summe = summe + n_s * wp.abs(_mittel(w_s))
                schicht = closure_layering_weight(w_s, schicht)

    # ---- Lack (Coat): glänzendes Dielektrikum, Normale = gültige Coat-Normale, Energieerhaltung immer, Albedo aus ggx_gen_schlick_ior_s
    if coat_w > CUTOFF:
        c_rau = saturatef(coat_r[i])
        c_ior = wp.max(coat_i[i], 1.0)
        w_c = _null_hoch(coat_w * schicht)
        if _mittel(w_c) >= CUTOFF:
            alpha = saturatef(c_rau * c_rau)
            rau4 = wp.sqrt(alpha)                          # (alpha_x · alpha_y)^(1/4) bei alpha_x = alpha_y
            mu = wp.dot(wi, lack_normale)
            fss = fresnel_dielectric_Fss(c_ior)
            w_c = wp.cw_mul(w_c, ggx_darkening(ggx_E, ggx_Eavg, mu, rau4, wp.vec3(fss, fss, fss)))
            summe = summe + lack_normale * wp.abs(_mittel(w_c))
            f = float(0.0)
            if c_ior > 1.0:
                s_c = schlick_s_ior(ggx_s_ior, rau4, mu, c_ior)
                f = F0_from_ior(c_ior) * (1.0 - s_c) + s_c           # mix(F0_from_ior(ior), 1, s)
            schicht = closure_layering_weight(w_c * f, schicht)
        tint = _null_hoch(coat_t[i])
        if not (tint[0] == 1.0 and tint[1] == 1.0 and tint[2] == 1.0):
            cos_ni = wp.dot(wi, lack_normale)
            cos_nt = wp.sqrt(1.0 - (1.0 / c_ior) * (1.0 / c_ior) * (1.0 - cos_ni * cos_ni))
            tiefe = 1.0 / cos_nt
            potenz = wp.vec3(wp.pow(tint[0], tiefe), wp.pow(tint[1], tiefe), wp.pow(tint[2], tiefe))
            schicht = wp.cw_mul(schicht, eins * (1.0 - coat_w) + potenz * coat_w)

    # ---- Grundwerte
    farbe = _null_hoch(basis[i])
    farbe_k = wp.vec3(wp.min(farbe[0], 1.0), wp.min(farbe[1], 1.0), wp.min(farbe[2], 1.0))
    ior = wp.max(ior_a[i], 1.0e-5)
    rau = saturatef(rauheit[i])
    alpha_x = rau * rau
    alpha_y = rau * rau
    an = saturatef(aniso[i])
    if an > 0.0 and tang_gueltig != 0:
        aspekt = wp.sqrt(1.0 - an * 0.9)
        alpha_x = alpha_x / aspekt
        alpha_y = alpha_y * aspekt
    alpha_x = saturatef(alpha_x)                           # bsdf_microfacet_ggx_setup
    alpha_y = saturatef(alpha_y)
    rau4 = wp.sqrt(wp.sqrt(alpha_x * alpha_y))
    mu = wp.dot(wi, gueltig)

    # ---- Metall (F82-Tint)
    met = saturatef(metallisch[i])
    if met > CUTOFF:
        w_m = _null_hoch(met * schicht)
        if _mittel(w_m) >= CUTOFF:
            if multi_ggx != 0:
                f82 = _null_hoch(spec_tint[i])
                f82 = wp.vec3(wp.min(f82[0], 1.0), wp.min(f82[1], 1.0), wp.min(f82[2], 1.0))
                b = wp.vec3(0.0, 0.0, 0.0)
                if not (f82[0] == 1.0 and f82[1] == 1.0 and f82[2] == 1.0):
                    b = fresnel_f82tint_B(farbe_k, f82)
                w_m = wp.cw_mul(w_m, ggx_darkening(ggx_E, ggx_Eavg, mu, rau4, fresnel_f82_Fss(farbe_k, b)))
            summe = summe + gueltig * wp.abs(_mittel(w_m))
        schicht = schicht * (1.0 - met)

    # ---- Transmission (Glas, nicht dünnwandig): ein Glas-Closure mit dem Gewicht transmission_weight * weight und der gültigen Normale; die Schichten darunter behalten (1 - transmission_weight)
    # (ohne Albedo-Abzug). Mit Multi-GGX rechnet `bsdf_microfacet_setup_fresnel_generalized_schlick` die Energieerhaltung mit den Glas-Tabellen ein: Fss = sqrt(Base Color) (Durchlass-Tönung);
    # ist die schwarz, gilt die Reflexion (`Fss = mix(f0, f90, s)`). Auf der Rückseite rechnet Cycles mit 1 / IOR (`bsdf->ior = backfacing ? 1 / ior : ior`).
    tw = saturatef(trans_g[i])
    if tw > CUTOFF:
        w_t = _null_hoch(tw * schicht)
        if _mittel(w_t) >= CUTOFF:
            if multi_ggx != 0:
                alpha_g = saturatef(rau * rau)                 # Glas ist immer isotrop: alpha_x = alpha_y = sqr(roughness)
                rau_g = wp.sqrt(wp.sqrt(alpha_g * alpha_g))
                ior_g = ior
                if rueck[i] != 0:
                    ior_g = 1.0 / ior
                durchlass = wp.vec3(wp.sqrt(farbe_k[0]), wp.sqrt(farbe_k[1]), wp.sqrt(farbe_k[2]))
                fss_g = durchlass
                if durchlass[0] == 0.0 and durchlass[1] == 0.0 and durchlass[2] == 0.0:
                    s_g = saturatef(inverse_lerp(F0_from_ior(ior_g), 1.0, fresnel_dielectric_Fss(ior_g)))
                    f0g = F0_from_ior(ior) * _null_hoch(spec_tint[i])
                    f0g = wp.vec3(saturatef(f0g[0]), saturatef(f0g[1]), saturatef(f0g[2]))
                    fss_g = f0g * (1.0 - s_g) + eins * s_g
                w_t = wp.cw_mul(w_t, glass_darkening(glass_E, glass_Eavg, glass_inv_E, glass_inv_Eavg, mu, rau_g, ior_g, fss_g))
            summe = summe + gueltig * wp.abs(_mittel(w_t))
        schicht = schicht * (1.0 - tw)

    # ---- Glanz (verallgemeinertes Schlick mit dem echten Dielektrikum, Exponent -eta)
    stufe = wp.max(spec_stufe[i], 0.0)
    eta = ior
    f0 = F0_from_ior(eta)
    if stufe != 0.5:
        f0 = f0 * 2.0 * stufe
        eta = ior_from_F0(f0)
        if ior < 1.0:
            eta = 1.0 / eta
    if eta != 1.0:
        w_g = _null_hoch(schicht)
        if _mittel(w_g) >= CUTOFF:
            tint = _null_hoch(spec_tint[i])
            f0v = f0 * tint
            f0v = wp.vec3(saturatef(f0v[0]), saturatef(f0v[1]), saturatef(f0v[2]))
            if multi_ggx != 0:
                s = saturatef(inverse_lerp(F0_from_ior(eta), 1.0, fresnel_dielectric_Fss(eta)))
                w_g = wp.cw_mul(w_g, ggx_darkening(ggx_E, ggx_Eavg, mu, rau4, f0v * (1.0 - s) + eins * s))
            summe = summe + gueltig * wp.abs(_mittel(w_g))
            sl = schlick_s_ior(ggx_s_ior, rau4, mu, eta)
            schicht = closure_layering_weight(wp.cw_mul(w_g, f0v * (1.0 - sl) + eins * sl), schicht)

    # ---- Untergrundstreuung und Diffus
    sss = saturatef(sss_g[i])
    if sss > CUTOFF:
        gew = _null_hoch(wp.cw_mul(farbe_k, schicht) * sss)
        if _mittel(gew) >= CUTOFF:
            radius = _null_hoch(sss_radius[i] * sss_skala[i])
            diffus = wp.vec3(0.0, 0.0, 0.0)
            streu = gew
            kanaele = int(3)
            for k in range(3):
                if radius[k] < BSSRDF_MIN_RADIUS:
                    diffus[k] = gew[k]
                    streu[k] = 0.0
                    kanaele = kanaele - 1
            if kanaele < 3 and _mittel(diffus) >= CUTOFF:
                summe = summe + gueltig * wp.abs(_mittel(diffus))
            if kanaele > 0:
                summe = summe + gueltig * wp.abs(_mittel(streu))
    w_d = _null_hoch(wp.cw_mul(farbe, schicht) * (1.0 - sss))
    if _mittel(w_d) >= CUTOFF:
        summe = summe + n * wp.abs(_mittel(w_d))

    if summe[0] == 0.0 and summe[1] == 0.0 and summe[2] == 0.0:
        aus[i] = nsd
    else:
        aus[i] = wp.normalize(summe)
