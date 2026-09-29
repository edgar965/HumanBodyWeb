# -*- coding: utf-8 -*-
"""Blendermodellgrundfigur — Schritt „grundfigur" von BlenderModel: die Genesis-9-Grundfigur, OHNE Netz aus
Fotos.

Edgar (29.09.2026): „trellis soll nicht laufen" — die Vorlagen dieses Bereichs sind gemalte Illustrationen,
und TRELLIS/Hunyuan3D liefern darauf kein brauchbares Netz (Auftrag 19.45.46: ein Drahtgeflecht). Bis heute
begann der Lauf trotzdem mit dem Netz-Schritt aus den Fotos und passte Genesis daran an („erkennung …
frisur"); ein Lauf mit einer übrig gebliebenen Option `formmodell: trellis2` hat am 29.09.2026 TRELLIS
gestartet und ist danach in der Körperkette gescheitert („index 0 is out of bounds"). Diese Kette ist
ausgebaut; der Körper ist jetzt die gewählte Grundfigur (Option „Grundfigur", `Meshfigurregler.GRUNDFIGUREN`),
das Kostüm baut der Schritt „kostuem" darüber.

Ergebnis: `arbeit/grundkoerper.glb` (Netz mit Rig, für Blender — `G9figurrigglb`) und
`ergebnis['regler']['stellung']` (so zeigt die Bühne die Figur, und `export` baut daraus die GLB mit Rig). Was
die alte Kette in `ergebnis` hinterlassen hat (Eigenmorph, Kacheln, Erkennung …), wird entfernt —
`job.stellung()` läse den Eigenmorph sonst weiter mit, und die Figur trüge die Form des TRELLIS-Netzes.
"""

import time

__all__ = ['Blendermodellgrundfigur']


class Blendermodellgrundfigur:
    DATEI = 'grundkoerper.glb'
    #: Ergebnisse der ausgebauten Kette Netz → Figur.
    ALTLASTEN = (
        'netz',
        'erkennung',
        'haar',
        'kleidung',
        'kalibrierung',
        'koerper',
        'gesicht',
        'rest',
        'kopfeigen',
        'textur',
        'fototextur',
        'vorschau',
        'frisur',
        'ketten',
        'anpassung',
        'regler',
    )

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage

    def ausfuehren(self):
        from Genesis9.figurrigglb import G9figurrigglb

        from .meshfigurregler import Meshfigurregler

        basis = self.lauf.optionen.get('basis') or 'masculine'
        stellung = dict(Meshfigurregler.GRUNDFIGUREN.get(basis, Meshfigurregler.GRUNDFIGUREN['masculine']))
        self.lauf.melden(0.1, 'Grundfigur Genesis 9 (%s) mit Rig' % basis)
        t = time.perf_counter()
        # MIT Rig: der Kreislauf stellt die Arme für den Vergleich (`effekte/blender/kostuem/koerperpose.py`).
        bericht = G9figurrigglb(stellung, name=self.job.name).schreiben(self.ablage.arbeit(self.DATEI))
        for alt in self.ALTLASTEN:
            self.job.ergebnis.pop(alt, None)
        self.job.ergebnis['regler'] = {'stellung': stellung}
        self.job.ergebnis['grundfigur'] = {
            'basis': basis,
            'datei': self.DATEI,
            'sekunden': round(time.perf_counter() - t, 1),
            **{k: v for k, v in (bericht or {}).items() if k != 'datei' and isinstance(v, (int, float))},
        }
        self.lauf.melden(1.0, 'Grundfigur %s bereit' % basis)
