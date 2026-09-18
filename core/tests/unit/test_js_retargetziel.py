# -*- coding: utf-8 -*-
"""Figurarten im Studio: `Retargetziel` und der Schlüssel der Modellzuständigkeit.

WARUM (Edgar, 15.09.2026: „bei Modell hinzufügen, mach das unterteilt, in
HumanBody, UMA, MakeHuman usw"): Ein Menüpunkt, der eine UMA-Figur in die
Zeitleiste legt, braucht ein Studio, das sie baut UND bespielt. Der Retarget
kennt die Ziele längst (Szene); hier steht, wie das Studio sie wählt:

1. HumanBody → kein Ziel (DEF), Schlüssel `def`, keine Abfrage.
2. UMA → `target=uma&figur=<glb>`; SMPL → `smpl` mit Körper; MakeHuman →
   `makehuman` mit Makros/Reglern im Rumpf (POST); UMA Python → `umapython`
   mit der Rasse, DNA im Rumpf.
3. Der Schlüssel unterscheidet Ziel, Figur UND Höhe — ein Clip, der für ein
   anderes Skelett gebaut wurde, wird neu geholt (`Bvhspur._neuHolen`).
4. `Modellzustaendigkeit.schluessel`: HumanBody bleibt der nackte Name,
   sonst `quelle:name`; `zerlegen` ist die Umkehrung.

Dazu die Verdrahtung als Quelltext: Spurkopfmenü zweigeteilt, Modellmenü mit
Ordnern je Figurart, `Spurfigurarten` mit allen fünf Bauern, Ruhelage je Art.

Sabotage-Gegenprobe: in `Retargetziel.wahl` `schluessel` ohne `figur` → Fall 3
rot (zwei UMA-Dateien hätten denselben Schlüssel).
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul
from ._studiovorlage import Studiovorlage

MODUL = Jsmodul("bvh_studio", "retargetziel.js")
ZUSTAENDIG = Jsmodul("bvh_studio", "modellzustaendigkeit.js")
STUDIO = Jsmodul.VIEWER / "bvh_studio"

SKRIPT = """
const { Retargetziel: R } = await import(MODUL);
const gleich = (was, a, b) => { if (a !== b) throw new Error(was + ': ' + a + ' statt ' + b); };
// 1. HumanBody
const def = R.wahl(null);
gleich('def target', def.target, null); gleich('def schluessel', def.schluessel, 'def');
gleich('def abfrage', R.abfrage(def), '');
gleich('modell-quelle', R.wahl({ quelle: 'modell' }).schluessel, 'def');
// 2. die fünf eigenen Ziele
const uma = R.wahl({ quelle: 'uma', datei: 'Female Elf.glb' }, 1.7);
gleich('uma target', uma.target, 'uma'); gleich('uma figur', uma.figur, 'Female Elf.glb');
gleich('uma abfrage', R.abfrage(uma), '&target=uma&figur=Female%20Elf.glb&body_height=1.7000');
gleich('uma rumpf', uma.rumpf, null);
const smpl = R.wahl({ quelle: 'smpl', koerper: 'mean_female' });
gleich('smpl', R.abfrage(smpl), '&target=smpl&figur=mean_female');
const mh = R.wahl({ quelle: 'makehuman', modell: 'basis', makro: { a: 1 }, regler: { b: 2 } });
gleich('mh target', mh.target, 'makehuman');
gleich('mh rumpf', JSON.stringify(mh.rumpf), '{"makro":{"a":1},"regler":{"b":2}}');
const up = R.wahl({ quelle: 'umapython', rasse: 'Human Female 3.0', dna: { height: 0.6 } });
gleich('up figur', up.figur, 'Human Female 3.0');
gleich('up rumpf', JSON.stringify(up.rumpf), '{"makro":null,"regler":{"height":0.6}}');
const g9 = R.wahl({ quelle: 'genesis9', figur: 'amala', regler: { Amala_figure_ctrl_Character: 1 } }, 1.7);
gleich('g9 target', g9.target, 'genesis9'); gleich('g9 figur', g9.figur, 'amala');
gleich('g9 rumpf', JSON.stringify(g9.rumpf), '{"makro":null,"regler":{"Amala_figure_ctrl_Character":1}}');
gleich('g9 ohne figur', R.wahl({ quelle: 'genesis9' }).figur, 'basis');
// 3. Schlüssel trennt Ziel, Figur, Höhe
const a = R.wahl({ quelle: 'uma', datei: 'a.glb' }, 1.7).schluessel;
const b = R.wahl({ quelle: 'uma', datei: 'b.glb' }, 1.7).schluessel;
const c = R.wahl({ quelle: 'uma', datei: 'a.glb' }, 1.8).schluessel;
if (a === b || a === c || a === def.schluessel) throw new Error('Schlüssel unterscheidet nicht');
gleich('gleiche Figur gleicher Schlüssel', a, R.wahl({ quelle: 'uma', datei: 'a.glb' }, 1.7).schluessel);
console.log(JSON.stringify({ ok: true }));
"""

SKRIPT_ZUSTAENDIG = """
const { Modellzustaendigkeit: Z } = await import(MODUL);
const gleich = (was, a, b) => { if (a !== b) throw new Error(was + ': ' + a + ' statt ' + b); };
gleich('humanbody', Z.schluessel({ preset: 'Female1' }), 'Female1');
gleich('modell', Z.schluessel({ preset: 'Female1', quelle: 'modell' }), 'Female1');
gleich('uma', Z.schluessel({ preset: 'Elf.glb', quelle: 'uma' }), 'uma:Elf.glb');
gleich('leer', Z.schluessel({}), null);
gleich('zerlegen hb', JSON.stringify(Z.zerlegen('Female1')), '{"quelle":"modell","preset":"Female1"}');
gleich('zerlegen uma', JSON.stringify(Z.zerlegen('uma:Elf:x.glb')), '{"quelle":"uma","preset":"Elf:x.glb"}');
const fps = 30;
const spur = { clips: [{ type: 'model', startFrame: 0, duration: 2, data: { preset: 'M', quelle: 'smpl' } }] };
gleich('preset liefert Schlüssel', Z.preset(spur, 1, fps), 'smpl:M');
gleich('ausserhalb', Z.preset(spur, 3, fps), null);
console.log(JSON.stringify({ ok: true }));
"""


class RetargetzielTest(SimpleTestCase):
    def test_ziele_abfrage_rumpf_und_schluessel(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get("ok"))

    def test_schluessel_der_modellzustaendigkeit(self):
        self.assertTrue(ZUSTAENDIG.laufen(SKRIPT_ZUSTAENDIG).get("ok"))

    def test_spurkopfmenue_zweigeteilt_und_modellmenue_je_figurart(self):
        vorlage = Studiovorlage.text()
        kopf = vorlage[vorlage.index('id="track-context-menu"') :]
        for kennung in (
            "track-ctx-add-label",
            "track-ctx-anim",
            "track-ctx-bvh-submenu",
            "ctx-mimik-track",
            "ctx-script-track",
        ):
            self.assertIn(kennung, kopf)
        kontext = RetargetzielTest._text(STUDIO / "zeitleiste_kontextmenue.js")
        self.assertIn("modell ? 'Modell hinzufügen' : 'Hinzufügen'", kontext)
        self.assertIn("Modellhinzufuegen.fuellen(spur, index, menue, bild,", kontext)
        modelle = RetargetzielTest._text(STUDIO / "menue_modelle.js")
        self.assertIn("for (const quelle of Figurkataloge.REIHENFOLGE)", modelle)
        self.assertIn("clip.data = { preset: zeile.name, quelle,", modelle)

    def test_studio_baut_und_bespielt_alle_sechs_figurarten(self):
        arten = RetargetzielTest._text(STUDIO / "spurfigurarten.js")
        for bauer in (
            "async modell(",
            "async uma(",
            "async makehuman(",
            "async smpl(",
            "async umapython(",
            "async genesis9(",
        ):
            self.assertIn(bauer, arten)
        self.assertIn("spur.modell?.ruhelageHerstellen", arten)
        clip = RetargetzielTest._text(STUDIO / "clipanimation.js")
        self.assertIn("Retargetziel.wahl(spur.modell, spur.figurHoehe)", clip)
        self.assertIn("clip._animZiel = ziel.schluessel;", clip)
        self.assertIn("ziel.rumpf ? await Serverabruf.senden(adresse, ziel.rumpf)", clip)
        # Der erste Abruf rechnet den Retarget (43 s bei 7.538 Bildern, 16.09.2026:
        # „keine Animation zu sehen … erst jetzt, nach ca. 1 Minute") — solange
        # steht es oben rechts, danach Bildzahl und gemessene Dauer.
        self.assertLess(clip.index("wird umgesetzt${bilder} …`"), clip.index("try {"))
        self.assertIn("${sekunden.toFixed(1)} s)`, 4000);", clip)
        bvh = RetargetzielTest._text(STUDIO / "bvhspur.js")
        self.assertIn("clip._animZiel !== ziel) Bvhspur._neuHolen(spur, clip);", bvh)
        self.assertIn("Spurfigurarten.ruhelage(spur);", bvh)
        self.assertIn(
            "quelle: c.data.quelle || 'modell'", RetargetzielTest._text(STUDIO / "projekt_daten.js")
        )
        self.assertIn(
            "track.quelle = td.quelle || 'modell';",
            RetargetzielTest._text(STUDIO / "projekt_wiederherstellung.js"),
        )
        self.assertIn(
            "for (const quelle of Figurkataloge.REIHENFOLGE)",
            RetargetzielTest._text(STUDIO / "modellwahl.js"),
        )

    @staticmethod
    def _text(pfad):
        return pfad.read_text(encoding="utf-8")
