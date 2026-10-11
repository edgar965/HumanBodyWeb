# -*- coding: utf-8 -*-
"""Hautglanzkernel — wo Cycles beim Backen der Normalen die Normale der Glanz-Closures verändert.

Der Principled BSDF gibt seine Normale an mehrere Closures (Diffus, Glanz, Lack, Untergrundstreuung). Die Glanz-Closures nehmen sie durch `maybe_ensure_valid_specular_reflection`
(`kernel/svm/closure.h`, `kernel/closure/bsdf_util.h`): zeigt die Spiegelung `R = 2·(N·I)·N − I` der Normale `N` unter die Fläche (`dot(Ng, R) < min(0.9·dot(I, Ng), 0.01)`), wird `N`
zur Flächennormale `Ng` hin gehoben — nur mit der Material-Einstellung „Bump Map Correction" (`SD_USE_BUMP_MAP_CORRECTION`, Vorgabe an) und wenn `N ≠ Ng` ist. Die gebackene Normale
ist das gewichtete Mittel der Closure-Normalen (`surface_shader_average_normal`); sie gleicht `N` genau dann, wenn keine Closure verändert wurde. Dieser Kernel findet die Texel, an
denen die Korrektur greift — dort stimmt `N` nicht mehr, und die Gewichte der Closures (Fresnel-Tabellen) sind noch nicht übernommen.
"""

import warp as wp

from ..hautfunktionen import safe_normalize3

__all__ = ['korrektur_noetig']


@wp.kernel
def korrektur_noetig(n: wp.array(dtype=wp.vec3), ng: wp.array(dtype=wp.vec3), n_glatt: wp.array(dtype=wp.vec3), rueck: wp.array(dtype=wp.int32), aus: wp.array(dtype=wp.int32)):
    """`aus[i] = 1`, wenn die Korrektur am Texel greift. `wi = −ray.D` ist die geglättete Normale vor der Rückseiten-Umkehr (`init_from_bake.h`: `ray.D = −N`); `n_glatt`, `ng` und `n`
    liegen schon nach der Umkehr vor."""
    i = wp.tid()
    wi = n_glatt[i]
    if rueck[i] != 0:
        wi = -wi
    # Der Principled BSDF nimmt die Normale als `safe_normalize_fallback(N, sd->N)` — eine Summe zweier Normalen (Vector Math) ist länger als 1.
    nn = safe_normalize3(n[i])
    if nn[0] == 0.0 and nn[1] == 0.0 and nn[2] == 0.0:
        nn = n_glatt[i]
    g = ng[i]
    gleich = nn[0] == g[0] and nn[1] == g[1] and nn[2] == g[2]
    if gleich:
        aus[i] = 0
        return
    r = 2.0 * wp.dot(nn, wi) * nn - wi
    iz = wp.dot(wi, g)
    schwelle = wp.min(0.9 * iz, 0.01)
    if wp.dot(g, r) >= schwelle:
        aus[i] = 0
    else:
        aus[i] = 1
