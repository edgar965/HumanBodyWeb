# -*- coding: utf-8 -*-
u"""Stoffnewton — Kleidung auf der bewegten HumanBody-Figur, gerechnet mit Newton.

    python stoffnewton.py <auftrag.npz> <ergebnis.npz> <warp-cache>

Laeuft in der Newton-Umgebung (Python 3.14, warp 1.17, newton 1.5.1 —
`settings.EFFEKTE_NEWTON_PYTHON`), OHNE Django: alles, was der Loeser
braucht, steht in der `.npz` (`stoffauftrag.py` schreibt sie).

WARUM NEWTON, NICHT BLENDER (Edgar, 12.09.2026: „Ich möchte mich nicht mit
blender herumschlagen"): `SolverStyle3D` ist dieselbe Klasse Physik wie
Blender Cloth — Dehnung und Biegung je Stoffpanel, Kollision mit dem
bewegten Koerpernetz, Selbstkollision, aeussere Kraefte je Punkt — als
GPU-Loeser unter Apache-2.0. Auf der Kleiderphysik-Seite ist er gemessen
(0 Punkte im bewegten Kollider) und als Motor gewaehlt; der Mechanismus
„Punkte + Geschwindigkeiten tauschen, refit" stammt aus
`TheatreJS/kleiderPhysik/proben/probe_newton_kollider.py`.

WIND ist eine Kraft je Stoffpunkt (`State.particle_f`, der Loeser liest sie):
Staudruck der Luft auf die Flaeche des Punkts, `rho * A * (u . n) * n` mit der
Relativgeschwindigkeit `u = wind - v`. Boeen: die Windstaerke schwankt mit
zwei Sinusanteilen in der Zeit und einem laengs der Windrichtung.

FESTE PUNKTE (Bund, Schultern) sind schwere Partikel (10 kg gegen 1e-5 kg
Stoff), die wir je Teilschritt auf die LBS-Lage des Bilds stellen. So folgt
der Bund dem Koerper, der Rest haengt frei. Nicht Masse 0: siehe `aufbauen`.

KOERPERKONTAKT gibt es in Style3D NUR ueber `solver.collision` (dort werden
die weichen Kontakte der `CollisionPipeline` angewendet) — wer die
Selbstkollision abschaltet, schaltet den Koerper mit ab (gemessen: der Rock
blieb bei einer Verschiebung des Koerpers um 30 cm stehen).
"""
import json
import os
import sys
import time

import numpy as np
import warp as wp


class Stoffnewton:

    RHO_LUFT = 1.2          # kg/m^3
    EINLAUF = 40            # Teilschritte mit stehendem Koerper vor Bild 0
    KONTAKT_KE = 5.0e3
    #: Reibung am Koerper wie in Newtons Style3D-Beispiel (0,2). Mit 0,5
    #: blieb der hochgeschobene Saum am Bein haengen (dieselbe Falle wie
    #: Reibung 5 in der Blender-Pipeline).
    KONTAKT_MU = 0.2
    RADIUS = 3.5e-3
    #: Masse eines festen Punkts (kg) — schwer gegen 1e-5 kg Stoff, aber
    #: nicht Null (siehe `aufbauen`).
    FESTMASSE = 10.0
    #: Steifigkeiten, ISOTROP: Die Panels sind einzeln flach gelegte
    #: Dreiecke (`_panels`), die Kantenrichtung im Panel ist darum beliebig
    #: — Style3D mischt die drei Biegewerte nach dieser Richtung, ein
    #: anisotroper Satz wuerde je Kante zufaellig gewichtet.
    #: GEMESSEN 12.09.2026 (Female1, 001_ShyrinKurz, 75 Bilder): mit den
    #: Werten der Kleiderphysik-Probe (Dehnung 1e4, Biegung 2e-6) knitterte
    #: der Rock wie Papier — Knickwinkel benachbarter Dreiecke 19 Grad;
    #: mit Biegung 1e-4 (Newtons Gitterbeispiel) 4–7 Grad, glatter
    #: Faltenwurf. Dehnung 1e3 = ein Zehntel der Probe, das Shirt sitzt
    #: weiter am Koerper (Sitzprobe unveraendert).
    DEHNUNG = (1.0e3, 1.0e3, 1.0e2)
    BIEGUNG = (1.0e-4, 1.0e-4, 1.0e-4)

    def __init__(self, auftrag, ergebnis):
        self.ergebnis = ergebnis
        with np.load(auftrag) as d:
            self.p = json.loads(str(d['parameter']))
            self.koerper = np.asarray(d['koerper_folge'], dtype=np.float32)
            self.koerper_dreiecke = np.asarray(d['koerper_dreiecke'], dtype=np.int32)
            self.koerper_ruhe = np.asarray(d['koerper_ruhe'], dtype=np.float32)
            self.koerper_rampe = np.asarray(d['koerper_rampe'], dtype=np.float32)
            self.stoff_rampe = np.asarray(d['stoff_rampe'], dtype=np.float32)
            self.stoff_folge = np.asarray(d['stoff_folge'], dtype=np.float32)
            self.stoff_dreiecke = np.asarray(d['stoff_dreiecke'], dtype=np.int32)
            self.ruhe = np.asarray(d['stoff_ruhe'], dtype=np.float64)
            self.fest = np.asarray(d['fest'], dtype=bool)
        self.bilder, self.n = self.stoff_folge.shape[:2]
        self.fps = float(self.p['fps'])
        self.sub = int(self.p['teilschritte'])
        self.dt = 1.0 / self.fps / self.sub
        self.zeiten = []
        self._flaechen_vorbereiten()

    # --------------------------------------------------------------- Aufbau

    def aufbauen(self):
        import newton
        from newton._src.solvers import style3d as st3
        builder = newton.ModelBuilder()
        newton.solvers.SolverStyle3D.register_custom_attributes(builder)
        s, b = float(self.p['steifigkeit']), float(self.p['biegung'])
        panel, panel_index = self._panels()
        st3.add_cloth_mesh(
            builder, pos=wp.vec3(0.0), rot=wp.quat_identity(), vel=wp.vec3(0.0),
            vertices=[wp.vec3(*q) for q in self.ruhe],
            indices=self.stoff_dreiecke.reshape(-1).tolist(),
            density=float(self.p['dichte']),
            panel_verts=[wp.vec2(*q) for q in panel],
            panel_indices=panel_index.tolist(),
            tri_aniso_ke=wp.vec3(*(k * s for k in self.DEHNUNG)),
            edge_aniso_ke=wp.vec3(*(k * b for k in self.BIEGUNG)),
            particle_radius=self.RADIUS)
        # FESTE PUNKTE NICHT ALS MASSE 0 (gemessen 12.09.2026): Zwei feste
        # Punkte in Kontaktnaehe (Schulterband des Shirts, zwei Reihen in
        # 3,5 mm) geben in Style3Ds Kollision NaN — der Kontakt teilt durch
        # die Summe der inversen Massen. Darum bleiben sie aktiv mit grosser
        # Masse; ihre Lage stellt `_feste_stellen` je Teilschritt.
        for i in np.nonzero(self.fest)[0]:
            builder.particle_mass[i] = self.FESTMASSE
        netz = newton.Mesh(self.koerper_ruhe, self.koerper_dreiecke.reshape(-1))
        shape = builder.add_shape_mesh(-1, mesh=netz,
                                       xform=wp.transform(wp.vec3(0.0), wp.quat_identity()))
        self.model = builder.finalize()
        self.model.soft_contact_ke = self.KONTAKT_KE
        self.model.soft_contact_mu = self.KONTAKT_MU
        self.solver = newton.solvers.SolverStyle3D(
            model=self.model, iterations=int(self.p['iterationen']))
        self.solver.collision.radius = self.RADIUS
        self.s0, self.s1 = self.model.state(), self.model.state()
        self.control = self.model.control()
        self.pipeline = newton.CollisionPipeline(self.model)
        self.contacts = self.pipeline.contacts()
        self.wpmesh = self.model.shape_source[shape].mesh
        self.masse = self.model.particle_mass.numpy()
        print(u'Stoff: %d Punkte, %d Dreiecke, %d fest, Masse %.3f kg; Koerper %d Dreiecke'
              % (self.n, len(self.stoff_dreiecke), int(self.fest.sum()),
                 float(self.masse[~self.fest].sum()), len(self.koerper_dreiecke)), flush=True)

    def _panels(self):
        u"""Jedes Dreieck einzeln flach gelegt (drei eigene Panel-Punkte je
        Dreieck): Rest-Laengen = Laengen der RUHELAGE, Flaeche positiv.
        Die UV der Rig-Datei taugt nicht — siehe `stoffauftrag.py`."""
        t = self.stoff_dreiecke
        a, b, c = self.ruhe[t[:, 0]], self.ruhe[t[:, 1]], self.ruhe[t[:, 2]]
        e1, e2 = b - a, c - a
        l1 = np.maximum(np.linalg.norm(e1, axis=1), 1e-9)
        x2 = np.einsum('ij,ij->i', e1, e2) / l1
        y2 = np.linalg.norm(np.cross(e1, e2), axis=1) / l1
        panel = np.zeros((len(t) * 3, 2), dtype=np.float32)
        panel[1::3, 0] = l1
        panel[2::3, 0] = x2
        panel[2::3, 1] = y2
        return panel, np.arange(len(t) * 3, dtype=np.int32)

    def _flaechen_vorbereiten(self):
        u"""Flaeche je Punkt (ein Drittel jeder Nachbarflaeche) fuer den Wind."""
        t = self.stoff_dreiecke
        q = self.stoff_folge[0].astype(np.float64)
        n = np.cross(q[t[:, 1]] - q[t[:, 0]], q[t[:, 2]] - q[t[:, 0]])
        flaeche = 0.5 * np.linalg.norm(n, axis=1)
        self.flaeche_punkt = np.zeros(self.n)
        for ecke in range(3):
            np.add.at(self.flaeche_punkt, t[:, ecke], flaeche / 3.0)

    # ----------------------------------------------------------------- Wind

    def _wind(self, q, v, zeit):
        u"""Kraft je Punkt: Staudruck der Relativgeschwindigkeit auf die Normale."""
        staerke = float(self.p['wind'])
        if staerke <= 0.0:
            return None
        richtung = np.asarray(self.p['richtung'], dtype=np.float64)
        richtung /= max(np.linalg.norm(richtung), 1e-9)
        turb = float(self.p['turbulenz'])
        laengs = q @ richtung
        boe = 1.0 + turb * (0.6 * np.sin(2 * np.pi * 0.7 * zeit + 0.4)
                            + 0.4 * np.sin(2 * np.pi * 2.3 * zeit + 3.0 * laengs))
        wind = richtung[None, :] * (staerke * boe)[:, None]
        t = self.stoff_dreiecke
        n = np.cross(q[t[:, 1]] - q[t[:, 0]], q[t[:, 2]] - q[t[:, 0]])
        normalen = np.zeros_like(q)
        for ecke in range(3):
            np.add.at(normalen, t[:, ecke], n)
        normalen /= np.maximum(np.linalg.norm(normalen, axis=1), 1e-12)[:, None]
        u = wind - v
        druck = self.RHO_LUFT * self.flaeche_punkt * np.einsum('ij,ij->i', u, normalen)
        kraft = druck[:, None] * normalen
        kraft[self.fest] = 0.0
        return kraft.astype(np.float32)

    # ----------------------------------------------------------------- Lauf

    def _koerper_stellen(self, punkte, tempo):
        self.wpmesh.points.assign(wp.array(punkte, dtype=wp.vec3))
        self.wpmesh.velocities.assign(wp.array(tempo, dtype=wp.vec3))
        self.wpmesh.refit()

    def _feste_stellen(self, ziel, tempo):
        if not self.fest.any():
            return
        q = self.s0.particle_q.numpy()
        v = self.s0.particle_qd.numpy()
        q[self.fest] = ziel[self.fest]
        v[self.fest] = tempo[self.fest]
        self.s0.particle_q.assign(wp.array(q, dtype=wp.vec3))
        self.s0.particle_qd.assign(wp.array(v, dtype=wp.vec3))

    def _teilschritt(self, zeit, mit_wind=True):
        self.s0.clear_forces()
        if mit_wind:
            kraft = self._wind(self.s0.particle_q.numpy().astype(np.float64),
                               self.s0.particle_qd.numpy().astype(np.float64), zeit)
            if kraft is not None:
                self.s0.particle_f.assign(wp.array(kraft, dtype=wp.vec3))
        self.pipeline.collide(self.s0, self.contacts)
        self.solver.step(self.s0, self.s1, self.control, self.contacts, self.dt)
        self.s0, self.s1 = self.s1, self.s0

    def _bvh(self):
        if self.solver.collision is not None:
            self.solver.rebuild_bvh(self.s0)

    def _bild_fahren(self, k0, k1, f0, f1, zeit, mit_wind):
        u"""Ein Bild: Koerper und feste Punkte laufen linear von 0 nach 1,
        `sub` Teilschritte."""
        tempo_k = (k1 - k0) * self.fps
        tempo_f = (f1 - f0) * self.fps
        for s in range(self.sub):
            a = (s + 1) / self.sub
            self._koerper_stellen(k0 + a * (k1 - k0), tempo_k)
            self._feste_stellen(f0 + a * (f1 - f0), tempo_f)
            self._teilschritt(zeit + a / self.fps, mit_wind)

    def _einlauf(self):
        u"""Von der Ruhelage (A-Haltung) ueber die Zwischenposen der Rampe
        (Gelenkraum, `Stofframpe`) in die Pose von Bild 0, ohne Wind; danach
        `EINLAUF` Teilschritte mit stehendem Koerper."""
        t0 = time.perf_counter()
        k_vor, f_vor = self.koerper_ruhe, self.ruhe.astype(np.float32)
        for i in range(len(self.koerper_rampe)):
            self._bvh()
            k_nach, f_nach = self.koerper_rampe[i], self.stoff_rampe[i]
            self._bild_fahren(k_vor, k_nach, f_vor, f_nach, 0.0, False)
            k_vor, f_vor = k_nach, f_nach
        k1, f1 = self.koerper[0], self.stoff_folge[0]
        self._bvh()
        self._bild_fahren(k_vor, k1, f_vor, f1, 0.0, False)
        still = np.zeros_like(k1)
        for _ in range(self.EINLAUF):
            self._koerper_stellen(k1, still)
            self._feste_stellen(f1, np.zeros_like(f1))
            self._teilschritt(0.0, mit_wind=False)
        print(u'Einlauf: %d Zwischenposen + %d Teilschritte in %.1f s' % (
            len(self.koerper_rampe), self.EINLAUF, time.perf_counter() - t0),
            flush=True)

    def laufen(self):
        self.aufbauen()
        folge = np.zeros_like(self.stoff_folge)
        self._einlauf()
        folge[0] = self.s0.particle_q.numpy()
        for bild in range(self.bilder - 1):
            wp.synchronize()
            t0 = time.perf_counter()
            self._bvh()
            self._bild_fahren(self.koerper[bild], self.koerper[bild + 1],
                              self.stoff_folge[bild], self.stoff_folge[bild + 1],
                              bild / self.fps, True)
            wp.synchronize()
            self.zeiten.append((time.perf_counter() - t0) * 1000.0)
            folge[bild + 1] = self.s0.particle_q.numpy()
            print(u'Effekte: Stoff Bild %d von %d — %d / %d'
                  % (bild + 2, self.bilder, bild + 2, self.bilder), flush=True)
        np.savez(self.ergebnis, folge=folge.astype(np.float32),
                 ms=np.asarray(self.zeiten, dtype=np.float32))
        print(u'Stoff fertig: median %.0f ms je Bild, p90 %.0f ms'
              % (np.median(self.zeiten), np.percentile(self.zeiten, 90)), flush=True)
        return 0


def main(argv):
    auftrag, ergebnis, cache = argv[1], argv[2], argv[3]
    # Kernelcache im Projekt, nicht unter %LOCALAPPDATA% — VOR wp.init().
    wp.config.kernel_cache_dir = cache
    wp.init()
    for strom in (sys.stdout, sys.stderr):
        if hasattr(strom, 'reconfigure'):
            strom.reconfigure(encoding='utf-8', errors='replace')
    import newton
    print(u'warp %s newton %s device %s' % (wp.__version__, newton.__version__,
                                           wp.get_device()), flush=True)
    return Stoffnewton(auftrag, ergebnis).laufen()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
