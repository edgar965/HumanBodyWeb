# -*- coding: utf-8 -*-
"""ordnersuchefenster — Windows-Fenster „Ordner suchen", Ergebnis als JSON auf stdout.

Aufruf (aus `core/dienste/ordnersuche.py`):

    python ordnersuchefenster.py --start <Ordner> --titel <Text> --eltern <PID>

Ausgabe: eine Zeile `{"ordner": "<Pfad>"}`, leer bei Abbruch. Als eigener Prozess, weil
tkinter seinen Hauptfaden braucht und der Server Anfragen in Nebenfäden beantwortet.

Der Wächterfaden beendet das Fenster, sobald der Server endet (`~/.claude/rules/subprozesse.md`):
ohne ihn bliebe nach einem harten Neustart ein offenes Fenster ohne Abnehmer stehen.
"""

import argparse
import ctypes
import json
import os
import sys
import threading


def argumente():
    parser = argparse.ArgumentParser(prog='ordnersuchefenster')
    parser.add_argument('--start', default='')
    parser.add_argument('--titel', default='Ordner suchen')
    parser.add_argument('--eltern', type=int, default=0)
    return parser.parse_args()


def waechter(eltern_pid):
    """Wartet auf das Ende des Elternprozesses und beendet dann diesen."""
    if not eltern_pid or os.name != 'nt':
        return
    synchronize = 0x00100000
    handle = ctypes.windll.kernel32.OpenProcess(synchronize, False, eltern_pid)
    if not handle:
        return

    def warten():
        ctypes.windll.kernel32.WaitForSingleObject(handle, 0xFFFFFFFF)
        os._exit(0)

    threading.Thread(target=warten, daemon=True).start()


def startordner(roh):
    """Der nächste vorhandene Ordner auf dem Weg nach oben — das Fenster öffnet sonst irgendwo."""
    pfad = os.path.normpath(roh) if roh else ''
    while pfad and not os.path.isdir(pfad):
        oben = os.path.dirname(pfad)
        if oben == pfad:
            return ''
        pfad = oben
    return pfad


def main():
    a = argumente()
    waechter(a.eltern)
    import tkinter
    from tkinter import filedialog

    wurzel = tkinter.Tk()
    wurzel.withdraw()
    # Ganz oben: Das Fenster gehört einem Hintergrundprozess, Windows ließe es sonst hinter Chrome aufgehen.
    wurzel.attributes('-topmost', True)
    wurzel.update()
    gewaehlt = filedialog.askdirectory(parent=wurzel, initialdir=startordner(a.start) or None,
                                       title=a.titel, mustexist=False)
    wurzel.destroy()
    ordner = os.path.normpath(gewaehlt) if gewaehlt else ''
    sys.stdout.write(json.dumps({'ordner': ordner}) + '\n')
    sys.stdout.flush()


if __name__ == '__main__':
    main()
