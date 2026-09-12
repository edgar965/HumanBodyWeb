# -*- coding: utf-8 -*-
u"""`Animationsentfernung`: was nach dem Löschen einer Animation geschieht.

WARUM (12.09.2026, Edgar): „nach löschen einer Animation geht der Tab zu, die
alte Animation bleibt usw. Es soll der Eintrag verschwinden, auf die nächste
Animation selektiert werden, und die aktuelle Animation soll stoppen."

Geprüft ohne DOM und ohne Three.js:

1. Der Nachfolger ist der nächste im selben Ordner, sonst der vorige dort,
   sonst der nächste der Liste, sonst der vorige — oder null.
2. `nach` stoppt NUR, wenn die gelöschte Animation gerade läuft (Adresse,
   nicht Name: zwei Ordner dürfen gleichnamige Dateien führen), nimmt sie
   allen Figuren aus dem Merker, holt den Baum neu und wählt den Nachfolger
   für die ausgewählte Figur — hervorgehoben und gemerkt, nicht geladen.
3. Ohne ausgewählte Figur wird nichts gemerkt; ohne Rest wird nichts gewählt.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'animationsentfernung.js')

SKRIPT = """
const { Animationsentfernung: A } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const e = (name, category) => ({ name, url: '/bvh/' + category + '/' + name + '/', category });
const baum = [e('a1', 'A'), e('a2', 'A'), e('a3', 'A'), e('b1', 'B'), e('c1', 'C')];

// --- 1. Nachfolger -----------------------------------------------------------
pruefe('naechster im Ordner', A.nachfolger(baum, 'A', 'a2').name, 'a3');
pruefe('letzter im Ordner -> voriger dort', A.nachfolger(baum, 'A', 'a3').name, 'a2');
pruefe('einziger im Ordner -> naechster der Liste', A.nachfolger(baum, 'B', 'b1').name, 'c1');
pruefe('letzter der Liste, allein im Ordner -> voriger', A.nachfolger(baum, 'C', 'c1').name, 'b1');
pruefe('einziger ueberhaupt -> null', A.nachfolger([e('x', 'X')], 'X', 'x'), null);
pruefe('unbekannt -> null', A.nachfolger(baum, 'A', 'gibtsnicht'), null);
const namensvettern = [e('w', 'A'), e('w', 'B')];
pruefe('gleicher Name, anderer Ordner', A.nachfolger(namensvettern, 'B', 'w').name, 'w');
pruefe('gleicher Name: der andere Ordner', A.nachfolger(namensvettern, 'B', 'w').category, 'A');
pruefe('keine Liste', A.nachfolger(null, 'A', 'a1'), null);

// --- 2. nach: stoppen, vergessen, Baum neu, Nachfolger waehlen --------------
const umfeld = (state) => {
    const ablauf = [];
    return { ablauf, umfeld: {
        eintraege: baum, state,
        fn: { stopAnimation: (d) => ablauf.push('stop:' + d),
              animationMarkieren: (n) => ablauf.push('markieren:' + n) },
        merker: { animationVergessen: (u) => { ablauf.push('vergessen:' + u); return 1; },
                  animationMerken: (id, w) => ablauf.push('merken:' + id + ':' + w.name) },
        baumNeu: async () => ablauf.push('baumNeu'),
        meldung: (t) => ablauf.push('meldung:' + t),
    } };
};

// die geloeschte laeuft gerade (Adresse passt)
let s = { currentAnimUrl: '/bvh/A/a2/', currentAnimName: 'a2', selectedCharacterId: 'fig1' };
let { ablauf, umfeld: u } = umfeld(s);
let erg = await A.nach(e('a2', 'A'), 'A', u);
pruefe('gestoppt', erg.gestoppt, true);
pruefe('Nachfolger', erg.gewaehlt.name, 'a3');
pruefe('Reihenfolge', ablauf,
       ['stop:true', 'vergessen:/bvh/A/a2/', 'baumNeu', 'markieren:a3', 'merken:fig1:a3',
        'meldung:„a2" gelöscht — „a3" gewählt.']);
pruefe('Name der Wahl im Zustand', s.currentAnimName, 'a3');

// eine ANDERE laeuft: nicht stoppen, aber vergessen und waehlen
s = { currentAnimUrl: '/bvh/C/c1/', currentAnimName: 'c1', selectedCharacterId: 'fig1' };
({ ablauf, umfeld: u } = umfeld(s));
erg = await A.nach(e('a2', 'A'), 'A', u);
pruefe('nicht gestoppt', erg.gestoppt, false);
pruefe('kein stop im Ablauf', ablauf.filter((z) => z.startsWith('stop')), []);
pruefe('trotzdem vergessen', ablauf[0], 'vergessen:/bvh/A/a2/');
pruefe('c1 laeuft weiter', s.currentAnimUrl, '/bvh/C/c1/');

// gleicher Name in anderem Ordner laeuft: Adresse entscheidet
s = { currentAnimUrl: '/bvh/A/w/', currentAnimName: 'w', selectedCharacterId: 'fig1' };
({ ablauf, umfeld: u } = umfeld(s));
u.eintraege = [e('w', 'A'), e('w', 'B')];
erg = await A.nach(e('w', 'B'), 'B', u);
pruefe('Namensvetter laeuft weiter', erg.gestoppt, false);

// --- 3. ohne Figur nichts merken; ohne Rest nichts waehlen ------------------
s = { currentAnimUrl: '', currentAnimName: 'a2', selectedCharacterId: null };
({ ablauf, umfeld: u } = umfeld(s));
erg = await A.nach(e('a2', 'A'), 'A', u);
pruefe('ohne Adresse zaehlt der Name', erg.gestoppt, true);
pruefe('ohne Figur nicht gemerkt', ablauf.filter((z) => z.startsWith('merken')), []);
pruefe('aber markiert', ablauf.includes('markieren:a3'), true);

s = { currentAnimUrl: '/bvh/X/x/', currentAnimName: 'x', selectedCharacterId: 'fig1' };
({ ablauf, umfeld: u } = umfeld(s));
u.eintraege = [e('x', 'X')];
erg = await A.nach(e('x', 'X'), 'X', u);
pruefe('nichts uebrig', erg.gewaehlt, null);
pruefe('nichts markiert', ablauf.filter((z) => z.startsWith('markieren')), []);
pruefe('Name geleert', s.currentAnimName, '');
pruefe('Meldung ohne Wahl', ablauf[ablauf.length - 1], 'meldung:„x" gelöscht.');

console.log(JSON.stringify({ ok: true }));
"""


class AnimationsentfernungTest(SimpleTestCase):

    def test_stoppt_vergisst_und_waehlt_den_nachfolger(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
