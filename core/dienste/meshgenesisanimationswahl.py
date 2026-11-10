# -*- coding: utf-8 -*-
"""Meshgenesisanimationswahl — die Standardanimation der Ergebnisfigur je Job und je Test von Mesh-Genesis (22.10.2026).

Edgar: „Mach die Standard Animation auf allen Jobs wieder rein, Testjob und trainings jobs, nur bei der Figur. So wie die Mesh-3D Jobs, mit der Standardanimation, playleiste, stop und pause usw.“
Dieselbe Wahl wie bei Mesh-3D (`Mesh3danimationswahl`: `animation.json` mit `{"bvh": "Kategorie/Name"}`, Vorgabe A_Results/DanceKurz, Prüfung gegen die BVH-Bibliothek, `fehlt` wenn die Datei
verschwunden ist) — nur liegt die Datei im Ordner des Jobs (`3DObjects/meshgenesis/<ordner>/`) bzw. des Tests (`_test/<kennung>/`), nicht im Importordner von Mesh-3D. Den Retarget rechnet der Browser über
denselben Endpunkt wie die Charakter-Seite (`/api/retarget/`, Ziel `genesis9`, Regler der Figur).

    Meshgenesisanimationswahl.fuer_job(job_id) / .fuer_test(kennung) -> Meshgenesisanimationswahl oder None
"""
from pathlib import Path
from types import SimpleNamespace

from .bvhverzeichnis import Bvhverzeichnis
from .mesh3danimationswahl import Mesh3danimationswahl

__all__ = ['Meshgenesisanimationswahl']


class Meshgenesisanimationswahl(Mesh3danimationswahl):
    def __init__(self, ordner, name, verzeichnis=None):
        # `Mesh3danimationswahl` liest nur `ablage.ordner()` (Ort der Datei) und `ablage.kennung` (Logzeile) — derselbe Vertrag, ein anderer Ordner.
        self.ablage = SimpleNamespace(kennung='Mesh-Genesis %s' % name, ordner=lambda: Path(ordner))
        self.verzeichnis = verzeichnis or Bvhverzeichnis()

    @classmethod
    def fuer_job(cls, job_id):
        from .meshgenesisattrappe import Meshgenesisattrappe
        from .meshgenesisdatensatz import Meshgenesisdatensatz

        job = Meshgenesisattrappe.job(job_id)
        if job is None:
            return None
        ordner = Meshgenesisdatensatz.ordner(job['ordner'])
        return cls(ordner, job['id']) if ordner.is_dir() else None

    @classmethod
    def fuer_test(cls, kennung):
        from .meshgenesistest import Meshgenesistest

        ordner = Meshgenesistest.pfad(kennung)
        return cls(ordner, 'test %s' % kennung) if ordner is not None else None

    def antwort(self):
        """Was die Seite braucht: Zustand der Wahl und die Kategorien der Bibliothek (`/api/animationen/<kategorie>/` liefert die Einträge)."""
        return {**self.zustand(), 'kategorien': self.kategorien()}
