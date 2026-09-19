/**
 * Proportionendialog — das Popup, in dem Edgar die Maße einstellt.
 *
 * Edgar (19.09.2026): „Mit einem Popup kommt ein Fenster, wo ich diese
 * anpassen kann. Diese Proportionen nutzt du dann für deine Berechnung."
 *
 * Eine Zeile je Maß (`katalog.proportionen`, 19): Eingabe in cm (leer = keine
 * Vorgabe, das Ziel aus den Bildern gilt), daneben das Ziel wie gemessen, das
 * Modell und die Differenz. Jede Eingabe zeichnet die Vorher-Linie sofort um
 * (`aenderung`), „Übernehmen" legt die Werte am Auftrag ab (POST
 * `proportionen/`), „… und neu berechnen" startet dazu ab „Anpassung" (ab „Zielnetz", wenn
 * Größe oder Gewicht geändert sind) — in der Anpassung formt `Bildmodellzielproportionen`
 * das Zielnetz. Der Augenabstand ist nicht
 * formbar (die Augäpfel folgen dem Käfig nicht) und steht nur zur Ansicht.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Proportionendialog {

    static ANSICHT = { vorn: 'vorn', seite: 'seite', kopf: 'Kopf' };

    constructor(auftrag, katalog, aenderung) {
        this.auftrag = auftrag;
        this.katalog = katalog || {};
        this.aenderung = aenderung || (() => {});
        this.dialog = document.getElementById('proportionen-dialog');
        this.eingaben = { ...((auftrag.zustand.optionen || {}).proportionen || {}) };
        if (!this.dialog) return;
        this.tabelle = this.dialog.querySelector('tbody');
        this.dialog.querySelector('[data-tat="uebernehmen"]')?.addEventListener('click', () => this.uebernehmen(false));
        this.dialog.querySelector('[data-tat="rechnen"]')?.addEventListener('click', () => this.uebernehmen(true));
        this.dialog.querySelector('[data-tat="alle-loeschen"]')?.addEventListener('click', () => this.alleLoeschen());
        this.dialog.querySelector('[data-tat="schliessen"]')?.addEventListener('click', () => this.dialog.close());
    }

    /** `{schluessel: cm}` der ausgefüllten Felder. */
    werte() {
        const aus = {};
        for (const [k, v] of Object.entries(this.eingaben)) {
            if (v !== null && v !== undefined && v !== '' && Number.isFinite(Number(v))) aus[k] = Number(v);
        }
        return aus;
    }

    /** `mass`: dieses Maß bekommt den Fokus (Klick auf die Linie im Bild). */
    oeffnen(daten, mass = null) {
        if (!this.dialog || !daten) return;
        this.daten = daten;
        this.tabelle.innerHTML = '';
        const [lo, hi] = this.katalog.proportion_cm || [0.5, 120];
        for (const m of this.katalog.proportionen || []) {
            const k = m.schluessel;
            const ziel = daten.ziel[k], modell = daten.modell[k];
            const tr = document.createElement('tr');
            tr.dataset.mass = k;
            const wert = this.eingaben[k] ?? '';
            const diff = (ziel !== undefined && modell !== undefined) ? (modell - ziel).toFixed(1) : '–';
            const formung = (daten.formung || {})[k];
            const hinweis = !m.formbar ? '<span class="hb-hinweis">nur Ansicht — Augäpfel folgen nicht</span>'
                : formung ? `<span class="hb-hinweis">geformt ${formung.vorher} → ${formung.nachher} cm</span>` : '';
            tr.innerHTML = `<th>${m.name}<br><span class="hb-hinweis">${Proportionendialog.ANSICHT[m.ansicht] || m.ansicht}</span></th>`
                + `<td><input type="number" step="0.1" min="${lo}" max="${hi}" value="${wert}" placeholder="${ziel ?? ''}" ${m.formbar ? '' : 'disabled'}>`
                + `<button type="button" class="btn btn-sm btn-secondary" data-tat="leeren" title="Vorgabe löschen — Ziel aus den Bildern">×</button></td>`
                + `<td>${ziel !== undefined ? ziel.toFixed(1) : '–'}</td><td>${modell !== undefined ? modell.toFixed(1) : '–'}</td>`
                + `<td>${diff}</td><td>${hinweis}</td>`;
            const input = tr.querySelector('input');
            input.addEventListener('input', () => {
                this.eingaben[k] = input.value === '' ? null : Number(input.value);
                this.aenderung();
            });
            tr.querySelector('[data-tat="leeren"]').addEventListener('click', () => {
                input.value = '';
                this.eingaben[k] = null;
                this.aenderung();
            });
            this.tabelle.appendChild(tr);
        }
        this.dialog.showModal();
        if (mass) {
            const feld = this.tabelle.querySelector(`tr[data-mass="${mass}"] input`);
            if (feld && !feld.disabled) { feld.focus(); feld.select(); feld.closest('tr').scrollIntoView({ block: 'center' }); }
        }
    }

    alleLoeschen() {
        this.eingaben = {};
        for (const i of this.tabelle.querySelectorAll('input')) i.value = '';
        this.aenderung();
    }

    async uebernehmen(rechnen) {
        const proportionen = this.werte();
        try {
            const antwort = await Serverabruf.senden(this.auftrag.adresse('proportionen/'), { proportionen });
            if (antwort.error) throw new Error(antwort.error);
            this.auftrag.zustand.optionen = { ...(this.auftrag.zustand.optionen || {}), proportionen: antwort.proportionen };
            this.eingaben = { ...antwort.proportionen };
            this.dialog.close();
            this.aenderung();
            if (rechnen) {
                // Größe/Gewicht unverändert: das Zielnetz steht, ab „Anpassung" reicht (spart den Zielschritt).
                const p = window.__bildmodell?.person;
                if (p) await p.neuBerechnen(p.unveraendert() ? 'anpassung' : 'ziel');
            }
        } catch (fehler) {
            window.alert(`Proportionen nicht übernommen: ${fehler.message}`);
        }
    }
}
