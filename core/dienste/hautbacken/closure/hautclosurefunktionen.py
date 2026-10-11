# -*- coding: utf-8 -*-
"""Hautclosurefunktionen — die kleinen Funktionen unter dem Closure-Modell des Principled BSDF, Zeile für Zeile aus dem Blender-Quelltext (v5.2.2, lokal unter
`ProjektTemp/_wegwerf/cycles_quelle/`):

    lookup_table_read / _2D / _3D        `kernel/util/lookup_table.h` (lineare Auslese der BSDF-Tabellen, `cycles_tabellen.npz`)
    F0_from_ior, ior_from_F0, fresnel_dielectric_Fss, fresnel_f82_Fss, fresnel_f82tint_B, closure_layering_weight   `kernel/closure/bsdf_util.h`
    ggx_darkening, glass_darkening       `microfacet_ggx_preserve_energy` (`kernel/closure/bsdf_microfacet.h`): der Faktor, mit dem die Energieerhaltung das Gewicht einer Closure ändert (GGX / GGX-Glas)
    schlick_s_ior                        `bsdf_microfacet_estimate_albedo` für das verallgemeinerte Schlick-Fresnel mit Exponent < 0 (die echte Dielektrikum-Kurve) und für das einfache Dielektrikum
"""

import warp as wp

from ..hautfunktionen import saturatef

__all__ = []


@wp.func
def lookup_table_read(tab: wp.array(dtype=wp.float32), x_in: float, offset: int, size: int) -> float:
    x = saturatef(x_in) * float(size - 1)
    index = wp.min(int(x), size - 1)
    nindex = wp.min(index + 1, size - 1)
    t = x - float(index)
    data0 = tab[index + offset]
    if t == 0.0:
        return data0
    data1 = tab[nindex + offset]
    return (1.0 - t) * data0 + t * data1


@wp.func
def lookup_table_read_2D(tab: wp.array(dtype=wp.float32), x: float, y_in: float, offset: int, xsize: int, ysize: int) -> float:
    y = saturatef(y_in) * float(ysize - 1)
    index = wp.min(int(y), ysize - 1)
    nindex = wp.min(index + 1, ysize - 1)
    t = y - float(index)
    data0 = lookup_table_read(tab, x, offset + xsize * index, xsize)
    if t == 0.0:
        return data0
    data1 = lookup_table_read(tab, x, offset + xsize * nindex, xsize)
    return (1.0 - t) * data0 + t * data1


@wp.func
def lookup_table_read_3D(tab: wp.array(dtype=wp.float32), x: float, y: float, z_in: float, offset: int, xsize: int, ysize: int, zsize: int) -> float:
    z = saturatef(z_in) * float(zsize - 1)
    index = wp.min(int(z), zsize - 1)
    nindex = wp.min(index + 1, zsize - 1)
    t = z - float(index)
    data0 = lookup_table_read_2D(tab, x, y, offset + xsize * ysize * index, xsize, ysize)
    if t == 0.0:
        return data0
    data1 = lookup_table_read_2D(tab, x, y, offset + xsize * ysize * nindex, xsize, ysize)
    return (1.0 - t) * data0 + t * data1


@wp.func
def F0_from_ior(ior: float) -> float:
    k = (ior - 1.0) / (ior + 1.0)
    return k * k


@wp.func
def ior_from_F0(f0: float) -> float:
    sqrt_f0 = wp.sqrt(wp.clamp(f0, 0.0, 0.99))
    return (1.0 + sqrt_f0) / (1.0 - sqrt_f0)


@wp.func
def fresnel_dielectric_Fss(eta: float) -> float:
    """Numerische Näherung (Kulla/Conty) des mittleren Einfachstreu-Fresnel."""
    if eta < 1.0:
        return 0.997118 + eta * (0.1014 - eta * (0.965241 + eta * 0.130607))
    return (eta - 1.0) / (4.08567 + 1.00071 * eta)


@wp.func
def fresnel_f82_Fss(f0: wp.vec3, b: wp.vec3) -> wp.vec3:
    return wp.cw_mul(f0, wp.vec3(1.0, 1.0, 1.0) * (1.0 - 1.0 / 21.0)) + wp.vec3(1.0, 1.0, 1.0) * (1.0 / 21.0) - b * (1.0 / 126.0)


@wp.func
def fresnel_f82tint_B(f0: wp.vec3, tint: wp.vec3) -> wp.vec3:
    f = 6.0 / 7.0
    f5 = f * f * f * f * f
    f_schlick = f0 * (1.0 - f5) + wp.vec3(f5, f5, f5)
    return wp.cw_mul(f_schlick * (7.0 / (f5 * f)), wp.vec3(1.0, 1.0, 1.0) - tint)


@wp.func
def inverse_lerp(a: float, b: float, x: float) -> float:
    return (x - a) / (b - a)


@wp.func
def reduce_max3(a: wp.vec3) -> float:
    return wp.max(a[0], wp.max(a[1], a[2]))


@wp.func
def safe_divide_color(a: wp.vec3, b: wp.vec3) -> wp.vec3:
    x = float(0.0)
    y = float(0.0)
    z = float(0.0)
    if b[0] != 0.0:
        x = a[0] / b[0]
    if b[1] != 0.0:
        y = a[1] / b[1]
    if b[2] != 0.0:
        z = a[2] / b[2]
    return wp.vec3(x, y, z)


@wp.func
def closure_layering_weight(layer_albedo: wp.vec3, weight: wp.vec3) -> wp.vec3:
    """`weight · saturate(1 − max(layer_albedo / weight))`: was die obere Schicht den unteren übrig lässt."""
    return weight * saturatef(1.0 - reduce_max3(safe_divide_color(layer_albedo, weight)))


@wp.func
def ggx_darkening(ggx_E: wp.array(dtype=wp.float32), ggx_Eavg: wp.array(dtype=wp.float32), mu: float, rough: float, fss: wp.vec3) -> wp.vec3:
    """`microfacet_ggx_preserve_energy` für GGX (nicht Glas): `bsdf->weight *= darkening`; ist `Fss` überall 1, bleibt das Gewicht (`darkening = 1`)."""
    e = lookup_table_read_2D(ggx_E, rough, mu, 0, 32, 32)
    e_avg = lookup_table_read(ggx_Eavg, rough, 0, 32)
    missing_factor = (1.0 - e) / e
    energy_scale = 1.0 + missing_factor
    if fss[0] == 1.0 and fss[1] == 1.0 and fss[2] == 1.0:
        return wp.vec3(1.0, 1.0, 1.0)
    one = wp.vec3(1.0, 1.0, 1.0)
    fms = wp.cw_div(fss * e_avg, one - fss * (1.0 - e_avg))
    return (one + fms * missing_factor) * (1.0 / energy_scale)


@wp.func
def glass_darkening(glass_E: wp.array(dtype=wp.float32), glass_Eavg: wp.array(dtype=wp.float32), glass_inv_E: wp.array(dtype=wp.float32), glass_inv_Eavg: wp.array(dtype=wp.float32),
                    mu: float, rough: float, ior_in: float, fss: wp.vec3) -> wp.vec3:
    """`microfacet_ggx_preserve_energy` für GGX-Glas (`CLOSURE_BSDF_MICROFACET_GGX_GLASS_ID`): wie `ggx_darkening`, aber mit den Glas-Tabellen (3D über `rough`, `mu`, `z`); unter 1 wird der Kehrwert
    der IOR mit den `inv`-Tabellen gelesen."""
    ior = ior_in
    umgekehrt = int(0)
    if ior < 1.0:
        ior = 1.0 / ior
        umgekehrt = int(1)
    z = wp.sqrt(wp.abs((ior - 1.0) / (ior + 1.0)))
    e = float(0.0)
    e_avg = float(0.0)
    if umgekehrt == 0:
        e = lookup_table_read_3D(glass_E, rough, mu, z, 0, 16, 16, 16)
        e_avg = lookup_table_read_2D(glass_Eavg, rough, z, 0, 16, 16)
    else:
        e = lookup_table_read_3D(glass_inv_E, rough, mu, z, 0, 16, 16, 16)
        e_avg = lookup_table_read_2D(glass_inv_Eavg, rough, z, 0, 16, 16)
    missing_factor = (1.0 - e) / e
    energy_scale = 1.0 + missing_factor
    if fss[0] == 1.0 and fss[1] == 1.0 and fss[2] == 1.0:
        return wp.vec3(1.0, 1.0, 1.0)
    one = wp.vec3(1.0, 1.0, 1.0)
    fms = wp.cw_div(fss * e_avg, one - fss * (1.0 - e_avg))
    return (one + fms * missing_factor) * (1.0 / energy_scale)


@wp.func
def schlick_s_ior(ggx_s_ior: wp.array(dtype=wp.float32), rough: float, cos_ni: float, ior: float) -> float:
    """Das `s` aus `ggx_gen_schlick_ior_s` (`bsdf_microfacet_estimate_albedo`, Zweige `DIELECTRIC` mit ior > 1 und `GENERALIZED_SCHLICK` mit Exponent < 0): die Albedo ist `mix(F0, F90, s)`."""
    z = wp.sqrt(wp.abs((ior - 1.0) / (ior + 1.0)))
    return lookup_table_read_3D(ggx_s_ior, rough, cos_ni, z, 0, 16, 16, 16)
