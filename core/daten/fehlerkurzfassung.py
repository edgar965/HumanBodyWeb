# -*- coding: utf-8 -*-
u"""Fehlerkurzfassung — aus einem Traceback die eine Zeile, die etwas sagt.

WARUM EIGENE KLASSE (29.08.2026, Befund `code-qualitaet`): `error_summary`
auf `BVHJob` hatte Rang C — acht Verzweigungen in einer Eigenschaft, die eine
Zeichenkette liefert. Die Verzweigungen sind nicht überflüssig, sie
beantworten vier verschiedene Fragen; sie standen nur alle übereinander.

WAS DIE KURZFASSUNG LEISTEN MUSS
================================
Die Fehlermeldung eines Auftrags ist oft ein ganzer Traceback aus einem
Unterprozess. In der Auftragsliste ist dafür eine Zeile Platz. Gesucht ist
die LETZTE Zeile der Bauart ``Fehlertyp: Text`` — Python schreibt sie ans
Ende, und bei verketteten Ausnahmen ist die letzte die, die wirklich
abgebrochen hat.

`File "...", line 42` sieht ihr zum Verwechseln ähnlich (auch mit
Doppelpunkt) und wird deshalb ausdrücklich übergangen.

DER VORSPANN ist alles vor dem Wort „Traceback": Die Pipeline schreibt dort
oft ihre eigene Einordnung („GVHMR-Lauf gescheitert"). Beides zusammen sagt
mehr als jedes für sich — deshalb wird zusammengesetzt, wenn es beides gibt.
"""


class Fehlerkurzfassung:
    """Eine Zeile aus einer Fehlermeldung, die ein Traceback enthalten kann."""

    #: Steht das im Text, ist es ein Traceback.
    MARKE = 'Traceback'

    #: Wenn sich nichts Besseres finden lässt.
    ERSATZ = 'Processing failed (traceback truncated)'

    @staticmethod
    def aus(meldung):
        """Die Kurzfassung — leer, wenn es keine Meldung gibt."""
        if not meldung:
            return ''
        if Fehlerkurzfassung.MARKE not in meldung:
            return meldung.split('\n')[0].strip()
        vorspann = (meldung.split(Fehlerkurzfassung.MARKE)[0]
                    .strip().rstrip(':').strip())
        fehlerzeile = Fehlerkurzfassung._fehlerzeile(meldung)
        if vorspann and fehlerzeile:
            return '%s: %s' % (vorspann, fehlerzeile)
        return vorspann or fehlerzeile or Fehlerkurzfassung.ERSATZ

    @staticmethod
    def _fehlerzeile(meldung):
        """Die LETZTE Zeile der Bauart ``Fehlertyp: Text`` — sonst leer.

        Von hinten gesucht: Bei verketteten Ausnahmen („During handling of
        the above exception …") ist die letzte die, die wirklich abgebrochen
        hat. `File "...", line 42` wird übergangen — sie sieht der gesuchten
        Zeile zum Verwechseln ähnlich.
        """
        for zeile in reversed(meldung.strip().splitlines()):
            gestrafft = zeile.strip()
            if not gestrafft or gestrafft.startswith('File '):
                continue
            if 'Error' in gestrafft and ':' in gestrafft:
                return gestrafft
        return ''
