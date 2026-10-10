# -*- coding: utf-8 -*-
"""Gleiche Retarget-Anfragen warten aufeinander (09.10.2026).

DER ANLASS
==========
Edgar (09.10.2026, „alle offenen Punkte lösen"): Der Server rechnete dieselbe Retarget-Anfrage mehrfach, wenn sie gleichzeitig kam. Gemessen
(`ProjektTemp/_wegwerf/retarget_sperre/gleich_messen.py`, StayStill-Clip `idle_08_1`, frischer Schlüssel): eine Anfrage 9,6 s und eine Rechnung; drei
gleiche zugleich je 31 s und drei Rechnungen. Mit `Retargetsperre` in `Retargetdaten.holen`: drei gleiche zugleich je 8,3 s und EINE Rechnung; zwei Anfragen
mit verschiedenem Schlüssel gleichzeitig 15,4 s und 15,5 s (parallel, nicht nacheinander).

WAS DIESE PRÜFUNG NICHT IST
===========================
Kein Retarget, kein Server: das Muster von `Retargetdaten.holen` (unter der Sperre Ablage prüfen, sonst rechnen und ablegen) mit Fäden und Zählern nachgespielt.
Dass `holen` die Sperre wirklich benutzt, zeigt die Messung oben (Zeilen „Haltungsbezug:" im Serverlog: 3 → 1).

BDD - GEGEBEN / DANN
====================
    zwei Anfragen mit demselben Schlüssel    ... eine rechnet, die andere wartet und liest das Ergebnis der ersten (eine Rechnung)
    Gegenprobe ohne Sperre                   ... beide rechnen (zwei Rechnungen) — so sah der Server vorher aus
    zwei Anfragen mit verschiedenem Schlüssel ... beide sind zugleich in der Sperre (sie halten sich nicht auf)
    die erste Rechnung scheitert             ... der Wartende rechnet selbst, danach ist nichts mehr gesperrt
"""
import threading
import time
from contextlib import nullcontext

from django.test import SimpleTestCase

from core.dienste.retargetsperre import Retargetsperre

WARTEN = 5.0


def _holen(schluessel, ablage, rechnungen, tor=None, gleichzeitig=None, kontext=Retargetsperre.fuer, scheitern=False):
    """Das Muster von `Retargetdaten.holen`: unter der Sperre erst die Ablage ansehen, sonst rechnen und ablegen."""
    with kontext(schluessel):
        if gleichzeitig is not None:
            gleichzeitig.append(schluessel)
        ergebnis = ablage.get(schluessel)
        if ergebnis is None:
            if tor is not None:
                tor.wait(WARTEN)           # die erste Rechnung dauert
            rechnungen.append(schluessel)
            if scheitern:
                raise RuntimeError('Rechnung gescheitert')
            ergebnis = 'ergebnis-' + schluessel
            ablage[schluessel] = ergebnis
    return ergebnis


def _faden(ziel, *args, **kwargs):
    ausgang = {}

    def lauf():
        try:
            ausgang['wert'] = ziel(*args, **kwargs)
        except RuntimeError as fehler:
            ausgang['fehler'] = str(fehler)

    faden = threading.Thread(target=lauf, daemon=True)
    faden.start()
    return faden, ausgang


def _warten_bis(bedingung, sekunden=2.0):
    ende = time.time() + sekunden
    while time.time() < ende:
        if bedingung():
            return True
        time.sleep(0.01)
    return False


class DieRetargetsperre(SimpleTestCase):
    def test_gleicher_schluessel_wird_einmal_gerechnet(self):
        ablage, rechnungen, tor = {}, [], threading.Event()
        erster, aus1 = _faden(_holen, 'a', ablage, rechnungen, tor)
        self.assertTrue(_warten_bis(lambda: Retargetsperre.offene() == 1))
        zweiter, aus2 = _faden(_holen, 'a', ablage, rechnungen, tor)
        # der zweite steht jetzt in der Sperre an: ein Schluessel, zwei Haltende und Wartende
        self.assertTrue(_warten_bis(lambda: Retargetsperre._eintraege.get('a', [None, 0])[1] == 2))
        tor.set()
        erster.join(WARTEN)
        zweiter.join(WARTEN)
        self.assertEqual(rechnungen, ['a'])
        self.assertEqual((aus1['wert'], aus2['wert']), ('ergebnis-a', 'ergebnis-a'))
        self.assertEqual(Retargetsperre.offene(), 0)

    def test_gegenprobe_ohne_sperre_rechnen_beide(self):
        ablage, rechnungen, tor = {}, [], threading.Event()
        faeden = [_faden(_holen, 'a', ablage, rechnungen, tor, kontext=lambda s: nullcontext()) for _ in range(2)]
        self.assertTrue(_warten_bis(lambda: len(rechnungen) == 0))   # beide stehen noch im Tor
        time.sleep(0.2)
        tor.set()
        for faden, _ in faeden:
            faden.join(WARTEN)
        self.assertEqual(len(rechnungen), 2)

    def test_verschiedene_schluessel_halten_sich_nicht_auf(self):
        ablage, rechnungen, tor, gleichzeitig = {}, [], threading.Event(), []
        a, _ = _faden(_holen, 'a', ablage, rechnungen, tor, gleichzeitig)
        b, _ = _faden(_holen, 'b', ablage, rechnungen, tor, gleichzeitig)
        self.assertTrue(_warten_bis(lambda: sorted(gleichzeitig) == ['a', 'b']))   # beide zugleich in der Sperre
        tor.set()
        a.join(WARTEN)
        b.join(WARTEN)
        self.assertEqual(sorted(rechnungen), ['a', 'b'])
        self.assertEqual(Retargetsperre.offene(), 0)

    def test_scheitert_die_erste_rechnung_rechnet_der_wartende_selbst(self):
        ablage, rechnungen, tor = {}, [], threading.Event()
        erster, aus1 = _faden(_holen, 'a', ablage, rechnungen, tor, scheitern=True)
        self.assertTrue(_warten_bis(lambda: Retargetsperre.offene() == 1))
        zweiter, aus2 = _faden(_holen, 'a', ablage, rechnungen, tor)
        self.assertTrue(_warten_bis(lambda: Retargetsperre._eintraege.get('a', [None, 0])[1] == 2))
        tor.set()
        erster.join(WARTEN)
        zweiter.join(WARTEN)
        self.assertEqual(aus1.get('fehler'), 'Rechnung gescheitert')
        self.assertEqual(aus2.get('wert'), 'ergebnis-a')
        self.assertEqual(rechnungen, ['a', 'a'])
        self.assertEqual(Retargetsperre.offene(), 0)
