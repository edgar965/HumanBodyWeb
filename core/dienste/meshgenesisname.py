# -*- coding: utf-8 -*-
"""Meshgenesisname — den Namen eines Jobs oder Tests von Mesh-Genesis auf seiner Seite ändern (19.10.2026).

Edgar: „ich möchte diese Jobs umbenennen können, so wie … der Stift auf /mesh-3D/<auftrag>/“ und „auch die testjobs /mesh-3D-AI/test/edgar/“. Vorne ist es derselbe Stift wie bei Mesh-3D und den
Aufträgen (`gemeinsam/auftragname.js`: Klick auf Namen oder Stift, Enter speichert, Escape nimmt zurück); die Endpunkte stehen in `core/api/meshgenesisname.py`.

**Der Name ist Beschriftung, kein Schlüssel.** Kennung (Adresse `/mesh-genesis/<job>/`; auf Foto-Genesis folgt die Adresse dem Namen, `Fotogenesisadresse`), Ordner des Datensatzes und Modell (`modell`: Rig und Häutung) bleiben; was ein Job sonst an Namen trägt, kommt
aus dem Code (`Meshgenesisattrappe.STAMMDATEN`), aus `paar.json` (`ProjektTemp/_wegwerf/meshgenesis_paar_job.py`) oder aus `test.json` (`meshgenesis_test_rechnen.py`). Alle drei schreibt ein Bau neu —
deshalb steht der eigene Name in einer eigenen Datei `name.json` im Ordner des Jobs bzw. Tests, die kein Lauf schreibt (wie `Mesh3dname` bei Mesh-3D), und wird beim Lesen darübergelegt.
Wer den Namen auf den ursprünglichen zurückstellt, löscht die Datei.

    Meshgenesisname.jobs(stammdaten)      -> dieselben Zeilen, `name` = eigener Name oder der ursprüngliche, `name_vorgabe` = der ursprüngliche
    Meshgenesisname.lesen(ordner)         -> eigener Name oder None
    Meshgenesisname.setzen(ordner, text, vorgabe) -> der gespeicherte Name; ValueError bei leerem Text

`jobs` läuft auf JEDER Seite der Anwendung (Menü, `Meshgenesismenue`) — gemerkt für `FRIST_S`, nach jedem `setzen` sofort neu gelesen.
"""

import json
import logging
import time
from pathlib import Path

from django.conf import settings

from ..atomic_write import AtomarSchreiber

logger = logging.getLogger('core')

__all__ = ['Meshgenesisname']


class Meshgenesisname:
    DATEI = 'name.json'
    #: Wie `Auftragsnameendpunkte.LAENGE` und `maxLength` des Feldes in `auftragname.js`.
    LAENGE = 200
    FRIST_S = 30.0
    _ablage = {}

    @staticmethod
    def wurzel():
        return Path(settings.OBJECTS_ROOT) / 'meshgenesis'

    @classmethod
    def saeubern(cls, text):
        """Leerraum am Rand weg, Zeilenumbrüche und Mehrfach-Leerzeichen zu einem; höchstens `LAENGE` Zeichen."""
        return ' '.join(str(text or '').split())[:cls.LAENGE]

    @classmethod
    def lesen(cls, ordner):
        try:
            daten = json.loads((Path(ordner) / cls.DATEI).read_text(encoding='utf-8'))
        except FileNotFoundError:
            return None
        except (OSError, ValueError) as fehler:
            logger.warning('Meshgenesisname: %s nicht lesbar (%s) — es gilt der ursprüngliche Name', Path(ordner) / cls.DATEI, fehler)
            return None
        if not isinstance(daten, dict):
            return None
        return cls.saeubern(daten.get('name')) or None

    @classmethod
    def jobs(cls, stammdaten):
        gemerkt = cls._ablage.get('jobs')
        if gemerkt is None or time.monotonic() - gemerkt['zeit'] > cls.FRIST_S:
            gemerkt = cls._ablage['jobs'] = {'zeit': time.monotonic(), 'namen': {}}
        namen = gemerkt['namen']
        for zeile in stammdaten:
            if zeile['ordner'] not in namen:
                namen[zeile['ordner']] = cls.lesen(cls.wurzel() / zeile['ordner'])
            zeile['name_vorgabe'] = zeile['name']
            zeile['name'] = namen[zeile['ordner']] or zeile['name']
        return stammdaten

    @classmethod
    def setzen(cls, ordner, text, vorgabe):
        name = cls.saeubern(text)
        if not name:
            raise ValueError('Der Name darf nicht leer sein')
        datei = Path(ordner) / cls.DATEI
        if name == vorgabe:
            datei.unlink(missing_ok=True)
        else:
            AtomarSchreiber.json_schreiben(datei, {'name': name, 'vorgabe': vorgabe, 'geaendert': time.strftime('%Y-%m-%dT%H:%M:%S')})
        cls._ablage.clear()
        return name
