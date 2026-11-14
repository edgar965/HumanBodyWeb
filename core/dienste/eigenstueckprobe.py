# -*- coding: utf-8 -*-
u"""Eigenstueckprobe — ein eigenes Stück auf Genesis 9 und HumanBody, als Bild.

Edgar (25.09.2026): „… Test der Ausgabe auf Genesis und HumanBody Modell
(Screenshot)". Das Stück wird NICHT eigens für die Probe gerechnet, sondern
über die Wege, die auch die Szene nimmt — sonst prüfte die Probe etwas anderes,
als Edgar später sieht:

    Genesis 9   `Durchschimmerprobe.ruhe` — Folger aus der Garderobe,
                `folgernetz` mit Kollision und Bindung, Browserstufe
    HumanBody   `G9kleidhumanbody.antwort` — derselbe Endpunkt wie „Daz auf
                HumanBody" im Browser, Antwort decodiert

Gerendert mit `Durchschimmerprobe.pixel` (pyrender, vier Ansichten, einfarbig):
das zählt nebenbei Hautpixel VOR dem Stoff (rot im Bild) — die obere Schranke
dessen, was der Browser zeigt, denn die Hautmaske entsteht erst dort.
Serverseitig, weil die Hilfeseite keine Szene hat; kein Headless-Browser.
"""
import base64
import logging
from pathlib import Path
from types import SimpleNamespace

import torch
from KoerperKI_alle.torchfeld import Torchfeld

logger = logging.getLogger('core')

__all__ = ['Eigenstueckprobe']


class Eigenstueckprobe:
    u"""`genesis(kennung, ziel)` und `humanbody(kennung, ziel)` → `{bild, pixel, teile}`."""

    def __init__(self):
        from core.dienste.durchschimmerprobe import Durchschimmerprobe
        self.probe = Durchschimmerprobe(rendern=True)

    def genesis(self, kennung, ziel):
        from core.api.g9figur import G9figur
        formung = G9figur.formung({'regler': {}}, {})
        koerper = self.probe.koerper(formung)
        teile = [t for t in self.probe.ruhe(kennung, formung, koerper) if t is not None]
        stoff = [(t.punkte, Torchfeld.feld(t.dreiecke).reshape(-1, 3)) for t in teile]
        return self._bild(koerper, stoff, 'Genesis 9', Path(ziel) / 'probe_genesis9.png')

    def humanbody(self, kennung, ziel, geschlecht='female'):
        from Genesis9.garderobe import G9garderobe

        from core.api.g9kleidhumanbody import G9kleidhumanbody
        from core.dienste.g9aufhumanbody import G9aufhumanbody
        eintrag = G9garderobe.eintrag(kennung) or {}
        antwort = G9kleidhumanbody.antwort(kennung, eintrag, {'geschlecht': geschlecht})
        if not isinstance(antwort, dict):
            # Eine JsonResponse heißt: der Endpunkt lehnt ab — die Probe sagt, warum.
            raise ValueError(antwort.content.decode('utf-8', 'ignore'))
        figur = G9aufhumanbody(geschlecht, None).figur()
        koerper = SimpleNamespace(punkte=Torchfeld.feld(figur['fein'], dtype=torch.float64),
                                  dreiecke=Torchfeld.feld(figur['fein_dreiecke']).reshape(-1, 3))
        stoff = [(Torchfeld.astype(self._feld(t['vertices'], torch.float32), torch.float64).reshape(-1, 3),
                  Torchfeld.astype(self._feld(t['faces'], torch.uint32), torch.int64).reshape(-1, 3))
                 for t in antwort['teile']]
        return self._bild(koerper, stoff, 'HumanBody', Path(ziel) / 'probe_humanbody.png')

    @staticmethod
    def _feld(text, typ):
        return torch.frombuffer(bytearray(base64.b64decode(text)), dtype=typ).to(Torchfeld.KARTE)

    def _bild(self, koerper, stoff, titel, pfad):
        u"""Alle Teile zu einem Netz, vier Ansichten, als PNG nach `pfad`."""
        if not stoff:
            raise ValueError(u'%s: das Stück hat keine tragbaren Teile' % titel)
        punkte, dreiecke, versatz = [], [], 0
        for p, d in stoff:
            punkte.append(p)
            dreiecke.append(Torchfeld.astype(d, torch.int64) + versatz)
            versatz += len(p)
        pixel, bild = self.probe.pixel(koerper, Torchfeld.cat(punkte),
                                       Torchfeld.cat(dreiecke), titel)
        pfad.parent.mkdir(parents=True, exist_ok=True)
        bild.save(pfad)
        logger.info('Eigenes Stück, Probe %s: %d Teile, %d Hautpixel vor dem Stoff, %s',
                    titel, len(stoff), pixel, pfad)
        return {'bild': pfad.name, 'pixel': int(pixel), 'teile': len(stoff)}
