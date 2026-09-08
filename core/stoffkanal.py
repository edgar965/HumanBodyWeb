# -*- coding: utf-8 -*-
u"""Stoffkanal — die WebSocket-Seite der Stoffvorschau.

WARUM EIGENE DATEI: `core/consumers.py` stand bei 259 Zeilen; mit dem
Stoffteil waere sie auf 312 gewachsen. Die Regel ist, dass eine Datei beim
Anfassen nicht ueber ihre Grenze waechst
(`~/.claude/rules/struktur.md`).

Hier steht ausschliesslich das Drahtformat. Was gerechnet wird, steht in
`core/dienste/stoffnachfuehrung.py`, und wie gerechnet wird in
`GarmentCode/stoffvorschau.py`.
"""
import json
import logging

import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('core')

__all__ = ['Stoffkanal', 'StoffConsumer']


class Stoffkanal:
    u"""Mischklasse fuer `CharacterConsumer`: Stoff senden und binden."""

    async def _send_stoff(self, grundnetz):
        u"""Drapierte Kleidung, die dem Koerper folgt.

        An EINER Stelle gerufen (`_send_vertices`), aus demselben Grund wie
        beim Skelett: Es gibt fuenf Stellen, die Punkte schicken. Eine davon
        zu vergessen hiesse, dass der Stoff bei genau einem Regler stehen
        bleibt — die Sorte Fehler, die niemand meldet.

        REIHENFOLGE IST DRAHTFORMAT: erst die Kennung als Text, dann die
        Punkte binaer. Ohne die Kennung waere eine Binaernachricht nicht von
        den Koerperpunkten zu unterscheiden, und der Browser legte den Stoff
        auf den Koerper.
        """
        if self._stoff.leer:
            return
        for stueck, punkte in self._stoff.punkte(grundnetz).items():
            await self.send(text_data=json.dumps({
                'type': 'stoff', 'stueck': stueck,
                'punkte': int(len(punkte)),
                # Wie weit die Vorschau von der simulierten Form weg ist —
                # die Zahl, die „Finalize" begruendet.
                'abstand_mm': self._stoff.abstand_mm(stueck, punkte)}))
            await self.send(bytes_data=punkte.astype(np.float32).tobytes())

    async def _handle_stoff_binden(self, msg):
        u"""Ein drapiertes Stueck an den aktuellen Koerper binden.

        Der Ordner kommt aus der Antwort der Drapierung und damit aus dem
        Browser — `Stoffnachfuehrung.netzpfad` prueft ihn gegen den
        Ausgabeordner, bevor irgendetwas gelesen wird.
        """
        from .dienste.charakterdaten import Charakterdaten
        pfad = self._stoff.netzpfad(msg.get('ordner'))
        if not pfad:
            await self.send(text_data=json.dumps({
                'type': 'stoff_bindung',
                'fehler': 'Kein Ergebnisnetz in diesem Ordner'}))
            return
        grundnetz = self._char_state.compute()
        netz = Charakterdaten.netzdaten(self._current_gender)
        bilanz = self._stoff.binden(
            msg.get('stueck') or 'kleidung', pfad, grundnetz, netz.faces)
        await self.send(text_data=json.dumps(
            {'type': 'stoff_bindung', **bilanz}))
        if 'fehler' not in bilanz:
            await self._send_stoff(grundnetz)


class StoffConsumer(Stoffkanal, AsyncWebsocketConsumer):
    u"""Der Kanal der SZENE-Seite: nur Stoff, kein Koerpernetz.

    WARUM EIN EIGENER KANAL (08.09.2026, Edgar: „du kannst vorschau auch per
    websocket ueber den Server laufen lassen!"): Die Szene holt ihr
    Koerpernetz per HTTP (`/api/character/mesh/`, `Charakterkoerper.neuLaden`)
    und hat keinen WebSocket — den hat nur „Szene – Modell".

    Die Bindung kostet einmalig 516 ms und muss deshalb ueber die Reglerzuege
    hinweg stehen bleiben. Ueber HTTP ginge das nur mit einem Sitzungs-
    speicher; ein WebSocket HAT diesen Zustand von Natur aus. Deshalb hier.

    Er rechnet den Koerper SELBST (gemessen 0,4 ms) statt ihn vom Browser zu
    bekommen: So kann er nie zu einem anderen Morphstand gehoeren als der
    Stoff, den er ausliefert — und die Nachricht bleibt klein.
    """

    async def connect(self):
        await self.accept()
        from GarmentCode.nachfuehrung import Stoffnachfuehrung
        self._stoff = Stoffnachfuehrung()
        self._char_state = None
        self._current_gender = 'female'
        self._init_state()

    def _init_state(self):
        try:
            from django.conf import settings
            from humanbody_core import (MorphData, CharacterState,
                                        CharacterDefaults)
            md = MorphData(data_dir=str(settings.HUMANBODY_DATA_DIR))
            md.load()
            cd = CharacterDefaults()
            cd.load(str(settings.HUMANBODY_ROOT / 'settings.yaml'))
            self._char_state = CharacterState(md, cd)
            self._char_state.set_body_type('Female_Caucasian')
        except Exception as fehler:                       # noqa: BLE001
            logger.error('StoffConsumer: CharacterState nicht aufgebaut: %s',
                         fehler)

    async def disconnect(self, close_code):
        self._stoff.loesen()
        self._char_state = None

    async def receive(self, text_data=None, bytes_data=None):
        u"""Morphs rein, Stoffpunkte raus.

        Kaputtes JSON bleibt stumm: Der Rumpf kommt aus dem Browser, ein Log
        daraus liesse sich von aussen beliebig oft ausloesen (dieselbe
        Begruendung wie in `CharacterConsumer.receive`).
        """
        if text_data is None or self._char_state is None:
            return
        try:
            msg = json.loads(text_data)
        except json.JSONDecodeError:
            return
        art = msg.get('type')

        if art == 'stoff_binden':
            self._stellen(msg)
            await self._handle_stoff_binden(msg)
        elif art == 'stoff_loesen':
            self._stoff.loesen(msg.get('stueck'))
        elif art == 'stellung':
            if self._stoff.leer:
                return
            self._stellen(msg)
            await self._send_stoff(self._char_state.compute())

    def _stellen(self, msg):
        u"""Bauart, Morphs und Metaregler uebernehmen.

        VOLLSTAENDIG, nicht einzeln: Der Browser schickt seinen ganzen
        Stand. Wer nur die geaenderten Werte schickt, muss den Rest
        nachhalten — und liegt nach dem ersten verlorenen Paket daneben,
        ohne dass es auffaellt.
        """
        bauart = msg.get('bauart') or 'Female_Caucasian'
        self._current_gender = ('male' if str(bauart).lower().startswith('m')
                                else 'female')
        # ERST leeren, DANN die Bauart setzen — dieselbe Reihenfolge wie in
        # `CharacterConsumer.receive` bei `reset`: `compute()` schreibt die
        # Regler aus `_user_morphs` zurueck, ein spaeteres Leeren traefe sie
        # nicht.
        self._char_state.zuruecksetzen()
        self._char_state.set_body_type(bauart)
        for name, wert in (msg.get('morphs') or {}).items():
            try:
                self._char_state.set_morph(name, float(wert))
            except (TypeError, ValueError):
                continue
        for name, wert in (msg.get('meta') or {}).items():
            try:
                self._char_state.set_meta(name, float(wert))
            except (TypeError, ValueError):
                continue
