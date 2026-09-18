# -*- coding: utf-8 -*-
"""Personenergebnisse — die BVHs der weiteren Personen eines Laufs.

WARUM (Edgar, 14.09.2026: „bei mehreren Personen brauche ich mehrere BVHs,
die aber synchron sein sollen, damit ich auch 2 Modelle haben kann")

`lift_3d.py --persons n` (GVHMR, GEM-SMPL) schreibt neben dem bestellten BVH
`<stamm>_p2.bvh`, `<stamm>_p3.bvh`, … — ein BVH je Personenspur, gleiche
Bildzahl, gleiche Kamera. Der Wrapper gibt weiter nur das erste zurueck
(`Smpllauf` erwartet einen Pfad); die weiteren findet diese Klasse ueber den
Namen, traegt sie am Auftrag ein (`bvh_file_personen`), legt sie wie das erste
in die Ergebnisablage (`<video>_<pipeline>_p2.bvh` in `A_Results`, wo das
Studio sie als Clip findet) und in die Bibliothek.
"""

import glob
import os
import re


class Personenergebnisse:
    """`<stamm>_p<n>.bvh` neben dem BVH der ersten Person."""

    MUSTER = re.compile(r"_p(\d+)\.bvh$", re.IGNORECASE)

    @classmethod
    def finden(cls, bvh):
        """Die weiteren BVHs, nach Personennummer sortiert; leer ohne."""
        if not bvh:
            return []
        stamm, _endung = os.path.splitext(str(bvh))
        gefunden = []
        for pfad in glob.glob(glob.escape(stamm) + "_p*.bvh"):
            treffer = cls.MUSTER.search(os.path.basename(pfad))
            if treffer and os.path.getsize(pfad) > 0:
                gefunden.append((int(treffer.group(1)), pfad))
        return [pfad for _n, pfad in sorted(gefunden)]

    @classmethod
    def nummer(cls, pfad):
        """Die Personennummer aus dem Dateinamen — 0, wenn keine."""
        treffer = cls.MUSTER.search(os.path.basename(str(pfad)))
        return int(treffer.group(1)) if treffer else 0

    @classmethod
    def eintragen(cls, job, bvh, quelle, bibliothek):
        """Am Auftrag merken, in die Ablage kopieren, in die Bibliothek
        eintragen. `bibliothek(pfad, quelle, namenszusatz)` ist
        `Auftragslauf._bibliothekseintrag`. Gibt die Auftragspfade zurueck."""
        from ..dienste.ergebnisablage import Ergebnisablage

        weitere = cls.finden(bvh)
        job.bvh_file_personen = weitere
        for pfad in weitere:
            zusatz = "_p%d" % cls.nummer(pfad)
            kopie = Ergebnisablage.kopieren(pfad, job.name, quelle + zusatz)
            bibliothek(kopie, quelle, zusatz)
        return weitere
