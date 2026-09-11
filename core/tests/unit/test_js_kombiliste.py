# -*- coding: utf-8 -*-
u"""`Kombiliste`: welche Stuecke gemeinsam angezogen werden.

WARUM DIE LISTE (Edgar, 09.09.2026: „mach das gleichzeitige Anziehen
mehrere Stuecke, dann brauche ich aber auch ein UI dafuer")
=====================================================================
Der Reiter zeigt die Feineinstellungen von genau EINEM Stueck. Also erst
einstellen, uebernehmen, dann das naechste — und die Liste haelt je
Eintrag die Reglerwerte von DIESEM Augenblick.

DER SCHARFE FALL IST DIE KOPIE: `garmentcodeRegler.werte` ist EIN Objekt,
das bei jedem Reglerzug weitergeschrieben wird. Ein Verweis darauf hiesse,
dass das Einstellen des zweiten Stuecks rueckwirkend das erste aendert,
ohne dass in der Liste etwas anders aussieht.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'kombiliste.js')

SKRIPT = """
const { Kombiliste } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt '
                        + JSON.stringify(soll));
    }
};

// --- 1. Leer darf nicht gebaut werden ------------------------------------
// Ein einzelnes Stueck baut der gewoehnliche Weg schneller; ein
// „gemeinsamer" Lauf mit einem Stueck waere eine falsche Behauptung.
let liste = new Kombiliste();
pruefe('leer', liste.darfBauen().ok, false);
liste.hinzufuegen('hose', 'Hose', {});
pruefe('eines', liste.darfBauen().ok, false);
liste.hinzufuegen('t-shirt', 'T-Shirt', {});
pruefe('zwei', liste.darfBauen().ok, true);
pruefe('anzahl', liste.anzahl, 2);

// --- 2. DIE WERTE WERDEN KOPIERT -----------------------------------------
liste = new Kombiliste();
const lebend = { 'sleeve.length': 0.3 };
liste.hinzufuegen('t-shirt', 'T-Shirt', lebend);
lebend['sleeve.length'] = 1.0;          // spaeterer Reglerzug
lebend['collar.width'] = 5;
pruefe('Wert eingefroren', liste.eintraege[0].regler['sleeve.length'], 0.3);
pruefe('kein Nachtrag', 'collar.width' in liste.eintraege[0].regler, false);

// --- 3. Dasselbe Stueck zweimal ist erlaubt ------------------------------
// Zwei Roecke uebereinander, mit verschiedenen Reglern.
liste = new Kombiliste();
pruefe('erster Rock', liste.hinzufuegen('rock', 'Rock', {a: 1}).ok, true);
pruefe('zweiter Rock', liste.hinzufuegen('rock', 'Rock', {a: 2}).ok, true);
pruefe('beide da', liste.fuerServer().length, 2);
pruefe('eigene Werte', liste.fuerServer().map(e => e.regler.a), [1, 2]);

// --- 4. Die Hoechstzahl haelt --------------------------------------------
liste = new Kombiliste();
for (let i = 0; i < Kombiliste.HOECHSTZAHL; i++) {
    pruefe('Stueck ' + i, liste.hinzufuegen('x', 'X', {}).ok, true);
}
const zuviel = liste.hinzufuegen('x', 'X', {});
pruefe('einer zuviel', zuviel.ok, false);
if (!/chstens/.test(zuviel.grund)) {
    throw new Error('Die Begruendung nennt die Grenze nicht: ' + zuviel.grund);
}
pruefe('nicht gewachsen', liste.anzahl, Kombiliste.HOECHSTZAHL);

// --- 5. Ohne Vorlage geht nichts -----------------------------------------
liste = new Kombiliste();
for (const leer of ['', null, undefined]) {
    pruefe('ohne Vorlage', liste.hinzufuegen(leer, 'X', {}).ok, false);
}
pruefe('leer geblieben', liste.anzahl, 0);

// --- 6. Entfernen und Leeren ---------------------------------------------
liste = new Kombiliste();
liste.hinzufuegen('a', 'A', {});
liste.hinzufuegen('b', 'B', {});
liste.hinzufuegen('c', 'C', {});
pruefe('entfernen', liste.entfernen(1), true);
pruefe('bleibt', liste.eintraege.map(e => e.vorlage), ['a', 'c']);
pruefe('daneben', liste.entfernen(9), false);
pruefe('daneben negativ', liste.entfernen(-1), false);
liste.leeren();
pruefe('geleert', liste.anzahl, 0);

// --- 7. Der Server bekommt Vorlage, Regler und Bauwerte ------------------
// Titel und Zaehler sind Sache der Oberflaeche. `bau` seit 11.09.2026
// (`test_gemeinsambau`), ohne Angabe leer.
liste = new Kombiliste();
liste.hinzufuegen('hose', 'Hose', {'pants.flare': 0.5});
pruefe('fuerServer', liste.fuerServer(),
       [{vorlage: 'hose', regler: {'pants.flare': 0.5}, bau: {}}]);

// --- 8. Merken und Wiederherstellen --------------------------------------
// Eine Attrappe statt `localStorage`: Der Test laeuft in node.
const ablage = {
    inhalt: {},
    getItem(k) { return this.inhalt[k] ?? null; },
    setItem(k, v) { this.inhalt[k] = String(v); },
};
liste = new Kombiliste();
liste.hinzufuegen('hose', 'Hose', {'pants.flare': 0.5});
liste.hinzufuegen('t-shirt', 'T-Shirt', {});
pruefe('gesichert', liste.sichern(ablage), true);
const zurueck = new Kombiliste();
pruefe('geladen', zurueck.laden(ablage), true);
pruefe('gleiche Stuecke', zurueck.fuerServer(), liste.fuerServer());
pruefe('Titel dabei', zurueck.eintraege[1].titel, 'T-Shirt');

// --- 9. Kaputter Inhalt wird uebergangen, nicht geworfen -----------------
// Ein privates Fenster, geleerte Daten, eine alte Fassung des Formats:
// alles davon darf die Seite nicht zerlegen.
for (const roh of ['kein json', '"text"', '42', '[1, 2, 3]', '[{}]',
                   '[{"vorlage": 5}]']) {
    const k = new Kombiliste();
    k.laden({ getItem: () => roh, setItem() {} });
    if (k.anzahl !== 0) {
        throw new Error('Muell kam durch: ' + roh + ' -> ' + k.anzahl);
    }
}
// Eine gemerkte Liste, die zu lang ist, wird gekappt.
const zuviele = new Kombiliste();
zuviele.laden({ getItem: () => JSON.stringify(
    Array.from({length: 9}, () => ({vorlage: 'x', regler: {}}))),
    setItem() {} });
pruefe('gekappt', zuviele.anzahl, Kombiliste.HOECHSTZAHL);

// --- 10. Eine werfende Ablage darf nicht durchschlagen -------------------
const boese = { getItem() { throw new Error('nope'); },
                setItem() { throw new Error('nope'); } };
const k = new Kombiliste();
pruefe('laden ueberlebt', k.laden(boese), false);
k.hinzufuegen('a', 'A', {});
pruefe('sichern ueberlebt', k.sichern(boese), false);

console.log(JSON.stringify({ok: true}));
"""


class KombilisteTest(SimpleTestCase):

    databases = []

    def test_die_liste_haelt_sich_an_die_regeln(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_hoechstzahl_stimmt_mit_dem_server_ueberein(self):
        u"""Zwei Grenzen fuer dieselbe Sache laufen auseinander.

        Ist die im Browser groesser, laesst er eine Liste bauen, die der
        Server ablehnt — und der Nutzer sieht eine Fehlermeldung, wo die
        Oberflaeche haette bremsen muessen.
        """
        import io
        import re
        from GarmentCode.gemeinsamdienst import Garmentgemeinsam
        quelle = io.open(MODUL.pfad, encoding='utf-8').read()
        treffer = re.search(r'HOECHSTZAHL\s*=\s*(\d+)', quelle)
        self.assertIsNotNone(treffer, 'HOECHSTZAHL steht nicht im Modul')
        self.assertEqual(int(treffer.group(1)),
                         Garmentgemeinsam.HOECHSTZAHL)
