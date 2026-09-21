# -*- coding: utf-8 -*-
"""`Ladehinweis`: Play, während die Animation noch lädt, zeigt ein Popup.

Edgar (21.09.2026, BVH Studio): „bei start auf Play der Animation tut sich
nichts. Mach einen Popup, falls die Animation noch lädt."

1. `offen` nennt die Figur einer Spur ohne Netz und jeden Bewegungsclip ohne
   `animClip`; ein Clip mit `_loadError` zählt nicht, Spuren ohne
   Bewegungsclips (Kamera, Modell, leere Bewegungsspur) auch nicht.
2. Ist alles da, ist `offen` leer — Play läuft ohne Popup (`togglePlay` fragt
   `zeigen` nur, solange nicht gespielt wird).

Sabotage-Gegenprobe: `!c._loadError` in `offen` streichen → Fall 1 rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('bvh_studio', 'ladehinweis.js')

SKRIPT = """
const { Ladehinweis } = await import(MODUL);
const fehler = [];
const fehl = (t) => fehler.push(t);

const clip = (name, animClip = null, extra = {}) => ({ type: 'bvh', name, animClip, ...extra });
const spurA = { type: 'bvh', name: 'Animation 1', mesh: null, clips: [clip('tanz')] };
const spurB = { type: 'bvh', name: 'Animation 2', mesh: {}, _loadingPreset: 'uma:Female',
                clips: [clip('gehen', {}), clip('weg', null, { _loadError: true }), clip('laufen')] };
const leer = { type: 'bvh', name: 'Animation 3', mesh: null, clips: [] };
const kamera = { type: 'camera', name: 'Kamera', clips: [{ type: 'camera_kf', name: 'K1' }] };
const state = { project: { tracks: [spurA, spurB, leer, kamera] } };

// --- 1. was noch fehlt ------------------------------------------------------
const offen = Ladehinweis.offen(state).map(o => o.spur + ': ' + o.was);
const soll = ['Animation 1: Figur', 'Animation 1: Bewegung „tanz"',
              'Animation 2: Figur „uma:Female"', 'Animation 2: Bewegung „laufen"'];
if (JSON.stringify(offen) !== JSON.stringify(soll)) fehl('offen: ' + JSON.stringify(offen));

// --- 2. alles da -> nichts offen --------------------------------------------
spurA.mesh = {}; spurA.clips[0].animClip = {};
spurB._loadingPreset = null; spurB.clips[2].animClip = {};
const rest = Ladehinweis.offen(state);
if (rest.length) fehl('noch offen: ' + JSON.stringify(rest));

console.log(JSON.stringify({ ok: fehler.length === 0, fehler }));
"""


class LadehinweisTest(SimpleTestCase):
    databases = set()

    def test_play_waehrend_des_ladens_nennt_was_fehlt(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_togglePlay_fragt_den_ladehinweis(self):
        from pathlib import Path

        from django.conf import settings
        text = (Path(settings.BASE_DIR) / 'static' / 'viewer' / 'bvh_studio' / 'playback.js').read_text(encoding='utf-8')
        self.assertIn('if (!state.playing && Ladehinweis.zeigen(state, togglePlay)) return;', text)
