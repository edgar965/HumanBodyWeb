# -*- coding: utf-8 -*-
"""Probe (10.09.2026): Newton 1.5.1 auf dieser Maschine — Stoff (VBD) faellt auf
ein DREIECKSNETZ, das sich je Bild VERFORMT und BEWEGT (Punkte tauschen +
refit), also der Mechanismus fuer einen animierten Koerper.
Aufruf: probe_newton_kollider.py <Gitter N> <an|ohne Selbstkontakt>"""

import os
import sys
import time

import numpy as np
import warp as wp

# Kernelcache im Projekt, nicht unter %LOCALAPPDATA% (Regel: keine Ablage auf C:)
wp.config.kernel_cache_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'warp_cache'
)
import newton  # noqa: E402 — der Kernelcache muss VOR dem Import stehen

wp.init()
print(
    'warp',
    wp.__version__,
    'newton',
    newton.__version__,
    'device',
    wp.get_device(),
    'cache',
    wp.config.kernel_cache_dir,
    flush=True,
)


def kugel(r, n_lat=32, n_lon=64):
    v = []
    for i in range(n_lat + 1):
        th = np.pi * i / n_lat
        for j in range(n_lon):
            ph = 2 * np.pi * j / n_lon
            v.append(
                [
                    r * np.sin(th) * np.cos(ph),
                    r * np.sin(th) * np.sin(ph),
                    r * np.cos(th),
                ]
            )
    f = []
    for i in range(n_lat):
        for j in range(n_lon):
            a = i * n_lon + j
            b = i * n_lon + (j + 1) % n_lon
            c = (i + 1) * n_lon + j
            d = (i + 1) * n_lon + (j + 1) % n_lon
            f += [[a, c, b], [b, c, d]]
    return np.array(v, dtype=np.float32), np.array(f, dtype=np.int32)


R = 0.4
N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
SELBST = (sys.argv[2] != 'ohne') if len(sys.argv) > 2 else True
STARR = len(sys.argv) > 3 and sys.argv[3] == 'starr'
STYLE3D = len(sys.argv) > 4 and sys.argv[4] == 'style3d'
# Masse JE PARTIKEL: 0,05 kg war ein 510-kg-Tuch; 5e-5 kg sind 0,5 kg fuer 2 x 2 m
MASSE = float(sys.argv[5]) if len(sys.argv) > 5 else 0.05
from newton._src.solvers import style3d as st3  # noqa: E402 — nach dem Cache

v0, f0 = kugel(R)
builder = newton.ModelBuilder()
if STYLE3D:
    newton.solvers.SolverStyle3D.register_custom_attributes(builder)
builder.add_ground_plane()
gemeinsam = dict(
    pos=wp.vec3(-1.0, -1.0, 1.6),
    rot=wp.quat_identity(),
    vel=wp.vec3(0.0),
    dim_x=N,
    dim_y=N,
    cell_x=2.0 / N,
    cell_y=2.0 / N,
    mass=MASSE,
    fix_left=False,
    particle_radius=0.004,
)
if STYLE3D:
    st3.add_cloth_grid(
        builder,
        **gemeinsam,
        tri_aniso_ke=wp.vec3(1.0e4, 1.0e4, 1.0e3),
        edge_aniso_ke=wp.vec3(2.0e-6, 1.0e-6, 5.0e-6),
    )
else:
    builder.add_cloth_grid(
        **gemeinsam,
        tri_ke=1.0e3,
        tri_ka=1.0e3,
        tri_kd=1.0e2,
        edge_ke=1.0e-1,
        edge_kd=0.0,
    )
netz = newton.Mesh(v0, f0.reshape(-1))
if STARR:
    koerper = builder.add_body(
        xform=wp.transform(wp.vec3(0.0, 0.0, 0.9), wp.quat_identity()),
        is_kinematic=True,
    )
    shape = builder.add_shape_mesh(koerper, mesh=netz)
else:
    koerper = -1
    shape = builder.add_shape_mesh(
        -1, mesh=netz, xform=wp.transform(wp.vec3(0.0, 0.0, 0.9), wp.quat_identity())
    )
if not STYLE3D:
    builder.color()
model = builder.finalize()
model.soft_contact_ke = 1.0e3
model.soft_contact_kd = 1.0e-1
model.soft_contact_mu = 0.5
print(
    'masse je partikel',
    MASSE,
    'STYLE3D' if STYLE3D else 'VBD',
    'STARR' if STARR else 'VERFORMT',
    'partikel',
    model.particle_count,
    'dreiecke stoff',
    model.tri_count,
    'kollider-dreiecke',
    len(f0),
    'selbstkontakt',
    SELBST,
    flush=True,
)

if STYLE3D:
    model.soft_contact_ke = 5.0e3
    model.soft_contact_mu = 0.5
    solver = newton.solvers.SolverStyle3D(model=model, iterations=10)
    solver.collision.radius = 3.5e-3
else:
    solver = newton.solvers.SolverVBD(
        model,
        iterations=10,
        particle_enable_self_contact=SELBST,
        particle_self_contact_radius=0.004,
        particle_self_contact_margin=0.008,
    )
s0, s1 = model.state(), model.state()
control = model.control()
pipeline = newton.CollisionPipeline(model)
contacts = pipeline.contacts()
wpmesh = model.shape_source[shape].mesh
print(
    'wp.Mesh am Shape:',
    wpmesh is not None,
    '| refit:',
    hasattr(wpmesh, 'refit'),
    flush=True,
)

FPS, SUB = 60, 10
dt = 1.0 / FPS / SUB
BILDER = 90
zeiten = []
v_alt = v0
for bild in range(BILDER):
    s = bild / BILDER
    v = v0 * np.array([1.0, 1.0, 1.0 + 0.3 * s], dtype=np.float32) + np.array(
        [0.6 * s, 0.0, 0.0], dtype=np.float32
    )
    dx, sz = 0.6 * s, 1.0 + 0.3 * s
    if STARR:
        sz = 1.0
        bq = s0.body_q.numpy()
        bq[koerper] = [dx, 0.0, 0.9, 0.0, 0.0, 0.0, 1.0]
        s0.body_q.assign(wp.array(bq, dtype=wp.transform))
        bqd = s0.body_qd.numpy()
        bqd[koerper] = [0.0, 0.0, 0.0, 0.6 / BILDER * FPS, 0.0, 0.0]
        s0.body_qd.assign(wp.array(bqd, dtype=wp.spatial_vector))
    else:
        vv = (v - (v_alt if bild else v)) * FPS
        wpmesh.points.assign(wp.array(v, dtype=wp.vec3))
        wpmesh.velocities.assign(wp.array(vv, dtype=wp.vec3))
        wpmesh.refit()
    v_alt = v
    wp.synchronize()
    t0 = time.perf_counter()
    if STYLE3D:
        solver.rebuild_bvh(s0)
    for _ in range(SUB):
        s0.clear_forces()
        pipeline.collide(s0, contacts)
        solver.step(s0, s1, control, contacts, dt)
        s0, s1 = s1, s0
    wp.synchronize()
    zeiten.append((time.perf_counter() - t0) * 1000)
    if bild % 15 == 0 or bild == BILDER - 1:
        q = s0.particle_q.numpy()
        rad = np.sqrt(
            ((q[:, 0] - dx) / R) ** 2
            + (q[:, 1] / R) ** 2
            + ((q[:, 2] - 0.9) / (R * sz)) ** 2
        )
        innen = rad < 1.0
        tief = float((1.0 - rad.min()) * R * 1000) if innen.any() else 0.0
        tief5 = int((rad < 1.0 - 0.005 / R).sum())
        print(
            f'bild {bild:3d}  {zeiten[-1]:7.1f} ms  kollider dx={dx:.2f} sz={sz:.2f}  '
            f'stoff min z={q[:, 2].min():.3f}  im kollider: {int(innen.sum())} punkte, '
            f'tiefster {tief:.1f} mm, tiefer als 5 mm: {tief5}',
            flush=True,
        )
warm = np.array(zeiten[5:])
print(
    f'ZEIT je 60-Hz-Bild ({SUB} Teilschritte, {model.particle_count} Partikel, '
    f'Selbstkontakt {"an" if SELBST else "AUS"}): median {np.median(warm):.1f} ms, '
    f'p90 {np.percentile(warm, 90):.1f} ms, '
    f'erstes Bild {zeiten[0]:.0f} ms',
    flush=True,
)
