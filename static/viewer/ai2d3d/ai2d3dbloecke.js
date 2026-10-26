/**
 * Ai2d3dbloecke — Ampel und Blöcke „Kopf/Körper vorne/seitlich“ der Jobseite (26.10.2026, Edgar: „kannst du die seite etwas aufräumen? … Ziel ist es, dass man sieht, wie weit das
 * Ergebnis noch von der Vorlage ist … Vorne, seitlich, so wie diese Eigenregler für den Kopf aufgebaut sind. Das Gleiche für den Körper“).
 *
 * Daten: `Abnahmebloecke` (koerperpruefung_lauf.py --seite) — `ampel.json` (je Eigenregler und Foto die mittlere Abweichung in mm) und `block_<id>.json` in der Form der Testzeilen.
 * Jeder Block ist eine `Ai2d3dmesspunkte`-Zeile mit eigener Fotowahl (er folgt nicht der Leiste oben: der Kopf von vorn gibt es nur in 1.jpg). Eine Zelle der Ampel wählt das Foto im Block.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Ai2d3dmesspunkte } from './ai2d3dmesspunkte.js';

export class Ai2d3dbloecke {
    constructor(daten) {
        this.daten = daten;
        const seite = nr => `/api/2d3dai/${daten.id}/abnahme/seite/${nr}/`;
        this.bloecke = new Map([...document.querySelectorAll('[data-block]')].map(karte => {
            const m = new Ai2d3dmesspunkte(karte, daten.id, daten.fotos, { daten: `/api/2d3dai/${daten.id}/abnahme/block/${karte.dataset.block}/`, seite });
            m.bereit.then(() => this._fotowahl(karte, m));
            return [karte.dataset.block, { karte, m }];
        }));
        const ampel = document.getElementById('ai2d3d-ampel');
        if (ampel) this._ampel(ampel).catch(fehler => { ampel.querySelector('[data-info]').textContent = `Keine Ampel: ${fehler.message}`; });
    }

    _fotowahl(karte, m) {
        const nrn = Object.keys(m.daten?.fotos || {}).map(Number).sort((a, b) => a - b);
        if (!nrn.length) {
            if (m.daten) m.info.textContent = 'Für diesen Block liegen keine Messungen vor — erst koerperpruefung_lauf.py --seite.';
            return;
        }
        const leiste = karte.querySelector('[data-fotowahl]');
        leiste.replaceChildren(...nrn.map(nr => Object.assign(document.createElement('button'),
            { type: 'button', className: 'ai2d3d-fotoknopf', textContent: m.daten.fotos[nr].datei, title: `Bild ${nr}` })));
        leiste.querySelectorAll('button').forEach((k, i) => { k.dataset.nr = nrn[i]; });
        leiste.addEventListener('click', e => {
            const nr = Number(e.target.closest('button[data-nr]')?.dataset.nr);
            if (nr) this.waehlen(karte.dataset.block, nr);
        });
        this.waehlen(karte.dataset.block, nrn[0]);
    }

    /** Block `block` zeigt Bild `nr` (ab 1, Reihenfolge der Abnahme). */
    waehlen(block, nr) {
        const b = this.bloecke.get(block);
        if (!b) return null;
        for (const k of b.karte.querySelectorAll('button[data-nr]')) k.classList.toggle('aktiv', Number(k.dataset.nr) === nr);
        return b.m.zeigen(nr - 1);
    }

    async _ampel(karte) {
        const a = await Serverabruf.json(`/api/2d3dai/${this.daten.id}/abnahme/ampel/`);
        const nrn = Object.keys(a.dateien).map(Number).sort((x, y) => x - y), z = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 });
        const werte = a.zeilen.flatMap(r => Object.values(r.werte));
        karte.querySelector('[data-info]').textContent = `Stand ${a.stand}, gemessen ${a.gerechnet.replace('T', ' ')} · ${a.zeilen.length} Eigenregler, `
            + `${werte.filter(w => w.ueber).length} von ${werte.length} Messungen über der Grenze.`;
        const tabelle = document.createElement('table');
        tabelle.className = 'ai2d3d-kopftabelle';
        tabelle.createTHead().insertRow().append(...['Regler', 'Name', ...nrn.map(nr => a.dateien[nr])].map(t => Object.assign(document.createElement('th'), { textContent: t })));
        const rumpf = tabelle.createTBody();
        let bereich = null;
        for (const r of a.zeilen) {
            if (r.kopf !== bereich) {
                bereich = r.kopf;
                const g = rumpf.insertRow();
                g.className = 'ai2d3d-mess-gruppe';
                Object.assign(g.insertCell(), { colSpan: 2 + nrn.length, textContent: bereich ? 'Kopf' : 'Körper' });
            }
            const tr = rumpf.insertRow();
            tr.insertCell().textContent = r.regler;
            tr.insertCell().textContent = r.titel.replace(`${r.regler} `, '');
            for (const nr of nrn) {
                const w = r.werte[a.dateien[nr]], td = tr.insertCell();
                td.className = `num ${w ? (w.ueber ? 'ai2d3d-ampel-rot' : 'ai2d3d-ampel-gruen') : 'ai2d3d-ampel-leer'}`;
                td.textContent = w ? `${z.format(w.mm)} mm` : '—';
                if (w) Object.assign(td.dataset, { block: w.block, nr: w.nr });
                if (w) td.title = `Grenze ${w.grenze_mm} mm · anklicken: Block zeigt ${a.dateien[nr]}`;
            }
        }
        rumpf.addEventListener('click', e => {
            const td = e.target.closest('td[data-block]');
            if (!td) return;
            this.waehlen(td.dataset.block, Number(td.dataset.nr));
            this.bloecke.get(td.dataset.block)?.karte.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
        karte.querySelector('[data-ampel]').replaceChildren(tabelle);
    }
}
