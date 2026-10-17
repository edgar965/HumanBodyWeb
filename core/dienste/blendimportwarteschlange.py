# -*- coding: utf-8 -*-
"""Blendimportwarteschlange — ein zweiter Import wartet, bis der erste fertig ist (14.10.2026).

Edgar: „Ich brauche keine Gaga-Meldung, sondern eine normale Meldung, dass der Job in eine Queue eingereiht wird" — bis dahin antworteten `starten` und `neu` mit 409 („Import … läuft noch — erst nach seinem
Ende starten"), sobald ein anderer Import rechnete, und der Nutzer musste selbst warten und noch einmal klicken. Zwei Importe zugleich teilen sich GPU („Mesh to 3D", Backen) und Kerne, also bleibt es bei EINEM
Rechner; der zweite wird eingereiht.

So geht es: Der Arbeitsprozess des eingereihten Imports startet sofort (`manage.py blendimport_fahren <kennung> --warten`), tut aber nichts, bis er an der Reihe ist. Im Stand steht in dieser Zeit
`status = laeuft` (alle Anzeigen behandeln ihn als laufend: Knöpfe gesperrt, „Anhalten" möglich), dazu `wartet = true`, `schritt = warteschlange`, `eingereiht` (Zeit) und ein Text, hinter wem er steht. Er zählt
NICHT als rechnend (`rechnender`): sonst würde er sich selbst aufhalten. An der Reihe ist, wer als Erster eingereiht wurde (`eingereiht`, dann Kennung), sobald kein anderer Import rechnet; der Wechsel von „wartet" zu „rechnet"
geschieht unter einer Sperrdatei im Importordner, damit zwei Wartende nie zugleich losrechnen. Ein Wartender, dessen Prozess nicht mehr lebt, zählt nicht mit (`Blendimportarbeiter.lebt`); wer angehalten wird, verlässt die Schlange.
"""

import os
import time
from contextlib import contextmanager

from django.utils import timezone

__all__ = ['Blendimportwarteschlange']


class Blendimportwarteschlange:
    #: Abstand der Nachfragen eines Wartenden (s).
    TAKT_S = 5.0
    SPERRE = 'warteschlange.lock'
    #: Eine Sperrdatei, die älter ist, stammt von einem abgestürzten Prozess (s).
    SPERRE_ALT_S = 60.0

    # ------------------------------------------------------------------ Wer rechnet, wer wartet

    @staticmethod
    def _importe():
        from ..daten.blendimportablage import Blendimportablage
        from .blendimportarbeiter import Blendimportarbeiter

        for kennung in Blendimportablage.alle():
            ablage = Blendimportablage(kennung)
            stand = ablage.stand()
            # Windows vergibt PIDs rasch neu: der Stand muss „läuft" sagen, nicht nur der Prozess leben.
            if stand.get('status') == 'laeuft' and Blendimportarbeiter.lebt(ablage):
                yield kennung, stand

    @classmethod
    def rechnender(cls, ausser=None):
        """Kennung eines Imports, der GERADE rechnet (nicht wartet) — sonst `None`."""
        for kennung, stand in cls._importe():
            if kennung != ausser and not stand.get('wartet'):
                return kennung
        return None

    @classmethod
    def wartende(cls, ausser=None):
        """Die eingereihten Importe in der Reihenfolge, in der sie an die Reihe kommen."""
        liste = [(stand.get('eingereiht') or '', kennung) for kennung, stand in cls._importe() if stand.get('wartet') and kennung != ausser]
        return [kennung for _, kennung in sorted(liste)]

    @classmethod
    def hinter(cls, ausser=None):
        """Wer hält den neuen Import auf? Der rechnende Import, sonst der letzte Wartende; `None`, wenn nichts davor steht."""
        return cls.rechnender(ausser) or (cls.wartende(ausser) or [None])[-1]

    # ------------------------------------------------------------------ Einreihen und abwarten

    @classmethod
    def einreihen(cls, ablage, hinter):
        """Den Stand eines Imports auf „eingereiht" setzen (der Arbeitsprozess wartet dann, `abwarten`). Gibt den Text zurück, den die Anzeige zeigt."""
        from ..daten.blendimportablage import Blendimportablage

        stand = Blendimportablage(hinter).stand() if hinter else {}
        name = (stand.get('quelle') or {}).get('name') or hinter
        text = 'In der Warteschlange — startet nach dem Import „%s"' % name if hinter else 'In der Warteschlange'
        stand = ablage.stand()
        stand.update(wartet=True, eingereiht=timezone.now().isoformat(), schritt='warteschlange', detail=text)
        ablage.stand_schreiben(stand)
        return text

    @classmethod
    def abwarten(cls, ablage):
        """Im Arbeitsprozess: warten, bis dieser Import an der Reihe ist. `True` = losrechnen, `False` = angehalten oder entfernt, nichts tun."""
        kennung = ablage.kennung
        while True:
            stand = ablage.stand()
            if not stand or stand.get('status') != 'laeuft' or not stand.get('wartet'):
                return False
            with cls._sperre(ablage):
                if cls.rechnender(ausser=kennung) is None and cls.wartende()[:1] == [kennung]:
                    stand = ablage.stand()
                    if stand.get('status') != 'laeuft':
                        return False
                    stand.update(wartet=False, detail='Arbeitsprozess gestartet', fortschritt=0)
                    ablage.stand_schreiben(stand)
                    return True
                cls._melden(ablage, kennung)
            time.sleep(cls.TAKT_S)

    @classmethod
    def _melden(cls, ablage, kennung):
        """Der Text der Anzeige folgt dem Stand der Schlange („nach dem Import X", dann „Platz 2")."""
        from ..daten.blendimportablage import Blendimportablage

        davor = cls.rechnender(ausser=kennung)
        platz = cls.wartende().index(kennung) + 1 if kennung in cls.wartende() else 1
        if davor:
            name = (Blendimportablage(davor).stand().get('quelle') or {}).get('name') or davor
            text = 'In der Warteschlange — startet nach dem Import „%s"' % name
        else:
            text = 'In der Warteschlange — Platz %d' % platz
        stand = ablage.stand()
        if stand.get('wartet') and stand.get('detail') != text:
            stand['detail'] = text
            ablage.stand_schreiben(stand)

    @classmethod
    @contextmanager
    def _sperre(cls, ablage):
        """Eine Sperrdatei neben den Importen: Nachsehen UND Losrechnen eines Wartenden in einem Zug."""
        pfad = ablage.ordner().parent / cls.SPERRE
        for _ in range(int(cls.SPERRE_ALT_S / 0.1) + 50):
            try:
                handle = os.open(str(pfad), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                break
            except (FileExistsError, PermissionError):     # Windows: während ein anderer die Datei löscht, meldet O_EXCL PermissionError (16.10.2026: 18 Wartende, ein Absturz)
                try:
                    if time.time() - pfad.stat().st_mtime > cls.SPERRE_ALT_S:
                        pfad.unlink()
                except OSError:
                    pass
                time.sleep(0.1)
        else:
            raise TimeoutError('Sperre der Warteschlange nicht zu bekommen')
        try:
            yield
        finally:
            os.close(handle)
            try:
                pfad.unlink()
            except OSError:
                pass
