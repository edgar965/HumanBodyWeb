# -*- coding: utf-8 -*-
"""Meshfigurnebenlauf — Schritte von „Mesh to 3D", die in einem Faden neben dem Hauptlauf rechnen (aus `Meshfigurlauf` herausgelöst, 12.10.2026: die Datei stand bei 301 Zeilen).

Ein Nebenlauf ist ein Schritt, der nur mit Dateien rechnet (CPU, kein Runner). Er arbeitet auf einer KOPIE des Auftrags — der Hauptfaden sichert `job.ergebnis` in die Datenbank, während der Faden schreibt —
und meldet nichts. Sein Ergebnis kommt erst beim Abwarten in den Auftrag; ein Fehler im Faden ist der Fehler des Schritts.

* „haar" und „kleidung" starten an ihrem Platz in `Meshfigurlauf.SCHRITTE` (nach der Erkennung) und verschwinden hinter den Ketten auf der GPU.
* „frisur" darf früher losgehen (`frueh`, 12.10.2026; `Meshfigurende.textur`, sonst `Meshfigurlauf.NACH_SCHRITT`): sobald der Runner der Textur die Figur mit Eigenmorph in `posiert.npy` festgelegt hat und `genesis_ende.npz`
  steht, rechnet die Frisurwahl neben dem Backen der Kacheln und der Vorschau (zusammen rund 85 s) statt hinter ihnen. Das setzt voraus, dass diese beiden Dateien danach nicht noch einmal anders geschrieben werden
  (`Meshfigurgenesis.speichern`, `_run_meshfigur._kette` lassen eine inhaltsgleiche Datei in Ruhe).
  Gemessen (Zauberer Kopie, Teile-Ablage warm): Frisur 99 s neben dem Backen (72 s allein neben der Vorschau, 114 s dahinter), die Textur bleibt bei 114 s. **Messfalle:** der erste Versuch zeigte 185 s und eine
  Textur von 134 s — die Ablage der 28 Frisuren (`G9teileablage`) war kalt, weil jede Änderung an `Genesis9/*.py` ihren Stempel entwertet; die Zeit war Neubau, nicht Streit um die Python-Sperre.
"""

import copy
import logging
import threading
import time

logger = logging.getLogger('core')

__all__ = ['Meshfigurnebenlauf']


class Meshfigurnebenlauf:
    @staticmethod
    def starten(lauf, name, fabrik):
        """Den Schritt `name` in einem Faden starten — mit einer Kopie des Auftrags (eigenes `ergebnis`) und ohne Fortschrittsmeldung.
        Gibt `(Faden, Kopie des Laufs, Ergebnis des Fadens)` zurück; `abwarten` übernimmt das Ergebnis."""
        kopie = copy.copy(lauf)
        kopie.job = copy.copy(lauf.job)
        kopie.job.ergebnis = dict(lauf.job.ergebnis)
        kopie.melden = lambda *args, **kwargs: None
        kopie.sichern = lambda *felder: None
        aus = {}

        def rechnen():
            t = time.perf_counter()
            try:
                fabrik(kopie)
            except BaseException as fehler:  # noqa: BLE001 — der Hauptfaden wirft ihn weiter, wenn er den Schritt abwartet
                aus['fehler'] = fehler
                logger.exception('Mesh to 3D %s: Schritt %s (Nebenlauf) gescheitert', lauf.job.kennung, name)
            aus['sekunden'] = round(time.perf_counter() - t, 1)

        faden = threading.Thread(target=rechnen, name='nebenlauf-' + name, daemon=True)
        faden.start()
        return faden, kopie, aus

    @staticmethod
    def abwarten(lauf, nebenlaeufe, namen):
        """Wartet auf die Nebenläufe `namen` und übernimmt ihr Ergebnis in `job.ergebnis` — ein Fehler des Fadens ist der Fehler des Schritts."""
        for name in namen:
            if name not in nebenlaeufe:
                continue
            faden, kopie, aus = nebenlaeufe.pop(name)
            faden.join()
            lauf.job.schritt = name
            if 'fehler' in aus:
                raise aus['fehler']
            if name in kopie.job.ergebnis:
                lauf.job.ergebnis[name] = kopie.job.ergebnis[name]
            lauf.job.ergebnis.setdefault('dauer', {})[name] = aus['sekunden']       # Zeit des Fadens, nicht der Wartezeit — sie überlappt mit den Ketten
            lauf.sichern('ergebnis')

    @classmethod
    def frueh(cls, lauf, name):
        """Den Nebenlauf `name` jetzt starten, vor seinem Platz in `SCHRITTE` (nur im Hauptfaden aufrufen). Wirkt nur im laufenden `ausfuehren` und nur für Nebenläufe dieses Laufs; läuft er schon, geschieht nichts.
        Was er lesen muss (`WARTEN_VOR`), wird vorher abgewartet — sein Ergebnis steht dann in der Kopie des Auftrags, die der Faden bekommt."""
        laufend = getattr(lauf, '_laufend', None)
        if laufend is None or name not in lauf.NEBENLAEUFIG:
            return False
        nebenlaeufe, fabriken = laufend
        if name in nebenlaeufe:
            return False
        schritt = lauf.job.schritt
        lauf._nebenlaeufe_abwarten(nebenlaeufe, lauf.WARTEN_VOR.get(name, ()))
        lauf.job.schritt = schritt                  # `abwarten` setzt den Schritt des Nebenlaufs; der Hauptfaden steht weiter in seinem
        nebenlaeufe[name] = cls.starten(lauf, name, fabriken[name])
        return True
