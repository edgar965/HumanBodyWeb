# -*- coding: utf-8 -*-
"""Mesh3dnetzansicht — das Netz eines Mesh-3D-Auftrags, leicht genug für die 3D-Ansicht (11.10.2026).

Edgar: „bei klick auf Auftrag kommt lange warteschleife". Gemessen am Zauberer (`2026.10.11.20.03.34`): Die 3D-Ansicht lud bei JEDEM Öffnen das ganze Netz — `koerper.glb`
des Auftrags „Mesh to 3D", 67 MB, 1.013.572 Punkte, 1.935.797 Dreiecke. Im Chrome: Laden 2,2 bis 6,7 s, `GLTFLoader.parse` 1,9 s auf dem Hauptfaden (Seite eingefroren), dazu
die GPU-Last für zwei Millionen Dreiecke. Die Figur selbst baut in 0,2 s (warm). Der Server liefert dieselbe Datei in 0,25 s (curl) — es war der Browser.

Die Bühne braucht das Netz nur zum Anschauen und Vergleichen mit der Figur. Deshalb steht neben dem Original eine VEREINFACHTE Kopie (`arbeit/ansicht/netz_ansicht.glb`):
quadratische Kantenreduktion auf `ZIEL_FLAECHEN` Dreiecke (pymeshlab), die Farbe je Punkt aus der Textur des Originals (`to_color`), Koordinaten unverändert — die Lage aus
der Erkennung (`erkennung.matrix`) gilt für beide. Gemessen am Zauberer: 150.000 Dreiecke, 74.961 Punkte, 3,0 MB, Höhe 2,0002 m gegen 2,0000 m, Farbmittel
(62,4 / 55,7 / 51,9) gegen (65,0 / 58,0 / 53,9) — 67 s auf einem ausgelasteten Rechner.

Das Original bleibt Eingang von „Mesh to 3D" und wird nicht angefasst. Gebaut wird in einem eigenen Prozess (`manage.py mesh3d_netzansicht <kennung>`), angestoßen von der Seite
(`POST …/netzansicht/`), nicht beim Lesen des Zustands: ein GET schreibt nichts. Unter `GROSS_BYTES` braucht es keine Kopie (`unnoetig`); scheitert der Bau, lädt die Bühne das Original (`fehler`).
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

from django.conf import settings
from django.urls import reverse

from ..daten.blendimportablage import Blendimportablage
from ..daten.meshfigurablage import Meshfigurablage

logger = logging.getLogger('core')

__all__ = ['Mesh3dnetzansicht']


class Mesh3dnetzansicht:
    ORDNER = 'ansicht'
    DATEI = 'netz_ansicht.glb'
    STAND = 'netz_ansicht.json'
    BAUT = 'baut.json'
    FEHLER = 'fehler.json'
    LOG = 'bauen.log'
    #: Fassung des Verfahrens — eine Kopie anderer Fassung gilt als veraltet (`artefakte-benennen.md`).
    FASSUNG = 1
    #: Darunter lädt die Bühne das Original selbst (Setzung: ab etwa 15 MB war die Ladezeit am Zauberer spürbar).
    GROSS_BYTES = 15_000_000
    ZIEL_FLAECHEN = 200_000
    #: Vorstufe des Baus (`vereinfachen(vorstufe=True)`): Gitter-Vereinfachung mit 0,15 % der Kastendiagonale ab 600.000 Dreiecken. Gemessen 12.10.2026 am Netz „Edgar“ (1.970.150 Dreiecke, `ProjektTemp/_wegwerf/mesh3d/ansicht_zeiten.py`):
    #: 133 s → 47 s (Gitter 3,0 s → 580.234 Dreiecke, Kantenreduktion 33,3 s statt 121,9 s); Abstand Originalfläche → Vorschau (200.000 Punkte, `ansicht_abweichung.py`) in beiden Fassungen Mittel 0,67 mm, p95 1,30 mm, größter 2,78 gegen 2,74 mm.
    VORSTUFE_AB = 600_000
    VORSTUFE_PROZENT = 0.15
    #: Ein Bau, der so lange läuft, gilt als verloren (der Zauberer brauchte 67 s auf einem ausgelasteten Rechner).
    BAUT_HOECHSTENS_S = 900
    FORMATE = ('.glb', '.gltf', '.obj', '.ply')

    def __init__(self, kennung):
        self.ablage = Blendimportablage(kennung)
        self.kennung = self.ablage.kennung

    # ------------------------------------------------------------------ Pfade

    def ordner(self):
        return self.ablage.arbeit(self.ORDNER)

    def pfad(self):
        return self.ordner() / self.DATEI

    def _eigene(self):
        """Die Datei `koerper.glb` des Imports selbst (beide Wege): der Eingang des Auftrags „Mesh to 3D“ ist ihre Kopie. Sie liegt nach dem Schritt „koerper“ da — der Bau kann also laufen, bevor der Auftrag angelegt wird (`vorab`)."""
        from .blendimportnetz import Blendimportnetz

        datei = self.ablage.arbeit(Blendimportnetz.DATEI)
        return datei if datei.is_file() and datei.suffix.lower() in self.FORMATE else None

    def _figurnetz(self):
        """Das Netz im Eingang des Auftrags „Mesh to 3D“ dieses Imports — oder `None`, solange es den Auftrag nicht gibt."""
        from ..models import Meshfigurauftrag

        figur = ((self.ablage.stand().get('ergebnis') or {}).get('figur') or {})
        if not figur.get('id'):
            return None
        try:
            job = Meshfigurauftrag.objects.filter(pk=figur['id']).first()
        except (ValueError, TypeError):
            return None
        datei = Meshfigurablage(job.kennung).netzdatei('koerper') if job is not None else None
        return datei if datei is not None and datei.suffix.lower() in self.FORMATE else None

    def quelle(self):
        """Das Netz, von dem die Vorschau stammt: `koerper.glb` des Imports, sonst das im Eingang des Auftrags „Mesh to 3D“ (`None`: es gibt noch keines)."""
        return self._eigene() or self._figurnetz()

    @classmethod
    def stempel(cls, quelle):
        """Woran die Kopie erkennt, dass sie zu diesem Original gehört: Fassung, Ziel, Größe und Änderungszeit."""
        stand = Path(quelle).stat()
        return [cls.FASSUNG, cls.ZIEL_FLAECHEN, stand.st_size, stand.st_mtime_ns]

    def _gelesen(self, name):
        try:
            return json.loads((self.ordner() / name).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    # ------------------------------------------------------------------ Zustand

    def aktuell(self, quelle):
        """Der Stempel der Vorschau gehört zur Quelle — oder zum Netz im Eingang des Auftrags: vor dem 12.10.2026 stammte er von dort (Zauberer, Zauberer Kopie), die Vorschau gilt weiter."""
        gespeichert = self._gelesen(self.STAND)
        if not gespeichert or not self.pfad().is_file():
            return False
        return any(gespeichert.get('stempel') == self.stempel(q) for q in (quelle, self._figurnetz()) if q is not None)

    def baut(self):
        from ..pipelines.prozesspruefung import Prozesspruefung

        marke = self._gelesen(self.BAUT)
        if not marke or time.time() - float(marke.get('start', 0)) > self.BAUT_HOECHSTENS_S:
            return False
        return bool(marke.get('pid')) and Prozesspruefung.lebt(int(marke['pid']))

    def zustand(self):
        """`{status, adresse?, datei?, mb?, fehler?}` — `keine` (kein Netz), `unnoetig` (klein genug), `bereit`, `baut`, `fehler`, `fehlt` (noch nicht gebaut).
        `adresse` und `datei` (Name mit Endung, nach der die Bühne den Lader wählt) stehen bei `bereit` UND `unnoetig`: Die Mesh-Ansicht zeigt das Netz damit auch, wenn es den Auftrag „Mesh to 3D“
        des Imports nicht gibt (13.10.2026, „Rosemary Winters“ — der Auftrag war gelöscht, die Ansicht blieb leer); bei `unnoetig` liefert der Endpunkt das Netz selbst."""
        quelle = self.quelle()
        if quelle is None:
            return {'status': 'keine'}
        if quelle.stat().st_size <= self.GROSS_BYTES:
            return {'status': 'unnoetig', 'datei': quelle.name, 'adresse': '%s?v=%s' % (reverse('mesh3d_netzansicht', args=[self.kennung]), quelle.stat().st_mtime_ns)}
        if self.aktuell(quelle):
            stempel = self._gelesen(self.STAND)['stempel']
            return {'status': 'bereit', 'datei': self.DATEI, 'mb': round(self.pfad().stat().st_size / 1e6, 1),
                    'adresse': '%s?v=%s' % (reverse('mesh3d_netzansicht', args=[self.kennung]), stempel[3])}
        if self.baut():
            return {'status': 'baut'}
        fehler = self._gelesen(self.FEHLER)
        if fehler and fehler.get('stempel') == self.stempel(quelle):
            return {'status': 'fehler', 'fehler': fehler.get('text', '')}
        return {'status': 'fehlt'}

    # ------------------------------------------------------------------ Bau anstoßen

    def anstossen(self):
        """Den Bau in einem eigenen Prozess starten, wenn er nötig ist und nicht schon läuft → der Zustand danach."""
        from .auftragsarbeiter import Auftragsarbeiter

        if self.zustand()['status'] != 'fehlt':
            return self.zustand()
        self.ordner().mkdir(parents=True, exist_ok=True)
        befehl = [sys.executable, str(Path(settings.BASE_DIR) / 'manage.py'), 'mesh3d_netzansicht', self.kennung]
        with open(self.ordner() / self.LOG, 'ab') as protokoll:
            prozess = Auftragsarbeiter._popen(befehl, protokoll)
        (self.ordner() / self.BAUT).write_text(json.dumps({'pid': prozess.pid, 'start': time.time()}), encoding='utf-8')
        logger.info('Mesh-3D %s: Netzansicht wird gebaut (Prozess %s)', self.kennung, prozess.pid)
        return {'status': 'baut'}

    @classmethod
    def vorab(cls, kennung):
        """Den Bau schon im Lauf des Imports anstoßen, nicht erst beim Öffnen der Seite (Edgar, 12.10.2026: „bei Edgar dauert es ewig, bis das Mesh in der 3D-View angezeigt wird“ — gemessen: der Bau
        brauchte beim ersten Öffnen 125 s, 09:56 bis 09:58). Er läuft in einem eigenen Prozess neben dem Rest des Imports und ist fertig, wenn der Auftrag fertig ist. Ein Fehler hier bricht den Import
        nie ab (die Seite stößt den Bau dann beim Öffnen an, wie vorher) → der Zustand oder `None`. Nur Aufträge der Jobseite „Mesh-3D“ (`stand.bereich`) haben eine 3D-Ansicht."""
        try:
            ansicht = cls(kennung)
            if ansicht.ablage.stand().get('bereich') != 'mesh3d':
                return None
            return ansicht.anstossen()
        except Exception:  # noqa: BLE001 — die Ansicht ist Beiwerk des Imports
            logger.warning('Mesh-3D %s: Netzansicht konnte nicht vorab angestoßen werden', kennung, exc_info=True)
            return None

    # ------------------------------------------------------------------ Bau (im eigenen Prozess)

    def bauen(self):
        """Die vereinfachte Kopie schreiben → Zahl der Dreiecke. Wirft bei einem Fehler; der Aufrufer merkt ihn mit `fehler_merken`."""
        quelle = self.quelle()
        if quelle is None:
            raise ValueError('Kein Netz im Auftrag „Mesh to 3D“')
        stempel = self.stempel(quelle)
        self.ordner().mkdir(parents=True, exist_ok=True)
        flaechen, punkte = self.vereinfachen(quelle, self.pfad(), vorstufe=True)
        (self.ordner() / self.STAND).write_text(json.dumps({'stempel': stempel, 'flaechen': flaechen, 'punkte': punkte}), encoding='utf-8')
        for name in (self.BAUT, self.FEHLER):
            (self.ordner() / name).unlink(missing_ok=True)
        logger.info('Mesh-3D %s: Netzansicht fertig (%d Dreiecke, %.1f MB)', self.kennung, flaechen, self.pfad().stat().st_size / 1e6)
        return flaechen

    def fehler_merken(self, text):
        quelle = self.quelle()
        self.ordner().mkdir(parents=True, exist_ok=True)
        (self.ordner() / self.FEHLER).write_text(json.dumps({'text': str(text)[:400], 'stempel': self.stempel(quelle) if quelle else None}), encoding='utf-8')
        (self.ordner() / self.BAUT).unlink(missing_ok=True)

    @classmethod
    def vereinfachen(cls, quelle, ziel, flaechen=None, farben=True, vorstufe=False):
        """Das Netz `quelle` (GLB, mit seinen Knoten-Transformationen) auf `flaechen` Dreiecke (Vorgabe `ZIEL_FLAECHEN`) vereinfachen und als GLB nach `ziel` schreiben → `(Dreiecke, Punkte)`.
        Koordinaten bleiben die des Originals. `farben`: die Farbe je Punkt aus der Textur mitnehmen (die Ansicht braucht sie, das Abstimm-Netz der Segmentierung nicht).
        `vorstufe`: bei einem Netz über `VORSTUFE_AB` Dreiecken erst eine Gitter-Vereinfachung (O(n), 3 s), dann die quadratische Kantenreduktion auf dem Rest."""
        import numpy as np
        import pymeshlab
        import trimesh

        szene = trimesh.load(str(quelle), process=False)
        netz = szene.to_geometry() if isinstance(szene, trimesh.Scene) else szene
        ziel_flaechen = int(flaechen or cls.ZIEL_FLAECHEN)
        if len(netz.faces) <= ziel_flaechen:
            kleines = netz
        else:
            punkt_farben = {'v_color_matrix': np.asarray(netz.visual.to_color().vertex_colors, dtype=np.float64) / 255.0} if farben else {}

            def neues_netz():
                return pymeshlab.Mesh(vertex_matrix=np.asarray(netz.vertices, dtype=np.float64), face_matrix=np.asarray(netz.faces, dtype=np.int32), **punkt_farben)

            ms = pymeshlab.MeshSet()
            ms.add_mesh(neues_netz())
            if vorstufe and len(netz.faces) > cls.VORSTUFE_AB:
                ms.meshing_decimation_clustering(threshold=pymeshlab.PercentageValue(cls.VORSTUFE_PROZENT))
                if ms.current_mesh().face_number() < ziel_flaechen:
                    # Das Gitter war für dieses Netz zu grob (weniger Dreiecke als das Ziel): ohne Vorstufe von vorn.
                    ms.clear()
                    ms.add_mesh(neues_netz())
            ms.meshing_decimation_quadric_edge_collapse(targetfacenum=ziel_flaechen, preserveboundary=True, preservenormal=True, optimalplacement=True)
            m = ms.current_mesh()
            rgba = (np.clip(m.vertex_color_matrix(), 0, 1) * 255).astype(np.uint8) if farben else None
            kleines = trimesh.Trimesh(vertices=m.vertex_matrix(), faces=m.face_matrix(), vertex_colors=rgba, process=False)
        kleines.vertex_normals  # noqa: B018 — im Zwischenspeicher, damit der GLB-Schreiber sie mitnimmt (sonst schattiert three.js flach)
        teil = Path(str(ziel) + '.teil')
        kleines.export(str(teil), file_type='glb')
        os.replace(teil, ziel)
        return int(len(kleines.faces)), int(len(kleines.vertices))
