# -*- coding: utf-8 -*-
"""Engine2d3dKleiderauftragsquelle — ein Auftrag „2D3D Kleider" aus einem Auftrag „Mesh to 3D" (30.09.2026).

Edgar: „erstelle einen neuen Job, der die Bilder aus …/modell-aus-dateien/meshfigur/2026.09.29.15.42.36/ nimmt."
Ein Auftrag „Mesh to 3D" hat selbst keine Fotos — sein Netz kam aus einem Auftrag „Mesh" (`eingang.ursprung`
zeigt auf dessen `ergebnis/mesh.glb`), und DER hat die Fotos mit ihren Rollen. `fotos()` kopiert sie in die
Ablage des neuen Auftrags (Rolle und Gewicht bleiben), `optionen()` stellt den Körper auf „übernehmen" aus
genau diesem Auftrag.
"""

import re
import shutil

from ..daten.meshablage import Meshablage
from ..models import Meshauftrag, Meshfigurauftrag

__all__ = ['Engine2d3dKleiderauftragsquelle']


class Engine2d3dKleiderauftragsquelle:
    KENNUNG = re.compile(r'(\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}\.\d{2})')

    @classmethod
    def _meshfigur(cls, kennung):
        job = Meshfigurauftrag.objects.filter(kennung=kennung).first()
        if job is None:
            raise ValueError('Auftrag „Mesh to 3D" %s gibt es nicht' % kennung)
        return job

    @classmethod
    def _meshauftrag(cls, meshfigur):
        """Der Auftrag „Mesh", aus dem das Netz kam — über den Pfad in `eingang.ursprung`."""
        ursprung = str((meshfigur.eingang or {}).get('ursprung') or '')
        treffer = cls.KENNUNG.search(ursprung.replace('\\', '/').split('/meshauftraege/')[-1]) \
            if '/meshauftraege/' in ursprung.replace('\\', '/') else None
        if treffer is None:
            return None
        return Meshauftrag.objects.filter(kennung=treffer.group(1)).first()

    @classmethod
    def fotos(cls, kennung, ablage):
        """Die Fotos des Mesh-Auftrags in `eingang/` des neuen Auftrags → Einträge für `bilder`."""
        meshfigur = cls._meshfigur(kennung)
        mesh = cls._meshauftrag(meshfigur)
        if mesh is None:
            raise ValueError('Auftrag %s: kein Auftrag „Mesh" mit Fotos gefunden (eingang.ursprung)' % kennung)
        quelle = Meshablage(mesh.kennung).unter(Meshablage.EINGANG)
        ablage.anlegen()
        aus = []
        for eintrag in mesh.bilder or []:
            datei = eintrag.get('datei') if isinstance(eintrag, dict) else None
            if not datei or not (quelle / datei).is_file():
                continue
            name = ablage.sauber(datei)
            shutil.copy2(quelle / datei, ablage.unter(ablage.EINGANG) / name)
            aus.append({'datei': name, 'original': datei, 'gewicht': eintrag.get('gewicht', 100),
                        'bereich': eintrag.get('bereich'), 'rolle': eintrag.get('rolle') or 'auto'})
        return aus

    @classmethod
    def optionen(cls, kennung, optionen):
        """`koerper.quelle = uebernehmen`, `koerper.auftrag = kennung` über die mitgeschickten Optionen."""
        aus = dict(optionen if isinstance(optionen, dict) else {})
        koerper = dict(aus.get('koerper') if isinstance(aus.get('koerper'), dict) else {})
        koerper.update(quelle='uebernehmen', auftrag=kennung)
        aus['koerper'] = koerper
        return aus
