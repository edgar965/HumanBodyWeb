# -*- coding: utf-8 -*-
"""`Genesis9teilregler`: welche Formregler hinter dem Zahnrad eines Teils stehen (09.10.2026), Node-Test.

Edgar: „Gibt es nicht mehr Einstellungen zu den Augenbrauen usw.?" — es gab sie, verstreut in der Liste
„Kopf" mit 386 Reglern (Brauen 9 + 4 Asymmetrie + 6 HB-Morphs, Wimpern 28, Nägel 5; im Popup gezählt). Das
Popup zeigt sie jetzt als Block „Form".

1. Brauen: nur Regler mit „brow" in Anzeige- oder Kanalname, auch die HB-Morphs (`hb:Eyebrows_*`) — aber KEIN
   Mimik-Regler (Brow Up, Brow Down sind Ausdrücke, keine Form).
2. Wimpern und Nägel: dasselbe Muster auf „lash" und „nail", ebenfalls ohne Mimik.
3. Augen nimmt als einziger Teil einen Mimik-Regler mit (`Eye Pupils Dilate`) und die Größe (`Eyes Scale`).
4. Jeder Kanal einmal, auch wenn er in zwei Bereichen steht; unbekannter Teil und leerer Plan → leere Liste.
5. `block` ohne passenden Regler liefert null (kein leerer Kopf im Popup).

Sabotage-Gegenprobe: `if (bereich.schluessel === 'mimik' && !art.mimik) continue;` streichen → Fall 1 rot;
die `gesehen`-Menge streichen → Fall 4 rot; `mimik: true` beim Teil „augen" streichen → Fall 3 rot.
Nicht gelaufen (09.10.2026).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('charakter', 'genesis9', 'genesis9teilregler.js')

SKRIPT = """
const { Genesis9teilregler: T } = await import(MODUL);
const r = (name, anzeige) => ({ name, anzeige: anzeige || name });
const plan = { bereiche: [
    { schluessel: 'kopf', regler: [
        r('200_head_bs_Brows Depth-0xa0f819c', '200+ Brows Depth'),
        r('head_bs_AsymmetryBrowHeightLeft', 'Asymmetry Brow Height Left'),
        r('head_bs_EyelashesCurvature', 'Eyelashes Curvature'), r('head_bs_NoseSize', 'Nose Size'),
        r('200_head_bs_Eyes Scale-0xa0f81b1', '200+ Eyes Scale'),
        r('200_head_bs_Eyes Depth', '200+ Eyes Depth') ] },
    { schluessel: 'mimik', regler: [
        r('facs_ctrl_BrowUp', 'Brow Up'), r('facs_bs_EyePupilsDilate', 'Eye Pupils Dilate'),
        r('facs_ctrl_EyesBlink', 'Eye Blink') ] },
    { schluessel: 'haende', regler: [ r('body_bs_NailsLengthRound', 'Nails Length Round') ] },
    { schluessel: 'hb_gesicht', regler: [
        r('hb:Eyebrows_Angle', 'Eyebrows Angle'), r('head_bs_AsymmetryBrowHeightLeft', 'Doppelt') ] },
] };
const namen = teil => T.reglerFuer(plan, teil).map(x => x.name);

// 1. Brauen: Form ja (auch HB-Morph), Mimik nein
pruefe('Brauen', namen('brauen'),
       ['200_head_bs_Brows Depth-0xa0f819c', 'head_bs_AsymmetryBrowHeightLeft', 'hb:Eyebrows_Angle']);
// 2. Wimpern, Nägel
pruefe('Wimpern', namen('wimpern'), ['head_bs_EyelashesCurvature']);
pruefe('Nägel', namen('naegel'), ['body_bs_NailsLengthRound']);
// 3. Augen: Größe und Pupille (Mimik ausdrücklich erlaubt), nicht Tiefe/Blinzeln
pruefe('Augen', namen('augen'), ['200_head_bs_Eyes Scale-0xa0f81b1', 'facs_bs_EyePupilsDilate']);
// 4. jeder Kanal einmal; unbekannter Teil, leerer Plan
pruefe('einmal', namen('brauen').filter(n => n === 'head_bs_AsymmetryBrowHeightLeft').length, 1);
pruefe('unbekannt', T.reglerFuer(plan, 'mund'), []);
pruefe('leer', [T.reglerFuer(null, 'brauen'), T.reglerFuer({}, 'brauen')], [[], []]);
// 5. Block ohne Regler: null (kein DOM nötig)
pruefe('Block leer', T.block({ bereiche: [] }, 'brauen', () => null), null);
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9teilreglerTest(SimpleTestCase):
    databases = set()

    def test_formregler_je_teil_ohne_mimik_und_ohne_doppelte(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
