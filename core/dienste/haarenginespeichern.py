# -*- coding: utf-8 -*-
"""Haarenginespeichern — Schritt „speichern" von „Haar Engine": Modell und Ablage (30.09.2026).

Alles wie `Meshfigurspeichern` (Modell `<Name> Haar Engine` in der Modellbibliothek, wenn die Option
`modell` an ist — Vorgabe hier aus, siehe `Haarengineoptionen`; Ablage mit Kacheln, Eigenmorph, Bildern
und `bericht.json`), mit drei Unterschieden:

    Ordner    `output/Export/HaarEngine/<Name>_<Anlagezeit>/` statt MeshTo3D
    Adressen  die Kacheln stehen im Modell als `/api/haarengine/<id>/datei/ergebnis/<name>` — `Texturquelle` löst sie zu Dateien
              auf, wenn `Modelltexturen.sichern` sie neben das Modell kopiert
    Herkunft  `art: haarengine`; dazu legt die Ablage das beste Modell der Iterationen (`haar.glb`) mit ab

Die Klasse erbt, statt zu kopieren: Modellformat und Ablage sind Sache von `Meshfigurspeichern`, hier steht
nur, was sich unterscheidet.
"""

import re
import shutil
from pathlib import Path
from types import SimpleNamespace

from django.conf import settings
from django.utils.timezone import template_localtime

from ..daten.haarengineablage import Haarengineablage
from .haarengineoptionen import Haarengineoptionen
from .meshfigurspeichern import Meshfigurspeichern

__all__ = ['Haarenginespeichern']


class Haarenginespeichern(Meshfigurspeichern):
    ZUSATZ = '2D3D Kleider'

    @classmethod
    def fuer(cls, job):
        """Ohne Lauf — für „Als Genesis-Figur speichern" auf der Auftragsseite."""
        return cls(
            SimpleNamespace(
                job=job,
                ablage=Haarengineablage(job.kennung),
                optionen=Haarengineoptionen.figur(job.optionen),
            )
        )

    def _adressen(self):
        stamm = '/api/haarengine/%s/datei/ergebnis/' % self.job.id
        return {k: stamm + n for k, n in self._bilder().items()}

    def modelldaten(self, name, kacheln):
        from Genesis9.modellmitkleidern import ModellMitKleidern
        daten = super().modelldaten(name, kacheln)
        daten['figur']['herkunft']['art'] = 'haarengine'
        # Kleider und Haar der Iterationen (30.09.2026): die beiden Sammeleinträge mit ihren Reglern — so trägt
        # das gespeicherte Modell in Szene, Studio und Theatre dasselbe wie die Bühne des Auftrags.
        modell = (self.job.ergebnis.get('kreislauf') or {}).get('modell')
        if modell:
            daten['figur']['kleidung'] = ModellMitKleidern.aus(modell).kleidung_modell()
        return daten

    @staticmethod
    def zielordner_fuer(job):
        """`HaarEngine/<Name>_<JJJJ.MM.TT.HH.MM>` (Anlagezeit) — auch das Ziel des Browser-Exports."""
        roh = (job.name or 'modell').strip()
        sauber = re.sub(r'[<>:"|?*\\/\x00-\x1f]', '_', roh).strip(' .') or 'modell'
        stamm = '%s_%s' % (sauber, template_localtime(job.created_at).strftime('%Y.%m.%d.%H.%M'))
        return Path(settings.HAARENGINE_EXPORT_DIR) / stamm

    def ablegen(self):
        aus = super().ablegen()
        # Das beste Modell der Iterationen (`Iterationskreislauf._abschluss`): Figur + Haar am Rig.
        name = (self.job.ergebnis.get('kreislauf') or {}).get('glb')
        if name and self.ablage.ergebnis(name).is_file():
            shutil.copy2(self.ablage.ergebnis(name), self.zielordner() / name)
            aus['dateien'].append(name)
        return aus
