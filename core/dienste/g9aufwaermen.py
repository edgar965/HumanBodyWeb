# -*- coding: utf-8 -*-
u"""G9aufwaermen — die Genesis-9-Merker nach dem Serverstart im Hintergrund fuellen.

BEFUND (Edgar, 18.09.2026 abends: „laden Ursula dauert lange … volle
Aufloesung immer noch mehr als 5 s"): Jeder Serverstart — auch der
Autoreload nach einer Python-Aenderung — leert alle Merker im Prozess.
Die erste Figur danach kostete gemessen (`ProjektTemp/g9_kaltstart_
messung.py`) 10,4 s fuer den Koerper und 23 s fuer das Hime-Cut-Haar,
danach 1,4 s und 0,2 s. Was sich ablegen liess, liegt seither auf der
Platte (Anhangmorphe, Stufenhaut, Nahtteilung); der Rest — DSON lesen,
Unterteiler laden, Formelgraph — wird HIER gefuellt, in einem Faden, den
`core.apps.CoreConfig.ready` startet: Wer in den ersten Sekunden fragt,
wartet auf denselben Merker statt ihn ein zweites Mal zu bauen
(`G9basisnetz._schloss`).

Laeuft nur im Serverprozess des Autoreloaders (`RUN_MAIN`), nicht im
Beobachter, nicht bei `manage.py test`/`migrate`.
"""
import logging
import os
import sys
import threading
import time

logger = logging.getLogger('core')

__all__ = ['G9aufwaermen']


class G9aufwaermen:
    u"""Ein Faden, der die Merker der Genesis-9-Figur fuellt."""

    #: Unterteilungsstufen, die der Browser anfragt (Kaefig, Ansicht, Strg+Alt+H).
    STUFEN = (0, 1, 2)
    _faden = None

    @classmethod
    def angebracht(cls, argv=None, umgebung=None):
        u"""Nur im Serverprozess: `runserver` und — mit Autoreloader — im
        Kind (`RUN_MAIN=true`), sonst liefe es zweimal."""
        argv = sys.argv if argv is None else argv
        umgebung = os.environ if umgebung is None else umgebung
        if 'runserver' not in argv:
            return False
        if '--noreload' in argv:
            return True
        return umgebung.get('RUN_MAIN') == 'true'

    @classmethod
    def starten(cls):
        if cls._faden is not None and cls._faden.is_alive():
            return cls._faden
        cls._faden = threading.Thread(target=cls.laufen, name='g9-aufwaermen',
                                      daemon=True)
        cls._faden.start()
        return cls._faden

    @classmethod
    def schritte(cls):
        u"""`[(name, funktion)]` — jeder Schritt fuer sich, Fehler einzeln."""
        from Genesis9.anhang import G9anhang
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.charaktere import G9charaktere
        from Genesis9.formung import G9formung
        from Genesis9.garderobe import G9garderobe
        from Genesis9.gelenkkorrekturen import G9gelenkkorrekturen
        from Genesis9.reglerplan import G9reglerplan
        aus = [('basisnetz', G9basisnetz.holen),
               ('charaktere', G9charaktere.liste),
               ('reglerplan', G9reglerplan.holen),
               ('skelett', lambda: G9formung({}).skelett())]
        for stufe in cls.STUFEN:
            aus.append(('koerper s%d' % stufe,
                        lambda s=stufe: G9basisnetz.netzstufe(s)))
        aus.append(('anhaenge', lambda: [f for _, f in G9anhang.alle()]))
        for stufe in cls.STUFEN:
            aus.append(('anhaenge s%d' % stufe,
                        lambda s=stufe: [f.netzstufe(s) for _, f in G9anhang.alle()]))
        aus += [('gelenkgraph', G9gelenkkorrekturen.graph),
                ('garderobe', G9garderobe.liste),
                ('duenne', G9basisnetz.duenne)]
        return aus

    @classmethod
    def laufen(cls):
        from Genesis9.pfade import G9pfade
        if not G9pfade.vorhanden():
            return
        t0 = time.time()
        zeiten = []
        for name, schritt in cls.schritte():
            t = time.time()
            try:
                schritt()
            except Exception as fehler:  # noqa: BLE001 — ein Schritt darf scheitern
                logger.warning('Genesis 9 aufwärmen, %s: %s', name, fehler)
                continue
            zeiten.append('%s %.1f s' % (name, time.time() - t))
        logger.info('Genesis 9 aufgewärmt in %.1f s: %s', time.time() - t0,
                    ', '.join(zeiten))
