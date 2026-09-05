# -*- coding: utf-8 -*-
u"""Umabauer — Unity baut auf Zuruf eine UMA-Figur in den Figurkatalog.

WARUM (06.09.2026, Edgar: „wo ist der Regler nach Typ (Elfe, Mann, Frau)?"):
Rasse und Kleidung einer UMA-Figur entstehen in Unity; der Browser kann das
Netz verformen, aber nicht neu zusammensetzen. Unity liegt auf diesem Rechner
(`settings.UNITY_EXE`) und läuft ohne Fenster: Start 23 s (gemessen
05.09.2026), dazu Bau und Export. Der Exporter im UMA-Projekt
(`Assets/Roomguest/Editor/UmaFigurExport.cs`) nimmt `-rasse`, `-name`,
`-zeiger` und `-rassenliste`; UMA selbst bleibt unberührt.

Ein Lauf zur Zeit. Der Stand lebt im Prozess (kein Datenbankfeld), Unitys
Ausgabe in `logs/unity_<name>.log`. Der Aufrufer fragt den Stand ab, bis
`laeuft` falsch ist; dann liegt `<name>.glb` mit Zettel im Katalog — oder
`exit` ist nicht 0 und `meldung` sagt, woran es lag.
"""
import json
import logging
import os
import re
import subprocess
import threading
import time

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Umabauer', 'UmabauerFehlt', 'UmabauerBelegt']


class UmabauerFehlt(Exception):
    u"""Unity oder das UMA-Projekt fehlen am erwarteten Ort."""


class UmabauerBelegt(Exception):
    u"""Es läuft schon ein Unity-Lauf; erst warten."""


class Umabauer:
    u"""Startet Unity im Batchmodus und meldet den Stand je Lauf."""

    METHODE = 'Roomguest3d.UmaFigurExport.Exportieren'
    NAME = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_\-]*$')
    RASSENDATEI = 'rassen.json'
    RASSENLAUF = 'rassenliste'

    _schloss = threading.Lock()
    _laeufe = {}
    _aktiv = None

    # ------------------------------------------------------------ Orte

    @staticmethod
    def unity():
        return str(settings.UNITY_EXE)

    @staticmethod
    def projekt():
        return str(settings.UMA_PROJEKT)

    @staticmethod
    def katalog():
        return os.path.join(str(settings.FIGUREN_KATALOG), 'uma')

    @staticmethod
    def logordner():
        u"""`settings.UMA_BAU_LOGS`, sonst `logs/` des Projekts — Tests legen ihn um."""
        ordner = str(getattr(settings, 'UMA_BAU_LOGS', '') or os.path.join(str(settings.BASE_DIR), 'logs'))
        os.makedirs(ordner, exist_ok=True)
        return ordner

    @classmethod
    def rassenpfad(cls):
        return os.path.join(cls.katalog(), cls.RASSENDATEI)

    @classmethod
    def pruefen(cls):
        if not os.path.isfile(cls.unity()):
            raise UmabauerFehlt('Unity fehlt: %s' % cls.unity())
        if not os.path.isdir(cls.projekt()):
            raise UmabauerFehlt('UMA-Projekt fehlt: %s' % cls.projekt())

    @staticmethod
    def name_fuer(rasse):
        u"""Dateiname aus der Rasse: „Human Female 3.0" → `Uma_HumanFemale30`."""
        return 'Uma_' + re.sub(r'[^A-Za-z0-9]+', '', rasse or '')

    # ------------------------------------------------------------ Läufe

    @classmethod
    def bauen(cls, rasse, name=None, zeiger=False, kleidung=None):
        u"""Figur der Rasse bauen; `kleidung` = Rezeptnamen, sonst UMAs Vorgabe je Platz."""
        if not rasse or not rasse.strip():
            raise ValueError('Keine Rasse angegeben')
        name = name or cls.name_fuer(rasse)
        if not cls.NAME.match(name):
            raise ValueError('Ungültiger Name: %r' % (name,))
        args = ['-rasse', rasse, '-name', name]
        if zeiger:
            args += ['-zeiger', '1']
        if kleidung:
            if any(',' in r for r in kleidung):
                raise ValueError('Rezeptnamen dürfen kein Komma enthalten')
            args += ['-kleidung', ','.join(r.strip() for r in kleidung if r.strip())]
        return cls._starten(name, args, rasse=rasse)

    @classmethod
    def rassen_ermitteln(cls):
        u"""Unity schreibt die Namen aller Rassen nach `rassen.json` im Katalog."""
        return cls._starten(cls.RASSENLAUF, ['-rassenliste', cls.rassenpfad()])

    @classmethod
    def rassen(cls):
        u"""Rassennamen aus dem Katalog — `None`, solange Unity die Liste nicht geschrieben hat."""
        details = cls.rassen_details()
        return None if details is None else list(details)

    @classmethod
    def rassen_details(cls):
        u"""`{name: [verträgliche Rassen]}` aus `rassen.json`; die alte Fassung (nur Namen) gilt weiter."""
        pfad = cls.rassenpfad()
        if not os.path.isfile(pfad):
            return None
        with open(pfad, encoding='utf-8') as datei:
            eintraege = json.load(datei)
        details = {}
        for eintrag in eintraege:
            if isinstance(eintrag, dict):
                details[eintrag['name']] = [str(r) for r in eintrag.get('kompatibel') or []]
            else:
                details[str(eintrag)] = []
        return details

    @classmethod
    def _starten(cls, name, args, rasse=None):
        cls.pruefen()
        with cls._schloss:
            if cls._aktiv and cls._aktiv['prozess'].poll() is None:
                raise UmabauerBelegt('Unity baut gerade %s' % cls._aktiv['name'])
            os.makedirs(cls.katalog(), exist_ok=True)
            log = os.path.join(cls.logordner(), 'unity_%s.log' % name)
            befehl = [cls.unity(), '-batchmode', '-projectPath', cls.projekt(),
                      '-executeMethod', cls.METHODE, '-logFile', log] + args
            prozess = subprocess.Popen(befehl)
            lauf = {'name': name, 'rasse': rasse, 'start': time.time(),
                    'prozess': prozess, 'log': log, 'pid': prozess.pid}
            cls._laeufe[name] = lauf
            cls._aktiv = lauf
            cls._merken(lauf)
            logger.info('Umabauer: Unity gestartet (%s): %s', name, ' '.join(befehl))
        return cls.stand(name)

    @classmethod
    def _merken(cls, lauf):
        u"""Den Lauf neben dem Log ablegen: der Dev-Server lädt sich bei jeder
        Codeänderung neu und vergisst `_laeufe`, Unity läuft aber weiter (06.09.2026)."""
        with open(lauf['log'][:-4] + '.json', 'w', encoding='utf-8') as datei:
            json.dump({k: lauf[k] for k in ('name', 'rasse', 'start', 'log', 'pid')}, datei)

    @classmethod
    def _erinnern(cls, name):
        pfad = os.path.join(cls.logordner(), 'unity_%s.json' % name)
        if not os.path.isfile(pfad):
            return None
        with open(pfad, encoding='utf-8') as datei:
            lauf = json.load(datei)
        lauf['prozess'] = None
        return lauf

    @staticmethod
    def _prozess_lebt(pid):
        u"""Windows: läuft der Prozess noch? (`GetExitCodeProcess` → 259 = STILL_ACTIVE)"""
        import ctypes
        from ctypes import wintypes
        oeffnen = ctypes.windll.kernel32.OpenProcess
        oeffnen.restype = wintypes.HANDLE
        handle = oeffnen(0x1000, False, int(pid))       # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        try:
            code = wintypes.DWORD()
            ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
            return code.value == 259
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)

    @classmethod
    def stand(cls, name):
        u"""`None`, wenn kein Lauf dieses Namens bekannt ist."""
        lauf = cls._laeufe.get(name) or cls._erinnern(name)
        if not lauf:
            return None
        if lauf['prozess'] is not None:
            exit_code = lauf['prozess'].poll()
        else:
            # Lauf aus einem früheren Serverprozess: nur „lebt noch" oder „vorbei";
            # den Rückgabewert kennt niemand mehr, die Datei entscheidet.
            exit_code = None if cls._prozess_lebt(lauf['pid']) else 0
        datei = os.path.join(cls.katalog(), name + '.glb')
        # Nur eine Datei, die DIESER Lauf geschrieben hat, zählt — eine ältere
        # gleichen Namens bliebe sonst nach einem gescheiterten Lauf als Erfolg stehen.
        fertig = (exit_code == 0 and os.path.isfile(datei)
                  and os.path.getmtime(datei) >= lauf['start'] - 1)
        return {
            'name': name,
            'rasse': lauf['rasse'],
            'laeuft': exit_code is None,
            'exit': exit_code,
            'sekunden': int(time.time() - lauf['start']),
            'datei': name + '.glb' if fertig else None,
            'log': os.path.basename(lauf['log']),
            'meldung': cls._letzte_meldung(lauf['log']),
        }

    @staticmethod
    def _letzte_meldung(log):
        u"""Die letzte Roomguest-Zeile aus Unitys Log — was der Exporter zuletzt sagte."""
        try:
            with open(log, encoding='utf-8', errors='replace') as datei:
                # „Roomguest:" mit Doppelpunkt — so beginnen die Meldungen des
                # Exporters; ohne ihn träfe auch Unitys Bauzeile der DLL.
                zeilen = [z.strip() for z in datei if 'Roomguest:' in z]
        except OSError:
            return ''
        return zeilen[-1][:200] if zeilen else ''
