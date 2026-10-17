# -*- coding: utf-8 -*-
"""Mesh3daianimation — die Standardanimation „Spagat" auf dem Rig von Ursula1, für die Seite „Mesh3D-AI" (14.10.2026).

Edgar: „ich brauche noch die Animationsleiste + Funktion. Standardanimation ist … Spagat, bei Taste / Klick auf Play in den einzelnen Zeilen möchte ich die animiert sehen." Die Bewegung kommt aus
`A_Results/Spagat.bvh` (125 Bilder, 0,0353 s): Retarget auf Genesis 9 und Häutung des Rigs von Ursula1 (`Mesh3dairig`, derselbe Kern wie Studio und Mesh-3D), die ganze Bewegung gemeinsam ausgerichtet (Blick von Bild 0
nach +Z, Mitte der Bahn, tiefster Fußpunkt auf dem Boden), dann je Bild dieselbe Rechnung wie für eine Probe (`Mesh3daibild`) mit weichem Rauschen (`Mesh3dairausch`, Pegel der Prüfposen): eine Bewegung, die das Netz nie gesehen
hat. Das Rig und die Posen sind echt, Flächen und Ausgabe erfunden. Jedes Bild hat dieselbe Form wie eine Probe — die Seite zeigt es mit demselben Code.

    Mesh3daianimation.bilder() -> {attrappe, name, quelle, bildzeit, fps, bilder: [Probe-förmig]}
"""

from .mesh3daibild import Mesh3daibild
from .mesh3dairausch import Mesh3dairausch
from .mesh3dairig import Mesh3dairig

__all__ = ['Mesh3daianimation']


class Mesh3daianimation:
    NAME = 'Spagat'
    BVH = ('A_Results', 'Spagat.bvh')
    PUNKTSAMEN = 7
    _ablage = None

    @classmethod
    def bilder(cls):
        if cls._ablage is not None:
            return cls._ablage
        from .mesh3daiattrappe import Mesh3daiattrappe as A

        datei = A.bvh(*cls.BVH)
        anzahl, pose = Mesh3dairig.bewegung(datei)
        roh = [pose(f) for f in range(anzahl)]
        # Die ganze Bewegung gemeinsam ausrichten: Blick aus Bild 0, Mitte = Mittel der Hüfte, Boden = tiefster Fußpunkt.
        _p, p0 = Mesh3dairig.ausrichten(roh[0])
        hip = Mesh3dairig.namen().index('hip')
        gedreht = [Mesh3dairig.ausrichten(r, heading=p0['heading'], zentrum=(0.0, 0.0)) for r in roh]
        mitte = [sum(g[0]['pos'][hip][a] for g in gedreht) / anzahl for a in (0, 2)]
        boden = min(g[1]['boden'] for g in gedreht)
        rausch = Mesh3dairausch(31, weich=True)
        bildzeit = cls.bildzeit(datei)
        bilder = []
        for f, r in enumerate(roh):
            ausgerichtet, _p = Mesh3dairig.ausrichten(r, heading=p0['heading'], zentrum=(mitte[0], mitte[1]), boden=boden)
            rausch.t = f * bildzeit
            bilder.append({'id': f + 1, 'punktsamen': cls.PUNKTSAMEN, 'name': '%s Bild %d' % (cls.NAME, f + 1), 'quelle': '%s.bvh' % cls.NAME, 'aufteilung': 'pruefung',
                           **Mesh3daibild.bauen(ausgerichtet, 'pruefung', rausch)})
        cls._ablage = {'attrappe': True, 'name': cls.NAME, 'quelle': 'A_Results/%s.bvh' % cls.NAME, 'bildzeit': round(bildzeit, 5), 'fps': round(1.0 / bildzeit, 2), 'bilder': bilder}
        return cls._ablage

    @staticmethod
    def bildzeit(datei):
        """Die Bildzeit der BVH-Datei (s) aus der Kopfzeile „Frame Time:"."""
        with open(datei, encoding='utf-8', errors='replace') as f:
            for zeile in f:
                if zeile.strip().lower().startswith('frame time'):
                    return float(zeile.split(':')[1])
        return 1.0 / 30.0
