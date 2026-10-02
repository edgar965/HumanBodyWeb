# -*- coding: utf-8 -*-
"""Engine2d3dKleiderspeichern — Schritt „speichern" von „Haar Engine": Modell und Ablage (30.09.2026).

Alles wie `Meshfigurspeichern` (Modell `<Name> Haar Engine` in der Modellbibliothek, wenn die Option
`modell` an ist — Vorgabe hier aus, siehe `Engine2d3dKleideroptionen`; Ablage mit Kacheln, Eigenmorph, Bildern
und `bericht.json`), mit drei Unterschieden:

    Ordner    `output/Export/Engine2d3dKleider/<Name>_<Anlagezeit>/` statt MeshTo3D
    Adressen  die Kacheln stehen im Modell als `/api/engine2d3dkleider/<id>/datei/ergebnis/<name>` — `Texturquelle` löst sie zu Dateien
              auf, wenn `Modelltexturen.sichern` sie neben das Modell kopiert
    Herkunft  `art: engine2d3dkleider`; dazu legt die Ablage das beste Modell der Iterationen (`haar.glb`) mit ab

Die Klasse erbt, statt zu kopieren: Modellformat und Ablage sind Sache von `Meshfigurspeichern`, hier steht
nur, was sich unterscheidet.
"""

import re
import shutil
from pathlib import Path
from types import SimpleNamespace

from django.conf import settings
from django.utils.timezone import template_localtime

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from .meshfigurspeichern import Meshfigurspeichern

__all__ = ['Engine2d3dKleiderspeichern']


class Engine2d3dKleiderspeichern(Meshfigurspeichern):
    ZUSATZ = '2D3D Kleider'

    @classmethod
    def fuer(cls, job):
        """Ohne Lauf — für „Als Genesis-Figur speichern" auf der Auftragsseite."""
        return cls(
            SimpleNamespace(
                job=job,
                ablage=Engine2d3dKleiderablage(job.kennung),
                optionen=Engine2d3dKleideroptionen.figur(job.optionen),
            )
        )

    def _adressen(self):
        stamm = '/api/engine2d3dkleider/%s/datei/ergebnis/' % self.job.id
        return {k: stamm + n for k, n in self._bilder().items()}

    def modelldaten(self, name, kacheln):
        from Genesis9.modellmitkleidern import ModellMitKleidern
        daten = super().modelldaten(name, kacheln)
        daten['figur']['herkunft']['art'] = 'engine2d3dkleider'
        # Kleider und Haar der Iterationen (30.09.2026): die beiden Sammeleinträge mit ihren Reglern — so trägt
        # das gespeicherte Modell in Szene, Studio und Theatre dasselbe wie die Bühne des Auftrags.
        modell = (self.job.ergebnis.get('kreislauf') or {}).get('modell')
        if modell:
            mk = ModellMitKleidern.aus(modell)
            daten['figur']['kleidung'] = mk.kleidung_modell()
            # Körper- und Gesichtsregler der Iterationen (`koerper_regler`, `koerper_ort`, `IterationGesicht`) über der
            # Stellung — wie `Kleidermodellbau(…, koerper=)` in der Runde; sonst zeigte die Szene den Körper ohne die
            # Nachformung, gegen die die Kleider gepasst wurden (01.10.2026).
            daten['figur']['regler'] = dict(daten['figur'].get('regler') or {},
                                            **{str(k): v for k, v in mk.koerper.items()})
        return daten

    @staticmethod
    def zielordner_fuer(job):
        """`Engine2d3dKleider/<Name>_<JJJJ.MM.TT.HH.MM>` (Anlagezeit) — auch das Ziel des Browser-Exports."""
        roh = (job.name or 'modell').strip()
        sauber = re.sub(r'[<>:"|?*\\/\x00-\x1f]', '_', roh).strip(' .') or 'modell'
        stamm = '%s_%s' % (sauber, template_localtime(job.created_at).strftime('%Y.%m.%d.%H.%M'))
        return Path(settings.ENGINE2D3DKLEIDER_EXPORT_DIR) / stamm

    def ablegen(self):
        aus = super().ablegen()
        # Das beste Modell der Iterationen (`Iterationskreislauf._abschluss`): Figur + Haar am Rig.
        name = (self.job.ergebnis.get('kreislauf') or {}).get('glb')
        if name and self.ablage.ergebnis(name).is_file():
            shutil.copy2(self.ablage.ergebnis(name), self.zielordner() / name)
            aus['dateien'].append(name)
        return aus
