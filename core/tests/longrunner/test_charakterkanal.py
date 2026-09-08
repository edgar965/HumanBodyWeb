# -*- coding: utf-8 -*-
u"""Was wirklich über den Morph-Kanal geht — Punkte UND Knochen.

WARUM ES DIESE DATEI GIBT (05.09.2026)
======================================
`core/consumers.py` hatte keinen einzigen Test. Beim Nachmessen der neuen
Skelett-Nachführung fiel deshalb ein Fehler auf, der seit jeher drin war:

    reset -> Punkte(70851), skelett(174), Punkte(70851), skelett(174)

Nach „Neues Modell" blieb der Körper groß. `reset` leerte `_morph_values`
und `_meta_values` von außen — `_user_morphs` aber nicht, und `compute()`
schreibt die Regler von dort in seiner ersten Zeile zurück. Gemessen:
2,28 m statt 1,68 m. Gesehen hat es niemand, weil die Oberfläche zusätzlich
jeden Regler einzeln auf Null schickt; der Befehl selbst tat nichts.

Sichtbar wurde er erst, als das Skelett dem Netz folgte und nach dem
Zurücksetzen 174 bewegte Knochen meldete. Ein Kanal ohne Test ist genau
die Stelle, an der so etwas jahrelang steht.

WAS GEPRÜFT WIRD
================
Die Reihenfolge auf der Leitung (erst Punkte, dann Knochen), das Schweigen
in der Ruhelage, der Rückweg auf Null und der Reset. Nicht die Rechnung —
die steht in `test_skelettnachfuehrung` und `test_gelenkanpassung`.
"""
import json

from channels.testing import WebsocketCommunicator
from django.test import SimpleTestCase

from core.consumers import CharacterConsumer

#: Punkte des unterteilten Netzes (Catmull-Clark über 18.210 Grundpunkte).
PUNKTE = 70851


class Morphkanal:
    u"""Ein Gespräch mit dem Consumer — als Klasse, nicht als freie Funktion.

    `alles()` liest bis zur Stille statt einer festen Anzahl Nachrichten:
    Wie viele es sind, ist Teil dessen, was geprüft wird. Genau daran hing
    der Befund oben — es waren vier statt zwei.

    NICHT `Kanal`: Den Namen trägt schon `tests/kanal.py` — der HTTP-Kanal
    der Oberflächenfälle. Zwei gleichnamige Klassen für zwei ganz
    verschiedene Dinge sind der Befund des Werkzeugs `namens-dubletten`,
    und beim Lesen eines Traceback hilft der Unterschied.
    """

    STILLE_S = 1.0

    def __init__(self, kommunikator):
        self.kommunikator = kommunikator

    async def alles(self, nachricht):
        u"""Sendet und sammelt, bis nichts mehr kommt.

        `receive_nothing()` UND NICHT `receive_output()` IM TRY-BLOCK: Läuft
        `receive_output` in seinen Zeitablauf, ruft asgiref
        ``self.future.cancel()`` — es beendet also die Anwendung. Der erste
        Durchgang sah dann richtig aus, jeder weitere scheiterte mit
        `CancelledError`, und zwar erst beim `disconnect()` am Ende. Wer die
        Ausnahme dort sucht, sucht an der falschen Stelle.

        :return: Liste aus ``('punkte', anzahl)`` und ``(art, inhalt)``
        """
        await self.kommunikator.send_json_to(nachricht)
        gesammelt = []
        while not await self.kommunikator.receive_nothing(self.STILLE_S):
            roh = await self.kommunikator.receive_output(timeout=self.STILLE_S)
            # in der Schleife gewollt: jede Runde bringt eine ANDERE Nachricht
            if 'bytes' in roh:
                gesammelt.append(('punkte', len(roh['bytes']) // 12))
            else:
                inhalt = json.loads(roh['text'])
                gesammelt.append((inhalt.get('type'), inhalt))
        return gesammelt

    @staticmethod
    def knochen(folge):
        u"""Die Knochen der letzten Skelett-Nachricht, oder ``None``."""
        skelette = [i for a, i in folge if a == 'skelett']
        return skelette[-1]['bones'] if skelette else None


class DerMorphKanal(SimpleTestCase):

    async def _offen(self):
        kommunikator = WebsocketCommunicator(CharacterConsumer.as_asgi(),
                                             '/ws/character/')
        verbunden, _ = await kommunikator.connect()
        self.assertTrue(verbunden)
        kanal = Morphkanal(kommunikator)
        await kanal.alles({'type': 'body_type', 'value': 'Female_Caucasian'})
        return kommunikator, kanal

    async def test_die_ruhelage_schickt_keine_knochen(self):
        u"""Sonst bindet der Browser die Haut bei jedem Regleranschlag neu,
        ohne dass sich etwas geändert hat."""
        kommunikator, kanal = await self._offen()
        try:
            folge = await kanal.alles(
                {'type': 'morph', 'key': 'Body_Size', 'value': 0.0})
            self.assertEqual(folge, [('punkte', PUNKTE)])
        finally:
            await kommunikator.disconnect()

    async def test_erst_die_punkte_dann_die_knochen(self):
        u"""Die Reihenfolge ist Drahtformat: Der Browser bindet die Haut an
        das Netz, das dazu gehört. Andersherum bände er ans vorige."""
        kommunikator, kanal = await self._offen()
        try:
            folge = await kanal.alles(
                {'type': 'morph', 'key': 'Body_Size', 'value': 1.0})
            self.assertEqual([a for a, _ in folge], ['punkte', 'skelett'])
            self.assertGreater(len(kanal.knochen(folge)), 170)
        finally:
            await kommunikator.disconnect()

    async def test_der_regler_zurueck_auf_null_holt_das_skelett_zurueck(self):
        u"""Die LEERE Nachricht — ohne sie bliebe das Rig in der letzten
        Größe stehen, während der Körper wieder schrumpft."""
        kommunikator, kanal = await self._offen()
        try:
            await kanal.alles({'type': 'morph', 'key': 'Body_Size', 'value': 1.0})
            folge = await kanal.alles(
                {'type': 'morph', 'key': 'Body_Size', 'value': 0.0})
            self.assertEqual(kanal.knochen(folge), {})
        finally:
            await kommunikator.disconnect()

    async def test_auch_ein_meta_regler_bewegt_das_skelett(self):
        u"""`meta` ist ein eigener Zweig im Consumer. Genau so eine Stelle
        wird beim Nachrüsten vergessen."""
        kommunikator, kanal = await self._offen()
        try:
            folge = await kanal.alles(
                {'type': 'meta', 'name': 'mass', 'value': 1.0})
            self.assertGreater(len(kanal.knochen(folge) or {}), 0)
        finally:
            await kommunikator.disconnect()

    async def test_reset_setzt_koerper_und_skelett_zurueck(self):
        u"""DER BEFUND. Vor dem 05.09.2026 kam hier 174 statt 0 — und zwar
        zweimal, weil `reset` zusätzlich doppelt sendete."""
        kommunikator, kanal = await self._offen()
        try:
            await kanal.alles({'type': 'morph', 'key': 'Body_Size', 'value': 1.0})
            await kanal.alles({'type': 'meta', 'name': 'mass', 'value': 1.0})
            folge = await kanal.alles({'type': 'reset',
                                       'body_type': 'Female_Caucasian'})
            self.assertEqual(kanal.knochen(folge), {})
        finally:
            await kommunikator.disconnect()

    async def test_und_schickt_das_netz_dabei_nur_einmal(self):
        u"""Vorher gingen 840 kB zweimal raus — erst der ALTE Körper, dann
        der zurückgesetzte. Mit der Nachführung sah man das als kurzes
        Aufblitzen des großen Rigs."""
        kommunikator, kanal = await self._offen()
        try:
            await kanal.alles({'type': 'morph', 'key': 'Body_Size', 'value': 1.0})
            folge = await kanal.alles({'type': 'reset',
                                       'body_type': 'Female_Caucasian'})
            self.assertEqual([a for a, _ in folge].count('punkte'), 1)
        finally:
            await kommunikator.disconnect()
