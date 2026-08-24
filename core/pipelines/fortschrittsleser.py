# -*- coding: utf-8 -*-
"""Fortschrittsleser — aus MocapNETs Ausgabe einen Prozentwert machen.

Aus `_run_processing` herausgeloest (Umbau 15.08.2026). MocapNET schreibt je
Bild eine Zeile wie `Frame 50/125`; daraus entstehen Prozent, Bildrate und
Restzeit. Der Block stand mitten in einer 302-Zeilen-Funktion und war dort
nicht pruefbar — hier ist er es (siehe `zeile_lesen`).
"""
import time


class Fortschrittsleser:
    """Wandelt Ausgabezeilen in Fortschrittsangaben, gedrosselt auf 1/Sekunde."""

    #: Die 2D-Erkennung gilt als erste Haelfte; MocapNET faengt bei 50 % an.
    BASIS_PROZENT = 50
    SPANNE_PROZENT = 48
    OBERGRENZE = 98
    MINDESTABSTAND_S = 1.0

    def __init__(self, gesamt=0, jetzt=None):
        self.gesamt = gesamt or 0
        self.beginn = jetzt or time.time()
        self.letzte_meldung = 0.0

    # ------------------------------------------------------------------ lesen

    @staticmethod
    def zahlen_aus(zeile):
        """`Frame 50/125` -> (50, 125). None, wenn die Zeile nichts hergibt.

        Absichtlich nachsichtig: MocapNET schreibt `Frame`, `frame` und
        gelegentlich `Frames:` — und manchmal ohne Gesamtzahl."""
        teile = zeile.split()
        for i, teil in enumerate(teile):
            if not teil.lower().startswith('frame') or i + 1 >= len(teile):
                continue
            try:
                zahlen = teile[i + 1].replace(':', '').split('/')
                aktuell = int(zahlen[0])
                gesamt = int(zahlen[1]) if len(zahlen) > 1 else 0
                return aktuell, gesamt
            # stumm gewollt: Diese Klasse liest FREMDE Ausgabezeilen. „frame“ ohne
            # Zahl dahinter ist Text, kein Fehler; geloggt wäre es je Zeile einmal.
            except (ValueError, IndexError):
                return None
        return None

    def zeile_lesen(self, zeile, jetzt=None):
        """(prozent, text) oder None — None heisst „nichts zu melden".

        Gedrosselt: Bei 30 Bildern je Sekunde waeren es sonst 30 Datenbank-
        schreibvorgaenge je Sekunde."""
        if 'rame' not in zeile:
            return None
        jetzt = jetzt or time.time()
        if jetzt - self.letzte_meldung < self.MINDESTABSTAND_S:
            return None
        werte = self.zahlen_aus(zeile.strip())
        if not werte:
            return None
        aktuell, gesamt = werte
        gesamt = gesamt or self.gesamt
        if gesamt <= 0:
            return None
        self.letzte_meldung = jetzt

        prozent = self.BASIS_PROZENT + int((aktuell / gesamt) * self.SPANNE_PROZENT)
        vergangen = max(jetzt - self.beginn, 0.1)
        rate = aktuell / vergangen
        rest = int((gesamt - aktuell) / max(rate, 0.01))
        text = ('3D estimation: %d / %d frames — %.1f fps, ~%ds left'
                % (aktuell, gesamt, rate, rest))
        return min(prozent, self.OBERGRENZE), text
