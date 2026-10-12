# -*- coding: utf-8 -*-
"""`Kleidersichtbarkeit`: „Kleider ein/aus" überlebt den Neubau der Stücke (11.10.2026), geprüft in Node.

Edgar: „Der Toggle Kleider ein/aus funktioniert nicht bei den Genesis Modellen." Gemessen im Chrome (Ursula1): der Schalter setzt `visible = false` an allen Netzen von `inst.clothMeshes`; beim Wechsel aufs feine
Netz zieht `Genesis9kleidung.anziehen` jedes Stück neu an, die neuen Netze waren wieder sichtbar, der Knopf zeigte weiter „aus". Das Modul rechnet nur über `inst.clothMeshes` und `inst.kleiderSichtbar` (Attrappen).

1. Ein Stück, das es gibt und sichtbar ist, entsteht wieder sichtbar; ist es ausgeblendet (Schalter oder einzeln), entsteht es ausgeblendet.
2. Ein Stück mit mehreren Teilen (`kennung/0`, `kennung/1`): sichtbar, wenn ein Teil sichtbar ist.
3. Ein Stück, das es noch nicht gibt, folgt dem Schalter: nach `setzen(inst, false)` unsichtbar, ohne Schalter sichtbar.
4. Ein ganzer Schlüssel (`gc_schuh`, `humanbody_frisur/0`) trifft nur sich selbst, ein Name nicht den Schlüssel eines anderen Stücks mit gleichem Anfang (`daz_a` gegen `daz_ab/0`).

Sabotage-Gegenprobe: in `fuer` die Zeile `if (alt.length) …` streichen → Fälle 1 und 2 rot; `startsWith(`${name}/`)` durch `startsWith(name)` ersetzen → Fall 4 rot; `setzen` leeren → Fall 3 rot.
Gelaufen 12.10.2026 (3 Tests, grün); die Sabotage-Gegenprobe ist nicht gefahren.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'kleidersichtbarkeit.js')


class KleidersichtbarkeitTest(SimpleTestCase):
    databases = set()

    def test_ein_neues_netz_erbt_die_sichtbarkeit_des_alten(self):
        skript = """
const { Kleidersichtbarkeit: K } = await import(MODUL);
const netz = (sichtbar) => ({ visible: sichtbar });

// 1. gibt es schon: Stand des alten Netzes
const inst = { clothMeshes: { 'hose/0': netz(false), 'hemd/0': netz(true), 'gc_schuh': netz(false), 'humanbody_frisur/0': netz(true) } };
pruefe('ausgeblendet bleibt aus', K.fuer(inst, 'hose'), false);
pruefe('sichtbar bleibt an', K.fuer(inst, 'hemd'), true);
pruefe('GarmentCode-Schlüssel ohne Nummer', K.fuer(inst, 'gc_schuh'), false);
pruefe('ganzer Schlüssel der Frisur', K.fuer(inst, 'humanbody_frisur/0'), true);

// 2. mehrere Teile: sichtbar, wenn ein Teil sichtbar ist
const teile = { clothMeshes: { 'kleid/0': netz(false), 'kleid/1': netz(true) } };
pruefe('ein Teil sichtbar', K.fuer(teile, 'kleid'), true);
teile.clothMeshes['kleid/1'].visible = false;
pruefe('alle Teile aus', K.fuer(teile, 'kleid'), false);

// 3. neues Stück folgt dem Schalter
const figur = { clothMeshes: {} };
pruefe('ohne Schalter sichtbar', K.fuer(figur, 'neu'), true);
K.setzen(figur, false);
pruefe('Schalter aus: neues Stück unsichtbar', K.fuer(figur, 'neu'), false);
K.setzen(figur, true);
pruefe('Schalter wieder an', K.fuer(figur, 'neu'), true);

// 4. Namensanfang ist kein Treffer
const nachbar = { kleiderSichtbar: true, clothMeshes: { 'daz_ab/0': netz(false) } };
pruefe('daz_a trifft daz_ab/0 nicht', K.fuer(nachbar, 'daz_a'), true);
pruefe('ohne Figur sichtbar', K.fuer(null, 'x'), true);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = MODUL.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_die_scham_ist_keine_kleidung(self):
        """Edgar, 12.10.2026 (Bild „cute girl DAZ"): Nach „Kleider aus" war die Scham weg und die eingebaute Körper-Scham zu sehen. Das Stück hat `hautTiefe` > 0.

        5. `istKoerperteil`: wahr nur bei `userData.hautTiefe` > 0 (Scham aus der .blend), nicht bei Kleidung, Haar, Augen (`hautTiefe` 0 oder fehlt).
        6. `anwenden(inst, false)` blendet Kleidung aus, die Scham bleibt; `anwenden(inst, true)` zeigt alles, auch eine vorher ausgeblendete Scham.
        7. `fuer` gibt für ein Körperteil immer wahr zurück, auch wenn sein altes Netz ausgeblendet war (neu gebaute Scham entsteht sichtbar).

        Sabotage-Gegenprobe: in `istKoerperteil` `> 0` zu `> 1` → Fälle 5 und 6 rot; in `anwenden` die Ausnahme streichen → Fall 6 rot. Nicht gelaufen (12.10.2026).
        """
        skript = """
const { Kleidersichtbarkeit: K } = await import(MODUL);
const netz = (sichtbar, tiefe) => ({ visible: sichtbar, userData: tiefe === undefined ? {} : { hautTiefe: tiefe } });

// 5. istKoerperteil
pruefe('Scham', K.istKoerperteil(netz(true, 0.03)), true);
pruefe('Kleidung ohne hautTiefe', K.istKoerperteil(netz(true)), false);
pruefe('hautTiefe 0 (Vorgabe)', K.istKoerperteil(netz(true, 0)), false);
pruefe('kein Netz', K.istKoerperteil(null), false);

// 6. anwenden
const inst = { clothMeshes: { 'hose/0': netz(true, 0), 'hemd/0': netz(true), 'daz5_scham/0': netz(true, 0.03) } };
K.anwenden(inst, false);
pruefe('Kleider aus, Scham bleibt', [inst.clothMeshes['hose/0'].visible, inst.clothMeshes['hemd/0'].visible, inst.clothMeshes['daz5_scham/0'].visible], [false, false, true]);
inst.clothMeshes['daz5_scham/0'].visible = false;           // eine früher ausgeblendete Scham kommt mit „an" wieder
K.anwenden(inst, true);
pruefe('alles an', Object.values(inst.clothMeshes).map(n => n.visible), [true, true, true]);
K.anwenden(null, false);                                    // ohne Figur: nichts

// 7. fuer
const alt = { kleiderSichtbar: false, clothMeshes: { 'daz5_scham/0': netz(false, 0.03), 'hose/0': netz(false, 0) } };
pruefe('Scham entsteht sichtbar', K.fuer(alt, 'daz5_scham'), true);
pruefe('Hose entsteht ausgeblendet', K.fuer(alt, 'hose'), false);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = MODUL.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_die_originalaugen_sind_keine_kleidung(self):
        """Edgar, 12.10.2026: „Augen werden wohl zu den Kleidern hinzugezählt, bei dem Push auf den Kleider disable Button verschwinden die Augen."

        Das Stück `cute_girl_augen` ersetzt die Augen der Figur (`userData.ersetzt = ['augen']`, `Genesis9ersatz` blendet deren Netze aus) — mit dem Stück weg bleiben leere Höhlen.

        8. `istKoerperteil` ist auch wahr bei `userData.ersetzt` mit Einträgen, falsch bei leerer Liste.
        9. `anwenden(inst, false)` lässt die Ersatz-Augen stehen; sind sie von gewählten Augen verdrängt (`ersatzGewichen`), bleiben sie unsichtbar, auch bei `anwenden(inst, true)`.

        Sabotage-Gegenprobe: in `istKoerperteil` den `ersetzt`-Zweig streichen → Fall 8 und 9 rot; in `anwenden` `!netz.userData.ersatzGewichen` durch `true` ersetzen → letzte Prüfung rot. Nicht gelaufen (12.10.2026).
        """
        skript = """
const { Kleidersichtbarkeit: K } = await import(MODUL);
const netz = (sichtbar, ud) => ({ visible: sichtbar, userData: ud });

pruefe('Augenstück', K.istKoerperteil(netz(true, { ersetzt: ['augen'] })), true);
pruefe('leere Liste', K.istKoerperteil(netz(true, { ersetzt: [] })), false);

const inst = { clothMeshes: { 'cute_girl_augen/0': netz(true, { ersetzt: ['augen'] }), 'hemd/0': netz(true, { ersetzt: [] }) } };
K.anwenden(inst, false);
pruefe('Kleider aus, Augen bleiben', [inst.clothMeshes['cute_girl_augen/0'].visible, inst.clothMeshes['hemd/0'].visible], [true, false]);

inst.clothMeshes['cute_girl_augen/0'].userData.ersatzGewichen = true;       // andere Augen gewählt: das Ersatzpaar bleibt weg
K.anwenden(inst, true);
pruefe('verdrängte Augen bleiben aus', [inst.clothMeshes['cute_girl_augen/0'].visible, inst.clothMeshes['hemd/0'].visible], [false, true]);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = MODUL.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
