# -*- coding: utf-8 -*-
"""Bewegungsschnitt — eine Bewegung (`tracks` Quaternionen je Knochen, `position_track`, `times`) auf `n` Bilder zu 30 je Sekunde für den Render (01.11.2026, Edgar zu
`Königin1_render.mp4`: „warum läuft das video so langsm? Framerate nicht richtig eingestellt?“).

Bis dahin hatten `exportleiste_render` und `engine2d3dkleider_render` je eine Kopie desselben Schnitts: die ersten `n` Bilder der Bewegung, die Zeiten auf 30 je Sekunde
überschrieben. Der Retarget liefert aber die Bildrate der BVH — DanceKurz 1004 Bilder zu 60 je Sekunde (16,73 s, `DanceKurz_retarget_da84afb2.json`): Das Video zeigte die ersten
8,4 s des Tanzes in halber Geschwindigkeit. Jetzt nimmt jedes Ausgabebild (t = i / 30) das Bild der Bewegung zum nächsten Zeitpunkt (`times`; ohne passende Zeiten gelten
30 je Sekunde wie bisher). Zwischenbilder werden nicht gemischt — bei 60 → 30 ist es jedes zweite.

    n = Bewegungsschnitt.bilder(bewegung, sekunden)      # Bilder zu 30 je Sekunde bis `sekunden`, höchstens bis zum Ende der Bewegung, mindestens 2
    Bewegungsschnitt.schreiben(bewegung, ziel, n)         # JSON mit `frame_count` n, `times` i / 30
"""
import json

import torch
from KoerperKI_alle.torchfeld import Torchfeld

__all__ = ['Bewegungsschnitt']


class Bewegungsschnitt:
    FPS = 30

    @classmethod
    def zeiten(cls, d):
        """Zeitpunkt jedes Bildes der Bewegung in Sekunden (`times`; ohne passende Zeiten i / 30)."""
        anzahl = int(d.get('frame_count') or len(d.get('times') or []))
        t = Torchfeld.feld(d.get('times') or [], dtype=torch.float64)
        return t if anzahl and len(t) == anzahl else Torchfeld.arange(anzahl) / cls.FPS

    @classmethod
    def bilder(cls, d, sekunden):
        t = cls.zeiten(d)
        ende = int(Torchfeld.floor(t[-1] * cls.FPS + 1e-6)) + 1 if len(t) else 0
        return max(2, int(round(min(float(sekunden) * cls.FPS, ende))))     # erst klemmen: `sekunden` darf unendlich sein (bis zum Ende)

    @classmethod
    def auswahl(cls, d, n):
        """(n,) Nummer des Bildes der Bewegung, das dem Zeitpunkt i / 30 am nächsten liegt."""
        t = cls.zeiten(d)
        soll = Torchfeld.arange(n) / cls.FPS
        j = Torchfeld.clip(Torchfeld.searchsorted(t, soll), 0, len(t) - 1)
        vor = Torchfeld.clip(j - 1, 0, len(t) - 1)
        return torch.where(Torchfeld.abs(t[vor] - soll) <= Torchfeld.abs(t[j] - soll), vor, j)

    @classmethod
    def schreiben(cls, d, ziel, n):
        j = cls.auswahl(d, n)

        def nehmen(werte, breite):
            a = Torchfeld.feld(werte, dtype=torch.float64).reshape(-1, breite)
            return a[Torchfeld.minimum(j, len(a) - 1)].reshape(-1).tolist() if len(a) else []

        neu = dict(d, tracks={k: nehmen(v, 4) for k, v in (d.get('tracks') or {}).items()})
        if d.get('position_track'):
            neu['position_track'] = dict(d['position_track'], values=nehmen(d['position_track']['values'], 3))
        neu.update(times=[round(i / cls.FPS, 6) for i in range(n)], frame_count=n, duration=round(n / cls.FPS, 6))
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(json.dumps(neu), encoding='utf-8')
