# -*- coding: utf-8 -*-
"""Probe (10.09.2026): Newton 1.5.1 auf dieser Maschine — Stoff (VBD) faellt auf
ein DREIECKSNETZ, das sich je Bild VERFORMT und BEWEGT (Punkte tauschen +
refit), also der Mechanismus fuer einen animierten Koerper.
Aufruf: probe_newton_kollider.py <Gitter N> <an|ohne Selbstkontakt> [starr]
        [style3d] [Masse je Partikel]

Als Klasse seit dem 12.09.2026 (Befund `klassenreif`: die Zeitenliste und
der Kollider standen als Modulzustand da). Die Rechnung ist dieselbe.
"""

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
from newton._src.solvers import style3d as st3  # noqa: E402 — nach dem Cache


class Kolliderprobe:
    """Ein Stofftuch faellt auf eine Kugel, die sich je Bild verformt und wandert."""

    R = 0.4
    FPS, SUB = 60, 10
    BILDER = 90
    KUGELMITTE = (0.0, 0.0, 0.9)

    def __init__(self, n=100, selbst=True, starr=False, style3d=False, masse=0.05):
        self.n, self.selbst, self.starr, self.style3d = n, selbst, starr, style3d
        # Masse JE PARTIKEL: 0,05 kg war ein 510-kg-Tuch; 5e-5 kg sind 0,5 kg
        # fuer 2 x 2 m
        self.masse = masse
        self.zeiten = []
        self.v0, self.f0 = self.kugel(self.R)
        self.koerper, self.shape, self.model = self._aufbauen()
        self.solver = self._loeser()
        self.s0, self.s1 = self.model.state(), self.model.state()
        self.control = self.model.control()
        self.pipeline = newton.CollisionPipeline(self.model)
        self.contacts = self.pipeline.contacts()
        self.wpmesh = self.model.shape_source[self.shape].mesh
        print('wp.Mesh am Shape:', self.wpmesh is not None,
              '| refit:', hasattr(self.wpmesh, 'refit'), flush=True)

    @staticmethod
    def kugel(r, n_lat=32, n_lon=64):
        v = []
        for i in range(n_lat + 1):
            th = np.pi * i / n_lat
            for j in range(n_lon):
                ph = 2 * np.pi * j / n_lon
                v.append([r * np.sin(th) * np.cos(ph),
                          r * np.sin(th) * np.sin(ph),
                          r * np.cos(th)])
        f = []
        for i in range(n_lat):
            for j in range(n_lon):
                a = i * n_lon + j
                b = i * n_lon + (j + 1) % n_lon
                c = (i + 1) * n_lon + j
                d = (i + 1) * n_lon + (j + 1) % n_lon
                f += [[a, c, b], [b, c, d]]
        return np.array(v, dtype=np.float32), np.array(f, dtype=np.int32)

    # --------------------------------------------------------------- Aufbau

    def _aufbauen(self):
        builder = newton.ModelBuilder()
        if self.style3d:
            newton.solvers.SolverStyle3D.register_custom_attributes(builder)
        builder.add_ground_plane()
        self._tuch(builder)
        netz = newton.Mesh(self.v0, self.f0.reshape(-1))
        lage = wp.transform(wp.vec3(*self.KUGELMITTE), wp.quat_identity())
        if self.starr:
            koerper = builder.add_body(xform=lage, is_kinematic=True)
            shape = builder.add_shape_mesh(koerper, mesh=netz)
        else:
            koerper = -1
            shape = builder.add_shape_mesh(-1, mesh=netz, xform=lage)
        if not self.style3d:
            builder.color()
        model = builder.finalize()
        model.soft_contact_ke = 1.0e3
        model.soft_contact_kd = 1.0e-1
        model.soft_contact_mu = 0.5
        print('masse je partikel', self.masse,
              'STYLE3D' if self.style3d else 'VBD',
              'STARR' if self.starr else 'VERFORMT',
              'partikel', model.particle_count,
              'dreiecke stoff', model.tri_count,
              'kollider-dreiecke', len(self.f0),
              'selbstkontakt', self.selbst, flush=True)
        return koerper, shape, model

    def _tuch(self, builder):
        n = self.n
        gemeinsam = dict(
            pos=wp.vec3(-1.0, -1.0, 1.6),
            rot=wp.quat_identity(),
            vel=wp.vec3(0.0),
            dim_x=n, dim_y=n,
            cell_x=2.0 / n, cell_y=2.0 / n,
            mass=self.masse,
            fix_left=False,
            particle_radius=0.004,
        )
        if self.style3d:
            st3.add_cloth_grid(
                builder, **gemeinsam,
                tri_aniso_ke=wp.vec3(1.0e4, 1.0e4, 1.0e3),
                edge_aniso_ke=wp.vec3(2.0e-6, 1.0e-6, 5.0e-6),
            )
        else:
            builder.add_cloth_grid(
                **gemeinsam,
                tri_ke=1.0e3, tri_ka=1.0e3, tri_kd=1.0e2,
                edge_ke=1.0e-1, edge_kd=0.0,
            )

    def _loeser(self):
        if self.style3d:
            self.model.soft_contact_ke = 5.0e3
            self.model.soft_contact_mu = 0.5
            solver = newton.solvers.SolverStyle3D(model=self.model, iterations=10)
            solver.collision.radius = 3.5e-3
            return solver
        return newton.solvers.SolverVBD(
            self.model, iterations=10,
            particle_enable_self_contact=self.selbst,
            particle_self_contact_radius=0.004,
            particle_self_contact_margin=0.008,
        )

    # ----------------------------------------------------------------- Lauf

    def _kollider_stellen(self, bild, v, v_alt):
        """Die Kugel wandert in x und streckt sich in z; starr nur wandern."""
        s = bild / self.BILDER
        dx = 0.6 * s
        if self.starr:
            bq = self.s0.body_q.numpy()
            bq[self.koerper] = [dx, 0.0, 0.9, 0.0, 0.0, 0.0, 1.0]
            self.s0.body_q.assign(wp.array(bq, dtype=wp.transform))
            bqd = self.s0.body_qd.numpy()
            bqd[self.koerper] = [0.0, 0.0, 0.0, 0.6 / self.BILDER * self.FPS, 0.0, 0.0]
            self.s0.body_qd.assign(wp.array(bqd, dtype=wp.spatial_vector))
            return dx, 1.0
        vv = (v - (v_alt if bild else v)) * self.FPS
        self.wpmesh.points.assign(wp.array(v, dtype=wp.vec3))
        self.wpmesh.velocities.assign(wp.array(vv, dtype=wp.vec3))
        self.wpmesh.refit()
        return dx, 1.0 + 0.3 * s

    def _schritt(self):
        dt = 1.0 / self.FPS / self.SUB
        wp.synchronize()
        t0 = time.perf_counter()
        if self.style3d:
            self.solver.rebuild_bvh(self.s0)
        for _ in range(self.SUB):
            self.s0.clear_forces()
            self.pipeline.collide(self.s0, self.contacts)
            self.solver.step(self.s0, self.s1, self.control, self.contacts, dt)
            self.s0, self.s1 = self.s1, self.s0
        wp.synchronize()
        self.zeiten.append((time.perf_counter() - t0) * 1000)

    def _melden(self, bild, dx, sz):
        q = self.s0.particle_q.numpy()
        rad = np.sqrt(((q[:, 0] - dx) / self.R) ** 2 + (q[:, 1] / self.R) ** 2
                      + ((q[:, 2] - 0.9) / (self.R * sz)) ** 2)
        innen = rad < 1.0
        tief = float((1.0 - rad.min()) * self.R * 1000) if innen.any() else 0.0
        tief5 = int((rad < 1.0 - 0.005 / self.R).sum())
        print(f'bild {bild:3d}  {self.zeiten[-1]:7.1f} ms  kollider dx={dx:.2f} '
              f'sz={sz:.2f}  stoff min z={q[:, 2].min():.3f}  '
              f'im kollider: {int(innen.sum())} punkte, '
              f'tiefster {tief:.1f} mm, tiefer als 5 mm: {tief5}', flush=True)

    def laufen(self):
        v_alt = self.v0
        for bild in range(self.BILDER):
            s = bild / self.BILDER
            v = (self.v0 * np.array([1.0, 1.0, 1.0 + 0.3 * s], dtype=np.float32)
                 + np.array([0.6 * s, 0.0, 0.0], dtype=np.float32))
            dx, sz = self._kollider_stellen(bild, v, v_alt)
            v_alt = v
            self._schritt()
            if bild % 15 == 0 or bild == self.BILDER - 1:
                self._melden(bild, dx, sz)
        warm = np.array(self.zeiten[5:])
        print(f'ZEIT je 60-Hz-Bild ({self.SUB} Teilschritte, '
              f'{self.model.particle_count} Partikel, '
              f'Selbstkontakt {"an" if self.selbst else "AUS"}): '
              f'median {np.median(warm):.1f} ms, '
              f'p90 {np.percentile(warm, 90):.1f} ms, '
              f'erstes Bild {self.zeiten[0]:.0f} ms', flush=True)


def main(argv):
    wp.init()
    print('warp', wp.__version__, 'newton', newton.__version__,
          'device', wp.get_device(), 'cache', wp.config.kernel_cache_dir, flush=True)
    Kolliderprobe(
        n=int(argv[1]) if len(argv) > 1 else 100,
        selbst=(argv[2] != 'ohne') if len(argv) > 2 else True,
        starr=len(argv) > 3 and argv[3] == 'starr',
        style3d=len(argv) > 4 and argv[4] == 'style3d',
        masse=float(argv[5]) if len(argv) > 5 else 0.05,
    ).laufen()


if __name__ == '__main__':
    main(sys.argv)
