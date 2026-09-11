# -*- coding: utf-8 -*-
u"""Schneidet die GarmentCode-Drapierung Bild fuer Bild mit.

WARUM (Edgar, 10.09.2026: „mach mir auch ein Video mit der Kleiderphysik,
die habe ich nicht gesehen"): Die Drapierung IST eine Stoffsimulation —
rund 440 Bilder, in denen ein Schnittmuster unter Schwerkraft auf den
Koerper faellt und sich legt. Bisher wurde davon nur das letzte Bild
aufgehoben; die Bewegung dazwischen hat nie jemand gesehen.

Gerechnet wird NICHTS NEU und NICHTS ANDERS: Es laeuft genau der Weg von
`drapierlauf.py`, nur ist `sim_frame_sequence` durch eine Fassung ersetzt,
die je Bild `garment.current_verts` mitschreibt. Damit ist das Video
garantiert dieselbe Simulation, die auch das Kleidungsstueck erzeugt.

Laeuft in `A:\\3DTools\\python10_Garment` (Warp-Fork, numpy 1.26).

Aufruf:
    python stofffilm.py --spez <..._specification.json>
                        --koerper <koerperordner> [--jedes 3]
"""
import argparse
import os
import sys

import numpy as np

ORDNER = os.path.dirname(os.path.abspath(__file__))
GC = os.path.join('A:', os.sep, '3DTools', 'Assets', 'GarmentCode')


class Stofffilm:
    u"""Faehrt die Drapierung und haelt jedes n-te Bild fest."""

    def __init__(self, spez, koerperordner, koerpername, jedes=3,
                 hoechstens=600):
        self.spez = spez
        self.koerperordner = koerperordner
        self.koerpername = koerpername
        self.jedes = int(jedes)
        self.hoechstens = int(hoechstens)
        self.bilder = []

    def _mitschnitt(self, urspruenglich):
        u"""Ersetzt `sim_frame_sequence` — rechnet dasselbe, sammelt dabei."""
        film = self

        def sequenz(garment, config, store_usd=False, verbose=False):
            for nummer in range(0, min(config.max_sim_steps, film.hoechstens)):
                garment.frame = nummer
                garment.run_frame()
                if nummer % film.jedes == 0:
                    film.bilder.append(np.array(garment.current_verts,
                                                dtype=np.float32))
                if (nummer >= config.zero_gravity_steps
                        and nummer >= config.min_sim_steps):
                    ruht, _ = garment.is_static()
                    if ruht:
                        break
            # Das letzte Bild gehoert dazu, auch wenn es nicht auf das
            # Raster faellt: Es ist das Ergebnis, das die Figur anzieht.
            film.bilder.append(np.array(garment.current_verts,
                                        dtype=np.float32))
            film.dreiecke = garment.f_cloth_sim if hasattr(
                garment, 'f_cloth_sim') else None
            film.garment = garment
        return sequenz

    def laufen(self):
        sys.path.insert(0, GC)
        import drapierlauf
        drapierlauf._cache_umlenken()
        repo = os.path.join(GC, 'upstream')
        os.chdir(repo)
        sys.path.insert(0, repo)

        import pygarment.data_config as data_config
        from pygarment.meshgen.boxmeshgen import BoxMesh
        from pygarment.meshgen.sim_config import PathCofig
        from pygarment.meshgen import simulation

        simulation.sim_frame_sequence = self._mitschnitt(
            simulation.sim_frame_sequence)
        from pygarment.meshgen.simulation import run_sim

        name = os.path.basename(self.spez)[:-len('_specification.json')]
        # Die Systemdatei sagt `PathCofig`, WO der Koerper liegt — sie wird
        # von der Platte gelesen, nicht aus dem Speicher. Dieselbe Funktion
        # wie im Produktivweg, damit kein zweiter Pfadbau entsteht.
        drapierlauf._systemdatei_schreiben(
            repo, self.koerpername, os.path.join(ORDNER, 'film'),
            self.koerperordner)
        eigenschaften = data_config.Properties(
            os.path.join(repo, 'assets', 'Sim_props', 'gui_sim_props.yaml'))
        # DICTS, nicht Listen — `run_sim` schreibt `stats[...][name]`.
        # Mit Listen bricht es NACH der Simulation ab, und der ganze
        # Mitschnitt waere weg gewesen.
        eigenschaften.set_section_stats(
            'sim', fails={}, sim_time={}, spf={}, fin_frame={},
            body_collisions={}, self_collisions={})
        eigenschaften.set_section_stats('render', render_time={})

        system = data_config.Properties(os.path.join(repo, 'system.json'))
        wege = PathCofig(
            in_element_path=os.path.dirname(self.spez),
            out_path=system['output'],
            in_name=name, body_name=self.koerpername,
            smpl_body=False, add_timestamp=False)
        netz = BoxMesh(wege.in_g_spec,
                       eigenschaften['sim']['config']['resolution_scale'])
        netz.load()
        netz.serialize(wege, store_panels=False,
                       uv_config=eigenschaften['render']['config']['uv_texture'])
        run_sim(netz.name, eigenschaften, wege,
                save_v_norms=False, store_usd=False,
                optimize_storage=False, verbose=False)
        return self.bilder


def main():
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument('--spez', default=os.path.join(
        GC, 'ausgabe', 't-shirt_female', 't-shirt_female_specification.json'))
    zerleger.add_argument('--koerper', default=os.path.join(
        GC, 'koerper', 'female'))
    zerleger.add_argument('--koerpername', default=None)
    zerleger.add_argument('--jedes', type=int, default=3)
    zerleger.add_argument('--aus', default=os.path.join(ORDNER, 'stofffilm.npz'))
    werte = zerleger.parse_args()

    name = werte.koerpername
    if not name:
        obj = sorted(f for f in os.listdir(werte.koerper) if f.endswith('.obj'))
        if not obj:
            raise SystemExit(u'Kein Koerpernetz in %s' % werte.koerper)
        name = obj[0][:-4]
    print(u'Koerper    %s aus %s' % (name, werte.koerper))
    film = Stofffilm(werte.spez, werte.koerper, name, werte.jedes)
    bilder = film.laufen()
    if not bilder:
        raise SystemExit(u'Kein einziges Bild mitgeschnitten.')
    feld = np.array(bilder)
    print(u'Mitschnitt %d Bilder, %d Stoffpunkte' % (len(feld), feld.shape[1]))
    weg = np.linalg.norm(feld[-1] - feld[0], axis=1)
    print(u'Fallweg    Median %.1f mm, groesster %.1f mm'
          % (float(np.median(weg)) * 10.0, float(weg.max()) * 10.0))
    np.savez_compressed(werte.aus, punkte=feld)
    print(u'Ablage     %s (%.1f MB)'
          % (werte.aus, os.path.getsize(werte.aus) / 1048576.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
