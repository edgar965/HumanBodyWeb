/**
 * Mesh3daitestfaelle — Karte „Testfälle der KI“ auf der Test- und der Jobseite (22.10.2026, Server `Mesh3daitestfaelle`).
 * Edgar: „schreibe immer rein, wieviel Fehler von wievielen insgesamt, für alle Prioritäten. Das soll auch in das UI kommen für die trainings und Testjobs. Evtl. auch den Namen der Tests die fehler
 * liefern, aber verständlich und kurzgefasst, in einer Tabelle“.
 * Je Messung (eine Datei `testfaelle.json` neben den Stücken): Kopfzeile (Training oder Test, Lauf, Zeit, Abnahme), je Prio FEHLER von Prüfungen, je Testfall eine Zeile mit Kurztext und dem
 * ersten FEHLER (alle im Tooltip), beim Training der Verlauf der Prio-1-Wache. Texte aus Dateien gehen nur als `textContent` in die Seite.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

const de = n => Number(n).toLocaleString('de-DE');
const BEDINGUNG = { 1: 'muss 0 sein', 2: 'darf nicht mehr werden als vorher', 3: 'wird nur berichtet' };
const NETZ = { deckung: 'Schnitt (wo Stoff liegt)', form: 'Form (Höhe über der Haut)' };
const KURZ = 90;

function el(tag, attribute = {}, ...kinder) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attribute)) if (v !== undefined && v !== null) e.setAttribute(k, v);
    e.append(...kinder.filter(k => k !== null && k !== undefined).map(k => (typeof k === 'object' ? k : String(k))));
    return e;
}

function tabelle(kopf, zeilen) {
    return el('table', { class: 'doku mesh3dai-kleider-tabelle mesh3dai-testfaelle-tabelle' },
        el('thead', {}, el('tr', {}, ...kopf.map(k => el('th', {}, k)))),
        el('tbody', {}, ...zeilen));
}

const von = (fehler, pruefungen) => `${de(fehler)} von ${pruefungen === null || pruefungen === undefined ? '?' : de(pruefungen)}`;

export class Mesh3daitestfaelle {
    constructor(karte) {
        this.karte = karte;
        this.inhalt = karte.querySelector('[data-testfaelle="inhalt"]');
    }

    /** Holt die Testfälle (`{testfaelle: dict | [dict] | null}`) und zeigt sie; ohne Messung bleibt die Karte mit einem Satz stehen. */
    async laden(adresse) {
        try {
            const d = await Serverabruf.json(adresse);
            this.zeigen(d.testfaelle);
        } catch (fehler) {
            this.inhalt.replaceChildren(el('p', { class: 'hb-hinweis' }, `Testfälle nicht lesbar: ${fehler.message}`));
        }
    }

    zeigen(daten) {
        const liste = Array.isArray(daten) ? daten : daten ? [daten] : [];
        if (!liste.length) {
            this.inhalt.replaceChildren(el('p', { class: 'hb-hinweis' }, 'Für diese Stücke liegt noch keine Messung gegen das Ziel vor (sie entsteht beim nächsten Einsatz der Stufe 2).'));
            return;
        }
        this.inhalt.replaceChildren(...liste.map(d => this._messung(d)));
    }

    _messung(d) {
        const a = d.abnahme || {};
        const rolle = d.rolle === 'Training' ? 'Trainingsjob' : 'Testjob';
        const zeit = d.gerechnet ? d.gerechnet.replace('T', ' ').slice(0, 16) : '?';
        const kopf = el('p', {}, el('b', {}, `${rolle} ${d.test} (${d.geschlecht})`), ` · Lauf ${d.lauf} · gemessen ${zeit} · Abnahme: `,
            el('span', { class: a.ok ? 'mesh3dai-gruen' : 'mesh3dai-rot' }, a.ok ? 'OK' : 'NICHT OK'));
        return el('div', { class: 'mesh3dai-testfaelle-messung' }, kopf, this._prios(d), this._tests(d), this._wache(d));
    }

    _prios(d) {
        const je = d.je_prio || {};
        const zeilen = [1, 2, 3].map(p => {
            const z = je[p] || je[String(p)];
            if (!z) return null;
            const rot = z.fehler > 0 && (p === 1 || (p === 2 && z.vorher !== null && z.vorher !== undefined && z.fehler > z.vorher));
            return el('tr', {},
                el('td', {}, `Prio ${p}`),
                el('td', { class: rot ? 'mesh3dai-rot' : z.fehler === 0 ? 'mesh3dai-gruen' : null }, von(z.fehler, z.pruefungen)),
                el('td', {}, `${de(z.tests_rot)} von ${de(z.tests)}`),
                el('td', {}, z.vorher === null || z.vorher === undefined ? '—' : de(z.vorher)),
                el('td', {}, BEDINGUNG[p]));
        });
        return tabelle(['Priorität', 'Fehler von Prüfungen', 'Tests mit Fehlern', 'Fehler vorher', 'Regel'], zeilen);
    }

    _tests(d) {
        const zeilen = (d.tests || []).slice().sort((x, y) => x.prio - y.prio || y.nachher - x.nachher).map(t => {
            const texte = t.fehlertexte || [];
            const erster = texte[0] ? (texte[0].length > KURZ ? `${texte[0].slice(0, KURZ)} …` : texte[0]) : '';
            const mehr = t.nachher > texte.length ? `\n… und ${de(t.nachher - texte.length)} weitere` : '';
            return el('tr', { title: texte.length ? texte.join('\n') + mehr : null },
                el('td', {}, `Prio ${t.prio}`),
                el('td', {}, el('b', {}, t.name)),
                el('td', {}, t.text || ''),
                el('td', { class: t.nachher > 0 ? 'mesh3dai-rot' : 'mesh3dai-gruen' }, von(t.nachher, t.pruefungen)),
                el('td', {}, t.vorher === null || t.vorher === undefined ? '—' : de(t.vorher)),
                el('td', { class: 'mesh3dai-testfaelle-fehler' }, t.geeicht === false ? `Messlatte nicht geeicht. ${erster}` : erster));
        });
        return tabelle(['Prio', 'Test', 'Was geprüft wird', 'Fehler von Prüfungen', 'vorher', 'Erster Fehler (alle im Tooltip)'], zeilen);
    }

    _wache(d) {
        const netze = Object.entries(d.wache || {});
        if (!netze.length) return null;
        const zeilen = [];
        for (const [netz, w] of netze) {
            for (const v of w.verlauf || []) {
                const je = v.je_prio || {};
                const zelle = p => {
                    const z = je[p] || je[String(p)];
                    return z ? von(z.fehler, z.pruefungen) : p === 1 ? von(v.prio1, null) : '—';
                };
                const gewaehlt = v.schritt === w.gewaehlt_schritt;
                zeilen.push(el('tr', { class: gewaehlt ? 'mesh3dai-testfaelle-gewaehlt' : null },
                    el('td', {}, NETZ[netz] || netz),
                    el('td', {}, de(v.schritt)),
                    el('td', { class: v.prio1 > 0 ? 'mesh3dai-rot' : 'mesh3dai-gruen' }, zelle(1)),
                    el('td', {}, zelle(2)),
                    el('td', {}, zelle(3)),
                    el('td', {}, gewaehlt ? 'dieser Stand gewählt' : '')));
            }
        }
        return el('div', {}, el('h3', {}, 'Wache im Training (alle 2.000 Schritte, Fehler von Prüfungen)'),
            tabelle(['Netz', 'Schritt', 'Prio 1', 'Prio 2', 'Prio 3', ''], zeilen));
    }
}
