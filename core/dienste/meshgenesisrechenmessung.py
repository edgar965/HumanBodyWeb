# -*- coding: utf-8 -*-
"""Meshgenesisrechenmessung — was ein Schritt der Ketten wirklich gekostet hat (06.11.2026, Edgar: „alles auf GPU, VRAM in einem Job? wo kann man die performacne noch verbessern“).

Bis dahin stand je Schritt nur `dauer_s` in `stand.json`, und darin steckt das Warten auf die Karte (`zeile1`: n2 31 s ohne Warten, durant 245 s mit Warten). Eine VRAM-Spitze je Schritt gab es
für keine Kette; `laufmesser.py` stammt vom 20.10.2026 und misst je Prozess.

Die Messung läuft im Arbeitsprozess neben dem Schritt und ändert am Rechencode nichts:
    Karte    ein `nvidia-smi --loop-ms`: Auslastung und belegter Speicher der GANZEN Karte (je Prozess meldet nvidia-smi unter WDDM `[N/A]`). Rechnet daneben ein anderer Lauf, steckt er mit
             in den Zahlen. Während des Wartens wird nicht gezählt.
    CPU      `psutil`: Nutzer- plus Systemzeit aller Fäden des rechnenden Prozesses (Skriptdienst oder eigener Prozess) und seiner Kinder: Unter Windows ist `Scripts\\python.exe` einer venv nur ein
             Starter, der Interpreter läuft als Kind (PSHuman meldete sonst 0,0 s). `cpu_s` über `rechen_s` ≈ Zahl der belegten Kerne.
    Warten   aus den Zeilen der GPU-Sperre: „wartet auf einen Platz“ bis „gehalten:“.

    with Meshgenesisrechenmessung() as messung:
        messung.prozess_holen = lambda: pid
        messung.zeile(text)
    eintrag.update(messung.bericht(dauer_s))
"""
import contextlib
import shutil
import subprocess
import threading
import time

import psutil

__all__ = ['Meshgenesisrechenmessung']


class Meshgenesisrechenmessung:
    TAKT_MS = 1000
    WARTET, GEHALTEN = 'wartet auf einen Platz', 'gehalten: '
    SMI = r'C:\Windows\System32\nvidia-smi.exe'

    def __init__(self):
        self.prozess_holen = None           # () → PID des rechnenden Prozesses oder None; der Skriptdienst kann während des Schritts neu starten
        self.warte_s = 0.0
        self.auslastung, self.speicher_mb = [], []
        self._wartet_seit, self._smi, self._leser = None, None, None
        self._cpu = {}                      # PID → [erster Wert, letzter Wert]
        self._dienst = {}                   # `vram_*` des Skriptdienstes: dieser Prozess allein, ohne andere Läufe auf der Karte

    def __enter__(self):
        befehl = [shutil.which('nvidia-smi') or self.SMI, '--query-gpu=utilization.gpu,memory.used', '--format=csv,noheader,nounits', '--loop-ms=%d' % self.TAKT_MS]
        try:
            self._smi = subprocess.Popen(befehl, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except OSError:                     # eine Messung hält nie einen Lauf auf; ohne Karte fehlen die Zahlen
            return self
        self._leser = threading.Thread(target=self._lesen, daemon=True)
        self._leser.start()
        return self

    def __exit__(self, *_ausnahme):
        if self._smi is not None:
            with contextlib.suppress(OSError):
                self._smi.terminate()
            self._leser.join(timeout=3)
        return False

    def _lesen(self):
        for zeile in self._smi.stdout:
            self.probe(zeile)

    def probe(self, zeile):
        """Eine Zeile von nvidia-smi („87, 12034“); CPU wird im selben Takt gelesen, denn am Ende kann der Prozess fort sein."""
        self._cpu_lesen()
        if self._wartet_seit is not None:
            return
        try:
            auslastung, speicher = (float(x) for x in zeile.split(','))
        except ValueError:                  # „[N/A]“, leere Zeile beim Beenden
            return
        self.auslastung.append(auslastung)
        self.speicher_mb.append(speicher)

    def _cpu_lesen(self):
        pid = self.prozess_holen() if self.prozess_holen else None
        if not pid:
            return
        try:
            wurzel = psutil.Process(int(pid))
            kinder = wurzel.children(recursive=True)
        except (psutil.Error, ValueError):
            return
        for prozess, start in [(wurzel, None)] + [(k, 0.0) for k in kinder]:         # ein Kind beginnt im Schritt, der Dienst läuft schon länger
            try:
                zeiten = prozess.cpu_times()
            except psutil.Error:
                continue
            wert = zeiten.user + zeiten.system
            self._cpu.setdefault(prozess.pid, [wert if start is None else start, wert])[1] = wert

    def dienst(self, ergebnis):
        """Ergebnis des Skriptdienstes (`Skriptdienst._speicher`): VRAM dieses Prozesses, genauer als die ganze Karte."""
        self._dienst = {k: v for k, v in (ergebnis or {}).items() if k.startswith('vram_')}

    def zeile(self, text, jetzt=None):
        """Jede Ausgabezeile des Schritts; nur die der GPU-Sperre zählen."""
        jetzt = time.perf_counter() if jetzt is None else jetzt
        if self.WARTET in text:
            self._wartet_seit = self._wartet_seit or jetzt
        elif self.GEHALTEN in text and self._wartet_seit is not None:
            self.warte_s += jetzt - self._wartet_seit
            self._wartet_seit = None

    def bericht(self, dauer_s):
        """Felder für den Eintrag des Schritts in `stand.json`. Ohne Proben fehlen die Felder der Karte, statt 0 zu behaupten."""
        warte = min(self.warte_s, dauer_s)
        aus = {'warte_s': round(warte, 1), 'rechen_s': round(dauer_s - warte, 1)}
        if self._cpu:
            aus['cpu_s'] = round(sum(b - a for a, b in self._cpu.values()), 1)
        if self.auslastung:
            aus.update(karte_pct=round(sum(self.auslastung) / len(self.auslastung), 1), vram_spitze_gb=round(max(self.speicher_mb) / 1024.0, 2), vram_grund_gb=round(min(self.speicher_mb) / 1024.0, 2))
        return dict(aus, **self._dienst)
