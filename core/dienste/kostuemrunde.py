# -*- coding: utf-8 -*-
"""Kostuemrunde — eine Runde des Kostüm-Kreislaufs rechnen (bauen, rendern, benoten) und im Auftrag ablegen.

`bewerten`: alle Kandidaten der Runde in EINEM Blender-Prozess (`Kostuemblender`), je Kandidat die Renders in
den Blickwinkeln der Vorlagen, benotet gegen die Vorlage (`Kostuemnote`, gewichtet nach dem Gewicht der
Fotos). `ablegen`: Vergleichstafel und Kostüm-GLB nach `iterationen/runde_NNN_*`, ein Eintrag in
`ergebnis['iterationen']` (Reiter „Iterationen" der Seite). Abgelegt werden nur Runden, die etwas zeigen — die
Ausgangslage, jede Verbesserung und jeder Vorschlag der Prüf-KI; alle Runden stehen als Zahlen in
`ergebnis['kostuem']['verlauf']`.
"""

import shutil

from django.utils import timezone

from .kostuembild import Kostuembild
from .kostuemblender import Kostuemblender
from .kostuemnote import Kostuemnote
from .kostuemtafel import Kostuemtafel

__all__ = ['Kostuemrunde']


class Kostuemrunde:
    def __init__(self, lauf, koerper, referenzen):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.koerper = koerper
        self.referenzen = referenzen
        self.blender = Kostuemblender(lauf)

    def winkel(self):
        return sorted({float(r.winkel) for r in self.referenzen})

    def ordner(self, runde):
        return self.ablage.arbeit('kostuem') / ('runde_%04d' % runde)

    def bewerten(self, runde, kandidaten, melden=None):
        """`kandidaten`: [(name, werte)] → [{name, werte, note, je_ansicht, renders, glb}] in derselben
        Folge."""
        aus = self.ordner(runde)
        bericht = self.blender.rendern(
            self.koerper, aus, kandidaten, self.winkel(), glb=True, fortschritt=melden
        )
        ergebnisse = []
        for name, werte in kandidaten:
            eintrag = bericht['kandidaten'][name]
            je_ansicht, renders, paare = [], {}, []
            for r in self.referenzen:
                datei = eintrag['bilder'][str(int(round(r.winkel)))]
                render = Kostuembild.aus_render(aus / name / datei)
                note = Kostuemnote.vergleichen(r.bild, render)
                renders[r.datei] = render
                je_ansicht.append({'datei': r.datei, 'original': r.original, 'winkel': r.winkel, **note})
                paare.append((r.gewicht, note))
            ergebnisse.append(
                {
                    'name': name,
                    'werte': werte,
                    'note': Kostuemnote.gesamt(paare),
                    'je_ansicht': je_ansicht,
                    'renders': renders,
                    'glb': aus / name / 'kostuem.glb',
                    'teile': eintrag.get('teile') or {},
                    'vorn_grad': bericht.get('vorn_grad'),
                    'sekunden': bericht.get('sekunden'),
                }
            )
        return ergebnisse

    def aufraeumen(self, runde):
        """Die Zwischendateien der Runde (Renders, GLBs der Kandidaten) — abgelegt ist, was bleiben soll."""
        shutil.rmtree(self.ordner(runde), ignore_errors=True)

    def ablegen(self, runde, art, erg, notiz, aenderungen=None, kritik=None, uebernommen=True):
        """Tafel (+ GLB, wenn übernommen) nach `iterationen/`, Eintrag in `ergebnis['iterationen']`. → Pfad
        der Tafel."""
        ziel = self.ablage.iterationen()
        ziel.mkdir(parents=True, exist_ok=True)
        tafel = 'runde_%03d_vergleich.png' % runde
        Kostuemtafel.bauen(
            [
                (r.winkel, r.bild, erg['renders'][r.datei], n)
                for r, n in zip(self.referenzen, erg['je_ansicht'], strict=True)
            ],
            ziel / tafel,
        )
        dateien = {'vergleich': tafel}
        if uebernommen and erg['glb'].is_file():
            dateien['kostuem'] = 'runde_%03d_kostuem.glb' % runde
            shutil.copyfile(erg['glb'], ziel / dateien['kostuem'])
        eintrag = {
            'runde': runde,
            'zeit': timezone.localtime().strftime('%Y-%m-%d %H:%M'),
            'art': art,
            'uebernommen': uebernommen,
            'notiz': notiz,
            'note': erg['note'],
            'je_ansicht': [
                {k: a[k] for k in ('original', 'winkel', 'iou', 'farbe')} for a in erg['je_ansicht']
            ],
            'aenderungen': aenderungen or {},
            'teile': erg['teile'],
            'dateien': dateien,
        }
        if kritik:
            eintrag['kritik'] = kritik
        self.job.ergebnis.setdefault('iterationen', []).append(eintrag)
        return ziel / tafel
