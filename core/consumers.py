import json
import logging

import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer

from .dienste.charakterdaten import Charakterdaten
from .dienste.skelettnachfuehrung import Skelettnachfuehrung
from .stoffkanal import Stoffkanal

logger = logging.getLogger(__name__)


class ProgressConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time job progress updates."""

    async def connect(self):
        self.job_id = self.scope['url_route']['kwargs']['job_id']
        self.group_name = f'job_{self.job_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def job_progress(self, event):
        """Send progress update to WebSocket."""
        await self.send(text_data=json.dumps({
            'status': event['status'],
            'progress': event['progress'],
            'error': event.get('error', ''),
            'bvh_file': event.get('bvh_file', ''),
        }))


class CharacterConsumer(Stoffkanal, AsyncWebsocketConsumer):
    """WebSocket consumer for live character morphing."""

    async def connect(self):
        await self.accept()
        self._char_state = None
        self._cc_subs = {}  # {'female': CC, 'male': CC}
        self._current_gender = 'female'
        #: Ob zuletzt bewegte Knochen unterwegs waren — siehe `_send_skelett`.
        self._skelett_bewegt = False
        #: Drapierte Kleidung, die den Reglern folgt (`_send_stoff`).
        from GarmentCode.nachfuehrung import Stoffnachfuehrung
        self._stoff = Stoffnachfuehrung()
        self._init_state()

    def _init_state(self):
        """Initialize CharacterState and CC subdivider lazily."""
        try:
            from humanbody_core import MorphData, CharacterState, CharacterDefaults
            from django.conf import settings

            md = MorphData(data_dir=str(settings.HUMANBODY_DATA_DIR))
            md.load()
            cd = CharacterDefaults()
            cd.load(str(settings.HUMANBODY_ROOT / 'settings.yaml'))

            self._char_state = CharacterState(md, cd)
            self._char_state.set_body_type('Female_Caucasian')

            # Preload female CC subdivider
            from core.dienste.charakterdaten import Charakterdaten
            self._cc_subs['female'] = Charakterdaten.unterteiler('female')
        except Exception as e:
            logger.error("Failed to init CharacterState: %s", e)

    def _get_cc(self):
        """Get CC subdivider for current gender, lazy-loading if needed."""
        if self._current_gender not in self._cc_subs:
            from core.dienste.charakterdaten import Charakterdaten
            self._cc_subs[self._current_gender] = (
                Charakterdaten.unterteiler(self._current_gender))
        return self._cc_subs.get(self._current_gender)

    async def disconnect(self, close_code):
        self._char_state = None
        self._cc_subs = {}
        self._stoff.loesen()

    async def _send_vertices(self, vertices):
        """Send vertices, applying CC subdivision if available.

        Das Skelett faehrt hier mit, nicht in den fuenf Aufrufern: Es gab am
        05.09.2026 fuenf Stellen, die Punkte schicken (`morph`, `morph_batch`,
        `meta`, `reset`, Koerperartwechsel) — eine davon zu vergessen hiesse,
        dass das Skelett bei genau einem Regler stehen bleibt. Genau die
        Sorte Fehler, die niemand meldet.

        REIHENFOLGE IST DRAHTFORMAT: erst die Punkte, dann die Knochen. Ein
        WebSocket haelt die Reihenfolge, und der Browser bindet die Haut an
        das Netz, das dazu gehoert.
        """
        cc = self._get_cc()
        grundnetz = vertices
        if cc is not None:
            vertices = cc.subdivide(vertices)
        await self.send(bytes_data=vertices.astype(np.float32).tobytes())
        await self._send_skelett(grundnetz)
        await self._send_stoff(grundnetz)

    async def _send_skelett(self, grundnetz):
        """Die bewegten Knochen — oder gar nichts.

        Auf dem UNTERTEILTEN Netz waere das falsch: Die Gelenkanpassung merkt
        sich Nachbarindizes des Grundnetzes (18.210 Punkte), das unterteilte
        hat 70.851.

        DIE NACHRICHT IST VOLLSTAENDIG: Was nicht drinsteht, steht in der
        Ruhelage. Deshalb muss die LEERE Nachricht raus, sobald vorher etwas
        bewegt war — sonst bliebe das Skelett beim Zurueckdrehen des Reglers
        (und bei `reset`) in der letzten Groesse stehen. Nur wenn schon
        vorher nichts bewegt war, ist Schweigen richtig; das ist der
        Normalfall und kostet dann auch keine 8,6 kB je Regleranschlag.
        """
        bewegte = Skelettnachfuehrung.bewegte(self._current_gender, grundnetz)
        if not bewegte and not self._skelett_bewegt:
            return
        self._skelett_bewegt = bool(bewegte)
        await self.send(text_data=json.dumps({
            'type': 'skelett',
            'bones': bewegte,
        }))

    async def _handle_body_type(self, body_type):
        """Koerperart wechseln und dabei einen Geschlechtswechsel erkennen.

        BEFUND 16.08.2026: Hier stand
            gender_changed = self._char_state.set_body_type(body_type)
            new_gender = self._char_state.current_gender
        `set_body_type` gibt aber nichts zurueck, und `CharacterState` hat kein
        Feld `current_gender` — nur `gender` als Zahl zwischen 0 und 1. Jede
        Koerperart-Umstellung endete deshalb in

            AttributeError: 'CharacterState' object has no attribute
            'current_gender'

        und riss die WebSocket-Verbindung ab; die linke Spalte der
        Vergleichsseite war danach tot. Das Geschlecht steht im Namen der
        Koerperart, und der Wechsel ergibt sich aus dem Vergleich mit dem
        bisher gemerkten Wert — genau dafuer gibt es `self._current_gender`.
        """
        self._char_state.set_body_type(body_type)
        new_gender = Charakterdaten.geschlecht_zu(body_type)
        gender_changed = new_gender != self._current_gender
        self._current_gender = new_gender

        if gender_changed:
            # Gender changed — client needs to reload mesh (different topology)
            await self.send(text_data=json.dumps({
                'type': 'reload_mesh',
                'body_type': body_type,
                'gender': new_gender,
            }))
            return

        # Same gender — just send updated vertices
        vertices = self._char_state.compute()
        await self._send_vertices(vertices)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return

        try:
            msg = json.loads(text_data)
        # stumm gewollt: Der Rumpf kommt aus einer WebSocket-Nachricht des
        # Browsers. Kaputtes JSON ist eine fremde Eingabe, kein Serverfehler —
        # ein Log daraus laesst sich von aussen beliebig oft ausloesen.
        except json.JSONDecodeError:
            return

        if self._char_state is None:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'CharacterState not initialized'
            }))
            return

        msg_type = msg.get('type')

        if msg_type == 'body_type':
            await self._handle_body_type(msg['value'])

        elif msg_type == 'morph':
            self._char_state.set_morph(msg['key'], float(msg['value']))
            vertices = self._char_state.compute()
            await self._send_vertices(vertices)

        elif msg_type == 'morph_batch':
            # Apply multiple morphs at once
            for key, val in msg.get('morphs', {}).items():
                self._char_state.set_morph(key, float(val))
            vertices = self._char_state.compute()
            await self._send_vertices(vertices)

        elif msg_type == 'meta':
            self._char_state.set_meta(msg['name'], float(msg['value']))
            vertices = self._char_state.compute()
            await self._send_vertices(vertices)

        elif msg_type == 'stoff_binden':
            await self._handle_stoff_binden(msg)

        elif msg_type == 'stoff_loesen':
            self._stoff.loesen(msg.get('stueck'))

        elif msg_type == 'reset':
            # ERST leeren, DANN die Koerperart setzen (05.09.2026).
            #
            # `zuruecksetzen()` statt zweier `clear()` von aussen: Die
            # trafen `_user_morphs` nicht, und `compute()` schreibt die
            # Regler von dort in seiner ersten Zeile zurueck. „Neues
            # Modell" liess den Koerper deshalb gross — gemessen 2,28 m
            # statt 1,68 m.
            #
            # Und in dieser Reihenfolge, weil `_handle_body_type` selbst
            # schickt: Vorher stand hier erst der Aufruf, dann das Leeren,
            # dann ein zweites Senden. Der Browser bekam also einmal den
            # ALTEN Koerper (840 kB) und gleich darauf den neuen — mit der
            # Skelett-Nachfuehrung sichtbar als kurzes Aufblitzen des
            # grossen Rigs. Jetzt geht eine Nachricht raus, die richtige.
            self._char_state.zuruecksetzen()
            await self._handle_body_type(msg.get('body_type',
                                                 'Female_Caucasian'))


class TestCharacterConsumer(CharacterConsumer):
    """WebSocket consumer for test character morphing (isolated version)."""

    def _init_state(self):
        """Initialize CharacterState from TestCharakter/ directory."""
        try:
            # `Testkern` seit dem 17.08.2026: Vorher standen hier fünf private
            # Funktionen von `test_character_api` — Modulinneres, das mit dem
            # Aufteilen der Datei verschwunden wäre.
            from core.api.testfigur import Testkern
            self._char_state = Testkern.zustand()
            self._cc_subs = {'test': Testkern.unterteiler()}
        except Exception as e:
            logger.exception('Test-CharacterState nicht aufbaubar: %s', e)

    async def _send_skelett(self, grundnetz):
        """Der Testcharakter bekommt keine Nachfuehrung.

        Er hat 17.996 Grundpunkte statt 18.210, und `def_skeleton.json`
        gehoert zum Produktionsnetz. `Gelenkanpassung.passt_zu` wuerde das
        auch abfangen — aber dann waere erst die ganze Anpassung samt
        KD-Baum gebaut worden, fuer eine Seite, die sie nie braucht.
        """
        return

    def _get_cc(self):
        """Der Unterteiler des TESTcharakters — nicht der der Produktion.

        BEFUND 16.08.2026: Diese Klasse legte ihren Unterteiler unter
        `self._cc_sub` ab (Einzahl), die geerbte `_get_cc` liest aber
        `self._cc_subs` (Mehrzahl) und holte dort den Produktionsunterteiler
        nach. Der ist auf 18.210 Grundvertices gebaut, der Testcharakter hat
        17.996 — beim ersten Unterteilen brach es mit

            ValueError: matmul: dimension mismatch with signature
            (n,k=18210),(k=17996,m)->(n,m)

        und die Verbindung riss ab. Ein Buchstabe Unterschied im Feldnamen.
        """
        return self._cc_subs.get('test')
