# -*- coding: utf-8 -*-
"""Genesisengine2d3dkleider — die Genesis-Engine: die EINE Stelle, an der „2D3D Kleider" Haar baut
und rendert (30.09.2026).

Sie ersetzt alle Blender-Aufrufe von „BlenderModel" (dort `Kostuemblender`/`Kostuemarbeiter` für die
Kandidaten der Iterationen und `Blendermodellblender` für den Film). Auftrag, Iterationen und Seiten sind
Kopien; nur was HINTER diesen Aufrufen passiert, ist neu.

STAND 30.09.2026: `rendern` ist gebaut und gemessen (`Genesishaarbau` rechnet die Punkte,
`Genesishaarrender` malt sie freigestellt). `film` ist es NICHT — er wirft `NichtAngebunden` mit
`FILM_MELDUNG`, weil er einen Renderer über die BEWEGUNG braucht (Häutung je Bild plus ffmpeg), nicht
nur ein Standbild. Ohne BVH überspringt `Engine2d3dKleiderlauf` den Schritt ohnehin.

Was die Schleife von der Engine erwartet (der Vertrag, abgeleitet von der Blender-Fassung; kommt die Engine,
ändert sich nur diese Datei — und `Haarparameter`, das Haar als Daten):

    rendern(koerper, aus, kandidaten, winkel, glb=False, haltung=True, fortschritt=None)
        `koerper`     die Grundfigur mit Rig (`arbeit/grundkoerper.glb`)
        `kandidaten`  [(name, werte)] — je Kandidat ein Wertesatz nach `Haarparameter`
        `winkel`      Blickwinkel in Grad (0 = von vorn, positiv zur LINKEN Seite der Figur)
        `glb`         je Kandidat auch Figur + Haar + Rig als GLB; `haltung`: in der gestellten
                      Haltung (sonst Ruhelage)
        `fortschritt` Aufruf mit einem Text (`Iterationsrunde` gibt ihn an die Statuszeile)
        → {'vorn_grad': float | None, 'sekunden': float,
           'kandidaten': {name: {'bilder': {'<winkel>': 'datei.png'}, 'teile': {…}, 'glb': 'datei.glb'}}}
        Die Bilder liegen als freigestellte PNG (Alpha = Umriss der Figur) unter `aus/<name>/`.

    film(glb, bewegung, aus, bilder, breite, hoehe, haarmodell=None, fortschritt=None)
        `glb` Figur mit Rig (`ergebnis/figur.glb`), `bewegung` die retargetete Bewegung
        (`Engine2d3dKleiderbewegung`), `haarmodell` das beste Modell der Iterationen
        (`ergebnis/haar.glb`) oder None
        → {'video': 'datei.mp4', 'bilder': int, 'bildrate': int, 'sekunden': float}
          (die Datei liegt unter `aus/`)

    schliessen()
        Prozesse und Zwischenstände der Engine beenden — auch nach einem Fehler oder „Anhalten".
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Genesisengine2d3dkleider']


class Genesisengine2d3dkleider:
    FILM_MELDUNG = (
        'Der Film der Genesis-Engine ist noch nicht gebaut — die Iterationen laufen, das '
        'Rendern einer Bewegung steht aus (`Genesisengine2d3dkleider.film`). Ohne BVH-Datei wird der '
        'Schritt „film" übersprungen.'
    )

    class NichtAngebunden(Exception):
        """Die Engine ist (noch) nicht gebaut. Bewusst KEIN `RuntimeError`: Die Schleife fängt
        `RuntimeError` an mehreren Stellen ab (ein gescheitertes Modell einer Runde, ein gescheiterter
        Arbeiter), um weiterzurechnen — das hier soll den Lauf beenden."""

    def __init__(self, lauf, parallel=1):
        self.lauf = lauf
        self.parallel = max(1, int(parallel))
        # Der Deltavorrat je Frisur lebt über den GANZEN Lauf, nicht je Aufruf: Ihn zu füllen
        # kostet einen vollen Bau je Regler (Kin: 9, rund 20 s); danach ist jeder Kandidat eine
        # Summe. Je Runde neu angelegt, zahlte jede Runde diese 20 s noch einmal.
        self._bau = None
        self._render = None

    def rendern(self, koerper, aus, kandidaten, winkel, glb=False, haltung=True, fortschritt=None):
        import time

        from Genesis9.formung import G9formung

        from .genesishaarbau import Genesishaarbau
        from .genesishaarrender import Genesishaarrender
        t0 = time.perf_counter()
        if self._bau is None:
            stellung = (self.lauf.job.ergebnis.get('regler') or {}).get('stellung') or {}
            self._bau = Genesishaarbau(G9formung(stellung))
        if self._render is None:
            self._render = Genesishaarrender(koerper)
        bau, render = self._bau, self._render
        bericht = {'vorn_grad': 0.0, 'kandidaten': {}}
        for nummer, (name, werte) in enumerate(kandidaten):
            if fortschritt:
                fortschritt('Rendern: Kandidat %d von %d' % (nummer + 1, len(kandidaten)))
            kennung, punkte = bau.punkte(werte)
            dreiecke = bau.dreiecke(kennung) if kennung else None
            eintrag = {'bilder': {}, 'teile': {kennung: 1} if kennung else {}}
            for grad in winkel:
                datei = 'ansicht_%+04d.png' % int(round(grad))
                render.bild(punkte, dreiecke, bau.farbe(werte), grad, aus / name / datei)
                eintrag['bilder'][str(int(round(grad)))] = datei
            if glb:
                eintrag['glb'] = self._glb(bau, werte, punkte, dreiecke, aus / name)
            bericht['kandidaten'][name] = eintrag
        bericht['sekunden'] = round(time.perf_counter() - t0, 2)
        return bericht

    @staticmethod
    def _glb(bau, werte, punkte, dreiecke, ordner):
        """Die Frisur als GLB (`haar.glb`) — die Bühne zeigt sie als „Modell (letzte Iteration)"."""
        import numpy as np
        import trimesh

        from .genesishaarrender import Genesishaarrender
        if punkte is None or dreiecke is None:
            return None
        netz = trimesh.Trimesh(vertices=np.asarray(punkte, dtype=np.float64),
                               faces=np.asarray(dreiecke, dtype=np.int64), process=False)
        rgb = [int(c * 255) for c in Genesishaarrender._hex(bau.farbe(werte))]
        netz.visual = trimesh.visual.ColorVisuals(
            netz, vertex_colors=np.tile(np.array([*rgb, 255], dtype=np.uint8), (len(netz.vertices), 1)))
        ordner.mkdir(parents=True, exist_ok=True)
        netz.export(ordner / 'haar.glb')
        return 'haar.glb'

    def film(self, glb, bewegung, aus, bilder, breite, hoehe, haarmodell=None, fortschritt=None):
        """Der Film (seit 30.09.2026, `Kleidertanz`): Körper, Kleider und Haar des Modells der Iterationen
        (`kreislauf.modell`, `ModellMitKleidern`) werden in Python über die Bewegung gehäutet und gerendert —
        `glb` und `haarmodell` bleiben die Dateien der Bühne, gebaut wird aus der Stellung. Ohne Modell der
        Iterationen tanzt der nackte Körper."""
        from Genesis9.modellmitkleidern import ModellMitKleidern

        from .kleidermodellbau import Kleidermodellbau
        from .kleidertanz import Kleidertanz
        job = self.lauf.job
        modell = ModellMitKleidern.aus((job.ergebnis.get('kreislauf') or {}).get('modell'))
        from .iterationsoptionen import Iterationsoptionen
        bau = Kleidermodellbau(job.stellung(), koerper=modell.koerper, ablage=self.lauf.ablage, haarumbau=Iterationsoptionen.haarumbau(job))
        teile = bau.teile(modell)
        # Das Skelett des Tanzes aus DERSELBEN Stellung wie der Bau (samt Reglern des Modells, 01.10.2026).
        tanz = Kleidertanz(bau.stellung, teile)
        return tanz.film(Kleidertanz.bewegung(bewegung), aus, bilder, breite, hoehe, fortschritt=fortschritt)

    def schliessen(self):
        """Den Renderer freigeben (er hält einen GPU-Kontext) — auch nach einem Fehler oder
        „Anhalten". Der Deltavorrat fällt mit der Engine weg."""
        if self._render is not None:
            self._render.schliessen()
            self._render = None
        self._bau = None
