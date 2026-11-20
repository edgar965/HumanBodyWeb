# -*- coding: utf-8 -*-
"""Meshgenesisformtrainingpapierkorb — gewählte Trainingsläufe und Formvarianten im Reiter „Formtraining“ auf `/mesh-genesis/` beiseitelegen (20.11.2026).

Edgar: „mach hier buttons zum löschen, die brauche ich doch nicht mehr, oder?“ (`/mesh-genesis/#formtraining`), dann „ja, alle“ auf „Löschknöpfe auch für die Formvarianten?“.
Wie `Meshgenesispapierkorb`: der Ordner wird VERSCHOBEN, nicht gelöscht — nach `3DObjects/_Output/MeshGenesisJobs/_beiseite/<JJJJ.MM.TT.HH.MM.SS>_geloescht/<art>/<Ordner>`.
Zurückholen = Ordner zurückschieben.

Nicht löschbar:
  * Trainingsläufe, die die Kette einsetzt: jeder Wert in `ki_fassungen.json` und in `Meshgenesiskifassungen.VORGABE` (die Vorgabe greift, wenn ein Eintrag der Datei fehlt) —
    Stand 20.11.2026 vorstufe, vorstufe_mia und formkopf; dieselben Namen stehen in `_vorstufe/gewaehlt.json`;
  * Trainingsläufe im Zustand „läuft“ (`Meshgenesisformtraining`), Formvarianten im Zustand „wird gerechnet“ (`Meshgenesisformvarianten`).
Die Formvarianten liest zur Laufzeit keine Kette (nur die Trainingsskripte und die Architekturseite, geprüft 20.11.2026 per Suche nach `Form\\d{3}`/`startswith('Form')`).
Gelöscht werden nur Namen, die die Liste kennt — kein Pfad aus der Anfrage.
"""
import json
import logging
import shutil
import time

from .meshgenesisformtraining import Meshgenesisformtraining
from .meshgenesisformvarianten import Meshgenesisformvarianten
from .meshgenesiskifassungen import Meshgenesiskifassungen
from .meshgenesispapierkorb import Meshgenesispapierkorb

logger = logging.getLogger('core')

__all__ = ['Meshgenesisformtrainingpapierkorb']


class Meshgenesisformtrainingpapierkorb:
    ARTEN = ('formtraining', 'formvarianten')

    @staticmethod
    def eingesetzt():
        """{Lauf: [wo er eingetragen ist]} — liest `ki_fassungen.json` ohne zu schreiben (anders als `Meshgenesiskifassungen.lesen`)."""
        try:
            gelesen = json.loads(Meshgenesiskifassungen.datei().read_text(encoding='utf-8'))
        except (OSError, ValueError):
            gelesen = {}
        datei = {k: v for k, v in (gelesen if isinstance(gelesen, dict) else {}).items() if isinstance(v, str) and v}
        aus = {}
        for schluessel, wert in datei.items():
            aus.setdefault(wert, []).append('ki_fassungen.json: %s' % schluessel)
        for schluessel, wert in Meshgenesiskifassungen.VORGABE.items():
            if isinstance(wert, str) and wert and datei.get(schluessel) != wert:
                aus.setdefault(wert, []).append('Vorgabe in Meshgenesiskifassungen, falls ki_fassungen.json ohne %s ist' % schluessel)
        return aus

    @classmethod
    def sperre(cls, lauf, eingesetzt):
        """Warum ein Lauf (aus `Meshgenesisformtraining.laeufe`) nicht gelöscht werden darf, sonst None."""
        if lauf['name'] in eingesetzt:
            return 'Setzt die Kette ein (%s)' % '; '.join(eingesetzt[lauf['name']])
        if lauf['zustand'] == 'läuft':
            return 'Läuft gerade'
        return None

    @staticmethod
    def sperre_variante(v):
        """Warum eine Formvariante (aus `Meshgenesisformvarianten.alle`) nicht gelöscht werden darf, sonst None."""
        return 'Wird gerade gerechnet (jüngste Datei unter 30 min alt)' if v['zustand'] == 'wird gerechnet' else None

    @classmethod
    def loeschen(cls, art, kennungen):
        """→ {'ziel': Ordner, 'ergebnis': [{kennung, ok, fehler?}]}; `art` aus `ARTEN`."""
        if art == 'formtraining':
            eingesetzt = cls.eingesetzt()
            bekannt, wurzel = {lf['name']: lf for lf in Meshgenesisformtraining.laeufe()}, Meshgenesisformtraining.ordner()
            sperre = lambda lf: cls.sperre(lf, eingesetzt)       # noqa: E731
        elif art == 'formvarianten':
            Meshgenesisformvarianten.leeren()                   # Zustand frisch von der Platte, nicht aus der 30-s-Ablage
            bekannt, wurzel, sperre = {v['name']: v for v in Meshgenesisformvarianten.alle()}, Meshgenesisformvarianten.ordner(), cls.sperre_variante
        else:
            raise ValueError('Unbekannte Art „%s“' % art)
        ziel = Meshgenesispapierkorb.ziel(time.strftime('%Y.%m.%d.%H.%M.%S'), art)
        ergebnis = []
        for k in map(str, kennungen):
            eintrag = bekannt.get(k)
            grund = 'nicht in der Liste' if eintrag is None else sperre(eintrag)
            if grund:
                ergebnis.append({'kennung': k, 'ok': False, 'fehler': grund})
                continue
            quelle = wurzel / k
            try:
                ziel.mkdir(parents=True, exist_ok=True)
                shutil.move(str(quelle), str(ziel / k))
                ergebnis.append({'kennung': k, 'ok': True})
                logger.info('Mesh-Genesis: %s „%s“ beiseitegelegt: %s → %s', art, k, quelle, ziel / k)
            except OSError as fehler:
                ergebnis.append({'kennung': k, 'ok': False, 'fehler': str(fehler)})
                logger.warning('Mesh-Genesis: %s „%s“ nicht verschoben: %s', art, k, fehler)
        if art == 'formvarianten':
            Meshgenesisformvarianten.leeren()
        return {'ziel': str(ziel), 'ergebnis': ergebnis}
