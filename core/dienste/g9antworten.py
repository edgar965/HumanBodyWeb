# -*- coding: utf-8 -*-
u"""G9antworten — fertige Netzantworten je Stellung merken und vorausrechnen.

WARUM (Edgar, 18.09.2026 nachts: „noch immer ca. 30 s bis ich das mit
Ctrl-Alt-H die volle Auflösung habe. das muss in 1-2 s gehen")
=====================================================================
Ursula auf Stufe 2 mit Kleid und Haar sind drei Anfragen von zusammen
93 MB, die der Server warm in 1,6 + 1,5 + 0,3 s rechnet — davon allein
0,55 s base64 und JSON. Schneller wird die Rechnung nicht mehr in dem
Rahmen, den die Taste verlangt. Was in 1–2 s geht: die fertige Antwort
AUSLIEFERN, wenn sie schon liegt.

Deshalb zwei Dinge:

1. Jede Netzantwort (Koerper, Stueck) wird unter dem Fingerabdruck von
   Rumpf, Eintrag, Stufe und Code-Fassung als Bytes gemerkt — die acht
   juengsten im Prozess, alle auf der Platte (`Genesis9/ablage/antworten/`,
   bis `PLATTE_MB`, die aeltesten fliegen), damit auch ein Neustart oder ein
   Seiten-Refresh sie noch hat: der Refresh holt erst den Kaefig (`?stufen=0`),
   dann die Stufe des Browsers — beides liegt dann. Geschrieben wird im
   Hintergrund, die Anfrage wartet nicht auf die Platte.
2. Nach einer Anfrage in der Ansichtsstufe rechnet ein Hintergrundfaden
   dieselbe Stellung VORAUS in der Stufe, die Strg+Alt+H setzt (Keks 3 =
   Daz' Renderstufe 2, mit 8K-Details) — sobald der Server zwei Sekunden
   lang keine Netzanfrage mehr bekommen hat, jeweils den juengsten Stand je
   Figur und Stueck. Drueckt Edgar dann die Taste, liegt die Antwort.

DIE FASSUNG IM SCHLUESSEL (`~/.claude/rules/artefakte-benennen.md`)
==================================================================
Der Schluessel traegt die juengste Aenderungszeit der Genesis-9-Quellen und
der Antwortmodule: Eine Codeaenderung macht jede alte Antwort ungueltig,
ohne dass jemand eine Nummer hochzaehlen muss. Was er NICHT sieht: eine
geaenderte Daz-Bibliothek (neues Materialpreset auf ein altes Stueck) —
dafuer `vergessen()` oder den Ordner loeschen.
"""
import contextvars
import hashlib
import json
import logging
import threading
import time
from pathlib import Path

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from .g9antwortvorrat import G9antwortvorrat

__all__ = ['G9antworten']

logger = logging.getLogger('core')


class G9antworten(G9antwortvorrat):
    u"""Netzantworten je Fingerabdruck liefern und vorausrechnen."""

    #: Der Keks-Wert von Strg+Alt+H (`Netzstufe.HOCH` im Browser).
    VORAUS = 3
    #: So lange muss der Server ruhig sein, bevor vorausgerechnet wird.
    RUHE_S = 2.0
    #: Laenger wartet niemand auf eine laufende Rechnung desselben Schluessels.
    WARTEN_S = 120.0
    #: Quellen, deren Aenderung jede alte Antwort ungueltig macht.
    QUELLEN = ('Genesis9', 'HumanBodyWeb/core/api', 'HumanBodyWeb/core/daten',
               'HumanBody/humanbody_core/catmull_clark.py',
               # Dienste, die Stueckantworten rechnen (19.09.2026): Lagen, Daz auf HumanBody.
               'HumanBodyWeb/core/dienste/g9lagenanfrage.py',
               # Die Stueckrechnung selbst und die GarmentCode-Stuecke darin (24.09.2026).
               'HumanBodyWeb/core/dienste/g9stueckteile.py',
               'HumanBodyWeb/core/dienste/gcrigpfad.py',
               'HumanBodyWeb/core/dienste/g9aufhumanbody.py',
               'HumanBodyWeb/core/dienste/g9hbknochen.py',
               'HumanBodyWeb/core/dienste/g9garmentfigur.py',
               'HumanBodyWeb/core/dienste/hbtraeger.py')

    _fassung = None
    _auftraege = {}
    #: Schluessel -> Event der laufenden Rechnung: der Browser fragte die
    #: Stufe 2 genau dann, wenn der Hintergrund sie rechnete — zweimal 7,9 s
    #: fuer dasselbe Kleid (Log 22:24, 18.09.2026). Jetzt wartet der Zweite.
    _laufend = {}
    _faden = None
    _letzte_anfrage = 0.0
    #: Vorausrechnen an? Nur im Serverprozess (`G9aufwaermen.angebracht`).
    voraus_an = None

    # ------------------------------------------------------------ liefern

    @classmethod
    def liefern(cls, art, name, rumpf, bauen, eintrag=None):
        u"""Die Antwort zu `bauen()` — aus dem Vorrat, sonst gerechnet und
        gemerkt. `bauen` liefert das Antwort-Dict oder eine fertige
        `HttpResponse` (Fehler), die unveraendert durchgeht."""
        from .netzstufenwahl import Netzstufenwahl
        gewaehlt = Netzstufenwahl.gewaehlt()
        cls._letzte_anfrage = time.time()
        schluessel = cls.schluessel(art, name, rumpf, gewaehlt, eintrag)
        daten = cls.holen(schluessel)
        if daten is None:
            daten = cls.rechnen(schluessel, bauen, platte=cls.platte_an())
            if isinstance(daten, HttpResponse):
                return daten
        if gewaehlt != cls.VORAUS:
            cls.vorausrechnen(art, name, rumpf, bauen, eintrag)
        return HttpResponse(daten, content_type='application/json')

    @classmethod
    def rechnen(cls, schluessel, bauen, platte):
        u"""`bauen()` einmal je Schluessel: laeuft es schon, warten und das
        Ergebnis nehmen. Liefert Bytes oder die Fehlerantwort von `bauen`."""
        with cls._schloss:
            laeuft = cls._laufend.get(schluessel)
            if laeuft is None:
                laeuft = cls._laufend[schluessel] = threading.Event()
                selbst = True
            else:
                selbst = False
        if not selbst:
            laeuft.wait(cls.WARTEN_S)
            daten = cls.holen(schluessel)
            if daten is not None:
                return daten
            return cls.rechnen(schluessel, bauen, platte)
        try:
            aus = bauen()
            if isinstance(aus, HttpResponse):
                return aus
            daten = cls.kodieren(aus)
            cls.merken(schluessel, daten, platte=platte)
            return daten
        finally:
            with cls._schloss:
                cls._laufend.pop(schluessel, None)
            laeuft.set()

    @staticmethod
    def kodieren(aus):
        return json.dumps(aus, cls=DjangoJSONEncoder,
                          separators=(',', ':')).encode('utf-8')

    # --------------------------------------------------------- Schluessel

    @classmethod
    def schluessel(cls, art, name, rumpf, gewaehlt, eintrag=None):
        text = json.dumps([art, name, rumpf, gewaehlt, eintrag, cls.fassung(),
                           cls._eigenstand(rumpf, eintrag)],
                          sort_keys=True, default=str)
        return '%s_%s_%s' % (art, cls._sicher(name),
                             hashlib.sha1(text.encode('utf-8')).hexdigest()[:16])

    @staticmethod
    def _eigenstand(rumpf, eintrag):
        u"""Eigenmorphe (`eigen:<kennung>`, `G9eigenmorphe`) erkennt der
        Schluessel nicht am Namen — ein neuer Lauf „Modell aus Bildern" schreibt
        dieselbe Kennung neu. Deshalb die juengste Aenderung der Ablage mit,
        sobald ein Eigenmorph im Spiel ist (ein Verzeichnislisting, sonst 0)."""
        regler = {}
        for quelle in (rumpf, eintrag):
            if isinstance(quelle, dict) and isinstance(quelle.get('regler'), dict):
                regler.update(quelle['regler'])
        stand = 0
        if any(str(k).startswith('eigen:') for k in regler):
            from Genesis9.eigenmorphe import G9eigenmorphe
            stand = G9eigenmorphe.stand()
        # HB-Morphs (`hb:`, 20.09.2026) genauso: `hbmorphe_bauen` schreibt
        # dieselben Kennungen neu — der Bestand traegt den Stand.
        if any(str(k).startswith('hb:') for k in regler):
            from Genesis9.hbmorphe import G9hbmorphe
            stand = (stand, G9hbmorphe.stand())
        return stand

    @staticmethod
    def _sicher(name):
        return ''.join(c if c.isalnum() or c in '-_' else '_' for c in str(name))[:40]

    @classmethod
    def fassung(cls):
        u"""Juengste Aenderungszeit der Quellen — einmal je Prozess."""
        if cls._fassung is None:
            from django.conf import settings
            wurzel = Path(settings.TOOLS_ROOT)
            juengste = 0
            for rel in cls.QUELLEN:
                pfad = wurzel / rel
                dateien = [pfad] if pfad.is_file() else pfad.glob('*.py')
                for datei in dateien:
                    try:
                        juengste = max(juengste, datei.stat().st_mtime_ns)
                    except OSError:
                        continue
            cls._fassung = juengste
        return cls._fassung

    @classmethod
    def vergessen(cls):
        super().vergessen()
        with cls._schloss:
            cls._auftraege.clear()

    # ------------------------------------------------------------- Voraus

    @classmethod
    def platte_an(cls):
        u"""Auf die Platte nur im Serverprozess — Testlaeufe und Skripte fuellten
        den Ordner sonst mit Stellungen, die nie jemand wieder anfragt."""
        if cls.voraus_an is None:
            from .g9aufwaermen import G9aufwaermen
            cls.voraus_an = G9aufwaermen.angebracht()
        return cls.voraus_an

    @classmethod
    def vorausrechnen(cls, art, name, rumpf, bauen, eintrag=None):
        u"""Die Stellung in der Strg+Alt+H-Stufe vormerken; der juengste
        Auftrag je Figur/Stueck gewinnt."""
        if not cls.platte_an():
            return
        with cls._schloss:
            cls._auftraege[(art, name)] = (rumpf, bauen, eintrag)
            if cls._faden is None or not cls._faden.is_alive():
                cls._faden = threading.Thread(target=cls._laufen, daemon=True,
                                              name='g9-voraus')
                cls._faden.start()

    @classmethod
    def _laufen(cls):
        while True:
            time.sleep(0.25)
            if time.time() - cls._letzte_anfrage < cls.RUHE_S:
                continue
            with cls._schloss:
                if not cls._auftraege:
                    return
                (art, name), auftrag = next(iter(cls._auftraege.items()))
                rumpf, bauen, eintrag = auftrag
            try:
                cls._rechnen(art, name, rumpf, bauen, eintrag)
            except Exception as fehler:  # noqa: BLE001 — nur Vorrat
                logger.warning('Genesis 9: Vorausrechnen %s %s: %s', art, name, fehler)
            with cls._schloss:
                # Nur weg, wenn inzwischen kein neuerer Auftrag kam.
                if cls._auftraege.get((art, name), (None,))[0] is rumpf:
                    cls._auftraege.pop((art, name), None)

    @classmethod
    def _rechnen(cls, art, name, rumpf, bauen, eintrag):
        from .netzstufenwahl import Netzstufenwahl
        schluessel = cls.schluessel(art, name, rumpf, cls.VORAUS, eintrag)
        if cls.holen(schluessel) is not None:
            return
        kontext = contextvars.copy_context()

        def im_kontext():
            Netzstufenwahl._gewaehlt.set(cls.VORAUS)
            return bauen()

        beginn = time.time()
        aus = kontext.run(lambda: cls.rechnen(schluessel, im_kontext, platte=True))
        if isinstance(aus, HttpResponse):
            return
        logger.info('Genesis 9: %s %s fuer Strg+Alt+H vorausgerechnet (%.1f s)',
                    art, name, time.time() - beginn)
