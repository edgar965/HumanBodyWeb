# -*- coding: utf-8 -*-
"""Ladeschloss — ein Schloss JE Zwischenspeicher statt eines fuer alle.

ANLASS (Sparring mit Nemotron, 18.08.2026): `Charakterdaten` hatte EIN
wiedereintretendes Schloss fuer saemtliche Zwischenspeicher. Der erste Aufruf
von `unterteiler()` haelt es waehrend der ganzen Catmull-Clark-Unterteilung —
**gemessen 1,21 s** (zweiter Aufruf: 0,0000 s). In dieser Zeit warten alle
anderen Anfragen, auch wenn sie mit der Unterteilung nichts zu tun haben:
Morphdaten, Netzdaten, SMPL-Bibliothek, Voreinstellungen. Daphne beantwortet
Anfragen in Faeden, also trifft das wirklich jede parallele Anfrage.

Mit einem Schloss je Name wartet nur noch, wer auf DENSELBEN Wert wartet — und
das soll er auch: Sonst rechnen zwei Faeden dieselbe Unterteilung.

Die Schloesser selbst entstehen unter einem winzigen Meta-Schloss; es wird nur
fuer das Anlegen gehalten, nie waehrend des Ladens.

WIEDEREINTRETEND (RLock), weil `unterteiler()` beim Fuellen `netzdaten()` und
`morphdaten()` braucht — das sind zwar andere Namen und damit andere Schloesser,
aber ein Aufruf mit demselben Namen (etwa ueber einen Rueckweg) wuerde sich
sonst selbst blockieren.
"""

import threading


class Ladeschloss:
    """Schloesser je Name, faul angelegt."""

    def __init__(self):
        self._schloesser = {}
        self._meta = threading.Lock()

    def fuer(self, name):
        """Das Schloss zu diesem Namen — bei Bedarf angelegt."""
        vorhanden = self._schloesser.get(name)
        if vorhanden is not None:
            return vorhanden
        with self._meta:
            if name not in self._schloesser:
                self._schloesser[name] = threading.RLock()
            return self._schloesser[name]

    def einmal(self, name, vorhanden, bauen):
        """Doppelt geprueftes Laden.

        `vorhanden()` liefert den fertigen Wert oder `None`; `bauen()` erzeugt
        ihn. Der zweite Blick INNERHALB des Schlosses ist der Punkt: Zwischen
        dem ersten Blick und dem Schloss kann ein anderer Faden fertig geworden
        sein.
        """
        wert = vorhanden()
        if wert is not None:
            return wert
        with self.fuer(name):
            wert = vorhanden()
            if wert is not None:
                return wert
            return bauen()
