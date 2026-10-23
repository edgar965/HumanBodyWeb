# -*- coding: utf-8 -*-
"""Mesh3daianimationswahl — die Standardanimation der Ergebnisfigur je Job und je Test von Mesh3D-AI (22.10.2026).

Edgar: „Mach die Standard Animation auf allen Jobs wieder rein, Testjob und trainings jobs, nur bei der Figur. So wie die Mesh-3D Jobs, mit der Standardanimation, playleiste, stop und pause usw.“
Dieselbe Wahl wie bei Mesh-3D (`Mesh3danimationswahl`: `animation.json` mit `{"bvh": "Kategorie/Name"}`, Vorgabe A_Results/DanceKurz, Prüfung gegen die BVH-Bibliothek, `fehlt` wenn die Datei
verschwunden ist) — nur liegt die Datei im Ordner des Jobs (`3DObjects/mesh3dai/<ordner>/`) bzw. des Tests (`_test/<kennung>/`), nicht im Importordner von Mesh-3D. Den Retarget rechnet der Browser über
denselben Endpunkt wie die Charakter-Seite (`/api/retarget/`, Ziel `genesis9`, Regler der Figur).

    Mesh3daianimationswahl.fuer_job(job_id) / .fuer_test(kennung) -> Mesh3daianimationswahl oder None
"""
from pathlib import Path
from types import SimpleNamespace

from .bvhverzeichnis import Bvhverzeichnis
from .mesh3danimationswahl import Mesh3danimationswahl

__all__ = ['Mesh3daianimationswahl']


class Mesh3daianimationswahl(Mesh3danimationswahl):
    def __init__(self, ordner, name, verzeichnis=None):
        # `Mesh3danimationswahl` liest nur `ablage.ordner()` (Ort der Datei) und `ablage.kennung` (Logzeile) — derselbe Vertrag, ein anderer Ordner.
        self.ablage = SimpleNamespace(kennung='Mesh3D-AI %s' % name, ordner=lambda: Path(ordner))
        self.verzeichnis = verzeichnis or Bvhverzeichnis()

    @classmethod
    def fuer_job(cls, job_id):
        from .mesh3daiattrappe import Mesh3daiattrappe
        from .mesh3daidatensatz import Mesh3daidatensatz

        job = Mesh3daiattrappe.job(job_id)
        if job is None:
            return None
        ordner = Mesh3daidatensatz.ordner(job['ordner'])
        return cls(ordner, job['id']) if ordner.is_dir() else None

    @classmethod
    def fuer_test(cls, kennung):
        from .mesh3daitest import Mesh3daitest

        ordner = Mesh3daitest.pfad(kennung)
        return cls(ordner, 'test %s' % kennung) if ordner is not None else None

    def antwort(self):
        """Was die Seite braucht: Zustand der Wahl und die Kategorien der Bibliothek (`/api/animationen/<kategorie>/` liefert die Einträge)."""
        return {**self.zustand(), 'kategorien': self.kategorien()}
