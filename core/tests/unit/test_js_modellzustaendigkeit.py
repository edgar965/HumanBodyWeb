# -*- coding: utf-8 -*-
u"""`Modellzustaendigkeit`: je Animationsspur setzt genau EINE Modellspur die Figur.

WARUM (11.09.2026, Edgar: „bei Klick auf Play im BVH Studio verschwindet das
Modell"): Zwei Modellspuren an derselben Animation — eine mit Clips, eine
leere — versteckten die Figur abwechselnd und lösten je Bild ein neues Laden
des Presets aus (39× `preset_load_start` in einer Minute im Client-Log). Der
Fall hier ist das Projekt TechnoDance nachgestellt.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('bvh_studio', 'modellzustaendigkeit.js')

SKRIPT = """
const { Modellzustaendigkeit } = await import(MODUL);
const pruefe = (was, ist) => { if (!ist) throw new Error(was); };
const FPS = 30;
const clip = (startFrame, dauer, preset) =>
    ({ type: 'model', startFrame, duration: dauer, data: { preset } });

const animation = { type: 'bvh', name: 'Animation 1', clips: [] };
const modell1 = { type: 'model', name: 'Modell 1', muted: false, _linkedAnimIdx: 0,
                  clips: [clip(0, 12, 'Female1'), clip(600, 46, 'FemaleGarment')] };
const modell2 = { type: 'model', name: 'Modell 2', muted: false, _linkedAnimIdx: 0, clips: [] };
const fremd = { type: 'model', name: 'Fremd', muted: false, _linkedAnimIdx: 5,
                clips: [clip(0, 999, 'Rig2')] };
const spuren = [animation, modell1, modell2, fremd];
const Z = Modellzustaendigkeit;

pruefe('im Clip: Modell 1', Z.spur(spuren, 0, 1, FPS) === modell1);
pruefe('Preset im Clip', Z.preset(modell1, 1, FPS) === 'Female1');
pruefe('Lücke: trotzdem Modell 1, nie die leere', Z.spur(spuren, 0, 13, FPS) === modell1);
pruefe('Lücke ohne Preset', Z.preset(modell1, 13, FPS) === null);
pruefe('zweiter Clip', Z.preset(modell1, 21, FPS) === 'FemaleGarment');
pruefe('andere Animation zählt nicht', Z.spur(spuren, 0, 1, FPS) !== fremd);
pruefe('unverknüpft: null', Z.spur([animation, fremd], 0, 1, FPS) === null);

// Die leere Spur bekommt einen Clip dort, wo Modell 1 keinen hat → dort gilt sie.
modell2.clips.push(clip(400 * 30, 10, 'Rig2'));
pruefe('Clip der zweiten füllt die Lücke', Z.spur(spuren, 0, 400, FPS) === modell2);
pruefe('erste hat Vorrang, wo beide Clips haben', Z.spur(spuren, 0, 1, FPS) === modell1);

// Stumm geschaltete Spur bestimmt nichts.
modell1.muted = true;
pruefe('stumm: die zweite', Z.spur(spuren, 0, 1, FPS) === modell2);
console.log(JSON.stringify({ok: true}));
"""


class ModellzustaendigkeitTest(SimpleTestCase):

    databases = set()

    def test_eine_spur_je_animation(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
