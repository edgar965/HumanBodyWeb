# -*- coding: utf-8 -*-
"""Standhose — die Hose des Standmodells aus dem Körpernetz (`Hosenkoerper`) statt aus ihrem eigenen Netz (05.10.2026).

Zwei Arten von Hosen kommen aus dem Körper:
  * die GarmentCode-Hose der Runden (`sorte` beginnt mit `gc_hose`): locker, weißer Stoff mit Seitenstreifen, Höhenband von der GC-Hose (Saum bis Bund) — so seit 04.10.2026;
  * die Hose aus den Fotostücken (`Fotostuecke`, Schritt „Kleiderstücke": `eigen_foto_<kennung>_hose_f<n>`, Edgar 05.10.2026: „Unterhose ist viel zu weit, in der Vorlage ist sie eng anliegend"): eng anliegend,
    einfarbig in der mittleren Farbe des Fotostücks, ohne Falten. Das Fotostück selbst ist aus dem Netz geschnitten und trug dessen Volumen — gemessen am Auftrag 2026.10.04.11.11.44 (`ProjektTemp/_wegwerf/sapiens/
    hose_abstand.py`) lag es im oberen Band bis 37 mm (p90 26 mm) neben der Körperfläche und stand als Wulst unter dem Hemd; von ihm bleibt das Höhenband.

    if Standhose.gilt(t['sorte']) and glb._koerper is not None:
        Standhose.ablegen(glb, t, name)
"""

import re

import numpy as np

__all__ = ['Standhose']


class Standhose:
    GC = 'gc_hose'
    FOTO = re.compile(r'^eigen_foto_.*_hose_')

    @classmethod
    def gilt(cls, sorte):
        s = str(sorte or '')
        return s.startswith(cls.GC) or bool(cls.FOTO.match(s))

    @classmethod
    def eng(cls, sorte):
        """Die Hose der Fotostücke ist eng, die der Runden locker."""
        return not str(sorte or '').startswith(cls.GC)

    @staticmethod
    def farbe(t):
        """Mittlere Farbe des Stücks (RGB 0–255): Mittel der sichtbaren Pixel seines Bildes mal Tönung, sonst die Farbe des Teils (`farbe`, 0–1) — None, wenn beides fehlt."""
        from PIL import Image

        for tx in t.get('textur') or []:
            if not tx.get('albedo'):
                continue
            try:
                with Image.open(tx['albedo']) as bild:
                    a = np.asarray(bild.convert('RGBA'), dtype=np.float64)
            except OSError:
                continue
            sicht = a[..., 3] > 10
            if sicht.any():
                ton = np.asarray(tx.get('faktor') if tx.get('faktor') is not None else (1.0, 1.0, 1.0), dtype=np.float64)[:3]
                return np.clip(a[sicht][:, :3].mean(axis=0) * ton, 0.0, 255.0)
        farbe = t.get('farbe')
        return np.clip(np.asarray(farbe[:3], dtype=np.float64) * 255.0, 0.0, 255.0) if farbe is not None else None

    @classmethod
    def ablegen(cls, glb, t, name):
        """Die Hose aus dem Körpernetz an die Datei: Höhenband vom Stück, Hautgewichte vom nächsten Körperpunkt."""
        from .hosenkoerper import Hosenkoerper

        k = glb._koerper  # noqa: SLF001 — das Körpernetz, das `Standmodellglb.koerper` abgelegt hat
        y = np.asarray(t['punkte'], dtype=np.float64)[:, 1]
        eng = cls.eng(t.get('sorte'))
        gebaut = Hosenkoerper(k['punkte'], k['dreiecke']).bauen(float(y.min()), float(y.max()) - (0.0 if eng else Hosenkoerper.BUND_UNTER_HOSE), eng=eng)
        index, gewicht = glb._haut(k['haut'], len(k['punkte']))  # noqa: SLF001
        q = gebaut['quelle']
        farbe = cls.farbe(t) if eng else None
        textur = glb._bild_aus(Hosenkoerper.textur(gebaut, farbe=farbe), 'hose:' + name)  # noqa: SLF001
        glb._netz(name + '_g0__hose', gebaut['punkte'], gebaut['dreiecke'], gebaut['normalen'], glb._uv(gebaut['uv']), (index[q], gewicht[q]), textur, (1.0, 1.0, 1.0))  # noqa: SLF001
