# -*- coding: utf-8 -*-
"""`Proportionenmarker`: Marker setzen, löschen, alle setzen — je Quelle, für jede Sicht (20.09.2026).

Herausgelöst aus dem Dialog, als die Modellsicht oben auf der Seite eine zweite
Sicht auf denselben Zustand wurde. Der Dialog ist hier eine Attrappe mit dem
Zustand (`quellen`, `lagen`, `start`, `entfernt`, `eingaben`, `sichten`) und
zählt, wie oft er nachzeichnet und meldet:

1. `setzen` legt die Linie waagerecht um den Punkt, Länge = Wert in cm × Maßstab,
   merkt sie als Start, nimmt sie aus `entfernt`, markiert sie in JEDER Sicht
   dieser Quelle — und nur dort.
2. `setzen` auf ein Maß, das schon liegt, tut nichts; ohne Quelle nichts.
3. `loeschen` nimmt Linie und Start, merkt `entfernt`, hebt die Markierung auf.
4. `alle` setzt jedes Maß, das die Ziel-Ansicht kennt und das noch fehlt — an
   der vorgeschlagenen Höhe — mit EINEM Nachzeichnen und EINER Meldung.
5. `alleLoeschen` leert die Eingaben, holt entfernte Marker zurück, Linien = Start.
6. Sabotage: eine Linie mit falscher Länge (Wert nicht in Pixel umgerechnet) — der
   Vergleich schlägt an.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('bildmodell', 'proportionenmarker.js')

SKRIPT = """
const { Proportionenmarker: M } = await import(MODUL);
const kopie = o => JSON.parse(JSON.stringify(o));
const sicht = id => ({ bild: { quelle: { id }, aktiv: null } });
const foto = { id: 'foto:a.jpg', art: 'foto', ansicht: 'vorn', breite: 1000, hoehe: 2000, px_je_m: 1000 };
const ziel = { linien: { ziel: { taille_breite: [[250, 900], [350, 900]],
                                 huefte_breite: [[200, 1100], [400, 1100]] } },
               px_je_m: { ziel: 500 } };
const d = {
    katalog: { proportionen: [{ schluessel: 'taille_breite' }, { schluessel: 'huefte_breite' },
                              { schluessel: 'brust_tiefe' }] },
    quellen: { [foto.id]: foto, 'ziel:vorn': { id: 'ziel:vorn', art: 'ziel', ansicht: 'vorn',
                                               breite: 600, hoehe: 800, px_je_m: 500 } },
    lagen: { [foto.id]: { huefte_breite: [[300, 1200], [600, 1200]] } },
    start: { [foto.id]: { huefte_breite: [[300, 1200], [600, 1200]] } },
    entfernt: { [foto.id]: new Set(['taille_breite']) },
    eingaben: { taille_breite: 24 },
    sichten: [sicht(foto.id), sicht('ziel:vorn'), sicht(foto.id)],
    tabelle: null, _quellstand: 'x',
    gezeichnet: 0, gemeldet: 0,
    daten: () => ({ ziel: { taille_breite: 22, huefte_breite: 30 }, ansichten: { vorn: ziel } }),
    wert(id, k) { return this.eingaben[k] ?? this.daten().ziel[k]; },
    nachzeichnen() { this.gezeichnet += 1; },
    aenderung() { this.gemeldet += 1; },
    quellenAufbauen() { this.lagen = kopie(this.start); this.entfernt = { [foto.id]: new Set() }; },
};

// 1. setzen: um den Punkt, Länge 24 cm × 1000 px/m = 240 px
M.setzen(d, 'taille_breite', [500, 800], foto.id);
pruefe('Linie um den Punkt', d.lagen[foto.id].taille_breite, [[380, 800], [620, 800]]);
pruefe('Start gemerkt', d.start[foto.id].taille_breite, [[380, 800], [620, 800]]);
pruefe('nicht mehr entfernt', d.entfernt[foto.id].has('taille_breite'), false);
pruefe('markiert in beiden Sichten der Quelle', [d.sichten[0].bild.aktiv, d.sichten[2].bild.aktiv],
       ['taille_breite', 'taille_breite']);
pruefe('andere Quelle nicht markiert', d.sichten[1].bild.aktiv, null);
pruefe('nachgezeichnet und gemeldet', [d.gezeichnet, d.gemeldet], [1, 1]);

// 2. schon da / ohne Quelle: nichts
M.setzen(d, 'taille_breite', [100, 100], foto.id);
M.setzen(d, 'brust_tiefe', [100, 100], null);
pruefe('unverändert', d.lagen[foto.id].taille_breite, [[380, 800], [620, 800]]);
pruefe('keine weitere Meldung', d.gemeldet, 1);

// 3. löschen
M.loeschen(d, 'taille_breite', foto.id);
pruefe('Linie weg', d.lagen[foto.id].taille_breite, undefined);
pruefe('Start weg', d.start[foto.id].taille_breite, undefined);
pruefe('entfernt', d.entfernt[foto.id].has('taille_breite'), true);
pruefe('Markierung weg', d.sichten[0].bild.aktiv, null);
pruefe('gemeldet', d.gemeldet, 2);

// 4. alle: Taille fehlt und die Ziel-Ansicht kennt sie → Höhe aus dem Nachbarn Hüfte
//    (Hüfte im Foto bei y 1200, im Ziel 1100 → Taille 900: 200 px Ziel × 1000/500 = 400 px höher → 800)
M.alle(d, foto.id);
pruefe('Taille gesetzt', d.lagen[foto.id].taille_breite, [[330, 800], [570, 800]]);
pruefe('Brusttiefe nicht (nicht von vorn)', d.lagen[foto.id].brust_tiefe, undefined);
pruefe('einmal gezeichnet, einmal gemeldet', [d.gezeichnet, d.gemeldet], [3, 3]);

// 5. alle Vorgaben löschen
M.alleLoeschen(d);
pruefe('Eingaben leer', d.eingaben.taille_breite, null);
pruefe('entfernte Marker zurück', d.entfernt[foto.id].size, 0);
pruefe('Linien wie Start', d.lagen[foto.id].huefte_breite, [[300, 1200], [600, 1200]]);

// 6. Sabotage: ohne Umrechnung wäre die Linie 24 px statt 240
const falsch = [[488, 800], [512, 800]];
if (JSON.stringify(falsch) === JSON.stringify(d.start[foto.id].taille_breite)) {
    throw new Error('Sabotage nicht erkannt');
}
console.log(JSON.stringify({ ok: true }));
"""


class ProportionenmarkerTest(SimpleTestCase):
    databases = set()

    def test_marker_je_quelle_fuer_jede_sicht(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
