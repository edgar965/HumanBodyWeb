# -*- coding: utf-8 -*-
"""Mesh3daimenue — die Jobs von Mesh3D-AI als Einträge im Menü der Seitenleiste (14.10.2026).

Edgar: „Ein selbst aufgebautes Menü würde eine Änderung an djangoBase brauchen … mach das." Die Gruppe Dashboard → Mesh3D-AI steht in `ui/settings/djangobase_menue.py` mit „Alle Jobs" und der Marke
`'dynamisch': 'mesh3dai_jobs'`; djangoBase ruft bei jedem Anzeigen den `menu_provider` (`DJANGOBASE['menu_provider']`, `djangobase/context_processors.py`), und der hängt hier je Job einen Eintrag an
die Gruppe mit dieser Marke. Dieselbe Quelle wie die Jobtabelle (`Mesh3daiattrappe.stammdaten()`): ein neuer Job erscheint in Tabelle, Menü und unter `/mesh-3D-AI/<job>/` zugleich.

Läuft auf JEDER Seite der Anwendung, nicht nur unter `/mesh-3D-AI/` — darum nur die Stammdaten (Kennung, Name), keine Zahlen, kein Verzeichnislauf.
Das feste Menü (`MENUE`) wird nie verändert, es entstehen Kopien.
"""

from .mesh3daiattrappe import Mesh3daiattrappe

__all__ = ['Mesh3daimenue', 'menue_erweitern']


class Mesh3daimenue:
    MARKE = 'mesh3dai_jobs'
    ICON = 'bi-person-standing-dress'

    @classmethod
    def erweitern(cls, menue, request=None):
        """Das Menü mit den Jobs; `menue` selbst bleibt unverändert."""
        jobs = [cls.eintrag(j) for j in Mesh3daiattrappe.stammdaten()]
        return cls._durchgehen(menue, jobs)

    @classmethod
    def eintrag(cls, job):
        return {'label': job['name'], 'icon': cls.ICON, 'url': '/mesh-3D-AI/%s/' % job['id']}

    @classmethod
    def _durchgehen(cls, eintraege, jobs):
        """Kopie der Liste; wo ein Eintrag die Marke trägt, kommen die Jobs hinter sein festes Untermenü."""
        raus = []
        for eintrag in eintraege:
            if isinstance(eintrag, dict) and eintrag.get('untermenu'):
                eintrag = dict(eintrag)
                kinder = cls._durchgehen(eintrag['untermenu'], jobs)
                if eintrag.get('dynamisch') == cls.MARKE:
                    kinder = kinder + jobs
                eintrag['untermenu'] = kinder
            raus.append(eintrag)
        return raus


#: Für `DJANGOBASE['menu_provider']`: djangoBase löst den Eintrag mit `import_string` auf, und der zerlegt am letzten Punkt — eine Klassenmethode ginge so nicht.
menue_erweitern = Mesh3daimenue.erweitern
