# -*- coding: utf-8 -*-
"""Gcstueckelauf — der GC-Stapellauf (`manage.py gcstuecke`) per Knopf.

WARUM (Edgar, 26.09.2026: „in einer vorherigen Session wurden alle GarmentCode
Standard Objekte als Genesis Assets gebacken... die müssten neu gebacken
werden, da die Drapierung von Garment Code anders ist" — „mach mit auf
/settings/kleider/ einen Button mit dem diese per script neu gebacken werden
können"): Die 171 GarmentCode-Stücke (`Genesis9/gcstuecke.py`, Konzept
`Docu/konzepte/2026-09-25_garmentcode-als-genesis-stuecke-konzept.md`) kamen
bisher nur ueber die Konsole (`manage.py gcstuecke`) zustande. Seit die
Bauart-Einstellung „Drapierung wie bei SMPL" / „Mit Nacharbeit"
(`garmentbauart.py`, 26.09.2026) in den Fingerabdruck jedes Stuecks einfliesst
(`G9gcstuecke.fingerabdruck`), gilt ein Grossteil der schon gebackenen Stuecke
als veraltet — ein Lauf OHNE `--neu` baut von selbst nur das neu, dessen
Fingerabdruck nicht mehr passt, alles andere ueberspringt er.

Der Lauf ist ein UNTERPROZESS wie bei `Figurvideo`/`Auftragsarbeiter`: er
braucht die GPU (`python10_Garment`) und dauert, je nachdem wie viel veraltet
ist, Minuten bis Stunden — weit ueber jede HTTP-Anfrage hinaus. Der Server
startet `manage.py gcstuecke_fortschritt`, merkt sich den Prozess
(`LaufendeProzesse`) und liest den Fortschritt aus einer Datei, die der
Unterprozess atomar fortschreibt. Nur ein Lauf gleichzeitig — ein zweiter
Start meldet, dass schon einer laeuft, statt sich die GPU zu teilen.
"""

import json
import logging
import os
import subprocess
import sys

from django.conf import settings

from .laufende_prozesse import LaufendeProzesse

logger = logging.getLogger('core')

__all__ = ['Gcstueckelauf']


class Gcstueckelauf:
    """Startet den GC-Stapellauf im Hintergrund und liest seinen Stand."""

    #: Schluessel in `LaufendeProzesse` — es gibt nur einen Lauf gleichzeitig.
    SCHLUESSEL = 'gcstuecke_lauf'

    @classmethod
    def _ordner(cls):
        ordner = os.path.join(str(settings.MEDIA_ROOT), 'gcstuecke_lauf')
        os.makedirs(ordner, exist_ok=True)
        return ordner

    @classmethod
    def _fortschritt_pfad(cls):
        return os.path.join(cls._ordner(), 'fortschritt.json')

    @classmethod
    def laeuft(cls):
        prozess = LaufendeProzesse.holen(cls.SCHLUESSEL)
        return prozess is not None and prozess.poll() is None

    # ----------------------------------------------------------------- Start

    @classmethod
    def starten(cls, neu=False):
        """Unterprozess starten. Wirft `ValueError`, wenn schon einer läuft.

        `neu`: auch Stücke bauen, deren Fingerabdruck noch passt (CLI `--neu`)
        — Edgar, 26.09.2026: „baue die neu, alle bitte", nicht nur die durch
        die Bauart-Einstellung veralteten."""
        if cls.laeuft():
            raise ValueError('Der GC-Stapellauf läuft schon.')
        ordner = cls._ordner()
        fortschritt = cls._fortschritt_pfad()
        try:
            os.remove(fortschritt)
        except OSError:
            pass
        manage_py = os.path.join(str(settings.BASE_DIR), 'manage.py')
        befehl = [sys.executable, manage_py, 'gcstuecke_fortschritt', '--fortschritt', fortschritt]
        if neu:
            befehl.append('--neu')
        # KEIN Fenster (`CREATE_NO_WINDOW`), auch wenn der Server aus einer
        # Konsole laeuft — wie bei `Figurvideo.starten`.
        flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        with open(os.path.join(ordner, 'lauf.log'), 'w', encoding='utf-8') as protokoll:
            prozess = subprocess.Popen(
                befehl, stdout=protokoll, stderr=subprocess.STDOUT,
                cwd=str(settings.BASE_DIR), creationflags=flags,
            )
        LaufendeProzesse.eintragen(cls.SCHLUESSEL, prozess)
        logger.info('Gcstueckelauf gestartet (PID %s, neu=%s)', prozess.pid, neu)

    # ------------------------------------------------------------------ Stand

    @classmethod
    def stand(cls):
        """Fortschritt aus der Datei, dazu ob der Prozess noch lebt."""
        pfad = cls._fortschritt_pfad()
        if not os.path.isfile(pfad):
            return {'gestartet': cls.laeuft(), 'geschafft': 0, 'gesamt': 0,
                    'zeile': '', 'fertig': False, 'fehler': None}
        with open(pfad, encoding='utf-8') as datei:
            stand = json.load(datei)
        stand['gestartet'] = True
        prozess = LaufendeProzesse.holen(cls.SCHLUESSEL)
        if prozess is not None and prozess.poll() is not None and not stand.get('fertig'):
            # Der Prozess ist weg, ohne sich abzumelden — abgestuerzt oder von
            # aussen beendet. Ohne diese Zeile stuende der Balken fuer immer
            # bei seinem letzten Wert (wie bei `Figurvideo.stand`).
            stand['fehler'] = stand.get('fehler') or (
                'Der Lauf endete ohne Ergebnis (Exit %s). Siehe lauf.log.' % prozess.returncode)
            stand['fertig'] = True
        if stand.get('fertig'):
            LaufendeProzesse.entfernen(cls.SCHLUESSEL)
        return stand

    @classmethod
    def stoppen(cls):
        return LaufendeProzesse.beenden(cls.SCHLUESSEL)
