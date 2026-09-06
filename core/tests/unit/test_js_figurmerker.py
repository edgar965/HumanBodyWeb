# -*- coding: utf-8 -*-
u"""`Figurmerker`: je Figur den Reiter, die Animation und das Kleidungsstück merken.

WARUM (06.09.2026, Edgar): „Merke dir den letzten Tab und die Auswahl, die ich
beim letzten Mal hatte, als ich auf einem Modell geklickt habe, und öffne diese
Property beim nächsten Mal, wenn ich die Person auswähle."

Geprüft wird die Ablage selbst, ohne Seite: dass je Kennung getrennt gemerkt
wird, dass ein Eintrag den anderen nicht überschreibt, dass `vergessen` nur
die eine Figur trifft, dass eine leere Kennung (nichts ausgewählt) NICHTS
schreibt, und dass der Zettel im sessionStorage landet und von dort
zurückkommt — sonst wäre er nach einem Reload weg, obwohl die Szene
(`session.js`) wiederkommt.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'figurmerker.js')

#: sessionStorage, so viel davon, wie die Klasse anfasst — mit Mitschrift,
#: damit der Test sieht, WANN geschrieben wird.
ABLAGE = """
const geschrieben = [];
globalThis.sessionStorage = {
    _werte: {},
    getItem(k) { return k in this._werte ? this._werte[k] : null; },
    setItem(k, v) { this._werte[k] = String(v); geschrieben.push(k); },
};
"""

SKRIPT = ABLAGE + """
const { Figurmerker } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};

// --- leer: nichts gemerkt, nichts geschrieben -------------------------------
pruefe('leer tab', Figurmerker.tab('a'), null);
pruefe('leer animation', Figurmerker.animation('a'), null);
pruefe('leer kleider', Figurmerker.kleider('a'), null);
pruefe('nichts geschrieben', geschrieben.length, 0);

// --- ohne Kennung (keine Figur ausgewaehlt) wird NICHTS gemerkt --------------
Figurmerker.tabMerken(null, 'animation');
Figurmerker.animationMerken('', {name: 'x', url: '/x/'});
pruefe('ohne Kennung nichts geschrieben', geschrieben.length, 0);

// --- je Figur getrennt, Felder ueberschreiben sich nicht --------------------
Figurmerker.tabMerken('a', 'animation');
Figurmerker.animationMerken('a', {name: 'Walk', url: '/api/character/bvh/Walk/01_01/', category: 'Walk'});
Figurmerker.kleiderMerken('a', 'pants/cargo');
Figurmerker.tabMerken('b', 'kleider');
pruefe('a tab', Figurmerker.tab('a'), 'animation');
pruefe('a animation', Figurmerker.animation('a'),
       {name: 'Walk', url: '/api/character/bvh/Walk/01_01/', category: 'Walk'});
pruefe('a kleider', Figurmerker.kleider('a'), 'pants/cargo');
pruefe('b tab', Figurmerker.tab('b'), 'kleider');
pruefe('b animation bleibt leer', Figurmerker.animation('b'), null);
Figurmerker.tabMerken('a', 'kleider');
pruefe('a tab neu', Figurmerker.tab('a'), 'kleider');
pruefe('a animation bleibt', Figurmerker.animation('a').name, 'Walk');

// --- Animation ohne Adresse ist „nichts gewaehlt" ---------------------------
Figurmerker.animationMerken('a', {name: 'kaputt'});
pruefe('ohne url = null', Figurmerker.animation('a'), null);

// --- vergessen trifft nur die eine Figur -----------------------------------
Figurmerker.vergessen('a');
pruefe('a weg', Figurmerker.tab('a'), null);
pruefe('b bleibt', Figurmerker.tab('b'), 'kleider');

// --- der Zettel liegt im sessionStorage und kommt von dort zurueck ----------
pruefe('Schluessel', geschrieben[geschrieben.length - 1], Figurmerker.SCHLUESSEL);
const roh = JSON.parse(sessionStorage.getItem(Figurmerker.SCHLUESSEL));
pruefe('gespeichert', roh, {b: {tab: 'kleider'}});
Figurmerker._zettel = null;                      // wie nach einem Reload
pruefe('nach Reload', Figurmerker.tab('b'), 'kleider');

// --- kaputter Zettel wirft nicht ------------------------------------------
sessionStorage._werte[Figurmerker.SCHLUESSEL] = '{kaputt';
Figurmerker._zettel = null;
pruefe('kaputt = leer', Figurmerker.tab('b'), null);

console.log(JSON.stringify({ok: true, schreibungen: geschrieben.length}));
"""


class FigurmerkerTest(SimpleTestCase):

    def test_merkt_je_figur_und_ueberlebt_den_reload(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertGreater(ausgabe.get('schreibungen', 0), 0)
