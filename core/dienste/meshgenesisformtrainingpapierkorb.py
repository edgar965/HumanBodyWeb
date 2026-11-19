# -*- coding: utf-8 -*-
"""Meshgenesisformtrainingpapierkorb — gewählte Trainingsläufe im Reiter „Formtraining“ auf `/mesh-genesis/` beiseitelegen (20.11.2026).

Edgar: „mach hier buttons zum löschen, die brauche ich doch nicht mehr, oder?“ (`/mesh-genesis/#formtraining`). Wie `Meshgenesispapierkorb`: der Ordner wird VERSCHOBEN, nicht gelöscht —
nach `3DObjects/_Output/MeshGenesisJobs/_beiseite/<JJJJ.MM.TT.HH.MM.SS>_geloescht/formtraining/<Lauf>`. Zurückholen = Ordner zurückschieben.

Nicht löschbar:
  * Läufe, die die Kette einsetzt: jeder Wert in `ki_fassungen.json` und in `Meshgenesiskifassungen.VORGABE` (die Vorgabe greift, wenn ein Eintrag der Datei fehlt) — Stand 20.11.2026
    vorstufe, vorstufe_mia und formkopf; dieselben Namen stehen in `_vorstufe/gewaehlt.json`;
  * Läufe im Zustand „läuft“ (`Meshgenesisformtraining`).
Gelöscht werden nur Namen, die die Liste kennt — kein Pfad aus der Anfrage.
"""
import json
import logging
import shutil
import time

from .meshgenesisformtraining import Meshgenesisformtraining
from .meshgenesiskifassungen import Meshgenesiskifassungen
from .meshgenesispapierkorb import Meshgenesispapierkorb

logger = logging.getLogger('core')

__all__ = ['Meshgenesisformtrainingpapierkorb']


class Meshgenesisformtrainingpapierkorb:
    ART = 'formtraining'

    @staticmethod
    def eingesetzt():
        """{Lauf: [Schlüssel der KI-Fassungen]} — liest `ki_fassungen.json` ohne zu schreiben (anders als `Meshgenesiskifassungen.lesen`)."""
        try:
            gelesen = json.loads(Meshgenesiskifassungen.datei().read_text(encoding='utf-8'))
        except (OSError, ValueError):
            gelesen = {}
        aus = {}
        for quelle in (Meshgenesiskifassungen.VORGABE, gelesen if isinstance(gelesen, dict) else {}):
            for schluessel, wert in quelle.items():
                if isinstance(wert, str) and wert and schluessel not in aus.setdefault(wert, []):
                    aus[wert].append(schluessel)
        return aus

    @classmethod
    def sperre(cls, lauf, eingesetzt):
        """Warum ein Lauf (aus `Meshgenesisformtraining.laeufe`) nicht gelöscht werden darf, sonst None."""
        if lauf['name'] in eingesetzt:
            return 'Setzt die Kette ein (ki_fassungen.json: %s)' % ', '.join(eingesetzt[lauf['name']])
        if lauf['zustand'] == 'läuft':
            return 'Läuft gerade'
        return None

    @classmethod
    def loeschen(cls, kennungen):
        """→ {'ziel': Ordner, 'ergebnis': [{kennung, ok, fehler?}]}"""
        laeufe = {lf['name']: lf for lf in Meshgenesisformtraining.laeufe()}
        eingesetzt = cls.eingesetzt()
        ziel = Meshgenesispapierkorb.ziel(time.strftime('%Y.%m.%d.%H.%M.%S'), cls.ART)
        ergebnis = []
        for k in map(str, kennungen):
            lauf = laeufe.get(k)
            grund = 'nicht in der Liste' if lauf is None else cls.sperre(lauf, eingesetzt)
            if grund:
                ergebnis.append({'kennung': k, 'ok': False, 'fehler': grund})
                continue
            quelle = Meshgenesisformtraining.ordner() / k
            try:
                ziel.mkdir(parents=True, exist_ok=True)
                shutil.move(str(quelle), str(ziel / k))
                ergebnis.append({'kennung': k, 'ok': True})
                logger.info('Mesh-Genesis: Trainingslauf „%s“ beiseitegelegt: %s → %s', k, quelle, ziel / k)
            except OSError as fehler:
                ergebnis.append({'kennung': k, 'ok': False, 'fehler': str(fehler)})
                logger.warning('Mesh-Genesis: Trainingslauf „%s“ nicht verschoben: %s', k, fehler)
        return {'ziel': str(ziel), 'ergebnis': ergebnis}
