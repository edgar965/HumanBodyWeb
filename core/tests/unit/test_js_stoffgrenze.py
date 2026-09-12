# -*- coding: utf-8 -*-
u"""Die JavaScript-Stoffgrenze gegen die Python-Fassung — dieselben Zahlen.

`gemeinsam/stoffgrenze.js` haelt im Browser den Weichgewebe-Zuschlag der
Kleidung aus dem Koerper; `TheatreJS/ModelPhysik/stoffgrenze.py` tut es im
Server-Video. Zwei Fassungen derselben Rechnung laufen auseinander, wenn
niemand sie aneinander haelt: Hier rechnet Python auf einem Kunstkoerper
(Kugel, nach aussen gewickelt) mit Zufallsstoff und Zufallsversatz, und
Node muss Punkt fuer Punkt dasselbe liefern — gekuerzter Versatz auf 1e-9,
dieselbe Zahl gekuerzter Punkte, dieselbe Durchdringung.

Die Naeherung der JS-Fassung (naechster Koerperpunkt in RUHE bestimmt, nicht
je Bild) prueft der zweite Fall: Koerper und Stoff starr verschoben — dort
muss das Ergebnis exakt dem einer frischen Python-Suche gleichen.

Und das Gitter selbst (`punktgitter.js`) gegen die rohe Suche: jeder
Treffer muss der wirklich naechste sein. Sabotage-Gegenprobe gemacht:
Ohne den Ringabbruch (`break` entfernt) bleibt der Test gruen — der Ring
laeuft dann nur weiter; mit einer falschen Schale (`<=` statt `<` im
Abbruch) wird er rot.
"""
import json
import os
import sys

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul
from ._pruefablage import Pruefablage

MODUL = Jsmodul('gemeinsam', 'stoffgrenze.js')
GITTER = Jsmodul('gemeinsam', 'punktgitter.js')
MODELPHYSIK = os.path.join(str(settings.BASE_DIR), 'TheatreJS', 'ModelPhysik')


SKRIPT = """
const { Stoffgrenze } = await import(MODUL);
// Die Fixture kommt aus einer Datei: 130 KB passen nicht in die
// Kommandozeile von `node -e` (Windows: 32 KB).
const F = JSON.parse((await import('node:fs')).readFileSync(FIXTURE, 'utf-8'));
const f32 = (l) => Float32Array.from(l.flat());
const f64 = (l) => Float64Array.from(l.flat());
// Ruhelage in f64: Der Sollabstand je Punkt wird daraus gerechnet und muss Python auf 1e-9 treffen.
const grenze = new Stoffgrenze(f64(F.koerper), Uint32Array.from(F.dreiecke.flat()), f64(F.stoff));
if (grenze.aussen !== 1) throw new Error('Wickelrichtung: ' + grenze.aussen);
for (let i = 0; i < F.soll.length; i++) {
    if (Math.abs(grenze.soll[i] - F.soll[i]) > 1e-9) throw new Error(`Sollabstand ${i}: ${grenze.soll[i]} statt ${F.soll[i]}`);
}
let geprueft = 0, geaendert = 0;
for (const fall of F.faelle) {
    const koerper = f64(fall.koerper), stoff = f64(fall.stoff);
    // Beim Messfall bleibt der Versatz unangetastet: gekuerzt wird ein Nullversatz.
    const versatz = fall.nur_messen ? new Float64Array(stoff.length) : f64(fall.versatz);
    const vorher = f64(fall.versatz);
    const zahl = grenze.kuerzen(stoff, versatz, koerper, null);
    if (zahl !== fall.gekuerzt) throw new Error(`${fall.name}: ${zahl} gekuerzt statt ${fall.gekuerzt}`);
    const soll = fall.ergebnis.flat();
    for (let i = 0; i < soll.length; i++) {
        if (Math.abs(versatz[i] - soll[i]) > 1e-9) throw new Error(`${fall.name}: Index ${i} ist ${versatz[i]} statt ${soll[i]}`);
        if (versatz[i] !== vorher[i]) geaendert += 1;
    }
    geprueft += soll.length;
    const nachher = new Float64Array(stoff.length);
    for (let i = 0; i < stoff.length; i++) nachher[i] = stoff[i] + (fall.nur_messen ? f64(fall.versatz)[i] : versatz[i]);
    const d = grenze.durchdringung(nachher, koerper, null);
    if (Math.abs(d.prozent - fall.durchdringung[0]) > 1e-6 || Math.abs(d.tiefe_mm - fall.durchdringung[1]) > 1e-6) {
        throw new Error(`${fall.name}: Durchdringung ${d.prozent} / ${d.tiefe_mm} statt ${fall.durchdringung}`);
    }
}
// Gegenprobe der Gegenrichtung: ein nach INNEN gewickelter Koerper wird erkannt.
const rueck = Uint32Array.from(F.dreiecke.map(([a, b, c]) => [a, c, b]).flat());
if (new Stoffgrenze(f32(F.koerper), rueck, f32(F.stoff)).aussen !== -1) throw new Error('Innenwicklung nicht erkannt');
console.log(JSON.stringify({ ok: true, geprueft, geaendert }));
"""

GITTER_SKRIPT = """
const { Punktgitter } = await import(MODUL);
let saat = 7;
const zufall = () => { saat = (saat * 16807) % 2147483647; return saat / 2147483647; };
const n = 4000, m = 600;
const wolke = new Float32Array(n * 3), fragen = new Float32Array(m * 3);
for (let i = 0; i < n * 3; i++) wolke[i] = zufall() * (i % 3 === 1 ? 1.8 : 0.6);
for (let i = 0; i < m * 3; i++) fragen[i] = zufall() * 2.2 - 0.2;   // auch ausserhalb der Wolke
const gitter = new Punktgitter(wolke);
const ist = gitter.alleNaechsten(fragen);
let falsch = 0;
for (let q = 0; q < m; q++) {
    let best = -1, bd = Infinity;
    for (let i = 0; i < n; i++) {
        const d = (wolke[3*i]-fragen[3*q])**2 + (wolke[3*i+1]-fragen[3*q+1])**2 + (wolke[3*i+2]-fragen[3*q+2])**2;
        if (d < bd) { bd = d; best = i; }
    }
    if (best !== ist[q]) falsch += 1;
}
if (falsch) throw new Error(`${falsch} von ${m} Anfragen fanden nicht den naechsten Punkt`);
console.log(JSON.stringify({ ok: true, anfragen: m, zelle: gitter.zelle, zellen: gitter.dim }));
"""


class StoffgrenzeJsTest(SimpleTestCase):

    databases = set()

    def _fixture(self):
        if MODELPHYSIK not in sys.path:
            sys.path.insert(0, MODELPHYSIK)
        from stoffgrenze import Stoffgrenze
        zufall = np.random.default_rng(3)
        mitte = (0.0, 1.0, 0.0)
        koerper, dreiecke = StoffgrenzeJsTest._kugelnetz(mitte=mitte)
        stoff = StoffgrenzeJsTest._stoff(zufall, 300, 0.3, mitte)
        ruhe = Stoffgrenze(koerper, dreiecke)
        # Der Sollabstand je Punkt aus der Ruhelage — so rechnet die
        # JS-Fassung im Konstruktor (11.09.2026).
        soll = ruhe.sollabstand(stoff)
        faelle = []
        ohne_grenze = None
        for name, schub in ((u'Ruhe', np.zeros(3)),
                            (u'verschoben', np.array([0.5, -0.2, 0.3])),
                            (u'eingedrueckt', np.zeros(3)),
                            (u'koerper_aussen', np.zeros(3))):
            k, s = koerper + schub, stoff + schub
            if name == u'koerper_aussen':
                # Der KOERPER geht 12 mm nach aussen (sein eigener
                # Weichgewebe-Zuschlag), der Stoff hat keinen Versatz. Die
                # alte Fassung kuerzte hier nichts (kein einwaerts gerichteter
                # Stoffversatz) — und die Haut stand durch die Leggings.
                k = koerper + 0.012 * ruhe.normalen
            grenze = Stoffgrenze(k, dreiecke)
            _abstand, naechster = grenze.baum.query(s)
            if name == u'eingedrueckt':
                # Nur MESSEN: alle Punkte 0 bis 20 mm in den Koerper
                # gedrueckt, nichts gekuerzt — die Durchdringungsprobe muss
                # sie zaehlen.
                tiefe = zufall.uniform(0.0, 0.020, size=(len(s), 1))
                versatz = -grenze.normalen[naechster] * tiefe
                ergebnis, zahl = np.zeros_like(versatz), 0
            elif name == u'koerper_aussen':
                versatz = np.zeros_like(s)
                ohne_grenze = grenze.durchdringung(s)[0]
                ergebnis, zahl = grenze.kuerzen(s, versatz, soll)
            else:
                versatz = zufall.normal(scale=0.012, size=s.shape)
                ergebnis, zahl = grenze.kuerzen(s, versatz, soll)
            # Die Durchdringung MIT DER BINDUNG DER RUHELAGE — so misst die
            # JS-Fassung. Pythons `durchdringung()` sucht je Aufruf neu und
            # findet fuer einen seitlich verschobenen Punkt womoeglich einen
            # anderen Nachbarn; das ist die Naeherung, nicht ein Fehler.
            rest = (s + versatz if name == u'eingedrueckt' else s + ergebnis)
            aussen = np.sum((rest - k[naechster]) * grenze.normalen[naechster],
                            axis=1)
            drin = aussen < -Stoffgrenze.TOLERANZ
            faelle.append({
                'name': name, 'koerper': k.tolist(), 'stoff': s.tolist(),
                'versatz': versatz.tolist(), 'ergebnis': ergebnis.tolist(),
                'gekuerzt': zahl, 'nur_messen': name == u'eingedrueckt',
                'durchdringung': [float(drin.mean()) * 100.0,
                                  float(-aussen[drin].min()) * 1000.0
                                  if drin.any() else 0.0],
                # Pythons eigene Probe auf denselben Punkten: Sie MUSS die
                # tiefste Stelle nennen, nicht die flachste (Fehler bis
                # 11.09.2026: `.max()` auf negativen Werten).
                'tiefe_python_mm': grenze.durchdringung(rest)[1],
            })
        # Dictionary gewollt: geht als JSON an das Node-Skript.
        return {'koerper': koerper.tolist(), 'dreiecke': dreiecke.tolist(),
                'stoff': stoff.tolist(), 'soll': soll.tolist(), 'faelle': faelle,
                'koerper_aussen_ohne_grenze': ohne_grenze}

    def test_js_kuerzt_wie_python(self):
        fixture = self._fixture()
        from stoffgrenze import Stoffgrenze      # nach `_fixture`: setzt den Pfad
        # Der Fall muss etwas zu kuerzen haben — sonst prueft er nichts.
        self.assertGreater(fixture['faelle'][0]['gekuerzt'], 20)
        self.assertLess(fixture['faelle'][0]['gekuerzt'], 300)
        # Und die Messprobe muss Punkte IM Koerper haben, sonst misst sie nichts.
        mess = fixture['faelle'][2]
        self.assertGreater(mess['durchdringung'][0], 20.0)
        # Der tiefste Punkt liegt bei bis zu 20 mm Eindrueckung tief, nicht
        # bei einem Millimeter.
        self.assertGreater(mess['tiefe_python_mm'], 10.0)
        self.assertAlmostEqual(mess['tiefe_python_mm'], mess['durchdringung'][1], places=6)
        # Der Koerper von innen: OHNE Stoffversatz muss angehoben werden —
        # jeder Punkt, dessen Ruheabstand unter 12 mm + Soll liegt. Danach
        # steckt nur noch im Koerper, was schon in RUHE darin stand (der
        # Kunstkoerper ist facettiert; ein Punkt ueber der Flaechenmitte
        # misst gegen die Punktnormale bis 1,6 mm „innen"). Mit der alten
        # Fassung war hier `gekuerzt` 0 (Sabotage-Gegenprobe gemacht).
        aussen = fixture['faelle'][3]
        soll = np.asarray(fixture['soll'])
        self.assertGreater(fixture['koerper_aussen_ohne_grenze'], 30.0)
        self.assertGreater(aussen['gekuerzt'], 100)
        in_ruhe_drin = 100.0 * float((soll < -Stoffgrenze.TOLERANZ).mean())
        self.assertLessEqual(aussen['durchdringung'][0], in_ruhe_drin)
        self.assertLess(aussen['durchdringung'][0], 2.0)
        # Eine Leggings auf 2 mm bekommt 2 mm als Soll, nicht 6.
        self.assertLess(soll.min(), 0.0025)
        self.assertAlmostEqual(soll.max(), 0.006, places=9)
        with Pruefablage.datei(json.dumps(fixture), '.json',
                               'stoffgrenze_') as pfad:
            skript = SKRIPT.replace('FIXTURE,', json.dumps(pfad) + ',', 1)
            ausgabe = MODUL.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertEqual(ausgabe['geprueft'], 4 * 300 * 3)
        self.assertGreater(ausgabe['geaendert'], 0)

    def test_gitter_findet_den_naechsten(self):
        ausgabe = GITTER.laufen(GITTER_SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertEqual(ausgabe['anfragen'], 600)

    @staticmethod
    def _kugelnetz(ringe=14, segmente=18, radius=0.3, mitte=(0.0, 1.0, 0.0)):
        u"""Geschlossene Kugel, Dreiecke NACH AUSSEN gewickelt."""
        punkte = [np.array(mitte) + [0, radius, 0]]
        for r in range(1, ringe):
            phi = np.pi * r / ringe
            for s in range(segmente):
                theta = 2 * np.pi * s / segmente
                punkte.append(np.array(mitte) + radius * np.array(
                    [np.sin(phi) * np.cos(theta), np.cos(phi),
                     np.sin(phi) * np.sin(theta)]))
        punkte.append(np.array(mitte) - [0, radius, 0])
        unten = len(punkte) - 1
        dreiecke = []
        for s in range(segmente):
            dreiecke.append([0, 1 + (s + 1) % segmente, 1 + s])
        for r in range(ringe - 2):
            a = 1 + r * segmente
            b = a + segmente
            for s in range(segmente):
                s2 = (s + 1) % segmente
                dreiecke.append([a + s, a + s2, b + s])
                dreiecke.append([a + s2, b + s2, b + s])
        a = 1 + (ringe - 2) * segmente
        for s in range(segmente):
            dreiecke.append([unten, a + s, a + (s + 1) % segmente])
        return np.array(punkte, dtype=np.float64), np.array(dreiecke, dtype=np.int64)

    @staticmethod
    def _stoff(zufall, zahl, radius, mitte):
        richtung = zufall.normal(size=(zahl, 3))
        richtung /= np.linalg.norm(richtung, axis=1, keepdims=True)
        # Abstand zur Haut zwischen 1 und 30 mm — einige nahe, einige weit.
        abstand = zufall.uniform(0.001, 0.030, size=(zahl, 1))
        return np.array(mitte) + richtung * (radius + abstand)
