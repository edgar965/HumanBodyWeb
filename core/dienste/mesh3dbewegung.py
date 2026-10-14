# -*- coding: utf-8 -*-
"""Mesh3dbewegung — die BVH-Bewegung auf der Figur eines Mesh-3D-Auftrags, für die Animationsleiste der 3D-Ansicht (11.10.2026).

Edgar (11.10.2026): „machst du mir noch die 3D-Ansicht wie bei dem anderen Job? mit den Filtern für Mesh, Kleider, Model, der Animation usw." Die Ansicht ist die Bühne von „Mesh to 3D" und „2D3D Kleider"
(`Meshfigurbuehne`, `Engine2d3dKleideranimation`); die Bewegung dazu rechnet KEIN neuer Weg, sondern derselbe wie dort: `Engine2d3dKleiderbewegung` (Retarget BVH → Genesis 9, `Retargetdaten`, CPU, im
Django-Prozess) auf der Stellung des Auftrags „Mesh to 3D", den der Import im Schritt „figur" gerechnet hat. Welche Datei, wählt der Auftrag (`Mesh3danimationswahl`, Vorgabe A_Results/DanceKurz.bvh, seit 13.10.2026);
ohne sie der Tanz der Bibliothek (`Engine2d3dKleiderfilmoptionen.tanz`, Daz/Dance.bvh, bis dahin die feste Vorgabe).

Ablage: `arbeit/bewegung/bewegung.json` + `stand.json` (Fingerabdruck aus BVH-Datei samt Änderungszeit, Stellung und Körperhöhe — ist er gleich, bleibt die Datei, wie sie ist).
"""

import hashlib
import json
import logging
import os
from types import SimpleNamespace

from ..daten.blendimportablage import Blendimportablage
from .mesh3danimationswahl import Mesh3danimationswahl

logger = logging.getLogger('core')

__all__ = ['Mesh3dbewegung']


class Mesh3dbewegung:
    ORDNER = 'bewegung'
    DATEI = 'bewegung.json'

    def __init__(self, kennung):
        self.ablage = Blendimportablage(kennung)

    def pfad(self):
        return self.ablage.arbeit(self.ORDNER) / self.DATEI

    def job(self):
        """Der Auftrag „Mesh to 3D“ des Schritts „figur“ — `ValueError`, solange es ihn oder eine Stellung nicht gibt."""
        from ..models import Meshfigurauftrag

        figur = ((self.ablage.stand().get('ergebnis') or {}).get('figur') or {})
        job = Meshfigurauftrag.objects.filter(pk=figur['id']).first() if figur.get('id') else None
        if job is None or not job.stellung():
            raise ValueError('Noch keine Figur — erst nach der Körperkette von „Mesh to 3D“')
        return job

    @staticmethod
    def bvh(wunsch=''):
        """Die BVH-Datei: die gewünschte (`rechnen` nimmt ohne Angabe die Standardanimation des Auftrags), sonst der Tanz der Bibliothek."""
        from .engine2d3dkleiderfilmoptionen import Engine2d3dKleiderfilmoptionen

        pfad = str(wunsch or '').strip()
        if pfad:
            if not (pfad.lower().endswith('.bvh') and os.path.isfile(pfad)):
                raise ValueError('Keine BVH-Datei: %s' % pfad)
            return pfad
        tanz = Engine2d3dKleiderfilmoptionen.tanz()
        if not tanz:
            raise ValueError('Der Tanz der Bibliothek (Daz/Dance.bvh) fehlt — eine BVH-Datei angeben')
        return tanz

    def rechnen(self, wunsch=''):
        """`{datei, bvh, bilder, neu}` — rechnet die Bewegung, wenn sich BVH, Stellung oder Körperhöhe seit dem letzten Mal geändert haben."""
        from .engine2d3dkleiderbewegung import Engine2d3dKleiderbewegung

        job = self.job()
        # Ohne ausdrückliche Datei gilt die Standardanimation des Auftrags (13.10.2026, `Mesh3danimationswahl`, Vorgabe A_Results/DanceKurz); fehlt sie im Bestand, der Tanz der Bibliothek.
        bvh = self.bvh(wunsch or Mesh3danimationswahl(self.ablage.kennung).pfad())
        hoehe = float((job.optionen or {}).get('hoehe_cm') or 0)
        stand = hashlib.md5(json.dumps([bvh, os.stat(bvh).st_mtime_ns, job.stellung(), hoehe], sort_keys=True, default=str).encode('utf-8')).hexdigest()[:12]
        ordner = self.ablage.arbeit(self.ORDNER)
        marke = ordner / 'stand.json'
        if self.pfad().is_file() and marke.is_file():
            alt = json.loads(marke.read_text(encoding='utf-8'))
            if alt.get('stand') == stand:
                return {**alt, 'neu': False}
        ordner.mkdir(parents=True, exist_ok=True)
        # `Engine2d3dKleiderbewegung` liest `job.stellung()` und `job.optionen['figur']['hoehe_cm']` — der Auftrag „Mesh to 3D“ trägt die Höhe flach (`optionen['hoehe_cm']`).
        huelle = SimpleNamespace(job=SimpleNamespace(stellung=job.stellung, optionen={'figur': {'hoehe_cm': hoehe}}))
        _pfad, spuren = Engine2d3dKleiderbewegung(huelle).rechnen(bvh, ordner)
        bericht = {'datei': self.DATEI, 'bvh': bvh, 'bilder': int(spuren.frame_count), 'stand': stand}
        marke.write_text(json.dumps(bericht, ensure_ascii=False), encoding='utf-8')
        logger.info('Mesh-3D %s: Bewegung %s (%d Bilder)', self.ablage.kennung, os.path.basename(bvh), bericht['bilder'])
        return {**bericht, 'neu': True}

    def stand(self):
        """Was schon gerechnet ist (`{datei, bvh, bilder}`) oder `None`."""
        marke = self.ablage.arbeit(self.ORDNER) / 'stand.json'
        if not (self.pfad().is_file() and marke.is_file()):
            return None
        return json.loads(marke.read_text(encoding='utf-8'))
