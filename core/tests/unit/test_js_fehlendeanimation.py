# -*- coding: utf-8 -*-
"""`Fehlendeanimation`: 404 vom Retarget auf der Charakter-Seite (`/Charakter/`).

WARUM (Edgar, 24.09.2026): „Falls es Animationen gibt im Studio oder
Charakter die es nicht mehr auf der Platte gibt, dann Fehlermeldung, mit
Abfrage ob die gelöscht werden sollen." Vorher stand nur „Fehler: ..." in der
Zeile unter der Leiste, ohne dass die gemerkte Auswahl (`Figurmerker`)
aufgeräumt wurde — der nächste Play-Versuch derselben Figur landete wieder
in derselben 404.

Geprüft wird: nur ein Fehler mit `status === 404` wird behandelt (sonst
`false` — der Aufrufer zeigt dann seine eigene Fehlermeldung); bei „Ja" wird
die gemerkte Auswahl bei ALLEN betroffenen Figuren gelöscht
(`Figurmerker.animationVergessen`); bei „Nein" bleibt sie stehen; die
Bezeichnung in der Meldung kommt aus der URL (`Kategorie/Name`).
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'fehlendeanimation.js')

#: `Fehlendeanimation` importiert `Figurmerker`, der `sessionStorage` braucht.
ABLAGE = """
globalThis.sessionStorage = {
    _werte: {},
    getItem(k) { return k in this._werte ? this._werte[k] : null; },
    setItem(k, v) { this._werte[k] = String(v); },
};
"""

SKRIPT = (
    ABLAGE
    + """
const { Fehlendeanimation } = await import(MODUL);
// Dieselbe (gespiegelte) Datei wie `Fehlendeanimation` importiert — der
// ES-Modul-Cache liefert darum dieselbe Instanz zurueck, keine zweite.
const FIGURMERKER = MODUL.replace(/fehlendeanimation\\.js$/, 'figurmerker.js');
const { Figurmerker } = await import(FIGURMERKER);

const meldungen = [];
const melden = (t) => meldungen.push(t);

// --- kein 404: unbehandelt, der Aufrufer zeigt seine eigene Meldung -------
pruefe('kein 404', Fehlendeanimation.behandeln(new Error('boom'), { url: '/x/' }, melden), false);
pruefe('nichts gemeldet ohne 404', meldungen.length, 0);
pruefe('ohne Fehlerobjekt', Fehlendeanimation.behandeln(null, { url: '/x/' }, melden), false);

// --- 404, Ja: bei allen Figuren geloescht ----------------------------------
Figurmerker.animationMerken('a', { name: 'Walk', url: '/api/character/bvh/Walk/01/', category: 'Walk' });
Figurmerker.animationMerken('b', { name: 'Walk', url: '/api/character/bvh/Walk/01/', category: 'Walk' });
globalThis.confirm = () => true;
const fehler404 = Object.assign(new Error('nicht gefunden'), { status: 404 });
const behandelt = Fehlendeanimation.behandeln(
    fehler404, { url: '/api/character/bvh/Walk/01/', name: 'Walk' }, melden);
pruefe('als 404 behandelt', behandelt, true);
pruefe('a geloescht', Figurmerker.animation('a'), null);
pruefe('b geloescht', Figurmerker.animation('b'), null);
pruefe('Meldung nennt Kategorie/Name', /Walk\\/01/.test(meldungen[meldungen.length - 1]), true);

// --- 404, Nein: bleibt stehen -----------------------------------------------
Figurmerker.animationMerken('c', { name: 'Run', url: '/api/character/bvh/Run/02/', category: 'Run' });
globalThis.confirm = () => false;
Fehlendeanimation.behandeln(
    Object.assign(new Error('nicht gefunden'), { status: 404 }),
    { url: '/api/character/bvh/Run/02/', name: 'Run' }, melden);
pruefe('c bleibt bei Nein', Figurmerker.animation('c').name, 'Run');

console.log(JSON.stringify({ ok: true }));
"""
)


class FehlendeanimationTest(SimpleTestCase):
    def test_404_fragt_alles_andere_nicht(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
