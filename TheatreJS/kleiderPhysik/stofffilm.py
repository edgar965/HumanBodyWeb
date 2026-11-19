# -*- coding: utf-8 -*-
"""Schneidet die GarmentCode-Drapierung Bild fuer Bild mit.

WARUM (Edgar, 10.09.2026: „mach mir auch ein Video mit der Kleiderphysik,
die habe ich nicht gesehen"): Die Drapierung IST eine Stoffsimulation —
rund 440 Bilder, in denen ein Schnittmuster unter Schwerkraft auf den
Koerper faellt und sich legt. Bisher wurde davon nur das letzte Bild
aufgehoben; die Bewegung dazwischen hat nie jemand gesehen.

Gerechnet wird NICHTS NEU und NICHTS ANDERS: Es laeuft genau der Weg von
`drapierlauf.py`, nur ist die Bildschleife (`Bildfolge.laufen`) durch eine
Fassung ersetzt, die jedes n-te Bild die Stofflage mitschreibt. Damit ist das
Video garantiert dieselbe Simulation, die auch das Kleidungsstueck erzeugt.

Seit 19.11.2026 mit den CUDA-Kernen (`xpbdtorch`, `Dateisimulation` wie in
`drapierlauf.py`) statt mit Warps `run_sim` (Edgar: „Stofffilm auch auf die
Kerne umstellen“). Laeuft in `A:\\3DTools\\python14`; die Ablage ist
`stofffilm.pt` ({'punkte': (Bilder, Punkte, 3) float32 in cm}), gelesen von
`stofffilm_video.py` — vorher `stofffilm.npz` aus `python10_Garment`.

Aufruf:
    python stofffilm.py --spez <..._specification.json>
                        --koerper <koerperordner> [--jedes 3]
"""

import argparse
import os
import sys
import time

import torch

ORDNER = os.path.dirname(os.path.abspath(__file__))
GC = os.path.join('A:', os.sep, '3DTools', 'Assets', 'GarmentCode')


class Stofffilm:
    """Faehrt die Drapierung und haelt jedes n-te Bild fest."""

    def __init__(self, spez, koerperordner, koerpername, jedes=3, hoechstens=600):
        self.spez = spez
        self.koerperordner = koerperordner
        self.koerpername = koerpername
        self.jedes = int(jedes)
        self.hoechstens = int(hoechstens)
        self.bilder = []
        self.stoff = None

    def _mitschnitt(self):
        """Ersetzt `Bildfolge.laufen` — dieselbe Schleife (Ruhe-Abbruch,
        Zeitgrenze), hoechstens `hoechstens` Bilder, sammelt dabei."""
        from GarmentCode.xpbdtorch.bildfolge import SimTimeOutError

        film = self

        def laufen(stoff, config):
            beginn = time.time()
            for nummer in range(0, min(config.max_sim_steps, film.hoechstens)):
                stoff.frame = nummer
                stoff.run_frame()
                if nummer % film.jedes == 0:
                    film.bilder.append(stoff.current_verts.clone())
                if nummer >= config.zero_gravity_steps and nummer >= config.min_sim_steps:
                    ruht, _ = stoff.is_static()
                    if ruht:
                        break
                if time.time() - beginn > config.max_sim_time:
                    raise SimTimeOutError
            # Das letzte Bild gehoert dazu, auch wenn es nicht auf das
            # Raster faellt: Es ist das Ergebnis, das die Figur anzieht.
            film.bilder.append(stoff.current_verts.clone())
            film.stoff = stoff

        return laufen

    def laufen(self):
        repo = os.path.join(GC, 'upstream')
        assets = os.path.dirname(GC)
        # 3DTools (KoerperKI_alle), Assets (GarmentCode.*), GarmentCode (drapierlauf), upstream (pygarment)
        for pfad in (os.path.dirname(assets), assets, GC, repo):
            if pfad not in sys.path:
                sys.path.insert(0, pfad)
        import drapierlauf

        os.chdir(repo)

        import pygarment.data_config as data_config
        from GarmentCode.schnelltriangulation import Schnelltriangulation
        from GarmentCode.xpbdtorch.bildfolge import Bildfolge
        from GarmentCode.xpbdtorch.dateisimulation import Dateisimulation
        from pygarment.meshgen.boxmeshgen import BoxMesh
        from pygarment.meshgen.sim_config import PathCofig

        Schnelltriangulation.einsetzen()    # wie `drapierlauf.py`: dasselbe Netz mit weniger Python-Aufwand
        Bildfolge.laufen = staticmethod(self._mitschnitt())

        name = os.path.basename(self.spez)[: -len('_specification.json')]
        # Die Systemdatei sagt `PathCofig`, WO der Koerper liegt — sie wird
        # von der Platte gelesen, nicht aus dem Speicher. Dieselbe Funktion
        # wie im Produktivweg, damit kein zweiter Pfadbau entsteht.
        drapierlauf._systemdatei_schreiben(
            repo, self.koerpername, os.path.join(ORDNER, 'film'), self.koerperordner
        )
        eigenschaften = data_config.Properties(
            os.path.join(repo, 'assets', 'Sim_props', 'gui_sim_props.yaml')
        )
        # DICTS, nicht Listen — die Simulation schreibt `stats[...][name]`.
        # Mit Listen bricht es NACH der Simulation ab, und der ganze
        # Mitschnitt waere weg gewesen.
        eigenschaften.set_section_stats(
            'sim', fails={}, sim_time={}, spf={}, fin_frame={}, body_collisions={}, self_collisions={}
        )
        eigenschaften.set_section_stats('render', render_time={})

        system = data_config.Properties(os.path.join(repo, 'system.json'))
        wege = PathCofig(
            in_element_path=os.path.dirname(self.spez),
            out_path=system['output'],
            in_name=name,
            body_name=self.koerpername,
            smpl_body=False,
            add_timestamp=False,
        )
        netz = BoxMesh(wege.in_g_spec, eigenschaften['sim']['config']['resolution_scale'])
        netz.load()
        netz.serialize(wege, store_panels=False, uv_config=eigenschaften['render']['config']['uv_texture'])
        Dateisimulation.laufen(netz.name, eigenschaften, wege)
        return self.bilder


def main():
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument(
        '--spez', default=os.path.join(GC, 'ausgabe', 't-shirt_female', 't-shirt_female_specification.json')
    )
    zerleger.add_argument('--koerper', default=os.path.join(GC, 'koerper', 'female'))
    zerleger.add_argument('--koerpername', default=None)
    zerleger.add_argument('--jedes', type=int, default=3)
    zerleger.add_argument('--aus', default=os.path.join(ORDNER, 'stofffilm.pt'))
    werte = zerleger.parse_args()

    name = werte.koerpername
    if not name:
        obj = sorted(f for f in os.listdir(werte.koerper) if f.endswith('.obj'))
        if not obj:
            raise SystemExit('Kein Koerpernetz in %s' % werte.koerper)
        name = obj[0][:-4]
    print('Koerper    %s aus %s' % (name, werte.koerper))
    film = Stofffilm(werte.spez, werte.koerper, name, werte.jedes)
    bilder = film.laufen()
    if not bilder:
        raise SystemExit('Kein einziges Bild mitgeschnitten.')
    feld = torch.stack(bilder)
    print('Mitschnitt %d Bilder, %d Stoffpunkte' % (feld.shape[0], feld.shape[1]))
    weg = torch.linalg.vector_norm(feld[-1] - feld[0], dim=1)
    print(
        'Fallweg    Median %.1f mm, groesster %.1f mm'
        % (float(weg.quantile(0.5)) * 10.0, float(weg.max()) * 10.0)
    )
    torch.save({'punkte': feld.cpu()}, werte.aus)  # cpu gewollt: Ablage fuer `stofffilm_video.py`
    print('Ablage     %s (%.1f MB)' % (werte.aus, os.path.getsize(werte.aus) / 1048576.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
