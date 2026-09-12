# -*- coding: utf-8 -*-
u"""Was kostet volumetrisches Weichgewebe (FEM) je Bild?

WARUM: Der teuerste der drei moeglichen Wege ist echte Physik — ein
tetraedrisches Netz aus Fleisch, innen an den Knochen festgehalten, aussen
frei schwingend. Newton kann das (`add_soft_grid` / `add_soft_mesh`,
Neo-Hookean, Solver VBD, Apache-2.0). Bevor irgendjemand das baut, muss die
Kostenkurve dastehen.

Gemessen wird die reine Schrittzeit ueber die ZELLZAHL, nicht ueber ein
Koerpernetz: Ein Koerper-Tetnetz braucht einen Vernetzer (fTetWild/TetGen),
den diese Umgebung nicht hat. Die Kurve gilt trotzdem — die Kosten haengen
an der Zahl der Tetraeder, nicht an ihrer Form.

Zum Einordnen die Groessenordnung eines Koerpers: rund 70 Liter Volumen.
Bei 3 cm Kantenlaenge sind das etwa 2.600 Wuerfelzellen (~15.600 Tetraeder),
bei 2 cm rund 8.750 Zellen (~52.500 Tetraeder).

Der Kernelcache liegt IM PROJEKT — `wp.config.kernel_cache_dir` muss vor
`wp.init()` stehen, sonst schreibt Warp nach %LOCALAPPDATA% auf C:
(derselbe Fehler wie am 09.09.2026 im GarmentCode-Weg).
"""
import os
import time

import warp as wp

HIER = os.path.dirname(os.path.abspath(__file__))
wp.config.kernel_cache_dir = os.path.join(HIER, '..', 'warp_cache')
wp.init()

import newton                                                # noqa: E402


class Fleischprobe:
    u"""Ein Quader aus Fleisch, an einer Wand festgehalten: Schrittzeit je Bild."""

    #: (Gitter, Zellkante) — die Kurve ueber die Netzgroesse.
    GITTER = (((8, 8, 8), 0.05), ((12, 12, 12), 0.04), ((16, 16, 16), 0.03),
              ((20, 20, 20), 0.03), ((26, 26, 26), 0.02), ((34, 34, 34), 0.015))
    #: (Teilschritte, Iterationen) — die Kurve ueber die Solver-Durchgaenge.
    DURCHGAENGE = ((10, 10), (10, 5), (5, 10), (5, 5), (2, 5), (1, 5))

    @staticmethod
    def bauen(dim, zelle, verankert=True):
        u"""Ein Quader aus Fleisch; die unterste Schicht ist kinematisch.

        `mass = 0` heisst in Newton `inv_mass = 0` — der Punkt bewegt sich nur,
        wenn ihn jemand setzt. Genau so haengt spaeter das Fleisch am Knochen.
        """
        builder = newton.ModelBuilder()
        builder.add_ground_plane()
        builder.add_soft_grid(
            pos=wp.vec3(0.0, 1.0, 0.0), rot=wp.quat_identity(dtype=wp.float32),
            vel=wp.vec3(0.0, 0.0, 0.0),
            dim_x=dim[0], dim_y=dim[1], dim_z=dim[2],
            cell_x=zelle, cell_y=zelle, cell_z=zelle,
            density=1000.0,                    # Weichgewebe, rund wie Wasser
            k_mu=2.0e4, k_lambda=2.0e4, k_damp=1.0e1,
        )
        if verankert:
            # Eine Wand aus kinematischen Punkten (der "Knochen").
            for i in range(len(builder.particle_mass)):
                if builder.particle_q[i][0] < 1e-6:
                    builder.particle_mass[i] = 0.0
        return builder

    @classmethod
    def messen(cls, dim, zelle, bilder=20, teilschritte=10, iterationen=10):
        builder = cls.bauen(dim, zelle)
        # Der VBD-Solver braucht eine Faerbung (unabhaengige Punktgruppen je
        # Durchgang) — ohne sie bricht `finalize` nicht ab, sondern erst der
        # Solver, mit klarer Meldung.
        builder.color()
        model = builder.finalize()
        model.soft_contact_ke = 1.0e4
        solver = newton.solvers.SolverVBD(model=model, iterations=iterationen)
        state_0, state_1 = model.state(), model.state()
        control = model.control()
        pipeline = newton.CollisionPipeline(model, broad_phase='nxn')
        contacts = pipeline.contacts()
        dt = 1.0 / 60.0 / teilschritte

        tets = model.tet_count
        punkte = model.particle_count

        # Ein Bild ausserhalb der Messung: Kernelbau und Aufwaermen.
        for _ in range(teilschritte):
            solver.step(state_0, state_1, control, contacts, dt)
            state_0, state_1 = state_1, state_0
        wp.synchronize()

        anfang = time.perf_counter()
        for _ in range(bilder):
            pipeline.collide(state_0, contacts)
            for _ in range(teilschritte):
                solver.step(state_0, state_1, control, contacts, dt)
                state_0, state_1 = state_1, state_0
        wp.synchronize()
        dauer = (time.perf_counter() - anfang) / bilder * 1000.0
        return punkte, tets, dauer

    @classmethod
    def laufen(cls):
        print('Geraet: %s' % wp.get_device())

        # Aufwaermen: der erste Lauf zahlt den Kernelbau (gemessen 1.847 ms
        # gegen 250 ms danach — ohne diesen Vorlauf sieht das kleinste Gitter
        # aus wie das teuerste).
        cls.messen((8, 8, 8), 0.05, bilder=2)

        print('')
        print('--- ueber die Netzgroesse (10 Teilschritte x 10 Iterationen) ---')
        print('%-12s %8s %10s %11s' % ('Gitter', 'Punkte', 'Tetraeder', 'ms je Bild'))
        for dim, zelle in cls.GITTER:
            punkte, tets, ms = cls.messen(dim, zelle)
            print('%-12s %8d %10d %11.1f' % ('%dx%dx%d' % dim, punkte, tets, ms))

        print('')
        print('--- ueber die Zahl der Solver-Durchgaenge (Gitter 20x20x20) ---')
        print('%-24s %11s %14s'
              % ('Teilschritte x Iter.', 'ms je Bild', 'ms je Durchgang'))
        for teil, iters in cls.DURCHGAENGE:
            _, _, ms = cls.messen((20, 20, 20), 0.03, teilschritte=teil,
                                  iterationen=iters)
            print('%-24s %11.1f %14.2f'
                  % ('%d x %d' % (teil, iters), ms, ms / (teil * iters)))


def main():
    Fleischprobe.laufen()


if __name__ == '__main__':
    main()
