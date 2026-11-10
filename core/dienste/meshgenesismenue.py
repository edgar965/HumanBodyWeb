# -*- coding: utf-8 -*-
"""Meshgenesismenue — die Jobs von Mesh-Genesis als Einträge im Menü der Seitenleiste (14.10.2026).

Edgar: „Ein selbst aufgebautes Menü würde eine Änderung an djangoBase brauchen … mach das." Die Gruppe Dashboard → Mesh-Genesis steht in `ui/settings/djangobase_menue.py` mit „Alle Jobs" und der Marke
`'dynamisch': 'meshgenesis_jobs'`; djangoBase ruft bei jedem Anzeigen den `menu_provider` (`DJANGOBASE['menu_provider']`, `djangobase/context_processors.py`), und der hängt hier je Job einen Eintrag an
die Gruppe mit dieser Marke. Dieselbe Quelle wie die Jobtabelle (`Meshgenesisattrappe.stammdaten()`): ein neuer Job erscheint in Tabelle, Menü und unter `/mesh-genesis/<job>/` zugleich.

Läuft auf JEDER Seite der Anwendung, nicht nur unter `/mesh-genesis/` — darum nur die Stammdaten (Kennung, Name), keine Zahlen, kein Verzeichnislauf.
Das feste Menü (`MENUE`) wird nie verändert, es entstehen Kopien.
"""

from .meshgenesisattrappe import Meshgenesisattrappe

__all__ = ['Meshgenesismenue', 'menue_erweitern']


class Meshgenesismenue:
    MARKE = 'meshgenesis_jobs'
    ICON = 'bi-person-standing-dress'

    @classmethod
    def erweitern(cls, menue, request=None):
        """Das Menü mit den Jobs; `menue` selbst bleibt unverändert."""
        jobs = [cls.eintrag(j) for j in Meshgenesisattrappe.stammdaten()]
        return cls._durchgehen(menue, jobs)

    @classmethod
    def eintrag(cls, job):
        return {'label': job['name'], 'icon': cls.ICON, 'url': '/mesh-genesis/%s/' % job['id']}

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
menue_erweitern = Meshgenesismenue.erweitern
