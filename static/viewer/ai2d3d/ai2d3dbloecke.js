/**
 * Ai2d3dbloecke — Ampel und Blöcke „Kopf/Körper vorne/seitlich“ der Jobseite (26.10.2026, Edgar: „kannst du die seite etwas aufräumen? … Ziel ist es, dass man sieht, wie weit das
 * Ergebnis noch von der Vorlage ist … Vorne, seitlich, so wie diese Eigenregler für den Kopf aufgebaut sind. Das Gleiche für den Körper“).
 *
 * Daten: `Abnahmebloecke` (koerperpruefung_lauf.py --seite) — `ampel.json` (je Eigenregler und Foto die mittlere Abweichung in mm) und `block_<id>.json` in der Form der Testzeilen.
 * Jeder Block zeigt JEDES seiner Fotos in einer eigenen `Ai2d3dmesspunkte`-Zeile untereinander (27.10.2026, Edgar: „mach eine Zeile für jedes Bild, so dass ich nicht klicken muss“;
 * bis dahin eine Zeile mit Fotowahl). Er folgt nicht der Leiste oben: den Kopf von vorn gibt es nur in 1.jpg. Eine Zelle der Ampel springt zur Zeile ihres Fotos.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Ai2d3dmesspunkte } from './ai2d3dmesspunkte.js';

export class Ai2d3dbloecke {
    constructor(daten) {
        this.daten = daten;
        this.seite = nr => `/api/2d3dai/${daten.id}/abnahme/seite/${nr}/`;
        this.bloecke = new Map([...document.querySelectorAll('[data-block]')].map(karte => {
            const m = new Ai2d3dmesspunkte(karte, daten.id, daten.fotos, { daten: `/api/2d3dai/${daten.id}/abnahme/block/${karte.dataset.block}/`, seite: this.seite });
            const b = { karte, zeilen: new Map() };
            m.bereit.then(() => this._zeilen(b, m));
            return [karte.dataset.block, b];
        }));
        const ampel = document.getElementById('ai2d3d-ampel');
        if (ampel) this._ampel(ampel).catch(fehler => { ampel.querySelector('[data-info]').textContent = `Keine Ampel: ${fehler.message}`; });
    }

    /** Je Foto des Blocks eine Zeile: die der Vorlage nimmt das erste, für die übrigen eine Kopie (Info, drei Felder, Tabelle) mit derselben Datenquelle. */
    _zeilen(b, m) {
        const nrn = Object.keys(m.daten?.fotos || {}).map(Number).sort((x, y) => x - y);
        if (!nrn.length) {
            if (m.daten) m.info.textContent = 'Für diesen Block liegen keine Messungen vor — erst koerperpruefung_lauf.py --seite.';
            return;
        }
        const vorlage = b.karte.querySelector('.ai2d3d-messzeile');
        nrn.forEach((nr, i) => {
            let zeile = m, element = vorlage;
            if (i > 0) {
                element = Object.assign(document.createElement('div'), { className: 'ai2d3d-blockzeile' });
                const kopie = vorlage.cloneNode(true);
                kopie.querySelector('tbody').replaceChildren();
                element.append(m.info.cloneNode(false), kopie);
                b.karte.append(element);
                zeile = new Ai2d3dmesspunkte(element, this.daten.id, this.daten.fotos, { daten: m.daten, seite: this.seite });
            }
            b.zeilen.set(nr, element);
            zeile.zeigen(nr - 1);
        });
    }

    /** Zur Zeile von Bild `nr` (ab 1, Reihenfolge der Abnahme) im Block `block` springen. */
    waehlen(block, nr) {
        this.bloecke.get(block)?.zeilen.get(nr)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
                if (w) td.title = `Grenze ${w.grenze_mm} mm · anklicken: zur Zeile von ${a.dateien[nr]} im Block`;
            }
        }
        rumpf.addEventListener('click', e => {
            const td = e.target.closest('td[data-block]');
            if (td) this.waehlen(td.dataset.block, Number(td.dataset.nr));
        });
        karte.querySelector('[data-ampel]').replaceChildren(tabelle);
    }
}
