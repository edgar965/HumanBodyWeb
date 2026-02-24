import json
import logging

import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer

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


class CharacterConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for live character morphing."""

    async def connect(self):
        await self.accept()
        self._char_state = None
        self._cc_sub = None
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

            # Reuse the CC subdivider singleton from character_api
            from core.character_api import _get_cc_subdivider
            self._cc_sub = _get_cc_subdivider()
        except Exception as e:
            logger.error("Failed to init CharacterState: %s", e)

    async def disconnect(self, close_code):
        self._char_state = None
        self._cc_sub = None

    async def _send_vertices(self, vertices):
        """Send vertices, applying CC subdivision if available."""
        if self._cc_sub is not None:
            vertices = self._cc_sub.subdivide(vertices)
        await self.send(bytes_data=vertices.astype(np.float32).tobytes())

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return

        try:
            msg = json.loads(text_data)
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
            self._char_state.set_body_type(msg['value'])
            vertices = self._char_state.compute()
            await self._send_vertices(vertices)

        elif msg_type == 'gender':
            self._char_state.set_gender(float(msg['value']))
            vertices = self._char_state.compute()
            await self._send_vertices(vertices)

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

        elif msg_type == 'reset':
            body_type = msg.get('body_type', 'Female_Caucasian')
            self._char_state.set_body_type(body_type)
            self._char_state.set_gender(0.0)
            self._char_state._morph_values.clear()
            vertices = self._char_state.compute()
            await self._send_vertices(vertices)
