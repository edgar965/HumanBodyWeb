# -*- coding: utf-8 -*-
"""`Figurwahlfuellung`: die Modelle stehen, bevor die abgebrochenen Importe da sind (Edgar, 10.10.2026).

Edgar: „warum dauert das Aufbauen des Dialogs so lange?" — der Genesis-9-Reiter blieb auf „Lade …", bis auch die Liste der verwaisten Importe
(`/api/character/blendimport/verwaist/`: 1,5 bis 41 s im `client.log`) da war; die Modelle selbst brauchten 0,3–1,2 s. Geprüft wird mit einer
DOM-Attrappe und gesteuerten Abrufen:

1. Die Modelle stehen in der Liste, während der Abruf der Importe noch aussteht; danach stehen die Importe dahinter.
2. Eine späte Antwort eines überholten Füllens (Löschen, Umbenennen starten ein neues) wird verworfen.
3. Eine schon getroffene Wahl wird nach dem Neuaufbau der Zeilen wieder markiert.
4. Scheitert der Abruf der Modelle, steht der Fehler in der Liste und die Importe werden gar nicht erst angefragt.

Sabotage-Gegenprobe: in `fuellen` vor `_zeigen` `await importe` setzen → Fall 1 rot; die Bedingung `this.stand[quelle] === lauf` streichen → Fall 2 rot;
in `_zeigen` den Aufruf `dialog._waehlen(dialog.gewaehlt)` streichen → Fall 3 rot; `Figurwahlimporte.zeilen` vor dem Abruf der Modelle
starten (`const importe = …` an den Anfang) → Fall 4 rot.

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage. FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'figurwahlfuellung.js')

SKRIPT = """
const { Figurwahlfuellung } = await import(MODUL);
const { Figurkataloge } = await import(new URL('./figurkataloge.js', MODUL).href);
const { Figurwahlimporte } = await import(new URL('./figurwahlimporte.js', MODUL).href);

const warte = () => new Promise(r => setTimeout(r, 0));

// --- DOM-Attrappe: ein Behälter mit den beiden Bereichen ------------------------------------
const bereich = () => {
    const ul = { innerHTML: '', kinder: [], appendChild(li) { this.kinder.push(li); } };
    ul.parentElement = { querySelector: () => ({ textContent: '' }) };
    return ul;
};
const baue = () => {
    const uls = { standard: bereich(), gespeichert: bereich() };
    return {
        uls,
        querySelector: (wahl) => {
            const treffer = /ul\\[data-bereich="(\\w+)"\\]/.exec(wahl);
            return treffer ? uls[treffer[1]] : null;
        },
    };
};
globalThis.document = { createElement: () => ({ dataset: {}, className: '', innerHTML: '',
                                                querySelector: () => ({ addEventListener() {} }) }) };
const namen = (b) => b.uls.gespeichert.kinder.map(k => k.name);

const dialogMit = (behaelter) => {
    const dialog = {
        quelle: 'genesis9', gewaehlt: null, gewaehltAufrufe: [],
        _liste: () => behaelter,
        _zeile: (eintrag) => ({ name: eintrag.name }),
        _waehlen(eintrag) { this.gewaehltAufrufe.push(eintrag.name); },
        _einzelnenVorwaehlen() {},
        _pflegen() {},
    };
    return dialog;
};

// --- Abrufe gesteuert ----------------------------------------------------------------------
let modelleAbrufe = 0;
let importeAbrufe = [];            // je Abruf der `resolve`, mit dem der Test antwortet
Figurkataloge.modelle = async () => {
    modelleAbrufe += 1;
    return [{ name: 'A', anzeige: 'A', bereich: 'gespeichert' }];
};
Figurwahlimporte.zeilen = () => new Promise(r => { importeAbrufe.push(r); });
const imp = (name) => ({ name, anzeige: name + ' (Import)', bereich: 'gespeichert', verwaist: true });

// --- 1: Modelle zuerst, Importe danach ------------------------------------------------------
{
    const b = baue();
    const fuellung = new Figurwahlfuellung(dialogMit(b));
    const lauf = fuellung.fuellen('genesis9');
    await warte(); await warte();
    pruefe('Modelle stehen, bevor die Importe da sind', namen(b), ['A']);
    importeAbrufe.at(-1)([imp('i1')]);
    await lauf;
    pruefe('Importe stehen dahinter', namen(b), ['A', 'i1']);
}

// --- 2: die späte Antwort eines überholten Füllens zählt nicht -------------------------------
{
    const b = baue();
    const fuellung = new Figurwahlfuellung(dialogMit(b));
    importeAbrufe = [];
    const alt = fuellung.fuellen('genesis9');
    await warte(); await warte();
    const neu = fuellung.fuellen('genesis9');
    await warte(); await warte();
    pruefe('zwei Abrufe der Importe', importeAbrufe.length, 2);
    importeAbrufe[1]([imp('neu')]);
    await neu;
    importeAbrufe[0]([imp('alt')]);
    await alt;
    pruefe('nur die Importe des letzten Füllens', namen(b), ['A', 'neu']);
}

// --- 3: eine getroffene Wahl wird nach dem Neuaufbau wieder markiert -------------------------
{
    const b = baue();
    const dialog = dialogMit(b);
    const fuellung = new Figurwahlfuellung(dialog);
    importeAbrufe = [];
    const lauf = fuellung.fuellen('genesis9');
    await warte(); await warte();
    dialog.gewaehlt = { quelle: 'genesis9', name: 'A' };
    importeAbrufe.at(-1)([imp('i1')]);
    await lauf;
    pruefe('Wahl neu markiert (nach den Modellen und nach den Importen)', dialog.gewaehltAufrufe, ['A', 'A']);
}

// --- 4: scheitert der Abruf der Modelle, wird nichts anderes angefragt -----------------------
{
    const b = baue();
    const fuellung = new Figurwahlfuellung(dialogMit(b));
    importeAbrufe = [];
    const vorher = Figurkataloge.modelle;
    Figurkataloge.modelle = async () => { throw new Error('kaputt'); };
    await fuellung.fuellen('genesis9');
    Figurkataloge.modelle = vorher;
    pruefe('Fehler steht in der Liste', b.uls.gespeichert.innerHTML.includes('Fehler: kaputt'), true);
    pruefe('keine Importe angefragt', importeAbrufe.length, 0);
}
console.log(JSON.stringify({ok: true}));
"""


class FigurwahlfuellungTest(SimpleTestCase):
    databases = set()

    def test_modelle_zuerst_importe_danach(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
