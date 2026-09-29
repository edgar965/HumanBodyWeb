# -*- coding: utf-8 -*-
"""Blendermodellspeichern — Schritt „speichern" von „BlenderModel": Modell und Ablage (29.09.2026).

Alles wie `Meshfigurspeichern` (Modell `<Name> BlenderModel` in der Modellbibliothek, wenn die Option
`modell` an ist — Vorgabe hier aus, siehe `Blendermodelloptionen`; Ablage mit Kacheln, Eigenmorph, Bildern
und `bericht.json`), mit vier Unterschieden:

    Ordner    `output/Export/BlenderModel/<Name>_<Anlagezeit>/` statt MeshTo3D
    Adressen  die Kacheln stehen im Modell als `/api/blendermodell/<id>/datei/ergebnis/<name>` —
              `Texturquelle` löst sie zu Dateien auf, wenn `Modelltexturen.sichern` sie neben das
              Modell kopiert
    Herkunft  `art: blendermodell` und das Netz, das der Lauf aus den Fotos gebaut hat
    Netz      das Netz aus den Fotos liegt als `netz.glb` mit in der Ablage (der Zwischenstand, den man
              sonst nur im Auftragsordner fände)

Die Klasse erbt, statt zu kopieren: Modellformat und Ablage sind Sache von `Meshfigurspeichern`, hier
steht nur, was sich unterscheidet.
"""

import re
import shutil
from pathlib import Path
from types import SimpleNamespace

from django.conf import settings
from django.utils.timezone import template_localtime

from ..daten.blendermodellablage import Blendermodellablage
from .blendermodelloptionen import Blendermodelloptionen
from .meshfigurspeichern import Meshfigurspeichern

__all__ = ['Blendermodellspeichern']


class Blendermodellspeichern(Meshfigurspeichern):
    ZUSATZ = 'BlenderModel'

    @classmethod
    def fuer(cls, job):
        """Ohne Lauf — für „Als Genesis-Figur speichern" auf der Auftragsseite."""
        return cls(
            SimpleNamespace(
                job=job,
                ablage=Blendermodellablage(job.kennung),
                optionen=Blendermodelloptionen.figur(job.optionen),
            )
        )

    def _adressen(self):
        stamm = '/api/blendermodell/%s/datei/ergebnis/' % self.job.id
        return {k: stamm + n for k, n in self._bilder().items()}

    def modelldaten(self, name, kacheln):
        daten = super().modelldaten(name, kacheln)
        herkunft = daten['figur']['herkunft']
        herkunft['art'] = 'blendermodell'
        herkunft['netz'] = (self.job.eingang or {}).get('original')
        return daten

    @staticmethod
    def zielordner_fuer(job):
        """`BlenderModel/<Name>_<JJJJ.MM.TT.HH.MM>` (Anlagezeit) — auch das Ziel des Browser-Exports."""
        roh = (job.name or 'modell').strip()
        sauber = re.sub(r'[<>:"|?*\\/\x00-\x1f]', '_', roh).strip(' .') or 'modell'
        stamm = '%s_%s' % (sauber, template_localtime(job.created_at).strftime('%Y.%m.%d.%H.%M'))
        return Path(settings.BLENDERMODELL_EXPORT_DIR) / stamm

    def ablegen(self):
        aus = super().ablegen()
        netz = self.ablage.netzdatei()
        if netz is not None:
            shutil.copy2(netz, self.zielordner() / 'netz.glb')
            aus['dateien'].append('netz.glb')
        # Das beste Kostüm des Kreislaufs (`Kostuemkreislauf._abschluss`): GLB ohne Körper, .blend mit Körper.
        for name in ((self.job.ergebnis.get('kostuem') or {}).get(k) for k in ('glb', 'blend')):
            if name and self.ablage.ergebnis(name).is_file():
                shutil.copy2(self.ablage.ergebnis(name), self.zielordner() / name)
                aus['dateien'].append(name)
        return aus
