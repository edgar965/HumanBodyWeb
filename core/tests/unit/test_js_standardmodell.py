# -*- coding: utf-8 -*-
"""`Standardmodell`: die Wahl aus dem Figurwahl-Dialog in die Formularfelder.

Edgar (19.09.2026, Einstellungen → Szene): „auch ein Genesis, UMA usw. als
Standard-Modell auswählen … in einem Dialog."

1. Der Dialog hat alle sechs Reiter, ohne Lage-Felder, ohne Pflege.
2. `uebernehmen` schreibt Name, Figurart und Bereich in die Felder und den
   Anzeigetext mit Figurart und Unterzeile darunter.
3. `bereinigt`: unbekannte Figurart, unbekannter Bereich und leerer Name
   fallen auf die Vorgabe zurück (HumanBody, femaleWithClothes, gespeichert).
4. Ein Lader des Dialogs ruft `uebernehmen` mit dem Eintrag — so kommt der
   Bereich (standard/gespeichert) mit, den die Szene beim Laden braucht.
5. Seit 21.09.2026 auf allen Einstellungsseiten (Edgar: „Korrigiere das auch
   bei den anderen"): `ausKasten` liest Reiter (`data-quellen`) und Leertext
   (`data-leer`) vom Kasten; nur HumanBody für Theatre und Co., „Keins"
   leert das Feld, und ohne Leertext bleibt die alte Vorgabe.

Sabotage-Gegenprobe: `eintrag?.bereich || 'standard'` → `'standard'` in
`uebernehmen` → Fall 2 rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('..', 'js', 'einstellungen', 'standardmodell.js')

SKRIPT = """
const { Standardmodell } = await import(MODUL);
const fehler = [];
const fehl = (t) => fehler.push(t);

// Ein Kasten wie in der Vorlage: drei Felder, zwei Anzeigen, ein Knopf.
const felder = {};
const kasten = { querySelector(wahl) {
    const m = wahl.match(/\\[data-(feld|anzeige|tun)="(\\w+)"\\]/);
    if (!m) return null;
    const k = m[1] + ':' + m[2];
    return felder[k] || (felder[k] = { value: '', textContent: '', addEventListener() {} });
} };

// --- 1. der Dialog --------------------------------------------------------
const sm = new Standardmodell(kasten, { name: 'Female2', quelle: 'modell', bereich: 'gespeichert' });
if (sm.dialog.quellen.join() !== 'modell,smpl,makehuman,uma,umapython,genesis9') fehl('Reiter: ' + sm.dialog.quellen.join());
if (sm.dialog.lagefelder !== null) fehl('Lagefelder vorhanden');
if (sm.dialog.pflege !== null) fehl('Pflege vorhanden');
if (sm.dialog.knopf !== 'Übernehmen') fehl('Knopf: ' + sm.dialog.knopf);

// --- 2. uebernehmen ---------------------------------------------------------
sm.uebernehmen('genesis9', 'Victoria 9', { name: 'Victoria 9', anzeige: 'Victoria 9', bereich: 'standard',
                                            unterzeile: 'weiblich · 25.000 Punkte' });
if (felder['feld:name'].value !== 'Victoria 9') fehl('Name: ' + felder['feld:name'].value);
if (felder['feld:quelle'].value !== 'genesis9') fehl('Quelle: ' + felder['feld:quelle'].value);
if (felder['feld:bereich'].value !== 'standard') fehl('Bereich: ' + felder['feld:bereich'].value);
if (felder['anzeige:name'].textContent !== 'Victoria 9') fehl('Anzeige: ' + felder['anzeige:name'].textContent);
if (felder['anzeige:meta'].textContent !== 'Genesis 9 · Standard-Modell · weiblich · 25.000 Punkte') fehl('Meta: ' + felder['anzeige:meta'].textContent);
sm.uebernehmen('uma', 'Anprobe_a.glb', { name: 'Anprobe_a.glb', anzeige: 'Anprobe_a', bereich: 'gespeichert', unterzeile: '' });
if (felder['feld:bereich'].value !== 'gespeichert') fehl('Bereich UMA: ' + felder['feld:bereich'].value);
if (felder['anzeige:meta'].textContent !== 'UMA · gespeichertes Modell') fehl('Meta UMA: ' + felder['anzeige:meta'].textContent);

// --- 3. bereinigt -------------------------------------------------------------
const b = new Standardmodell(kasten, { name: '', quelle: 'quatsch', bereich: 'irgendwas' });
if (JSON.stringify(b.wahl) !== JSON.stringify(Standardmodell.VORGABE)) fehl('Vorgabe: ' + JSON.stringify(b.wahl));
const c = new Standardmodell(kasten, { name: 'X', quelle: 'smpl', bereich: 'standard' });
if (c.wahl.quelle !== 'smpl' || c.wahl.bereich !== 'standard' || c.wahl.name !== 'X') fehl('gültig: ' + JSON.stringify(c.wahl));

// --- 4. der Lader des Dialogs -----------------------------------------------
const ergebnis = await sm.dialog.lader.makehuman('base', null, { name: 'base', bereich: 'standard' });
if (ergebnis.quelle !== 'makehuman' || felder['feld:quelle'].value !== 'makehuman') fehl('Lader: ' + JSON.stringify(ergebnis));

// --- 5. nur HumanBody, leer erlaubt (Theatre, Effekte) -----------------------
const felder5 = {};
const kasten5 = { id: 'standardmodell-theatre_default_model',
    dataset: { quellen: 'modell', leer: '(Kein Auto-Load)' },
    querySelector(wahl) {
        const m = wahl.match(/\\[data-(feld|anzeige|tun)="(\\w+)"\\]/);
        if (!m) return null;
        if (m[1] === 'feld' && m[2] !== 'name') return null;   // nur das Namensfeld
        const k = m[1] + ':' + m[2];
        return felder5[k] || (felder5[k] = { value: '', textContent: '', addEventListener() {} });
    } };
const t = Standardmodell.ausKasten(kasten5);
if (t.dialog.quellen.join() !== 'modell') fehl('Theatre-Reiter: ' + t.dialog.quellen.join());
if (t.dialog.kennung !== 'standardmodell-theatre_default_model-dialog') fehl('Kennung: ' + t.dialog.kennung);
if (t.wahl.name !== '') fehl('leer erlaubt, aber Name: ' + t.wahl.name);
t.zeigen(null);
if (felder5['anzeige:name'].textContent !== '(Kein Auto-Load)') fehl('Leertext: ' + felder5['anzeige:name'].textContent);
if (felder5['anzeige:meta'].textContent !== '') fehl('Meta bei leer: ' + felder5['anzeige:meta'].textContent);
t.uebernehmen('modell', 'Female_Caucasian', { name: 'Female_Caucasian', anzeige: 'Female Caucasian',
                                              bereich: 'standard', unterzeile: 'weiblich · Körpertyp' });
if (felder5['feld:name'].value !== 'Female_Caucasian') fehl('Theatre-Name: ' + felder5['feld:name'].value);
if (felder5['anzeige:meta'].textContent !== 'HumanBody · Standard-Modell · weiblich · Körpertyp') fehl('Theatre-Meta: ' + felder5['anzeige:meta'].textContent);
t.leeren();
if (felder5['feld:name'].value !== '') fehl('Keins: ' + felder5['feld:name'].value);
if (felder5['anzeige:name'].textContent !== '(Kein Auto-Load)') fehl('Keins-Anzeige: ' + felder5['anzeige:name'].textContent);
// Ohne Leertext bleibt die Vorgabe, auch wenn das Feld leer ankommt.
felder5['feld:name'].value = '';
const u = Standardmodell.ausKasten({ ...kasten5, dataset: { quellen: 'modell', leer: '' } });
if (u.wahl.name !== 'femaleWithClothes') fehl('Vorgabe ohne Leertext: ' + u.wahl.name);

console.log(JSON.stringify({ ok: fehler.length === 0, fehler }));
"""


class StandardmodellTest(SimpleTestCase):
    databases = set()

    def test_die_wahl_landet_in_den_feldern(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
