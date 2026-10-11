# -*- coding: utf-8 -*-
"""Hautalphakernel — der Normal-Pass, der bei kleinem Alpha wegfällt (`film_write_data_passes`, `kernel/film/data_passes.h`, Blender v5.2.2).

    if (!(sd->flag & (SD_TRANSPARENT | SD_RAY_PORTAL)) || kernel_data.film.pass_alpha_threshold == 0.0f ||
        average(surface_shader_alpha(sd)) >= kernel_data.film.pass_alpha_threshold)
      { … film_write_pass_float3(buffer + pass_normal, surface_shader_average_normal(sd)); … }

Beim Backen setzt Blender die Schwelle nie (`BlenderSession::bake` ruft `sync_render_passes` nicht auf): es gilt die Vorgabe des Films, `Film::pass_alpha_threshold` = 0,5 (`scene/film.cpp`),
nicht die der View Layer. Texel mit Alpha unter 0,5 bekommen keine Normale — der Puffer bleibt 0, und `RE_bake_normal_world_to_tangent` macht daraus `0 · ½ + ½` = (128, 128, 128).
"""

import warp as wp

__all__ = ['nullen']


@wp.kernel
def nullen(alpha: wp.array(dtype=wp.float32), schwelle: float, welt: wp.array(dtype=wp.vec3), aus: wp.array(dtype=wp.vec3)):
    """`aus[i]` = die Normale, oder der Nullvektor, wenn `saturate(alpha) < schwelle` (`surface_shader_alpha` ist `saturate(1 − Auslöschung)`)."""
    i = wp.tid()
    a = wp.clamp(alpha[i], 0.0, 1.0)
    if a < schwelle:
        aus[i] = wp.vec3(0.0, 0.0, 0.0)
    else:
        aus[i] = welt[i]
