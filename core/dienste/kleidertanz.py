# -*- coding: utf-8 -*-
"""Kleidertanz — der Film von „2D3D Kleider": Körper, Kleider und Haar über eine Bewegung häuten und rendern
(30.09.2026).

Edgar: „der test des Jobs muss auch beinhalten dass das modell tanzen kann (mit der Animation), und die kleider
richtig animiert werden. mach aber den TANZEN test kurz, nur max. 10 Frames." Der Film ist damit der Beleg, dass
das Modell der Iterationen am Rig hängt: `G9tanzhaut` häutet jedes Teil mit SEINER Haut über die Weltmatrizen der
Bewegung (`Bewegungsspuren`, wie `Clipanimation` im Browser), `Genesishaarrender` malt jedes Bild, cv2 schreibt
das Video (`mp4v`).

Gemessen wird dabei, was „richtig animiert" heißt: je Kleiderteil der mittlere Abstand seiner Punkte zur
Körperoberfläche im ersten und im letzten Bild (`abstand_mm`: bleibt er, folgt der Stoff dem Körper) und der Weg
der Punkte zwischen beiden Bildern (`weg_mm`: bewegt er sich überhaupt). Ohne Stoffschwung — wie die Bühne ohne
dForce.
"""

import json
import logging
import time

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Kleidertanz']


class Kleidertanz:
    def __init__(self, stellung, teile):
        """`teile` wie `Kleidermodellbau.teile` (Körper zuerst, jedes mit `haut`)."""
        from Genesis9.formung import G9formung
        from Genesis9.tanzhaut import G9tanzhaut
        self.teile = teile
        self.haut = G9tanzhaut(G9formung(stellung).skelett().kette().bauplan())

    @staticmethod
    def bewegung(pfad):
        from humanbody_core.skeleton.bewegungsspuren import Bewegungsspuren
        with open(pfad, encoding='utf-8') as datei:
            return Bewegungsspuren.aus_dict(json.load(datei))

    def bild(self, spuren, nummer):
        """Die Punkte aller Teile im Bild `nummer` — ein Teil ohne Haut bleibt in Ruhe."""
        welt = self.haut.matrizen(spuren, nummer)
        return [self.haut.haeuten(t['punkte'], t['haut'], welt) if t.get('haut') else np.asarray(t['punkte'])
                for t in self.teile]

    def film(self, spuren, aus, bilder, breite, hoehe, fortschritt=None):
        """→ {video, bilder, bildrate, sekunden, teile: {sorte: {abstand_mm: [erstes, letztes], weg_mm}}}."""
        import cv2
        from scipy.spatial import cKDTree

        from .genesishaarrender import Genesishaarrender
        t0 = time.perf_counter()
        anzahl = max(1, min(int(bilder), int(spuren.frame_count or 1)))
        # Bilder gleichmäßig über die Bewegung verteilt — zehn Bilder sollen den Tanz zeigen, nicht seine erste Sekunde.
        if spuren.frame_count > anzahl:
            nummern = [int(round(i * (spuren.frame_count - 1) / max(1, anzahl - 1))) for i in range(anzahl)]
            dauer = float(spuren.duration or anzahl)          # die Bilder decken die ganze Bewegung ab
        else:
            nummern = list(range(anzahl))
            dauer = float(spuren.duration or anzahl) * anzahl / max(1, spuren.frame_count)
        bildrate = max(1, min(30, int(round(anzahl / max(0.5, dauer)))))
        aus.mkdir(parents=True, exist_ok=True)
        render = Genesishaarrender(None)
        video = aus / 'film.mp4'
        schreiber = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*'mp4v'), bildrate, (int(breite), int(hoehe)))
        stand = {}
        # Dieselben Bilder wie in der Runde (Fotoprojektion, Normalkarten) — bis 01.10.2026 tanzten die Teile flach in
        # ihrer Mittelfarbe, ein fotoprojiziertes Shirt kam im Film hellrosa statt grau. Ein Paket je Teil für alle
        # Bilder: gleiche Felder = gleiche Szene, Mitsuba tauscht dann nur die Punkte.
        pakete = [Genesishaarrender.extra(t, kurven=False) for t in self.teile]
        try:
            for i, nummer in enumerate(nummern):
                if fortschritt:
                    fortschritt('Film: Bild %d von %d' % (i + 1, anzahl))
                punkte = self.bild(spuren, nummer)
                pfad = aus / ('bild_%04d.png' % i)
                render.bild_teile([(p, t['dreiecke'], t['farbe'], e)
                                   for p, t, e in zip(punkte, self.teile, pakete, strict=True)],
                                  0.0, pfad, groesse=(int(breite), int(hoehe)))
                bgr = cv2.imread(str(pfad), cv2.IMREAD_UNCHANGED)
                if bgr.shape[2] == 4:                       # Alpha auf Weiß
                    alpha = bgr[:, :, 3:4].astype(np.float32) / 255.0
                    bgr = (bgr[:, :, :3].astype(np.float32) * alpha + 255.0 * (1.0 - alpha)).astype(np.uint8)
                schreiber.write(bgr)
                if i in (0, len(nummern) // 2):     # Anfang und Mitte: Anfang und Ende einer Schleife sind gleich
                    stand[i] = punkte
        finally:
            schreiber.release()
            render.schliessen()
        return {'video': video.name, 'bilder': anzahl, 'bildrate': bildrate, 'bildnummern': nummern,
                'sekunden': round(time.perf_counter() - t0, 1), 'teile': self._messen(stand, cKDTree)}

    def _messen(self, stand, cKDTree):
        """Je Kleiderteil: Abstand zur Körperoberfläche im ersten/letzten Bild und der Weg dazwischen (mm)."""
        if not stand:
            return {}
        erstes, letztes = stand[min(stand)], stand[max(stand)]      # `letztes` = die Mitte der Bewegung
        aus = {}
        for i, t in enumerate(self.teile):
            if t['art'] == 'koerper':
                weg = float(np.linalg.norm(letztes[i] - erstes[i], axis=1).mean()) * 1e3
                aus['koerper'] = {'weg_mm': round(weg, 1)}
                continue
            abstand = []
            for punkte in (erstes, letztes):
                d, _ = cKDTree(punkte[0]).query(punkte[i])
                abstand.append(round(float(d.mean()) * 1e3, 1))
            aus[t['sorte']] = {'abstand_mm': abstand,
                               'weg_mm': round(float(np.linalg.norm(letztes[i] - erstes[i], axis=1).mean()) * 1e3, 1)}
        return aus
