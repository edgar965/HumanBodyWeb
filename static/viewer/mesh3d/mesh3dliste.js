/**
 * Mesh3dliste — die Tabelle der Aufträge auf `/mesh-3D/` (11.10.2026): Klick auf eine Zeile öffnet den Auftrag, Kästchen und „Gewählte löschen“,
 * und im Takt (4 s) der Stand der laufenden Aufträge, damit Balken und Status ohne Neuladen weiterlaufen.
 *
 * Gelöscht wird über den Endpunkt des Modell-Imports (`/api/character/blendimport/<kennung>/loeschen/`); ein Auftrag, der rechnet, wird dabei nicht
 * angehalten (der Server antwortet 409 — erst auf seiner Seite „Anhalten“).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Mesh3dkopie } from './mesh3dkopie.js';

export class Mesh3dliste {
    static TAKT_MS = 4000;

    static aufbauen() {
        return new Mesh3dliste();
    }

    constructor() {
        this.tabelle = document.querySelector('table.mesh3dtabelle');
        this.alle = document.getElementById('mesh3d-select-all');
        this.loeschen = document.getElementById('mesh3d-bulk-delete');
        this.zaehler = document.getElementById('mesh3d-bulk-count');
        this.meldung = document.getElementById('mesh3d-liste-meldung');
        this._status = {};
        // „Kopie ohne Daten“ / „Kopie mit allen Daten“ für die angehakten Zeilen (wie die Liste von „2D3D Kleider“).
        this.kopie = new Mesh3dkopie(() => this.gewaehlt(), [
            { knopf: 'mesh3d-kopie-ohne', zaehler: 'mesh3d-kopie-ohne-count', mitDaten: false },
            { knopf: 'mesh3d-kopie-alles', zaehler: 'mesh3d-kopie-alles-count', mitDaten: true }]);
        if (!this.tabelle) return;
        this.tabelle.addEventListener('click', e => this.geklickt(e));
        if (this.alle) this.alle.addEventListener('change', () => this.alleWaehlen(this.alle.checked));
        this.loeschen.addEventListener('click', () => this.gewaehlteLoeschen());
        this.takt();
    }

    zeilen() {
        return [...this.tabelle.querySelectorAll('tbody tr[data-id]')];
    }

    gewaehlt() {
        return this.zeilen().filter(z => z.querySelector('.mesh3d-wahl')?.checked).map(z => z.dataset.id);
    }

    geklickt(e) {
        if (e.target.closest('input, a, button, select')) {
            this.zaehlen();
            return;
        }
        const zeile = e.target.closest('tr[data-id]');
        if (zeile) window.location.href = `/mesh-3D/${zeile.dataset.id}/`;
    }

    alleWaehlen(an) {
        this.zeilen().forEach(z => { const k = z.querySelector('.mesh3d-wahl'); if (k) k.checked = an; });
        this.zaehlen();
    }

    zaehlen() {
        const n = this.gewaehlt().length;
        this.zaehler.textContent = String(n);
        this.loeschen.disabled = n === 0;
        this.kopie.anzeigen(n);
    }

    async gewaehlteLoeschen() {
        const kennungen = this.gewaehlt();
        if (!kennungen.length) return;
        if (!window.confirm(`${kennungen.length} Auftrag/Aufträge mit Dateien, Auftrag „Mesh to 3D“ und gespeichertem Modell löschen? Stücke, die ein anderes Modell braucht, bleiben.`)) return;
        this.loeschen.disabled = true;
        const fehler = [];
        for (const k of kennungen) {
            try {
                const antwort = await Serverabruf.senden(`/api/character/blendimport/${k}/loeschen/`, {});
                if (antwort && antwort.error) throw new Error(antwort.error);
            } catch (grund) {
                fehler.push(`${k}: ${grund.message}`);
            }
        }
        if (fehler.length) {
            this.meldung.textContent = `Nicht gelöscht — ${fehler.join(' · ')}`;
            this.zaehlen();
            return;
        }
        window.location.reload();
    }

    /** Laufende Aufträge im Takt nachziehen; wechselt ein Status (fertig, gescheitert …), lädt die Seite einmal neu (Icon, Dauer, Stücke stimmen erst dann). */
    takt() {
        window.setInterval(async () => {
            if (document.hidden) return;
            try {
                const antwort = await Serverabruf.json('/api/mesh3d/laufende/');
                for (const a of antwort.auftraege) {
                    const vorher = this._status[a.kennung];
                    this._status[a.kennung] = a.status;
                    if (vorher && vorher !== a.status) {
                        window.location.reload();
                        return;
                    }
                    if (a.status === 'laeuft') this.balken(a);
                }
            } catch (fehler) { /* stumm gewollt: der nächste Takt versucht es wieder, die Liste steht so lange auf dem alten Stand */ }
        }, Mesh3dliste.TAKT_MS);
    }

    balken(a) {
        const zelle = document.getElementById(`mesh3d-status-${a.kennung}`);
        if (!zelle) return;
        const fuellung = zelle.querySelector('.progress-fill-mini');
        const text = zelle.querySelector('.hb-fortschritt');
        if (fuellung) fuellung.style.width = `${a.fortschritt}%`;
        if (text) text.textContent = `${a.fortschritt} % ${a.detail}`;
    }
}
