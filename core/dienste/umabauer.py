# -*- coding: utf-8 -*-
u"""Umabauer — Unity baut auf Zuruf eine UMA-Figur in den Figurkatalog.

WARUM (06.09.2026, Edgar: „wo ist der Regler nach Typ (Elfe, Mann, Frau)?"):
Rasse und Kleidung einer UMA-Figur entstehen in Unity; der Browser kann das
Netz verformen, aber nicht neu zusammensetzen. Unity liegt auf diesem Rechner
(`settings.UNITY_EXE`) und läuft ohne Fenster.

AUFTRAGSMODUS (06.09.2026, Edgar: „du kannst den UnityEditor offen lassen"):
Der Start des Editors kostete 50 der 90 Sekunden je Figur. Deshalb bleibt er
offen: `Unity.exe -batchmode … -auftraege <ordner>` liest Aufträge
`<name>.auftrag.json` aus `logs/bauer/`, schreibt `<name>.ergebnis.json`
(exit, Zeiten je Schritt, Datei) und meldet sich alle zwei Sekunden in
`bauer.json` (pid, stand). Lebt kein Bauer, startet dieser Dienst einen; nach
zehn Minuten Leerlauf beendet er sich selbst und gibt das Projekt frei. Der
Exporter im UMA-Projekt (`Assets/Roomguest/Editor/UmaFigurExport.cs`) bleibt
die einzige Stelle, die baut; UMA selbst bleibt unberührt.

Aufträge stehen in einer Reihe, nichts geht verloren. Ein Lauf bleibt über
einen Neustart des Dev-Servers hinweg abfragbar (`unity_<name>.json`).
"""
import json
import logging
import os
import re
import subprocess
import time

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Umabauer', 'UmabauerFehlt']


class UmabauerFehlt(Exception):
    u"""Unity oder das UMA-Projekt fehlen am erwarteten Ort."""


class Umabauer:
    u"""Aufträge an den Unity-Bauer geben und ihren Stand melden."""

    METHODE = 'Roomguest3d.UmaFigurExport.Exportieren'
    NAME = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_\-]*$')
    RASSENDATEI = 'rassen.json'
    RASSENLAUF = 'rassenliste'
    BAUERLOG = 'unity_bauer.log'
    #: So alt darf das Lebenszeichen sein; der Bauer schreibt alle 2 s.
    FRISCH_S = 15
    #: Vorwärmen (06.09.2026): Der erste Bau nach einem Start kostet rund 90 s
    #: (Editor, Skripte, Rezept-Index, erster Export), jeder weitere 4–6 s.
    #: Deshalb startet der Bauer, sobald die Szene eine UMA-Figur zeigt, und
    #: baut einmal ins Leere — nach `logs/bauer/`, nie in den Katalog.
    WARMNAME = '_warm'
    WARMRASSE = 'Human Female 3.0'
    WARMDATEI = 'warm.glb'
    #: Geteilte Farben der Rasse, wie UMA sie nennt — Browser-Schlüssel → UMA-Name.
    FARBEN = {'haut': 'Skin', 'haar': 'Hair'}
    FARBWERT = re.compile(r'^#[0-9A-Fa-f]{6}$')

    _laeufe = {}
    _prozess = None

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
    def auftragsordner(cls):
        ordner = os.path.join(cls.logordner(), 'bauer')
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

    # ------------------------------------------------------------ Aufträge

    @classmethod
    def bauen(cls, rasse, name=None, zeiger=False, kleidung=None, farben=None):
        u"""Figur der Rasse bauen; `kleidung` = Rezeptnamen (sonst UMAs Vorgabe je
        Platz), `farben` = `{'haut': '#rrggbb', 'haar': '#rrggbb'}` (sonst die der Rasse)."""
        if not rasse or not rasse.strip():
            raise ValueError('Keine Rasse angegeben')
        name = name or cls.name_fuer(rasse)
        if not cls.NAME.match(name):
            raise ValueError('Ungültiger Name: %r' % (name,))
        auftrag = {'rasse': rasse, 'name': name, 'zeiger': 1 if zeiger else 0}
        if kleidung:
            if any(',' in r for r in kleidung):
                raise ValueError('Rezeptnamen dürfen kein Komma enthalten')
            auftrag['kleidung'] = ','.join(r.strip() for r in kleidung if r.strip())
        farbtext = cls._farbtext(farben)
        if farbtext:
            auftrag['farben'] = farbtext
        return cls._auftrag(name, auftrag, rasse=rasse)

    @classmethod
    def _farbtext(cls, farben):
        u"""`{'haut': '#e0b090'}` → `Skin=#e0b090`, wie der Exporter es liest; leer → ''."""
        if not farben:
            return ''
        if not isinstance(farben, dict):
            raise ValueError('farben muss ein Wörterbuch haut/haar → #rrggbb sein')
        teile = []
        for schluessel, wert in farben.items():
            if schluessel not in cls.FARBEN:
                raise ValueError('Unbekannte Farbe %r — erlaubt: %s'
                                 % (schluessel, ', '.join(cls.FARBEN)))
            if not wert:
                continue
            if not cls.FARBWERT.match(str(wert)):
                raise ValueError('Farbwert %r ist kein #rrggbb' % (wert,))
            teile.append('%s=%s' % (cls.FARBEN[schluessel], str(wert).lower()))
        return ','.join(teile)

    @classmethod
    def vorwaermen(cls):
        u"""Den Bauer starten und einmal ins Leere bauen, falls keiner lebt.

        Gibt `{'gestartet': bool, 'bauer': bauer_stand()}`. Lebt schon einer
        (oder startet gerade), passiert nichts — der Aufruf ist billig und
        darf bei jedem Öffnen der UMA-Eigenschaften kommen.
        """
        cls.pruefen()
        if cls.bauer_lebt() or (cls._prozess is not None and cls._prozess.poll() is None):
            return {'gestartet': False, 'bauer': cls.bauer_stand()}
        cls._auftrag(cls.WARMNAME, {
            'rasse': cls.WARMRASSE, 'name': cls.WARMNAME, 'zeiger': 0,
            'ziel': os.path.join(cls.auftragsordner(), cls.WARMDATEI),
        }, rasse=cls.WARMRASSE)
        return {'gestartet': True, 'bauer': cls.bauer_stand()}

    @classmethod
    def bauer_stand(cls):
        u"""`{'lebt', 'stand', 'startet', 'seit_s', 'pid'}` — was der Browser anzeigt."""
        zeichen = cls.bauer() or {}
        lebt = cls.bauer_lebt()
        startet = not lebt and cls._prozess is not None and cls._prozess.poll() is None
        return {
            'lebt': lebt,
            'stand': (zeichen.get('stand') or 'aus') if lebt else ('startet' if startet else 'aus'),
            'startet': startet,
            'seit_s': int(time.time() - float(zeichen.get('zeit') or time.time())) if lebt else None,
            'pid': zeichen.get('pid') if lebt else None,
        }

    @classmethod
    def rassen_ermitteln(cls):
        u"""Unity schreibt die Rassen (Name + verträgliche Rassen) nach `rassen.json`."""
        return cls._auftrag(cls.RASSENLAUF, {'name': cls.RASSENLAUF, 'rassenliste': cls.rassenpfad()})

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
    def _auftrag(cls, name, auftrag, rasse=None):
        u"""Auftragsdatei ablegen; den Bauer starten, falls keiner lebt."""
        cls.pruefen()
        ordner = cls.auftragsordner()
        os.makedirs(cls.katalog(), exist_ok=True)
        ergebnis = os.path.join(ordner, name + '.ergebnis.json')
        if os.path.isfile(ergebnis):
            os.remove(ergebnis)                         # ein alter Erfolg zählt nicht für diesen Lauf
        with open(os.path.join(ordner, name + '.auftrag.json'), 'w', encoding='utf-8') as datei:
            json.dump(auftrag, datei, ensure_ascii=False)
        gestartet = cls._bauer_sicherstellen()
        lauf = {'name': name, 'rasse': rasse, 'start': time.time(),
                'log': os.path.join(cls.logordner(), cls.BAUERLOG), 'gestartet': gestartet}
        cls._laeufe[name] = lauf
        cls._merken(lauf)
        logger.info('Umabauer: Auftrag %s abgelegt (%s)', name,
                    'Bauer neu gestartet' if gestartet else 'Bauer lebt')
        return cls.stand(name)

    @classmethod
    def _bauer_sicherstellen(cls):
        u"""Lebt ein Bauer (Lebenszeichen frisch) oder startet gerade einer? Sonst Unity starten."""
        if cls.bauer_lebt():
            return False
        if cls._prozess is not None and cls._prozess.poll() is None:
            return False                                # startet noch, Lebenszeichen kommt gleich
        log = os.path.join(cls.logordner(), cls.BAUERLOG)
        # `-leerlauf 0`: Der Editor bleibt offen (Edgar, 06.09.2026: „du kannst
        # den UnityEditor offen lassen") — sonst zahlt jede Pause den Neustart.
        # `UMA_BAUER_LEERLAUF_S` in den Einstellungen setzt eine Frist.
        leerlauf = int(getattr(settings, 'UMA_BAUER_LEERLAUF_S', 0) or 0)
        befehl = [cls.unity(), '-batchmode', '-projectPath', cls.projekt(),
                  '-executeMethod', cls.METHODE, '-logFile', log,
                  '-auftraege', cls.auftragsordner(), '-leerlauf', str(leerlauf)]
        cls._prozess = subprocess.Popen(befehl)
        logger.info('Umabauer: Unity-Bauer gestartet (pid %s): %s', cls._prozess.pid, ' '.join(befehl))
        return True

    # ------------------------------------------------------------ Bauer

    @classmethod
    def bauer(cls):
        u"""Das Lebenszeichen `bauer.json` — `None`, wenn keines da ist."""
        pfad = os.path.join(cls.auftragsordner(), 'bauer.json')
        try:
            with open(pfad, encoding='utf-8') as datei:
                return json.load(datei)
        except (OSError, ValueError):
            return None

    @classmethod
    def bauer_lebt(cls):
        zeichen = cls.bauer()
        if not zeichen or zeichen.get('stand') == 'beendet':
            return False
        if time.time() - float(zeichen.get('zeit') or 0) > cls.FRISCH_S:
            return False
        return cls._prozess_lebt(zeichen.get('pid'))

    @staticmethod
    def _prozess_lebt(pid):
        u"""Windows: läuft der Prozess noch? (`GetExitCodeProcess` → 259 = STILL_ACTIVE)"""
        if not pid:
            return False
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

    # ------------------------------------------------------------ Stand

    @classmethod
    def _merken(cls, lauf):
        u"""Den Lauf neben dem Log ablegen: der Dev-Server lädt sich bei jeder
        Codeänderung neu und vergisst `_laeufe`, der Bauer arbeitet aber weiter."""
        pfad = os.path.join(cls.logordner(), 'unity_%s.json' % lauf['name'])
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump({k: lauf[k] for k in ('name', 'rasse', 'start', 'log', 'gestartet')}, datei)

    @classmethod
    def _erinnern(cls, name):
        pfad = os.path.join(cls.logordner(), 'unity_%s.json' % name)
        if not os.path.isfile(pfad):
            return None
        with open(pfad, encoding='utf-8') as datei:
            return json.load(datei)

    @classmethod
    def stand(cls, name):
        u"""`None`, wenn kein Lauf dieses Namens bekannt ist."""
        lauf = cls._laeufe.get(name) or cls._erinnern(name)
        if not lauf:
            return None
        ordner = cls.auftragsordner()
        ergebnis = cls._ergebnis(os.path.join(ordner, name + '.ergebnis.json'), lauf['start'])
        wartet = os.path.isfile(os.path.join(ordner, name + '.auftrag.json'))
        bauer = cls.bauer() or {}
        if ergebnis is not None:
            laeuft, exit_code = False, int(ergebnis.get('exit', 1))
            meldung = ergebnis.get('zeiten') or cls._letzte_meldung(lauf['log'])
        elif cls.bauer_lebt() or (cls._prozess is not None and cls._prozess.poll() is None):
            laeuft, exit_code = True, None
            if wartet:
                meldung = 'wartet auf den Bauer (%s)' % (bauer.get('stand') or 'startet')
            else:
                meldung = 'Bauer %s · %s' % (bauer.get('stand') or 'startet',
                                             cls._letzte_meldung(lauf['log']))
        else:
            laeuft, exit_code = False, -1
            meldung = 'Unity läuft nicht (mehr) — ' + (cls._letzte_meldung(lauf['log']) or 'kein Log')
        datei = os.path.join(cls.katalog(), name + '.glb')
        fertig = (exit_code == 0 and os.path.isfile(datei)
                  and os.path.getmtime(datei) >= lauf['start'] - 1)
        return {
            'name': name,
            'rasse': lauf['rasse'],
            'laeuft': laeuft,
            'wartet': wartet,
            'exit': exit_code,
            'sekunden': int(time.time() - lauf['start']),
            'datei': name + '.glb' if fertig else None,
            'log': os.path.basename(lauf['log']),
            'meldung': meldung,
        }

    @staticmethod
    def _ergebnis(pfad, start):
        u"""Das Ergebnis dieses Laufs — ein älteres gleichen Namens zählt nicht."""
        if not os.path.isfile(pfad) or os.path.getmtime(pfad) < start - 1:
            return None
        try:
            with open(pfad, encoding='utf-8') as datei:
                return json.load(datei)
        except (OSError, ValueError):
            return None

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
