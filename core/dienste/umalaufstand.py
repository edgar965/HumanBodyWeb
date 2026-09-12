# -*- coding: utf-8 -*-
u"""Der Stand eines UMA-Baulaufs — aus Auftragsordner, Ergebnisdatei und Log.

Herausgelöst aus `umabauer.py` (12.09.2026, 388 Zeilen; `stand` mit 16
Verzweigungen). `Umabauer` bleibt der Zugang (`Umabauer.stand(name)`), die
Klasse hier bekommt ihn als `bauer` gereicht und fragt dort nur nach Orten
und Lebenszeichen: `auftragsordner()`, `katalog()`, `logordner()`,
`bauer()`, `bauer_lebt()`, `startet()`, `_laeufe`.
"""
import json
import os
import time


class Umalaufstand:

    @staticmethod
    def merken(bauer, lauf):
        u"""Den Lauf neben dem Log ablegen: der Dev-Server lädt sich bei jeder
        Codeänderung neu und vergisst `_laeufe`, der Bauer arbeitet aber weiter."""
        pfad = os.path.join(bauer.logordner(), 'unity_%s.json' % lauf['name'])
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump({k: lauf[k] for k in ('name', 'rasse', 'start', 'log', 'gestartet')}, datei)

    @staticmethod
    def erinnern(bauer, name):
        pfad = os.path.join(bauer.logordner(), 'unity_%s.json' % name)
        if not os.path.isfile(pfad):
            return None
        with open(pfad, encoding='utf-8') as datei:
            return json.load(datei)

    @classmethod
    def stand(cls, bauer, name):
        u"""`None`, wenn kein Lauf dieses Namens bekannt ist."""
        lauf = bauer._laeufe.get(name) or cls.erinnern(bauer, name)
        if not lauf:
            return None
        ordner = bauer.auftragsordner()
        ergebnis = cls.ergebnis(os.path.join(ordner, name + '.ergebnis.json'), lauf['start'])
        wartet = os.path.isfile(os.path.join(ordner, name + '.auftrag.json'))
        laeuft, exit_code, meldung = cls._lage(bauer, lauf, ergebnis, wartet)
        datei = os.path.join(bauer.katalog(), name + '.glb')
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

    @classmethod
    def _lage(cls, bauer, lauf, ergebnis, wartet):
        u"""(läuft, exit, Meldung) — fertig, unterwegs, oder Unity ist weg."""
        if ergebnis is not None:
            meldung = ergebnis.get('zeiten') or cls.letzte_meldung(lauf['log'])
            return False, int(ergebnis.get('exit', 1)), meldung
        if bauer.bauer_lebt() or bauer.startet():
            zeichen = (bauer.bauer() or {}).get('stand') or 'startet'
            if wartet:
                return True, None, 'wartet auf den Bauer (%s)' % zeichen
            return True, None, 'Bauer %s · %s' % (zeichen, cls.letzte_meldung(lauf['log']))
        return (False, -1, 'Unity läuft nicht (mehr) — '
                + (cls.letzte_meldung(lauf['log']) or 'kein Log'))

    @staticmethod
    def ergebnis(pfad, start):
        u"""Das Ergebnis dieses Laufs — ein älteres gleichen Namens zählt nicht."""
        if not os.path.isfile(pfad) or os.path.getmtime(pfad) < start - 1:
            return None
        try:
            with open(pfad, encoding='utf-8') as datei:
                return json.load(datei)
        # stumm gewollt: das Ergebnis ist noch nicht geschrieben — der naechste Takt liest es
        except (OSError, ValueError):
            return None

    @staticmethod
    def letzte_meldung(log):
        u"""Die letzte Roomguest-Zeile aus Unitys Log — was der Exporter zuletzt sagte."""
        try:
            with open(log, encoding='utf-8', errors='replace') as datei:
                # „Roomguest:" mit Doppelpunkt — so beginnen die Meldungen des
                # Exporters; ohne ihn träfe auch Unitys Bauzeile der DLL.
                zeilen = [z.strip() for z in datei if 'Roomguest:' in z]
        # stumm gewollt: ohne Unity-Log gibt es keine letzte Meldung, nur einen leeren Text
        except OSError:
            return ''
        return zeilen[-1][:200] if zeilen else ''
