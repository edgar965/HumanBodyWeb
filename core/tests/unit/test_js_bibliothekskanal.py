# -*- coding: utf-8 -*-
"""Bibliothekskanal: ein Tab löscht, die anderen holen ihren Baum neu.

WARUM (Edgar, 16.09.2026: „nach löschen einer Animation z.B. bei
/humanbody/scene/ oder BVH-Studio (kontext menü) ist die Animation immer noch
im Baum"): Der löschende Tab holte seinen Baum neu, ein daneben offener Tab
(Szene, Studio, Animationen) nicht — dort stand der Eintrag, bis man die Seite
neu lud. Dazu stand der Eintrag auch im löschenden Tab noch, solange das
Neuladen dauerte (unter Last 9 s, gemessen im Log).

1. `Bibliothekskanal` (Node, `BroadcastChannel`): eine Meldung erreicht einen
   ANDEREN Kanal desselben Namens mit Aktion und Daten; der Sender selbst
   bekommt sie nicht; Abmelden wirkt.
2. Verdrahtung: die drei Sender (`Bibliothekablage`, `Animationsmenue`,
   `bvhManage`) melden nach dem Erfolg; die drei Bäume hören; Studio und Szene
   nehmen den gelöschten Eintrag sofort aus dem Baum, vor dem Neuladen.

Sabotage-Gegenprobe: in `Bibliothekskanal.melden` das `postMessage` entfernen
→ Fall 1 rot (keine Meldung beim Empfänger).
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'bibliothekskanal.js')
VIEWER = Jsmodul.VIEWER

SKRIPT = """
const { Bibliothekskanal: K } = await import(MODUL);
const gleich = (was, a, b) => {
    if (a !== b) throw new Error(was + ': ' + a + ' statt ' + b); };
const warten = (ms) => new Promise(r => setTimeout(r, ms));
const anderer = new BroadcastChannel(K.NAME);
const empfangen = [];
anderer.onmessage = (e) => empfangen.push(e.data);
const eigene = [];
const abmelden = K.hoeren((m) => eigene.push(m));
K.melden('delete', { category: 'A_Results', name: 'probe' });
await warten(50);
gleich('empfangen', empfangen.length, 1);
gleich('aktion', empfangen[0].aktion, 'delete');
gleich('kategorie', empfangen[0].category, 'A_Results');
gleich('name', empfangen[0].name, 'probe');
gleich('sender bekommt nichts', eigene.length, 0);
// ein zweiter Kanal im selben Prozess erreicht den Hörer
anderer.postMessage({ aktion: 'rename' });
await warten(50);
gleich('hoeren', eigene.length, 1);
gleich('hoeren aktion', eigene[0].aktion, 'rename');
abmelden();
anderer.postMessage({ aktion: 'move' });
await warten(50);
gleich('abgemeldet', eigene.length, 1);
anderer.close(); K.kanal().close();
console.log(JSON.stringify({ ok: true }));
"""


class BibliothekskanalTest(SimpleTestCase):
    def test_meldung_erreicht_andere_kanaele_nicht_den_sender(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

    def test_sender_und_hoerer_haengen_am_kanal(self):
        melden = 'Bibliothekskanal.melden('
        sender = (
            ('studio', 'bibliothekablage.js', melden + 'aktion, daten);'),
            ('scene', 'animationsmenue.js', melden + 'aktion, daten);'),
            ('animation', 'baum.js', melden + 'action, data);'),
            ('scene', 'animation.js', melden + "'save', { category, name });"),
        )
        for ordner, datei, marke in sender:
            self.assertIn(marke, BibliothekskanalTest._text(ordner, datei), datei)
        hoeren = 'Bibliothekskanal.hoeren(() => '
        hoerer = (
            ('studio', 'bibliotheksbaum.js', hoeren + 'this.laden());'),
            ('scene', 'animation.js', hoeren + 'loadAnimationUI());'),
            ('animation', 'baum.js', hoeren + 'loadAnimationTree());'),
        )
        for ordner, datei, marke in hoerer:
            self.assertIn(marke, BibliothekskanalTest._text(ordner, datei), datei)
        # Sofort aus dem Baum, bevor das Neuladen (unter Last Sekunden) fertig ist.
        studio = BibliothekskanalTest._text('studio', 'bibliothekmenues.js')
        self.assertLess(
            studio.index('this.baum.eintragEntfernen(ziel.category, ziel.name);'),
            studio.index('this.baum.laden();', studio.index('async loeschen(ziel)')),
        )
        szene = BibliothekskanalTest._text('scene', 'animation.js')
        entfernt = szene.index('item.remove();')
        self.assertLess(entfernt, szene.index('return Animationsentfernung.nach(anim, cat, {'))
        self.assertLess(
            szene.index('const eintraege = Animationsentfernung.'),
            entfernt,
            'Nachfolger wird VOR dem Entfernen bestimmt',
        )

    @staticmethod
    def _text(*teile):
        return VIEWER.joinpath(*teile).read_text(encoding='utf-8')
