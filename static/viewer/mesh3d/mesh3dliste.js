/**
 * Mesh3dliste — die Tabellen der Aufträge auf `/mesh-3D/` (11.10.2026): Klick auf eine Zeile öffnet den Auftrag, Kästchen und „Gewählte löschen“,
 * und im Takt (4 s) der Stand der laufenden Aufträge, damit Balken und Status ohne Neuladen weiterlaufen.
 *
 * Seit 13.10.2026 gibt es einen Reiter je Liste (`Mesh3dreiter`): eine Instanz bedient EINE Liste (`.mesh3d-liste`), die Knöpfe stehen als `data-aktion` darin — „Nach … verschieben“
 * legt die gewählten Aufträge in einen anderen Reiter. Der Takt ist einer für alle Listen.
 *
 * Gelöscht wird über den Endpunkt des Modell-Imports (`/api/character/blendimport/<kennung>/loeschen/`); ein Auftrag, der rechnet, wird dabei nicht
 * angehalten (der Server antwortet 409 — erst auf seiner Seite „Anhalten“).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Mesh3dkopie } from './mesh3dkopie.js';

export class Mesh3dliste {
    static TAKT_MS = 4000;
    static VERSCHIEBEN = '/api/mesh3d/reiter/verschieben/';

    static aufbauen() {
        const listen = [...document.querySelectorAll('.mesh3d-liste')].map(feld => new Mesh3dliste(feld));
        if (listen.length) Mesh3dliste.takt();
        return listen;
    }

    /** @param {HTMLElement} feld die Karte einer Liste (Knöpfe `[data-aktion]`, Tabelle `table.mesh3dtabelle`) */
    constructor(feld) {
        this.feld = feld;
        this.tabelle = feld.querySelector('table.mesh3dtabelle');
        this.alle = feld.querySelector('.mesh3d-alle');
        this.meldung = feld.querySelector('.mesh3d-liste-meldung');
        this.loeschen = this.knopf('loeschen');
        this.verschieben = [...feld.querySelectorAll('[data-aktion="verschieben"]')];
        // „Kopie ohne Daten“ / „Kopie mit allen Daten“ für die angehakten Zeilen (wie die Liste von „2D3D Kleider“).
        this.kopie = new Mesh3dkopie(() => this.gewaehlt(), [
            { knopf: this.knopf('kopie-ohne'), zaehler: this.zaehlerVon(this.knopf('kopie-ohne')), mitDaten: false },
            { knopf: this.knopf('kopie-alles'), zaehler: this.zaehlerVon(this.knopf('kopie-alles')), mitDaten: true }]);
        if (!this.tabelle) return;
        this.tabelle.addEventListener('click', e => this.geklickt(e));
        this.tabelle.addEventListener('change', () => this.zaehlen());
        if (this.alle) this.alle.addEventListener('change', () => this.alleWaehlen(this.alle.checked));
        this.loeschen.addEventListener('click', () => this.gewaehlteLoeschen());
        for (const knopf of this.verschieben) knopf.addEventListener('click', () => this.gewaehlteVerschieben(knopf));
        // Chrome stellt die Haken beim Zurückkehren auf die Seite wieder her (Formularzustand, auch aus dem bfcache), ohne ein Ereignis — die Knöpfe standen dann bei „(0)“ und gesperrt,
        // obwohl Zeilen angehakt waren (16.10.2026, Edgar: „Gewählte löschen ist inaktiv“). Also beim Aufbau und bei `pageshow` aus den Haken zählen.
        this.zaehlen();
        window.addEventListener('pageshow', () => this.zaehlen());
    }

    knopf(aktion) {
        return this.feld.querySelector(`[data-aktion="${aktion}"]`);
    }

    zaehlerVon(knopf) {
        return knopf ? knopf.querySelector('.mesh3d-zaehler') : null;
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
        // Ein Klick knapp neben das Kästchen (in seine Zelle) hakt an, statt den Auftrag zu öffnen — so verlor Edgar seine Auswahl (client.log 16.10.2026 12:43:05: `klick td` 5 px neben dem Kästchen, Seite verlassen).
        const kaestchen = e.target.closest('td')?.querySelector('.mesh3d-wahl');
        if (kaestchen) {
            kaestchen.checked = !kaestchen.checked;
            this.zaehlen();
            return;
        }
        const zeile = e.target.closest('tr[data-id]');
        // Der Link der Zeile trägt den Namen im Pfad (`Mesh3dlink`); fehlt er, leitet der Server um.
        if (zeile) window.location.href = zeile.querySelector('a[href^="/mesh-3D/"]')?.getAttribute('href') || `/mesh-3D/${zeile.dataset.id}/`;
    }

    alleWaehlen(an) {
        this.zeilen().forEach(z => { const k = z.querySelector('.mesh3d-wahl'); if (k) k.checked = an; });
        this.zaehlen();
    }

    zaehlen() {
        const n = this.gewaehlt().length;
        this.loeschen.querySelector('.mesh3d-zaehler').textContent = String(n);
        this.loeschen.disabled = n === 0;
        for (const knopf of this.verschieben) {
            knopf.disabled = n === 0;
            this.zaehlerVon(knopf).textContent = String(n);
        }
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

    /** Die angehakten Aufträge in den Reiter des Knopfes legen; danach lädt die Seite neu und bleibt auf diesem Reiter (die Adresse trägt ihn). Ohne Rückfrage — ein Klick auf den anderen Knopf nimmt es zurück. */
    async gewaehlteVerschieben(knopf) {
        const ids = this.gewaehlt();
        if (!ids.length) return;
        for (const k of this.verschieben) k.disabled = true;
        try {
            const antwort = await Serverabruf.senden(Mesh3dliste.VERSCHIEBEN, { ids, reiter: knopf.dataset.ziel });
            if (antwort && antwort.error) throw new Error(antwort.error);
            window.location.reload();
        } catch (fehler) {
            this.meldung.textContent = `Nicht verschoben — ${fehler.daten?.error || fehler.message}`;
            this.zaehlen();
        }
    }

    /** Laufende Aufträge im Takt nachziehen — ein Abruf für alle Listen; wechselt ein Status (fertig, gescheitert …), lädt die Seite einmal neu (Icon, Dauer, Stücke stimmen erst dann). */
    static takt() {
        const status = {};
        window.setInterval(async () => {
            if (document.hidden) return;
            try {
                const antwort = await Serverabruf.json('/api/mesh3d/laufende/');
                for (const a of antwort.auftraege) {
                    const vorher = status[a.kennung];
                    status[a.kennung] = a.status;
                    if (vorher && vorher !== a.status) {
                        window.location.reload();
                        return;
                    }
                    if (a.status === 'laeuft') Mesh3dliste.balken(a);
                }
            } catch (fehler) { /* stumm gewollt: der nächste Takt versucht es wieder, die Liste steht so lange auf dem alten Stand */ }
        }, Mesh3dliste.TAKT_MS);
    }

    static balken(a) {
        const zelle = document.getElementById(`mesh3d-status-${a.kennung}`);
        if (!zelle) return;
        const fuellung = zelle.querySelector('.progress-fill-mini');
        const text = zelle.querySelector('.hb-fortschritt');
        if (fuellung) fuellung.style.width = `${a.fortschritt}%`;
        if (text) text.textContent = `${a.fortschritt} % ${a.detail}`;
    }
}
